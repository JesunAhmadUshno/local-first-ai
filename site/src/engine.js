// In-browser port of the repo's retrieval pipeline.
// Mirrors level-1-learn/local_first.py (tokenize, idf, tf-idf, cosine) and
// level-2-build/assistant.py (ingest, chunking, ranking, answer, refusal, evaluate),
// plus level-3-deep/study.py (modelled cost) and level-3-deep/rigor.py (Wilson,
// leave-one-out threshold). engine.check.mjs asserts it reproduces the recorded results.

export const STOPWORDS = new Set([
  'a', 'an', 'the', 'and', 'or', 'of', 'to', 'in', 'on', 'for',
  'with', 'without', 'before', 'after', 'over', 'between',
  'during', 'until', 'away', 'from', 'is', 'are', 'it', 'its',
  'let', 'how', 'what', 'does', 'do', 'should', 'be',
]);
export const CHUNK_SIZE_WORDS = 30;
export const CHUNK_OVERLAP_WORDS = 10;
export const REFUSAL_THRESHOLD = 0.30;
export const ANSWER_SENTENCES = 2;
export const REFUSAL_TEXT = 'No evidence in the local documents for this question.';

// Python 3.12 sum() over floats uses Neumaier compensated summation; mirror it.
export function pysum(values) {
  let s = 0, c = 0;
  for (const x of values) {
    const t = s + x;
    if (Math.abs(s) >= Math.abs(x)) c += (s - t) + x; else c += (x - t) + s;
    s = t;
  }
  return c && Number.isFinite(c) ? s + c : s;
}

export function tokenize(text) {
  return (text.toLowerCase().match(/[a-z0-9]+/g) || []).filter((t) => !STOPWORDS.has(t));
}

// Smoothed idf: log((1 + N) / (1 + df)) + 1, over docs given as plain texts.
export function computeIdf(texts) {
  const df = new Map();
  for (const text of texts) for (const t of new Set(tokenize(text))) df.set(t, (df.get(t) || 0) + 1);
  const n = texts.length, idf = new Map();
  for (const [t, c] of df) idf.set(t, Math.log((1 + n) / (1 + c)) + 1.0);
  return idf;
}

// Map keeps first-seen order, like Python's Counter, so float sums run in the same order.
export function tfidfVector(text, idf) {
  const tokens = tokenize(text);
  const vec = new Map();
  if (!tokens.length) return vec;
  const counts = new Map();
  for (const t of tokens) counts.set(t, (counts.get(t) || 0) + 1);
  for (const [t, c] of counts) if (idf.has(t)) vec.set(t, (c / tokens.length) * idf.get(t));
  return vec;
}

export function cosine(a, b) {
  if (!a.size || !b.size) return 0.0;
  const dot = pysum([...a].map(([t, v]) => v * (b.get(t) || 0.0)));
  const na = Math.sqrt(pysum([...a.values()].map((v) => v * v)));
  const nb = Math.sqrt(pysum([...b.values()].map((v) => v * v)));
  if (na === 0 || nb === 0) return 0.0;
  return dot / (na * nb);
}

const cmp = (x, y) => (x < y ? -1 : x > y ? 1 : 0); // Python string order, not localeCompare

export function splitSentences(text) {
  return (text.match(/[^.!?]+[.!?]/g) || []).map((s) => s.trim()).filter(Boolean);
}

// files: { 'B01.txt': raw text, ... } -> Learn style documents, sorted by file name.
export function ingest(files) {
  return Object.keys(files).sort(cmp).map((name) => {
    const lines = files[name].split(/\r\n|\r|\n/);
    if (!lines[0].startsWith('Title: ')) throw new Error(`${name}: first line must be 'Title: <title>'`);
    const body = lines.slice(1).map((l) => l.trim()).filter(Boolean).join(' ');
    return { id: name.replace(/\.txt$/, ''), title: lines[0].slice(7).trim(), sentences: splitSentences(body) };
  });
}

export function chunkDocument(doc, size = CHUNK_SIZE_WORDS, overlap = CHUNK_OVERLAP_WORDS) {
  const words = doc.sentences.join(' ').split(/\s+/).filter(Boolean);
  const step = size - overlap, chunks = [];
  let start = 0, index = 0;
  while (start < words.length) {
    const end = Math.min(start + size, words.length);
    chunks.push({ chunk_id: `${doc.id}-C${index + 1}`, doc_id: doc.id, title: doc.title, start_word: start, end_word: end, text: words.slice(start, end).join(' ') });
    index += 1;
    if (end === words.length) break;
    start += step;
  }
  return chunks;
}

