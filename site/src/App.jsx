import { useMemo, useState, useEffect, useRef, useId, useCallback } from 'react';
import build from '../../level-2-build/results_build.json';
import learn from '../../level-1-learn/results_learn.json';
import deep from '../../level-3-deep/results_deep.json';
import rigor from '../../level-3-deep/results_rigor.json';
import learnReadme from '../../level-1-learn/README.md?raw';
import buildReadme from '../../level-2-build/README.md?raw';
import deepReadme from '../../level-3-deep/README.md?raw';
import ciYml from '../../.github/workflows/ci.yml?raw';
import {
  ChunkIndex, ingest, evaluate, questionsFrom, refusalAt, leaveOneOut, wilson, costPerQuery,
  parseGrade, bullets, ciCommands, REFUSAL_THRESHOLD, CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS,
} from './engine.js';

// The real corpus, read from level-2-build/data at build time.
const files = Object.fromEntries(Object.entries(import.meta.glob('../../level-2-build/data/*.txt', { query: '?raw', import: 'default', eager: true }))
  .map(([p, text]) => [p.split('/').pop(), text]));
const DOCS = ingest(files);
const INDEX = new ChunkIndex(DOCS);
const QUESTIONS = questionsFrom(build);
const HARD = rigor.hard_set.rows;
const RECORDED = build.questions;
const S = build.summary;
const T = deep.timing;
const BUILD_LIMITS = bullets(buildReadme, 'Failure modes and limits');
const DEEP_LIMITS = bullets(deepReadme, 'Failure modes and limits');
const GRADES = [['Learn', parseGrade(learnReadme), 'level-1-learn/README.md'], ['Build', parseGrade(buildReadme), 'level-2-build/README.md'], ['Deep', parseGrade(deepReadme), 'level-3-deep/README.md']];

const REPO = 'https://github.com/JesunAhmadUshno/local-first-ai';
const blob = (p) => `${REPO}/blob/main/${p}`;
const pct = (x, d = 0) => `${(x * 100).toFixed(d)}%`;
const fmt = (n) => Math.round(n).toLocaleString('en-US');
const ms = (v) => (v >= 100 ? `${fmt(v)} ms` : v >= 1 ? `${v.toFixed(2)} ms` : `${v.toFixed(3)} ms`);
const usd = (v) => (v === 0 ? '0 USD' : v >= 100 ? `${fmt(v)} USD` : v >= 1 ? `${v.toFixed(2)} USD` : `${v.toPrecision(3)} USD`);
const ivText = (k, n) => { const [lo, hi] = wilson(k, n); return `Wilson 95% ${lo.toFixed(2)} to ${hi.toFixed(2)}`; };

const SECTIONS = [['top', 'Overview', '◎'], ['ask', 'Ask your files', '?'], ['eval', 'Evaluation', '✓'], ['threshold', 'Refusal threshold', '⊣'], ['chunking', 'Chunking', '▤'], ['cost', 'Cost', '$'], ['latency', 'Speed', '◷'], ['privacy', 'Privacy audit', '⌂'], ['verdict', 'Verdict and limits', '≡'], ['reproduce', 'Reproduce', '❯_']];

function useReveal() {
  useEffect(() => {
    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.08 });
    els.forEach((e) => io.observe(e));
    return () => io.disconnect();
  }, []);
}

function MenuBar() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const t = setInterval(() => setNow(new Date()), 30000); return () => clearInterval(t); }, []);
  return (
    <div className="menubar" role="banner">
      <span className="apple" aria-hidden="true">◆</span>
      <a className="app" href="#top">Local-First Lab</a>
      <a className="m" href={blob('level-1-learn/README.md')}>Learn</a>
      <a className="m" href={blob('level-2-build/README.md')}>Build</a>
      <a className="m" href={blob('level-3-deep/README.md')}>Deep</a>
      <a className="m" href={blob('docs/research-review.md')}>Research review</a>
      <span className="spacer" />
      <span className="status"><i /> Runs offline</span>
      <a href={REPO}>GitHub ↗</a>
      <span className="clock">{now.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' })}</span>
    </div>
  );
}

function Dock() {
  const [active, setActive] = useState('top');
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && setActive(e.target.id)), { rootMargin: '-45% 0px -50% 0px' });
    SECTIONS.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    return () => io.disconnect();
  }, []);
  return (
    <nav className="dock" aria-label="Sections">
      {SECTIONS.map(([id, label, icon]) => (
        <a key={id} href={`#${id}`} className={active === id ? 'on' : ''} aria-current={active === id ? 'true' : undefined} aria-label={label}>
          <span className="ico" aria-hidden="true">{icon}</span><span className="lbl">{label}</span>
        </a>
      ))}
    </nav>
  );
}

function Range({ label, value, min, max, step, onChange, show }) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label} <span>{show}</span></label>
      <input id={id} type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} />
    </div>
  );
}

export default function App() {
  useReveal();
  // Load every font face up front so the request counter in "Ask" sees only requests made by a question.
  useEffect(() => { document.fonts?.load?.('italic 20px "Instrument Serif"'); document.fonts?.load?.('500 12px "JetBrains Mono"'); }, []);
  return (
    <div className="wrap">
      <MenuBar />
      <div className="glow" aria-hidden="true" />
      <Hero />
      <Ask />
      <Evaluation />
      <Threshold />
      <Chunking />
      <Cost />
      <Latency />
      <Privacy />
      <Verdict />
      <Reproduce />
      <Dock />
      <footer>
        Corpus: 24 synthetic documents committed in <code>level-2-build/data</code>. Code: Apache-2.0. Every number on this page is read from the repo's results and README files at build time or computed live in your browser by a port that the build checks against those results.
      </footer>
    </div>
  );
}

