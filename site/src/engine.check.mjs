// Known-answer check, run by `npm run build` before vite. It fails the build if the
// in-browser port drifts from the Python pipeline's recorded results.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  ChunkIndex, ingest, evaluate, questionsFrom, refusalAt, leaveOneOut, fitThreshold, wilson,
  costPerQuery, parseLearnSource, learnAnswer, parseGrade, bullets, ciCommands, REFUSAL_THRESHOLD,
} from './engine.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8');
const json = (p) => JSON.parse(read(p));
const build = json('level-2-build/results_build.json');
const learn = json('level-1-learn/results_learn.json');
const deep = json('level-3-deep/results_deep.json');
const rigor = json('level-3-deep/results_rigor.json');
const dataDir = path.join(root, 'level-2-build/data');
const files = Object.fromEntries(fs.readdirSync(dataDir).filter((n) => n.endsWith('.txt')).map((n) => [n, fs.readFileSync(path.join(dataDir, n), 'utf8')]));

// 1. Build pipeline parity: every recorded question, to 1e-9 on the score.
const docs = ingest(files);
assert.equal(docs.length, build.summary.documents);
assert.deepEqual(docs.map((d) => d.sentences.length), build.inventory.map((r) => r.sentences));
assert.deepEqual(docs.map((d) => d.sentences.join(' ').split(/\s+/).length), build.inventory.map((r) => r.words));
const index = new ChunkIndex(docs);
assert.equal(index.chunks.length, build.summary.chunks);
const questions = questionsFrom(build);
const live = evaluate(index, questions);
let maxDiff = 0;
live.rows.forEach((r, i) => {
  const rec = build.questions[i];
  maxDiff = Math.max(maxDiff, Math.abs(r.top1_score - rec.top1_score));
  assert.ok(Math.abs(r.top1_score - rec.top1_score) < 1e-9, `${rec.question_id} score ${r.top1_score} vs ${rec.top1_score}`);
  for (const k of ['top1_doc', 'refused', 'answer_sentence', 'answer_text', 'hit_at_1', 'chunk_hit_at_3', 'sentence_correct'])
    assert.deepEqual(r[k], rec[k], `${rec.question_id} ${k}`);
  assert.deepEqual(r.top3_chunk_docs, rec.top3_chunk_docs, `${rec.question_id} top3`);
});
for (const k of Object.keys(live.summary)) if (k in build.summary) assert.equal(live.summary[k], build.summary[k], `summary ${k}`);

// 2. Learn level parity: corpus and questions read from local_first.py source.
const L = parseLearnSource(read('level-1-learn/local_first.py'));
assert.equal(L.docs.length, learn.summary.documents);
assert.equal(L.questions.length, learn.summary.questions);
L.questions.forEach((q, i) => {
  const r = learnAnswer(L.docs, q.question), rec = learn.questions[i];
  assert.equal(q.question, rec.question);
  assert.equal(r.top1_doc, rec.top1_doc, `${q.id} top1`);
  assert.ok(Math.abs(r.top1_score - rec.top1_score) < 1e-9, `${q.id} score`);
  assert.deepEqual(r.top3, rec.top3_docs, `${q.id} top3`);
  assert.equal(r.answer_sentence, rec.answer_sentence, `${q.id} sentence`);
});

// 3. Threshold explorer and held-out threshold against results_rigor.json.
const scores = live.rows.map((r) => r.top1_score), isEv = live.rows.map((r) => r.is_evidence);
const at = refusalAt(scores, isEv, REFUSAL_THRESHOLD);
assert.equal(at.precision, build.summary.refusal_precision);
assert.equal(at.recall, build.summary.refusal_recall);
for (const c of rigor.threshold.curve) {
  const m = refusalAt(scores, isEv, c.threshold);
  assert.deepEqual([m.refused, m.tp, m.fp, m.fn], [c.refused, c.true_refusals, c.false_refusals, c.missed_refusals], `curve at ${c.threshold}`);
}
assert.ok(Math.abs(fitThreshold(scores, isEv) - rigor.threshold.fitted_on_all_24) < 1e-9);
const loo = leaveOneOut(scores, isEv);
for (const k of ['refusal_true_positive', 'refusal_false_positive', 'refusal_false_negative']) assert.equal(loo[k], rigor.threshold.leave_one_out[k], `loo ${k}`);
assert.ok(Math.abs(loo.threshold_min - rigor.threshold.leave_one_out.threshold_min) < 1e-9);