export class ChunkIndex {
  constructor(docs, size = CHUNK_SIZE_WORDS, overlap = CHUNK_OVERLAP_WORDS) {
    if (!(Number.isInteger(size) && size >= 1 && Number.isInteger(overlap) && overlap >= 0 && overlap < size)) throw new Error('overlap must be in [0, chunk size)');
    this.docs = docs;
    this.chunks = docs.flatMap((d) => chunkDocument(d, size, overlap));
    this.idf = computeIdf(this.chunks.map((c) => c.text));
    this.vectors = new Map(this.chunks.map((c) => [c.chunk_id, tfidfVector(c.text, this.idf)]));
    this.byId = new Map(docs.map((d) => [d.id, d]));
  }
  retrieve(question, topK = 3) {
    const q = tfidfVector(question, this.idf);
    const scored = this.chunks.map((c) => ({ chunk_id: c.chunk_id, doc_id: c.doc_id, text: c.text, score: cosine(q, this.vectors.get(c.chunk_id)) }));
    scored.sort((a, b) => b.score - a.score || cmp(a.chunk_id, b.chunk_id));
    return scored.slice(0, topK);
  }
  bestSentences(doc, question, count = ANSWER_SENTENCES) {
    const q = tfidfVector(question, this.idf);
    const scored = doc.sentences.map((s, i) => ({ sentence_id: `S${i + 1}`, text: s, score: cosine(q, tfidfVector(s, this.idf)), index: i }));
    scored.sort((a, b) => b.score - a.score || a.index - b.index);
    return scored.slice(0, count);
  }
  answer(question, threshold = REFUSAL_THRESHOLD) {
    const ranked = this.retrieve(question, 3);
    const best = ranked[0];
    if (best.score < threshold) return { refused: true, ranked, best_score: best.score, sentences: [], answer_text: REFUSAL_TEXT };
    const doc = this.byId.get(best.doc_id);
    const sentences = this.bestSentences(doc, question).map((e) => ({ ...e, doc_id: doc.id, citation: `[${doc.id} ${e.sentence_id}]` }));
    return { refused: false, ranked, best_score: best.score, doc_id: doc.id, title: doc.title, sentences, answer_text: sentences.map((s) => `${s.text} ${s.citation}`).join(' ') };
  }
}

// Mirrors assistant.evaluate(): rows plus the summary counts.
export function evaluate(index, questions, threshold = REFUSAL_THRESHOLD) {
  const rows = questions.map((item) => {
    const ranked = index.retrieve(item.question, 3);
    const docs = ranked.map((e) => e.doc_id);
    const res = index.answer(item.question, threshold);
    const ev = item.gold_doc !== 'NONE';
    const first = res.sentences[0];
    return {
      question_id: item.question_id, question: item.question, gold_doc: item.gold_doc, gold_sentence: item.gold_sentence, is_evidence: ev,
      top1_doc: docs[0], top3_chunk_docs: docs, top1_score: ranked[0].score,
      hit_at_1: ev && docs[0] === item.gold_doc, chunk_hit_at_3: ev && docs.includes(item.gold_doc), refused: res.refused,
      answer_sentence: first ? first.sentence_id : null,
      sentence_correct: !!(ev && first && first.sentence_id === item.gold_sentence && first.doc_id === item.gold_doc),
      answer_text: res.answer_text,
    };
  });
  return { rows, summary: summarize(rows, index.chunks.length) };
}

export function summarize(rows, chunks) {
  const ev = rows.filter((r) => r.is_evidence);
  const tp = rows.filter((r) => r.refused && !r.is_evidence).length;
  const fp = rows.filter((r) => r.refused && r.is_evidence).length;
  const fn = rows.filter((r) => !r.refused && !r.is_evidence).length;
  return {
    chunks, questions: rows.length, evidence_questions: ev.length, no_evidence_questions: rows.length - ev.length,
    top1_correct: ev.filter((r) => r.hit_at_1).length, chunk_recall_at_3_correct: ev.filter((r) => r.chunk_hit_at_3).length,
    sentence_correct: ev.filter((r) => r.sentence_correct).length,
    refusal_true_positive: tp, refusal_false_positive: fp, refusal_false_negative: fn,
    refusal_precision: tp + fp ? tp / (tp + fp) : 0, refusal_recall: tp + fn ? tp / (tp + fn) : 0,
  };
}

// Refusal metrics at any threshold from recorded or live top-1 scores (refuse when score < t).
export function refusalAt(scores, isEvidence, t) {
  let tp = 0, fp = 0, fn = 0;
  scores.forEach((s, i) => {
    const r = s < t;
    if (r && !isEvidence[i]) tp++; else if (r && isEvidence[i]) fp++; else if (!r && !isEvidence[i]) fn++;
  });
  return { tp, fp, fn, refused: tp + fp, precision: tp + fp ? tp / (tp + fp) : 0, recall: tp + fn ? tp / (tp + fn) : 0 };
}

