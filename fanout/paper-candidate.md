# Paper candidate brief: a measured local against modelled cloud study for document lookup

Project: P15 local-first-ai
Status: CANDIDATE, brief dated 2026-11-05
Submission note: submission is Jesun's tap. Nothing is submitted by
this brief, and no venue has been contacted.

## Working title

Local first for document lookup: measured retrieval, refusal, and
privacy on a synthetic corpus, against cloud costs modelled from
published pricing

## Candidate claim, in one line

On a small synthetic corpus, a standard-library TF-IDF core can
answer document lookups offline with cited verbatim sentences and
a working refusal rule, at zero marginal API cost; the claim is
the measurement discipline and the decision rule, not general
assistant quality, because the corpus is synthetic with distinct
topics and the cloud side is modelled, not measured.

## Abstract draft

Based only on the measured v1.0 results recorded in the repo.
Scope limits are stated inside the abstract, not after it.

A local-first assistant keeps documents and questions on the
machine. This candidate reports a three level open study. Learn
built a TF-IDF core over 8 synthetic documents and scored 10
labelled questions at top-1 1.000, recall at 3 1.000, and sentence
accuracy 1.000, with a source scan privacy audit clean (2 files,
7 patterns, 0 matches). Build scaled to 24 synthetic documents
(72 chunks), 24 labelled questions (20 evidence, 4 no-evidence),
and scored top-1 1.000, chunk recall at 3 1.000, sentence
accuracy 1.000, and refusal precision and recall 1.000 at a named
threshold of 0.30, with persistent session memory verified by
reload. Deep measured the Build pipeline (mean answer latency
0.3326 ms over 120 timed answers) and modelled cloud cost from
published pricing checked 2026-11-05 at a stated token estimate
of 163.33 input and 29.46 output tokens per query: 0.000031 USD
per query at budget rates to 0.000621 USD at flagship rates.
There is no Ollama and no language model in the local core, the
corpus is synthetic with distinct topics so the perfect scores
are weak evidence, cloud quality and latency were not measured,
and token counts use a word based estimator. The candidate
claims the reproducible measurement, the refusal calibration
record, and the five step local against cloud decision rule on
these sets, not real-world assistant performance.

## Method outline

1. Retrieval. TF-IDF with smoothed idf, log((1 + N) / (1 + df)) + 1,
   cosine ranking, deterministic tie break on document id.
2. Build pipeline. Chunking at 30 words with 10 words overlap,
   top chunk decides the document, best two sentences returned
   with per-sentence citations, refusal below 0.30, session memory
   as a JSON list verified by reload.
3. Privacy audit. Source scan for 7 network patterns over the
   level source files, plus an import guard test in Build.
4. Deep study. Local quality, latency, and index time measured;
   cloud cost computed in code from dated published rates and a
   documented token estimator; cloud latency stated as one
   assumed range only.
5. Determinism. Learn and Build results files are byte-identical
   across runs; Deep is deterministic apart from timing fields.

## Results table

Measured 2026-11-05, Muse VM, Python 3.12, from the level
READMEs and results files in the repo.

| Item | Result |
| --- | --- |
| Learn | 8 docs, 10 questions, top-1 1.000, recall at 3 1.000, sentence 1.000 |
| Build | 24 docs, 72 chunks, top-1 1.000, chunk recall at 3 1.000, sentence 1.000, refusal 1.000 / 1.000 |
| Deep local | Latency 0.3326 ms mean over 120, index 3.6389 ms mean over 5 |
| Deep cloud (modelled) | 0.000031 to 0.000621 USD per query; 3.11 to 62.13 USD per 100k |
| Tests | 62 in total, plus the scaffold smoke test |

## Limits a reviewer will raise, stated first

- Synthetic distinct-topic corpus: perfect scores are weak
  evidence and will not transfer to overlapping real documents.
- No language model: no generation, paraphrase, or synthesis.
- Cloud side modelled, not measured: no head to head quality,
  latency, or billing evidence.
- Threshold tuned on the reported set; generalisation unproven.
- Token estimator is word based, not provider tokenizers.
- Single site: Muse VM on CPU, not the assigned fleet node.

## What would strengthen the candidate

Each item is v1.1 backlog in ROADMAP.md, not done work: the
Ollama generative run, a real private corpus eval, provider
tokenizer counts, a free tier cloud measurement where terms
allow, and a corpus scaling run.

## Venue note

No venue is named as submitted or contacted. Venue choice and
any submission click are Jesun's tap only.