// 4. Chunk size / overlap explorer: every recorded sweep row.
for (const row of rigor.chunk_sweep) {
  const s = evaluate(new ChunkIndex(docs, row.chunk_size, row.overlap), questions).summary;
  for (const k of ['chunks', 'top1_correct', 'chunk_recall_at_3_correct', 'sentence_correct', 'refusal_true_positive', 'refusal_false_positive'])
    assert.equal(s[k], row[k], `sweep ${row.chunk_size}/${row.overlap} ${k}`);
}

// 5. Hard set: live rerun matches the recorded rows.
for (const r of rigor.hard_set.rows) {
  const res = index.answer(r.question);
  assert.equal(res.ranked[0].doc_id, r.top1_doc, `${r.id} top1`);
  assert.ok(Math.abs(res.ranked[0].score - r.top1_score) < 1e-9, `${r.id} score`);
  assert.equal(res.refused, r.refused, `${r.id} refused`);
}

// 6. Wilson intervals match the Python helper.
for (const [name, iv] of Object.entries(rigor.intervals)) {
  const [lo, hi] = wilson(iv.k, iv.n);
  assert.ok(Math.abs(lo - iv.wilson95[0]) < 1e-12 && Math.abs(hi - iv.wilson95[1]) < 1e-12, `wilson ${name}`);
}

// 7. Cost calculator reproduces study.py for all six modelled rows.
const tm = deep.token_model;
for (const row of deep.cloud_costs_modelled.rows) {
  const c = costPerQuery(row, tm.mean_input_tokens_est, tm.mean_output_tokens_est);
  assert.ok(Math.abs(c - row.cost_per_query_usd) < 1e-15, `${row.model} cost ${c} vs ${row.cost_per_query_usd}`);
  assert.ok(Math.abs(c * 100000 - row.cost_per_100000_queries_usd) < 1e-9, `${row.model} 100k`);
}
const meanIn = tm.per_query.reduce((a, r) => a + r.input_tokens_est, 0) / tm.per_query.length;
assert.ok(Math.abs(meanIn - tm.mean_input_tokens_est) < 1e-12, 'per-query tokens average to the recorded mean');

// 8. Text parsed from the repo docs: grades, limits, CI commands.
const grades = ['level-1-learn', 'level-2-build', 'level-3-deep'].map((l) => parseGrade(read(`${l}/README.md`)));
assert.ok(grades.every(Number.isFinite), 'three grades parsed');
assert.ok(read('docs/index.md').includes(`Learn ${grades[0].toLocaleString('en-US')}, Build ${grades[1].toLocaleString('en-US')}, Deep ${grades[2].toLocaleString('en-US')}`), 'grades agree with docs/index.md');
assert.ok(bullets(read('level-2-build/README.md'), 'Failure modes and limits').length >= 8, 'build limits parsed');
assert.ok(bullets(read('level-3-deep/README.md'), 'Failure modes and limits').length >= 6, 'deep limits parsed');
assert.ok(ciCommands(read('.github/workflows/ci.yml')).some((c) => c.includes('run_build.py')), 'ci commands parsed');

console.log('engine ok', { questions: live.rows.length, maxScoreDiff: maxDiff, learn: L.questions.length, sweepRows: rigor.chunk_sweep.length, hardRows: rigor.hard_set.rows.length, grades });