// Mirrors rigor.fit_threshold and rigor.leave_one_out_threshold.
export function fitThreshold(scores, isEvidence) {
  const none = scores.filter((_, i) => !isEvidence[i]), ev = scores.filter((_, i) => isEvidence[i]);
  return (Math.max(...none) + Math.min(...ev)) / 2;
}
export function leaveOneOut(scores, isEvidence) {
  let tp = 0, fp = 0, fn = 0;
  const ts = scores.map((s, i) => {
    const t = fitThreshold(scores.filter((_, j) => j !== i), isEvidence.filter((_, j) => j !== i));
    const r = s < t;
    if (r && !isEvidence[i]) tp++; else if (r && isEvidence[i]) fp++; else if (!r && !isEvidence[i]) fn++;
    return t;
  });
  return { refusal_true_positive: tp, refusal_false_positive: fp, refusal_false_negative: fn, threshold_min: Math.min(...ts), threshold_max: Math.max(...ts) };
}

export const Z95 = 1.959963984540054;
// Mirrors rigor.wilson: Wilson score interval for k of n.
export function wilson(k, n, z = Z95) {
  const p = k / n, d = 1 + (z * z) / n;
  const centre = (p + (z * z) / (2 * n)) / d;
  const half = (z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n))) / d;
  return [Math.max(0, centre - half), Math.min(1, centre + half)];
}

// Mirrors study.cost_for_tokens: modelled USD per query at published per-million rates.
export function costPerQuery(row, inTokens, outTokens) {
  return (inTokens / 1000000.0) * row.input_rate + (outTokens / 1000000.0) * row.output_rate;
}

// The labelled set exactly as recorded in results_build.json (nothing retyped).
export function questionsFrom(results) {
  return results.questions.map((q) => ({ question_id: q.question_id, question: q.question, gold_doc: q.gold_doc, gold_sentence: q.gold_sentence }));
}

// The Learn corpus and questions are defined in local_first.py source; read them from it.
export function parseLearnSource(src) {
  const docs = [...src.matchAll(/\{"id": "(D\d+)", "title": "([^"]+)", "sentences": \[([\s\S]*?)\]\}/g)]
    .map((m) => ({ id: m[1], title: m[2], sentences: [...m[3].matchAll(/"([^"]+)"/g)].map((s) => s[1]) }));
  const questions = [...src.matchAll(/\{"id": "(Q\d+)", "question": "([^"]+)",\s*"gold_doc": "(D\d+)", "gold_sentence": "(S\d+)"\}/g)]
    .map((m) => ({ id: m[1], question: m[2], gold_doc: m[3], gold_sentence: m[4] }));
  return { docs, questions };
}

// Learn level: document level index and one best sentence (local_first.LocalIndex).
export function learnAnswer(docs, question) {
  const texts = docs.map((d) => d.sentences.join(' '));
  const idf = computeIdf(texts);
  const q = tfidfVector(question, idf);
  const ranked = docs.map((d, i) => ({ doc_id: d.id, score: cosine(q, tfidfVector(texts[i], idf)) }))
    .sort((a, b) => b.score - a.score || cmp(a.doc_id, b.doc_id));
  const doc = docs.find((d) => d.id === ranked[0].doc_id);
  let best = null;
  doc.sentences.forEach((s, i) => { const sc = cosine(q, tfidfVector(s, idf)); if (!best || sc > best.score) best = { i, score: sc }; });
  return { top1_doc: ranked[0].doc_id, top1_score: ranked[0].score, top3: ranked.slice(0, 3).map((r) => r.doc_id), answer_sentence: `S${best.i + 1}` };
}

// "Grade: 7,100 of 10,000" from a level README.
export function parseGrade(md) {
  const m = md.match(/^Grade: ([\d,]+) of 10,000/m);
  return m ? Number(m[1].replace(/,/g, '')) : null;
}

// Bullets under a "## <heading>" in a README, joined across wrapped lines.
export function bullets(md, heading) {
  const start = md.indexOf(`## ${heading}`);
  if (start < 0) return [];
  const rest = md.slice(start).split('\n').slice(1);
  const end = rest.findIndex((l) => l.startsWith('## '));
  const block = (end < 0 ? rest : rest.slice(0, end)).join('\n');
  return block.split(/\n- /).slice(1).map((b) => b.replace(/\s*\n\s*/g, ' ').trim());
}

// The `run:` commands of ci.yml, in order.
export function ciCommands(yml) {
  return [...yml.matchAll(/^\s+run: (python .+)$/gm)].map((m) => m[1].trim());
}
