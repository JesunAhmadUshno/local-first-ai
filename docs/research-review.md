# Research review: local-first-ai

Reviewed 2026-11-07 against a doctoral-level research rubric. This file grades the study as research, lists what was fixed in this change, and names the exact compute or data each remaining gap needs. Every number below comes from a committed results file: `level-1-learn/results_learn.json`, `level-2-build/results_build.json`, `level-3-deep/results_deep.json`, or the new `level-3-deep/results_rigor.json` (written by `level-3-deep/run_rigor.py`, rerun in CI).

## Verdict

| | Before this change | After this change |
| --- | --- | --- |
| As doctoral research | about 6.0 / 10 | about 6.8 / 10 |
| As engineering hygiene | about 8 / 10 | about 8.5 / 10 |

The engineering is strong: standard library only, deterministic hashed results, a CI matrix, and honest limits written in every level README. The research is held back by one thing above all: the central question (a local language model against a cloud one) is not answered, because no local generative model ran and the cloud side is modelled from pricing, not measured. This change does not and cannot fix that without a GPU and paid API calls. What it does fix is the measurable rigor of the local side: uncertainty, a held-out threshold, baselines, a sensitivity sweep, a harder question set, a scaling curve and a runtime egress test.

## Rubric

| Criterion | Grade before | What was missing | Fixed in this change | Grade after |
| --- | --- | --- | --- | --- |
| Research question | 6 | The stated question (local LLM against cloud) is broader than what was run (extractive TF-IDF against modelled cloud cost). | Not fixable cheaply; scope stated plainly on the dashboard banner and here. | 6 |
| Hypotheses | 4 | No written hypotheses or falsification rules. | Hypotheses stated below, each with its test and result. They are written after the original runs, so they are post hoc for the labelled set; the hard set was written before its first run. | 5 |
| Method | 7 | Clear, deterministic, but parameters (chunk size, overlap, threshold) never varied. | Chunk size and overlap sweep (24 settings), threshold curve (17 thresholds). | 8 |
| Baselines and ablations | 3 | No baseline at all. | BM25 over the same chunks, and TF-IDF over whole documents (no chunking) as an ablation. | 6 |
| Statistics and uncertainty | 3 | Point estimates only on n = 20 and n = 4. | Wilson 95% intervals for every count metric, recorded and shown on the dashboard. | 7 |
| Threshold validity | 3 | REFUSAL_THRESHOLD 0.30 tuned on the set it is reported on. | Leave-one-out threshold: each question scored with a threshold fitted on the other 23. | 7 |
| Construct validity | 3 | 24 synthetic documents on 24 topics, questions reuse document wording, perfect scores are a ceiling. | A 16-question hard set: 10 synonym paraphrases and 6 cross-topic distractors. The drop is reported. | 5 |
| Reproducibility | 9 | Already strong. | The rigor run joins CI; the dashboard build fails if the browser port drifts from the recorded results. | 9 |
| Threats to validity | 7 | Listed honestly in each README. | The hard set and threshold curve turn two listed threats into measured ones. | 8 |
| Related work | 2 | NOVELTY.md is an unfilled draft with "NO MEASUREMENT YET". | A short related-work section below. A measured comparison against real local tools still needs compute (see remaining gaps). | 4 |
| Limitations | 8 | Already candid. | Carried onto every dashboard panel next to the numbers it qualifies. | 8 |

## Hypotheses and results

H1. TF-IDF chunk retrieval finds the gold document for evidence questions on this corpus.
Result: 20 of 20 top-1 correct. Wilson 95% interval 0.839 to 1.000. Supported, with the ceiling caveat: the lower bound says the true rate on questions like these could be as low as about 84%.

H2. A single score threshold separates evidence from no-evidence questions without tuning on the test items.
Result: leave-one-out refusal is 4 of 4 with 0 false refusals; the fitted thresholds range from 0.335 to 0.356 (0.338 when fitted on all 24). Supported on the labelled set. The refusal recall interval is wide: Wilson 95% 0.510 to 1.000, because only 4 no-evidence questions exist.

H3. The H2 separation survives questions the documents do not word-match.
Result: not supported. On the hard set at the 0.30 threshold, 2 of 10 paraphrases were answered from the right document (8 refused, though 6 of 10 had the right document as the top chunk) and only 2 of 6 cross-topic distractors were refused. Paraphrase and distractor scores overlap, so no single threshold separates them. This is the honest ceiling of exact token matching, now measured.

H4. Chunking and the ranking function matter on this corpus.
Result: not testable here. TF-IDF over 30/10 chunks, BM25 over the same chunks, and TF-IDF over whole documents all score 20 of 20 top-1 and 20 of 20 recall at 3. Across the 24-point chunk sweep, top-1 stays 20 of 20; only refusal changes, with chunks of 10 or 15 words refusing just 1 of 4 no-evidence questions, because a short chunk sharing one word scores high. The labelled set is too easy to rank retrieval settings.