function Hero() {
  return (
    <header className="card hero window" id="top" data-title="local-first.app — README">
      <div className="head">
        <p className="eyebrow">Learn · Build · Deep · one offline study</p>
        <span className="pill good">● {build.audit.total_matches} network patterns found</span>
      </div>
      <h1>A private assistant whose answers stay <em>home</em>.</h1>
      <p className="sub">
        On {S.documents} local documents it found the right document for {S.top1_correct} of {S.evidence_questions} evidence questions and refused {S.refusal_true_positive} of {S.no_evidence_questions} it had no evidence for,
        in a mean of {ms(T.answer_latency_ms_mean)} per answer. Hosted APIs would cost from {usd(Math.min(...deep.cloud_costs_modelled.rows.map((r) => r.cost_per_100000_queries_usd)))} to {usd(Math.max(...deep.cloud_costs_modelled.rows.map((r) => r.cost_per_100000_queries_usd)))} per 100,000 queries, <b>modelled</b> from pricing checked {deep.pricing_checked}, not measured.
      </p>
      <div className="banner" role="note">
        <b>No language model ran.</b> {deep.ollama.check}. The core is extractive TF-IDF over chunks, and the {S.documents} documents are synthetic, written to stand in for a private folder.
      </div>
      <div className="actions">
        <a className="btn primary" href="#ask">Ask the documents</a>
        <a className="btn ghost" href={blob('docs/research-review.md')}>Read the research review</a>
        <span className="hint">The pipeline on this page runs in your browser and matches the Python results to the last digit.</span>
      </div>
      <div className="tiles">
        <div className="tile"><div className="num">{S.top1_correct}/{S.evidence_questions}</div><div className="cap">Top-1 document correct. {ivText(S.top1_correct, S.evidence_questions)}</div></div>
        <div className="tile"><div className="num">{S.sentence_correct}/{S.evidence_questions}</div><div className="cap">Answer sentence correct. {ivText(S.sentence_correct, S.evidence_questions)}</div></div>
        <div className="tile"><div className="num">{S.refusal_true_positive}/{S.no_evidence_questions}</div><div className="cap">No-evidence questions refused, {S.refusal_false_positive} false refusals. {ivText(S.refusal_true_positive, S.no_evidence_questions)}</div></div>
        <div className="tile"><div className="num">{T.answer_latency_ms_mean.toFixed(2)}<small> ms</small></div><div className="cap">Mean answer latency, {T.queries_timed} recorded answers on the study VM</div></div>
      </div>
      <p className="hint caveat">Read the perfect scores as weak evidence. From the Build README: “{BUILD_LIMITS[0]}”</p>
    </header>
  );
}

function useRequestCounter() {
  const since = useRef(null);
  const [count, setCount] = useState(null);
  useEffect(() => {
    if (!('PerformanceObserver' in window)) return undefined;
    const po = new PerformanceObserver((list) => {
      if (since.current == null) return;
      const n = list.getEntries().filter((e) => e.startTime >= since.current).length;
      if (n) setCount((c) => (c ?? 0) + n);
    });
    try { po.observe({ type: 'resource' }); } catch { return undefined; }
    return () => po.disconnect();
  }, []);
  const arm = useCallback(() => { since.current = performance.now(); setCount(0); }, []);
  return [count, arm];
}