H5. Local latency stays interactive as the corpus grows.
Result: on the corpus replicated with new ids (synthetic scaling, wall clock on the machine that ran `run_rigor.py`), mean answer latency grows roughly linearly from 0.143 ms at 72 chunks to 13.7 ms at 7,200 chunks, and index build from 1.16 ms to 107 ms. Supported up to 7,200 chunks; the brute-force scan is linear, so a much larger private folder would need an inverted index.

## What changed in this branch

- `level-3-deep/rigor.py` and `level-3-deep/run_rigor.py`: Wilson intervals, leave-one-out threshold, threshold curve, BM25 baseline, whole-document ablation, chunk sweep, hard question set, scaling curve. Standard library only, under one second. Deterministic except the labelled scaling block.
- `tests/test_deep_rigor.py`: tests for each helper, including hand-computed Wilson bounds and a network-pattern audit of the new sources.
- `tests/test_deep_egress.py`: a runtime egress test. Every socket constructor and name lookup is replaced with a function that raises, then ingest, indexing, answering, refusal, evaluation and session memory run end to end. Before this, the privacy claim rested on a static source scan.
- `site/`: the live dashboard. Its `engine.check.mjs` runs inside `npm run build` and asserts that the in-browser port reproduces every recorded top-1 document, score (to 1e-9; the observed difference is 0), refusal, answer sentence and answer text in `results_build.json`, the Learn results in `results_learn.json`, all 24 sweep rows, the threshold curve, the leave-one-out result, all 16 hard-set rows, the Wilson intervals, and all six modelled cost rows in `results_deep.json`.

## Related work (positioning, not measured)

- Sparse retrieval: TF-IDF weighting (Salton and Buckley, 1988, "Term-weighting approaches in automatic text retrieval") and BM25 (Robertson and Zaragoza, 2009, "The Probabilistic Relevance Framework: BM25 and Beyond"). This study uses the first and now reports the second as a baseline.
- Retrieval-augmented generation: Lewis et al., 2020, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks". This study implements only the retrieval half and returns extracted sentences instead of generated text.
- Local model runtimes and local document question-answering tools such as llama.cpp, Ollama, GPT4All and PrivateGPT pair a local generative model with retrieval over personal files. This study ran none of them (Ollama was unavailable on the study VM, see `level-3-deep/results_deep.json`), so it makes no measured claim against them.
- Interval estimation for small samples: Wilson, 1927, "Probable inference, the law of succession, and statistical inference", the interval used here.

The honest novelty, at present, is not the retrieval method. It is a fully reproducible, standard-library, offline baseline with a privacy audit and a live browser replica that is checked against its own recorded results.

## Remaining gaps and what each one needs

| Gap | Why it is not fixed here | Exact compute or data needed |
| --- | --- | --- |
| No local generative model | Needs a model runtime and weights; GPU work is out of scope for this change. | Ollama (or llama.cpp) with a 7B to 8B instruction model on the BlackBox GPU node, running the same 24 + 16 questions with the same retrieved chunks; about one GPU hour including grading. |
| Cloud quality, latency and billed cost not measured | Every call is a paid or rate-limited API call. | API keys for the six recorded models; 40 questions times 6 models = 240 calls per run, about 0.07 USD at the recorded modelled rates, plus a blind grading protocol for answer quality. |
| Synthetic, easy corpus | A realistic test needs real documents with consent or a licence, and labels. | A public proxy corpus of personal-style text (for example a released email or notes collection under an open licence) with at least 100 human-written questions and gold passages; roughly a day of annotation by two annotators with agreement measured. |
| Too few questions for tight intervals | More labelled questions are new data, not compute. | With all answers correct, the Wilson lower bound passes 0.95 only at about 73 questions; at least 75 evidence and 25 no-evidence questions, written by someone who has not read the corpus closely. |
| Multi-hop questions | The extractive core cannot combine facts by design. | Only meaningful once a generative model runs (first row); then a 20-question multi-hop set with two gold passages each. |
| Runtime egress at the operating-system level | The new test blocks Python sockets in-process; it does not sandbox the process. | A run inside a network namespace (`unshare -rn` on Linux, or a container with networking disabled) in CI, which needs a runner that permits user namespaces. |
| Latency on the target fleet node | Timings come from the study VM and from the machine that ran `run_rigor.py`. | One rerun of `run_deep.py` and `run_rigor.py` on the BlackBox node, under five minutes of CPU. |
| Electricity and hardware cost of local | Needs metering, not code. | A power meter reading over a fixed query load, plus the hardware price and lifetime assumption, to turn local cost into USD per query. |