function Ask() {
  const all = useMemo(() => [...QUESTIONS.map((q) => ({ id: q.question_id, q: q.question, group: 'Labelled set (recorded in results_build.json)' })),
    ...HARD.map((h) => ({ id: h.id, q: h.question, group: 'Hard set (added in results_rigor.json)' }))], []);
  const [pick, setPick] = useState(all[0].id);
  const [text, setText] = useState(all[0].q);
  const [res, setRes] = useState(null);
  const [count, arm] = useRequestCounter();
  const ask = (q) => { arm(); const t0 = performance.now(); const r = INDEX.answer(q); setRes({ ...r, q, ms: performance.now() - t0 }); };
  useEffect(() => { ask(all[0].q); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  const chooser = (id) => { setPick(id); const item = all.find((a) => a.id === id); setText(item.q); ask(item.q); };
  return (
    <section id="ask" className="card window reveal" data-title="assistant.py — live in your browser">
      <div className="head">
        <div>
          <p className="eyebrow">Live · computed in your browser</p>
          <h2>Ask the {DOCS.length} documents. Nothing leaves this tab.</h2>
          <p className="sub">
            A line-for-line port of <a href={blob('level-2-build/assistant.py')}>assistant.py</a>: {INDEX.chunks.length} chunks of {CHUNK_SIZE_WORDS} words with {CHUNK_OVERLAP_WORDS} overlap, TF-IDF cosine ranking, the two best sentences of the top document with a citation each, and a refusal below {REFUSAL_THRESHOLD.toFixed(2)}.
            Try a question in your own words: exact token matching means synonyms usually miss.
          </p>
        </div>
        <span className={`pill ${count ? 'warn' : 'good'}`} aria-live="polite">Network: {count ?? 0} requests since you asked</span>
      </div>
      <div className="controls">
        <div className="field"><label htmlFor="q-pick">Pick a question</label>
          <select id="q-pick" value={pick} onChange={(e) => chooser(e.target.value)}>
            {['Labelled set (recorded in results_build.json)', 'Hard set (added in results_rigor.json)'].map((g) => (
              <optgroup key={g} label={g}>{all.filter((a) => a.group === g).map((a) => <option key={a.id} value={a.id}>{a.id}: {a.q}</option>)}</optgroup>
            ))}
          </select>
        </div>
      </div>
      <form className="askrow" onSubmit={(e) => { e.preventDefault(); if (text.trim()) ask(text); }}>
        <label htmlFor="q-text" className="sr-only">Your question</label>
        <input id="q-text" type="text" value={text} onChange={(e) => setText(e.target.value)} placeholder="Ask about the garden, budget, coffee, backups…" autoComplete="off" />
        <button className="btn primary" type="submit">Ask</button>
      </form>
      {res && (
        <div className="grid2" style={{ marginTop: 16 }}>
          <div>
            <h3>{res.refused ? 'Refused' : 'Answer'} <span className="hint">· {ms(res.ms)} in your browser</span></h3>
            <div className={`answer ${res.refused ? 'refused' : ''}`}>
              {res.refused
                ? <p>{res.answer_text} <span className="hint">Best chunk scored {res.best_score.toFixed(4)}, below the {REFUSAL_THRESHOLD.toFixed(2)} threshold.</span></p>
                : res.sentences.map((s) => <p key={s.sentence_id}>{s.text} <span className="cite">{s.citation}</span> <span className="hint">score {s.score.toFixed(3)}</span></p>)}
            </div>
            {!res.refused && <p className="hint">From “{res.title}”. The first sentence is the scored answer; the second is context and can be weakly related.</p>}
          </div>
          <div>
            <h3>Top 3 chunks by cosine</h3>
            <ol className="chunks">
              {res.ranked.map((c) => (
                <li key={c.chunk_id}>
                  <div className="lab"><span className="mono">{c.chunk_id}</span><b>{c.score.toFixed(4)}</b></div>
                  <div className="track"><div className="fill" style={{ width: `${Math.min(100, c.score * 100)}%`, background: c.score >= REFUSAL_THRESHOLD ? 'var(--primary)' : 'var(--muted)' }} /><div className="alpha" style={{ left: `${REFUSAL_THRESHOLD * 100}%` }} /></div>
                  <p className="hint chunktext">{c.text}</p>
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </section>
  );
}

function Evaluation() {
  const [set, setSet] = useState('labelled');
  const [run, setRun] = useState(null);
  const rerun = () => {
    const t0 = performance.now();
    const r = evaluate(INDEX, QUESTIONS);
    const match = r.rows.filter((row, i) => Math.abs(row.top1_score - RECORDED[i].top1_score) < 1e-9 && row.top1_doc === RECORDED[i].top1_doc && row.refused === RECORDED[i].refused).length;
    const hard = HARD.map((h) => { const a = INDEX.answer(h.question); return { ...h, live: a, match: Math.abs(a.ranked[0].score - h.top1_score) < 1e-9 && a.refused === h.refused }; });
    setRun({ ...r, match, hard, ms: performance.now() - t0 });
  };
  useEffect(rerun, []);
  const b = rigor.baselines;
  const hs = rigor.hard_set;
  return (
    <section id="eval" className="card window reveal" data-title="run_build.py — parity check">
      <div className="head">
        <div>
          <p className="eyebrow">Live rerun · checked against the record</p>
          <h2>The labelled set, rerun in your browser, matches the Python run.</h2>
          <p className="sub">
            Each row is computed now and compared with <a href={blob('level-2-build/results_build.json')}>results_build.json</a>: same top document, same refusal, and the same top-1 score to within 1e-9.
            The hard set was written for the research review to probe the ceiling: synonym paraphrases and cross-topic distractors. It shows where exact matching breaks.
          </p>
        </div>
        {run && <span className={`pill ${run.match === RECORDED.length ? 'good' : 'bad'}`}>● Parity {run.match}/{RECORDED.length}</span>}
      </div>
      <div className="actions" style={{ marginTop: 0, marginBottom: 16 }}>
        <div className="seg" role="group" aria-label="Question set">
          {[['labelled', `Labelled set (${QUESTIONS.length})`], ['hard', `Hard set (${HARD.length})`]].map(([k, l]) => <button key={k} aria-pressed={set === k} onClick={() => setSet(k)}>{l}</button>)}
        </div>
        <button className="btn ghost" onClick={rerun}>Rerun all in your browser</button>
        {run && <span className="hint">{QUESTIONS.length + HARD.length} questions in {ms(run.ms)}</span>}
      </div>
      {run && set === 'labelled' && (
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead><tr><th>Q</th><th>Question</th><th>Gold</th><th>Top 1</th><th>Score</th><th>Hit@1</th><th>Sentence</th><th>Refused</th><th>Matches record</th></tr></thead>
            <tbody>
              {run.rows.map((r, i) => (
                <tr key={r.question_id}><td className="mono">{r.question_id}</td><td className="qcell">{r.question}</td><td>{r.gold_doc}</td><td>{r.top1_doc}</td><td>{r.top1_score.toFixed(4)}</td>
                  <td className={r.is_evidence ? (r.hit_at_1 ? 'ok' : 'no') : ''}>{r.is_evidence ? (r.hit_at_1 ? 'yes' : 'no') : 'n/a'}</td>
                  <td className={r.is_evidence ? (r.sentence_correct ? 'ok' : 'no') : ''}>{r.is_evidence ? (r.sentence_correct ? 'yes' : 'no') : 'n/a'}</td>
                  <td>{r.refused ? 'yes' : 'no'}</td>
                  <td className={Math.abs(r.top1_score - RECORDED[i].top1_score) < 1e-9 ? 'ok' : 'no'}>{Math.abs(r.top1_score - RECORDED[i].top1_score) < 1e-9 ? '✓' : '✗'}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {run && set === 'hard' && (
        <>
          <div className="tiles" style={{ gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', marginTop: 0, marginBottom: 16 }}>
            <div className="tile"><div className="num">{hs.paraphrase_answered_correctly}/{hs.paraphrase_questions}</div><div className="cap">Paraphrases answered from the right document ({hs.paraphrase_refused} refused). {ivText(hs.paraphrase_answered_correctly, hs.paraphrase_questions)}</div></div>
            <div className="tile"><div className="num">{hs.paraphrase_top1_correct}/{hs.paraphrase_questions}</div><div className="cap">Paraphrases whose top chunk is in the right document, ignoring the threshold</div></div>
            <div className="tile"><div className="num">{hs.distractor_refused}/{hs.distractor_questions}</div><div className="cap">Cross-topic distractors refused. {ivText(hs.distractor_refused, hs.distractor_questions)}</div></div>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead><tr><th>Q</th><th>Kind</th><th>Question</th><th>Gold</th><th>Top 1</th><th>Score</th><th>Refused</th><th>Correct</th><th>Matches record</th></tr></thead>
              <tbody>
                {run.hard.map((h) => (
                  <tr key={h.id}><td className="mono">{h.id}</td><td>{h.kind === 'synonym_paraphrase' ? 'paraphrase' : 'distractor'}</td><td className="qcell">{h.question}</td><td>{h.gold_doc}</td><td>{h.live.ranked[0].doc_id}</td><td>{h.live.ranked[0].score.toFixed(4)}</td>
                    <td>{h.live.refused ? 'yes' : 'no'}</td><td className={h.correct ? 'ok' : 'no'}>{h.correct ? 'yes' : 'no'}</td><td className={h.match ? 'ok' : 'no'}>{h.match ? '✓' : '✗'}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
      <h3 style={{ marginTop: 24 }}>Baselines on the same {b.bm25_chunks_30_10.evidence_questions} evidence questions <span className="hint">· recorded in results_rigor.json</span></h3>
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead><tr><th>Ranker</th><th>Top-1 correct</th><th>Recall@3</th><th>Top-1 Wilson 95%</th></tr></thead>
          <tbody>
            {[['TF-IDF over 30/10 chunks (the pipeline)', b.tfidf_chunks_30_10], ['BM25 over the same chunks', b.bm25_chunks_30_10], ['TF-IDF over whole documents (no chunking)', b.tfidf_whole_documents]].map(([k, v]) => (
              <tr key={k}><td>{k}</td><td>{v.top1_correct}/{v.evidence_questions}</td><td>{v.recall_at_3_correct}/{v.evidence_questions}</td><td>{wilson(v.top1_correct, v.evidence_questions).map((x) => x.toFixed(2)).join(' to ')}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="hint">All three rankers tie on this set, so the set cannot tell them apart. That is a ceiling effect, not evidence that chunking or BM25 does not matter.</p>
    </section>
  );
}

function useNarrow() {
  const q = '(max-width: 760px)';
  const [n, setN] = useState(() => typeof window !== 'undefined' && window.matchMedia?.(q).matches);
  useEffect(() => { const m = window.matchMedia?.(q); if (!m) return undefined; const f = () => setN(m.matches); m.addEventListener('change', f); return () => m.removeEventListener('change', f); }, []);
  return n;
}

function Threshold() {
  const narrow = useNarrow();
  const scores = useMemo(() => evaluate(INDEX, QUESTIONS).rows.map((r) => ({ id: r.question_id, s: r.top1_score, ev: r.is_evidence })), []);
  const [t, setT] = useState(REFUSAL_THRESHOLD);
  const [hard, setHard] = useState(false);
  const m = refusalAt(scores.map((x) => x.s), scores.map((x) => x.ev), t);
  const loo = useMemo(() => leaveOneOut(scores.map((x) => x.s), scores.map((x) => x.ev)), [scores]);
  const noneMax = Math.max(...scores.filter((x) => !x.ev).map((x) => x.s));
  const evMin = Math.min(...scores.filter((x) => x.ev).map((x) => x.s));
  const hm = refusalAt(HARD.map((h) => h.top1_score), HARD.map((h) => h.gold_doc !== 'NONE'), t);
  const W = narrow ? 360 : 960, H = hard ? 210 : 150, pad = { l: narrow ? 52 : 100, r: 14 }, x = (v) => pad.l + (v / 0.8) * (W - pad.l - pad.r);
  const row = (ev, i) => (ev ? 52 : 98) + ((i % 3) - 1) * 9;
  return (
    <section id="threshold" className="card window reveal" data-title="threshold.svg — refusal sweep">
      <div className="head">
        <div>
          <p className="eyebrow">Live · computed in your browser</p>
          <h2>Where to stop answering: one slider, the whole trade-off.</h2>
          <p className="sub">
            Each mark is a question's best chunk score. Questions below the line are refused. On the labelled set the no-evidence questions top out at {noneMax.toFixed(4)} and the weakest evidence question scores {evMin.toFixed(4)}, so any threshold in that gap scores perfectly.
            The recorded {REFUSAL_THRESHOLD.toFixed(2)} was tuned on this same set. Held out by leave-one-out (each question scored with a threshold fitted on the other {scores.length - 1}), refusal is still {loo.refusal_true_positive}/{S.no_evidence_questions} with {loo.refusal_false_positive} false refusals, thresholds {loo.threshold_min.toFixed(3)} to {loo.threshold_max.toFixed(3)}.
          </p>
        </div>
        <span className="pill info">Threshold {t.toFixed(2)}</span>
      </div>
      <div className="controls">
        <Range label="Refusal threshold" value={t} min={0} max={0.8} step={0.01} onChange={setT} show={t.toFixed(2)} />
        <div className="field"><label htmlFor="hard-overlay">Overlay the hard set</label>
          <select id="hard-overlay" value={hard ? 'on' : 'off'} onChange={(e) => setHard(e.target.value === 'on')}><option value="off">Labelled set only</option><option value="on">Add the 16 hard questions</option></select>
        </div>
      </div>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Strip chart of ${scores.length} top-1 scores with the refusal threshold at ${t.toFixed(2)}`}>
        <rect x={x(noneMax)} width={x(evMin) - x(noneMax)} y={30} height={90} fill="var(--good)" opacity="0.1" />
        <text x={(x(noneMax) + x(evMin)) / 2} y={24} textAnchor="middle">{narrow ? '' : 'recorded '}gap {noneMax.toFixed(4)} to {evMin.toFixed(4)}</text>
        {[0, 0.2, 0.4, 0.6, 0.8].map((v) => <g key={v}><line className="axis" x1={x(v)} x2={x(v)} y1={30} y2={H - 22} /><text x={x(v)} y={H - 6} textAnchor="middle">{v.toFixed(1)}</text></g>)}
        <text x={0} y={56} style={{ fill: 'var(--text)' }}>evidence</text>
        <text x={0} y={102} style={{ fill: 'var(--text)' }}>{narrow ? 'none' : 'no evidence'}</text>
        {scores.map((p, i) => (p.ev
          ? <circle key={p.id} cx={x(p.s)} cy={row(true, i)} r="6" fill={p.s < t ? 'var(--bad)' : 'var(--primary)'}><title>{p.id}: {p.s.toFixed(4)}</title></circle>
          : <rect key={p.id} x={x(p.s) - 6} y={row(false, i) - 6} width="12" height="12" fill={p.s < t ? 'var(--good)' : 'var(--bad)'}><title>{p.id}: {p.s.toFixed(4)}</title></rect>))}
        {hard && <>
          <text x={0} y={172} style={{ fill: 'var(--text)' }}>hard set</text>
          {HARD.map((h, i) => (h.gold_doc !== 'NONE'
            ? <circle key={h.id} cx={x(h.top1_score)} cy={168 + ((i % 3) - 1) * 9} r="5.5" fill="none" stroke="var(--primary)" strokeWidth="2"><title>{h.id}: {h.top1_score.toFixed(4)}</title></circle>
            : <rect key={h.id} x={x(h.top1_score) - 5} y={168 + ((i % 3) - 1) * 9 - 5} width="10" height="10" fill="none" stroke="var(--warn)" strokeWidth="2"><title>{h.id}: {h.top1_score.toFixed(4)}</title></rect>))}
        </>}
        <line x1={x(t)} x2={x(t)} y1={30} y2={H - 22} stroke="var(--text)" strokeWidth="2" strokeDasharray="5 4" />
      </svg>
      <div className="legend"><span><i style={{ background: 'var(--primary)', borderRadius: '50%' }} />evidence, answered</span><span><i style={{ background: 'var(--bad)', borderRadius: '50%' }} />evidence, falsely refused</span><span><i style={{ background: 'var(--good)' }} />no evidence, refused</span><span><i style={{ background: 'var(--bad)' }} />no evidence, answered</span>{hard && <span><i style={{ border: '2px solid var(--warn)' }} />hard set (hollow)</span>}</div>
      <div className="tiles">
        <div className="tile"><div className="num">{pct(m.precision)}</div><div className="cap">Refusal precision ({m.tp} of {m.refused} refusals were right)</div></div>
        <div className="tile"><div className="num">{pct(m.recall)}</div><div className="cap">Refusal recall ({m.tp} of {S.no_evidence_questions} no-evidence refused)</div></div>
        <div className="tile"><div className="num">{m.fp}</div><div className="cap">False refusals of the {S.evidence_questions} evidence questions</div></div>
        <div className="tile"><div className="num">{hm.tp}/{HARD.filter((h) => h.gold_doc === 'NONE').length}</div><div className="cap">Hard-set distractors refused at this threshold, with {hm.fp} of {HARD.filter((h) => h.gold_doc !== 'NONE').length} paraphrases refused</div></div>
      </div>
      <p className="hint">On the hard set the two groups overlap, so no single threshold separates them: the gap above is a property of this easy labelled set.</p>
    </section>
  );
}

function Chunking() {
  const [size, setSize] = useState(CHUNK_SIZE_WORDS);
  const [overlap, setOverlap] = useState(CHUNK_OVERLAP_WORDS);
  const ov = Math.min(overlap, size - 1);
  const res = useMemo(() => { const t0 = performance.now(); const idx = new ChunkIndex(DOCS, size, ov); const r = evaluate(idx, QUESTIONS).summary; return { ...r, ms: performance.now() - t0 }; }, [size, ov]);
  const isDefault = size === CHUNK_SIZE_WORDS && ov === CHUNK_OVERLAP_WORDS;
  const recorded = rigor.chunk_sweep.find((r) => r.chunk_size === size && r.overlap === ov);
  return (
    <section id="chunking" className="card window reveal" data-title="chunker.py — sensitivity explorer">
      <div className="head">
        <div>
          <p className="eyebrow">Live · computed in your browser · new analysis</p>
          <h2>Change the chunk size and the whole index rebuilds.</h2>
          <p className="sub">
            Each move re-chunks the {DOCS.length} real documents, rebuilds the TF-IDF index and reruns all {QUESTIONS.length} labelled questions with the {REFUSAL_THRESHOLD.toFixed(2)} threshold.
            The repo records only the default {CHUNK_SIZE_WORDS}/{CHUNK_OVERLAP_WORDS}; the numbers here are computed live. The build checks the port against a {rigor.chunk_sweep.length}-point sweep in <a href={blob('level-3-deep/results_rigor.json')}>results_rigor.json</a>.
          </p>
        </div>
        <span className={`pill ${isDefault ? 'good' : 'info'}`}>{isDefault ? '● Recorded default' : recorded ? '● Also in the recorded sweep' : '● Computed live only'}</span>
      </div>
      <div className="controls">
        <Range label="Chunk size (words)" value={size} min={5} max={100} step={1} onChange={setSize} show={size} />
        <Range label="Overlap (words)" value={ov} min={0} max={Math.min(40, size - 1)} step={1} onChange={setOverlap} show={ov} />
      </div>
      <div className="tiles">
        <div className="tile"><div className="num">{res.chunks}</div><div className="cap">chunks, rebuilt in {ms(res.ms)}</div></div>
        <div className="tile"><div className="num">{res.top1_correct}/{res.evidence_questions}</div><div className="cap">top-1 document · recall@3 {res.chunk_recall_at_3_correct}/{res.evidence_questions}</div></div>
        <div className="tile"><div className="num">{res.sentence_correct}/{res.evidence_questions}</div><div className="cap">answer sentence correct</div></div>
        <div className="tile"><div className="num">{res.refusal_true_positive}/{res.no_evidence_questions}</div><div className="cap">no-evidence refused · {res.refusal_false_positive} false refusals</div></div>
      </div>
      <p className="hint">Small chunks raise no-evidence scores, because a short chunk that shares one word looks similar. Retrieval stays perfect across all {rigor.chunk_sweep.length} recorded settings, another sign the set is too easy to rank them.</p>
    </section>
  );
}

function Cost() {
  const rows = deep.cloud_costs_modelled.rows, tm = deep.token_model;
  const [exp, setExp] = useState(5);
  const [basis, setBasis] = useState('mean');
  const q = Math.round(10 ** exp);
  const data = rows.map((r) => {
    const per = tm.per_query.map((p) => costPerQuery(r, p.input_tokens_est, p.output_tokens_est));
    return { ...r, mean: costPerQuery(r, tm.mean_input_tokens_est, tm.mean_output_tokens_est) * q, lo: Math.min(...per) * q, hi: Math.max(...per) * q };
  });
  const max = Math.max(...data.map((d) => (basis === 'mean' ? d.mean : d.hi)));
  return (
    <section id="cost" className="card window reveal" data-title="study.py — modelled cost">
      <div className="head">
        <div>
          <p className="eyebrow">Calculator · modelled, never measured</p>
          <h2>Local costs nothing per query. Cloud cost is a <em>model</em>.</h2>
          <p className="sub">
            Cost = input tokens × input rate + output tokens × output rate, per million, the formula in <a href={blob('level-3-deep/study.py')}>study.py</a>, at {tm.mean_input_tokens_est.toFixed(2)} input and {tm.mean_output_tokens_est.toFixed(2)} output tokens per query.
            Tokens are estimated by a word rule ({tm.estimator}). Rates and model names are exactly as recorded on {deep.pricing_checked}; they are a dated snapshot. No API was called. Local side: {deep.cloud_costs_modelled.local_cost_note}.
          </p>
        </div>
        <span className="pill warn">MODELLED</span>
      </div>
      <div className="controls">
        <Range label="Queries per month" value={exp} min={3} max={7} step={0.1} onChange={setExp} show={fmt(q)} />
        <div className="field"><span className="flabel" id="basis-l">Token basis</span>
          <div className="seg" role="group" aria-labelledby="basis-l">
            {[['mean', 'Mean of 24'], ['range', 'Per-question range']].map(([k, l]) => <button key={k} aria-pressed={basis === k} onClick={() => setBasis(k)}>{l}</button>)}
          </div>
        </div>
      </div>
      <div className="bars">
        <div className="bar-row"><div className="lab"><span>Local pipeline (marginal API cost)</span><b>{usd(deep.cloud_costs_modelled.local_marginal_api_cost_usd * q)}</b></div><div className="track"><div className="fill" style={{ width: '0%' }} /></div></div>
        {data.map((d) => (
          <div className="bar-row" key={d.model}>
            <div className="lab"><span>{d.provider} · <span className="mono">{d.model}</span> · {d.input_rate}/{d.output_rate} USD per M · <a href={d.source}>source</a></span><b>{basis === 'mean' ? usd(d.mean) : `${usd(d.lo)} to ${usd(d.hi)}`}</b></div>
            <div className="track">
              {basis === 'mean'
                ? <div className="fill" style={{ width: `${(d.mean / max) * 100}%`, background: 'var(--warn)' }} />
                : <div className="fill" style={{ marginLeft: `${(d.lo / max) * 100}%`, width: `${((d.hi - d.lo) / max) * 100}%`, minWidth: 4, background: 'var(--warn)' }} />}
            </div>
          </div>
        ))}
      </div>
      <p className="hint" style={{ marginTop: 12 }}>The output side assumes a cloud answer as short as the local extractive one, so these are a floor. Electricity and hardware are excluded from the local side.</p>
    </section>
  );
}

function Latency() {
  const narrow = useNarrow();
  const [mine, setMine] = useState(null);
  const time = () => {
    const rounds = 5, samples = [];
    for (let r = 0; r < rounds; r++) for (const qq of QUESTIONS) { const t0 = performance.now(); INDEX.answer(qq.question); samples.push(performance.now() - t0); }
    samples.sort((a, b) => a - b);
    setMine({ mean: samples.reduce((a, b) => a + b, 0) / samples.length, median: samples[Math.floor(samples.length / 2)], n: samples.length });
  };
  const [c0, c1] = deep.cloud_latency_assumption.range_ms;
  const W = narrow ? 420 : 960, l = narrow ? 8 : 240, r = narrow ? 24 : 20, gap = narrow ? 58 : 40;
  const lx = (v) => l + ((Math.log10(v) + 2) / 6) * (W - l - r); // 0.01 ms to 10,000 ms
  const marks = [
    { k: `Local answer (recorded, n=${T.queries_timed})`, lo: T.answer_latency_ms_min, hi: T.answer_latency_ms_max, mid: T.answer_latency_ms_median, c: 'var(--primary)' },
    { k: `Local index build (recorded, ${T.rounds} rounds)`, lo: T.index_build_ms_min, hi: T.index_build_ms_max, mid: T.index_build_ms_mean, c: 'var(--primary)' },
    { k: 'Cloud API answer (ASSUMED range)', lo: c0, hi: c1, mid: null, c: 'var(--warn)' },
    mine && { k: `Your browser now (n=${mine.n})`, lo: mine.median, hi: mine.mean, mid: mine.mean, c: 'var(--good)' },
  ].filter(Boolean);
  const rowsY = marks.map((_, i) => (narrow ? 52 : 40) + i * gap), H = rowsY[rowsY.length - 1] + 54;
  const sc = rigor.scaling.rows;
  const SW = narrow ? 360 : 460, SH = 200, sp = { l: 48, r: 12, t: 12, b: 26 };
  const sx = (v) => sp.l + (v / sc[sc.length - 1].chunks) * (SW - sp.l - sp.r);
  const smax = Math.max(...sc.map((s) => s.answer_latency_ms_mean));
  const sy = (v) => sp.t + (1 - v / smax) * (SH - sp.t - sp.b);
  return (
    <section id="latency" className="card window reveal" data-title="timing.json — recorded and live">
      <div className="head">
        <div>
          <p className="eyebrow">Recorded replay · plus a live timer</p>
          <h2>Sub-millisecond answers, on a corpus of {S.chunks} chunks.</h2>
          <p className="sub">
            Recorded on the study VM by <a href={blob('level-3-deep/run_deep.py')}>run_deep.py</a>: mean {ms(T.answer_latency_ms_mean)}, median {ms(T.answer_latency_ms_median)}, range {ms(T.answer_latency_ms_min)} to {ms(T.answer_latency_ms_max)}.
            The cloud figure is {deep.cloud_latency_assumption.label}: {deep.cloud_latency_assumption.note}. The axis is logarithmic.
          </p>
        </div>
        <button className="btn primary" onClick={time}>Time the port in your browser</button>
      </div>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Latency on a log axis: recorded local answer and index build times against the assumed cloud range">
        {(narrow ? [-2, 0, 2, 4] : [-2, -1, 0, 1, 2, 3, 4]).map((e) => <g key={e}><line className="axis" x1={lx(10 ** e)} x2={lx(10 ** e)} y1={20} y2={H - 26} /><text x={lx(10 ** e)} y={H - 8} textAnchor="middle">{e < 0 ? (10 ** e).toFixed(-e) : fmt(10 ** e)} ms</text></g>)}
        {marks.map((m, i) => (
          <g key={m.k}>
            <text x={narrow ? l : 0} y={narrow ? rowsY[i] - 14 : rowsY[i] + 4} style={{ fill: 'var(--text)', fontSize: 13 }}>{m.k}</text>
            <line x1={lx(m.lo)} x2={lx(m.hi)} y1={rowsY[i]} y2={rowsY[i]} stroke={m.c} strokeWidth="8" strokeLinecap="round" opacity="0.45" />
            {m.mid != null && <circle cx={lx(m.mid)} cy={rowsY[i]} r="6" fill={m.c} />}
          </g>
        ))}
      </svg>
      <p className="hint">{mine ? `Measured in your browser now, not the recorded VM figure: mean ${ms(mine.mean)}, median ${ms(mine.median)} over ${mine.n} answers.` : 'Bars run from minimum to maximum; dots mark the median (answers) or mean (index build).'}</p>
      <div className="grid2" style={{ marginTop: 16 }}>
        <div>
          <h3>Synthetic scaling: corpus copied up to {sc[sc.length - 1].factor}×</h3>
          <svg className="chart" viewBox={`0 0 ${SW} ${SH}`} role="img" aria-label="Mean answer latency against number of chunks for replicated corpora">
            {[0, 0.5, 1].map((f) => <g key={f}><line className="axis" x1={sp.l} x2={SW - sp.r} y1={sy(smax * f)} y2={sy(smax * f)} /><text x={sp.l - 6} y={sy(smax * f) + 4} textAnchor="end">{(smax * f).toFixed(1)}</text></g>)}
            <polyline fill="none" stroke="var(--primary)" strokeWidth="2.5" points={sc.map((s) => `${sx(s.chunks)},${sy(s.answer_latency_ms_mean)}`).join(' ')} />
            {sc.map((s) => <g key={s.factor}><circle cx={sx(s.chunks)} cy={sy(s.answer_latency_ms_mean)} r="4.5" fill="var(--primary)" /><text x={sx(s.chunks)} y={SH - 8} textAnchor="middle">{fmt(s.chunks)}</text></g>)}
          </svg>
          <p className="hint">ms per answer (y) against chunks (x). Recorded by <a href={blob('level-3-deep/run_rigor.py')}>run_rigor.py</a>; {rigor.scaling.label}.</p>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead><tr><th>Copies</th><th>Chunks</th><th>Index build</th><th>Answer, mean</th></tr></thead>
            <tbody>{sc.map((s) => <tr key={s.factor}><td>{s.factor}×</td><td>{fmt(s.chunks)}</td><td>{ms(s.index_build_ms)}</td><td>{ms(s.answer_latency_ms_mean)}</td></tr>)}</tbody>
          </table>
          <p className="hint">Linear brute-force scoring grows with corpus size; an inverted index would be the next step for a real private folder.</p>
        </div>
      </div>
    </section>
  );
}

function Privacy() {
  const audits = [['Learn', learn.audit], ['Build', build.audit], ['Deep', deep.privacy.local_audit_deep]];
  const patterns = audits[0][1].patterns.map((p) => p.pattern);
  const notProven = BUILD_LIMITS.find((b) => b.startsWith('The privacy proof'));
  return (
    <section id="privacy" className="card window reveal" data-title="audit.log — network pattern scan">
      <p className="eyebrow">Recorded audit</p>
      <h2>Zero network calls in the source. The cloud path sends your chunks by design.</h2>
      <p className="sub">Each level scans its own source files for {patterns.length} network patterns. Counts below are copied from each level's results file.</p>
      <div style={{ overflowX: 'auto', marginTop: 16 }}>
        <table>
          <thead><tr><th>Pattern</th>{audits.map(([k, a]) => <th key={k}>{k} <span className="hint">({a.files_scanned.join(', ')})</span></th>)}</tr></thead>
          <tbody>
            {patterns.map((p) => <tr key={p}><td className="mono">{p}</td>{audits.map(([k, a]) => { const c = a.patterns.find((x) => x.pattern === p).count; return <td key={k} className={c ? 'no' : 'ok'}>{c}</td>; })}</tr>)}
            <tr><td><b>Total · passed</b></td>{audits.map(([k, a]) => <td key={k} className={a.passed ? 'ok' : 'no'}>{a.total_matches} · {a.passed ? 'passed' : 'failed'}</td>)}</tr>
          </tbody>
        </table>
      </div>
      <div className="grid2" style={{ marginTop: 16 }}>
        <div className="tile"><h3>Local data transfer</h3><p className="hint">{deep.privacy.local_data_transfer}.</p><h3 style={{ marginTop: 10 }}>Cloud data transfer</h3><p className="hint">{deep.privacy.cloud_data_transfer}. Note: {deep.privacy.google_tier_note}.</p></div>
        <div className="tile"><h3>What this audit does not prove</h3><p className="hint">{notProven}</p><p className="hint">This change adds a runtime check, <a href={blob('tests/test_deep_egress.py')}>test_deep_egress.py</a>: the whole Build pipeline runs with every socket constructor replaced by one that raises. It still does not sandbox the operating system.</p></div>
      </div>
    </section>
  );
}

function Verdict() {
  const v = deep.verdict;
  return (
    <section id="verdict" className="card window reveal" data-title="README.md — verdict and limits">
      <p className="eyebrow">Verdict · from results_deep.json</p>
      <h2>Local wins lookups and privacy. Cloud wins anything that needs writing.</h2>
      <div style={{ overflowX: 'auto', marginTop: 16 }}>
        <table>
          <thead><tr><th>Axis</th><th>Winner</th><th>Evidence</th></tr></thead>
          <tbody>{v.axis_winners.map((a) => <tr key={a.axis}><td className="mono">{a.axis}</td><td><span className={`pill ${a.winner === 'local' ? 'good' : 'info'}`}>{a.winner}</span></td><td>{a.evidence}</td></tr>)}</tbody>
        </table>
      </div>
      <h3 style={{ marginTop: 20 }}>Decision rules</h3>
      <ul className="rules">{v.decision_rules.map((d) => <li key={d.condition}><span className={`pill ${d.winner === 'local' ? 'good' : 'info'}`}>{d.winner}</span> <b>If {d.condition}.</b> <span className="hint">{d.reason}.</span></li>)}</ul>
      <div className="grid2" style={{ marginTop: 20 }}>
        <details className="tile"><summary><b>Build failure modes and limits ({BUILD_LIMITS.length})</b></summary><ul className="limits">{BUILD_LIMITS.map((b) => <li key={b}>{b}</li>)}</ul></details>
        <details className="tile"><summary><b>Deep failure modes and limits ({DEEP_LIMITS.length})</b></summary><ul className="limits">{DEEP_LIMITS.map((b) => <li key={b}>{b}</li>)}</ul></details>
      </div>
      <h3 style={{ marginTop: 20 }}>Self-graded in the repo <span className="hint">· the authors' own grades, not external review</span></h3>
      <div className="tiles" style={{ gridTemplateColumns: 'repeat(3, minmax(0, 1fr))' }}>
        {GRADES.map(([k, g, p]) => <div className="tile" key={k}><div className="num">{fmt(g)}</div><div className="cap">{k} of 10,000 · <a href={blob(p)}>deductions</a></div></div>)}
      </div>
    </section>
  );
}

function Reproduce() {
  const cmds = ciCommands(ciYml);
  return (
    <section id="reproduce" className="card window reveal" data-title="Terminal — python, standard library only">
      <p className="eyebrow">Reproduce it</p>
      <h2>No installs. Standard-library Python reruns every number.</h2>
      <ol className="steps" style={{ marginTop: 16 }}>
        <li><span className="n">1</span><div><b>Clone</b><div className="hint"><code>git clone {REPO}.git && cd local-first-ai</code></div></div></li>
        <li><span className="n">2</span><div><b>The CI steps, in order</b> <span className="hint">(read from ci.yml)</span><div className="hint">{cmds.map((c) => <div key={c}><code>{c}</code></div>)}</div></div></li>
        <li><span className="n">3</span><div><b>Check the corpus fingerprint</b><div className="hint">sha256 over the {DOCS.length} sorted document hashes: <code>{build.corpus_fingerprint_sha256}</code></div></div></li>
        <li><span className="n">4</span><div><b>Rebuild this page</b><div className="hint"><code>cd site && npm ci && npm run build</code> runs <span className="mono">engine.check.mjs</span> first, which fails the build if the browser port drifts from the recorded results.</div></div></li>
      </ol>
    </section>
  );
}
