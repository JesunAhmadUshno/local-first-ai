# local-first-ai

A private local assistant on Ollama, fully offline local RAG, a local against cloud study.

Status: Deep DONE, v1.0 SHIPPED (2026-11-05, ROADMAP-V3-BATCH). All three levels are built, tested, and measured below. The v1.1 backlog is ROADMAP.md at the repo root.
Project: P15. Fleet node: BlackBox (GPU). Wave: Wave 7. All levels were run on the Muse VM (CPU); see the level READMEs for the named deduction. There is no Ollama and no language model in any level: Ollama was rechecked unavailable on the Muse VM on 2026-11-05, so the assistant is an extractive core, named plainly in level-2-build/BUILD-SPEC.md, and Deep compares that measured local core against cloud costs modelled from published pricing only.

## Start here

1. Read SPEC.md for scope and acceptance criteria.
2. Read DOSSIER.md for the past, present, and future of this problem (v1).
3. Read NOVELTY.md for the proposed novelty (DRAFT, pending the Jev claim_check gate).
4. Start at level-1-learn/README.md, then level-2-build, then level-3-deep.

## Level map

- Level 1, Learn: the core idea, built small and clean, with a teaching path.
- Level 2, Build: a real working system other people can run.
- Level 3, Deep: benchmarks, optimization, evaluation, hard cases.

## Benchmarks

Measured 2026-11-05 with level-1-learn/run_learn.py on the Muse VM, Python 3.12. The documents are synthetic, the retrieval is TF-IDF, and the answers are extracted sentences, not a real LLM.

| Test | Result |
| --- | --- |
| Learn corpus | 8 synthetic documents, 24 sentences, 196 words, 1,179 characters |
| Labelled questions | 10 questions with gold document and gold sentence |
| Top-1 accuracy | 1.000 (10 of 10) |
| Recall at 3 | 1.000 (10 of 10) |
| Answer sentence accuracy | 1.000 (10 of 10) |
| Privacy audit | 2 source files scanned, 7 network patterns, 0 matches, passed |
| Unit tests | 21 passed, plus the scaffold smoke test |
| Determinism | results_learn.json identical across two runs (hash verified) |

Measured 2026-11-05 with level-2-build/run_build.py on the Muse VM, Python 3.12. The documents are synthetic, the retrieval is TF-IDF over chunks, and the answers are extracted sentences, not a real LLM.

| Test | Result |
| --- | --- |
| Build corpus | 24 synthetic documents, 144 sentences, 1,472 words, 9,290 characters |
| Chunks | 72 chunks, 30 words per chunk, 10 words overlap |
| Labelled questions | 24 questions: 20 evidence, 4 no-evidence |
| Top-1 document accuracy | 1.000 (20 of 20) |
| Chunk recall at 3 | 1.000 (20 of 20) |
| Answer sentence accuracy | 1.000 (20 of 20) |
| Refusal precision / recall | 1.000 / 1.000 (4 of 4 no-evidence refused, threshold 0.30) |
| Privacy audit | 2 source files scanned, 7 network patterns, 0 matches, passed |
| Session memory | 3 entries recorded, 3 reloaded identically |
| Unit tests | 42 passed in total (21 Learn, 21 Build), plus the scaffold smoke test |
| Determinism | results_build.json identical across two runs (hash verified) |
| Build grade | 7,100 of 10,000 (deductions in level-2-build/README.md) |

Measured and modelled 2026-11-05 with level-3-deep/run_deep.py on the Muse VM, Python 3.12. Local figures are measured with the Build pipeline. Cloud figures are MODELLED from published pricing checked 2026-11-05, never measured: no API was called.

| Test | Result |
| --- | --- |
| Local quality on the Build eval set | Top-1 1.000, sentence 1.000, refusal precision and recall 1.000 |
| Local answer latency, mean | 0.3326 ms over 120 timed answers (median 0.3528 ms) |
| Local index build time, mean | 3.6389 ms over 5 builds |
| Token estimate (stated assumption) | Mean 163.33 input and 29.46 output tokens per query |
| Modelled cloud cost per query | 0.000031 USD budget (gpt-6-luna, claude-haiku-5.5) to 0.000621 USD flagship (gpt-6.1-sol, claude-sonnet-5.5) |
| Modelled cloud cost per 100k queries | 3.11 USD budget to 62.13 USD flagship; local marginal API cost 0 USD |
| Cloud quality and latency | Not measured; capability comparison plus one labelled assumed latency range (1,000 to 3,000 ms) |
| Privacy | Local: Deep audit 2 files, 7 patterns, 0 matches. Cloud: prompt and retrieved chunks leave the machine by construction |
| Unit tests | 62 passed in total (42 prior, 20 new Deep), plus the scaffold smoke test |
| Determinism | results_deep.json deterministic part identical across two runs (hash verified), timing fields excluded |
| Deep grade | 7,400 of 10,000 (deductions in level-3-deep/README.md) |
| Verdict | Local wins cost, speed on this corpus, eval set quality, and privacy; cloud wins capability (generation, paraphrase, synthesis). Full decision rule in level-3-deep/README.md |

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.

## Fan-out

Written fan-out set for v1.0 in fanout/: blog-post.md,
tutorial.md (every command verified by running it),
website-page.md, linkedin-post.md (DRAFT NOT POSTED, link as
the first-comment line), paper-candidate.md (submission is
Jesun's tap), and release-notes.md covering v0.1, v0.5, and
v1.0. The full channel log and per-piece publicity grades are
in PUBLICITY.md. Overall fan-out grade: 9,457 of 10,000.
Social posting is held under the standing platform rules:
Threads awaits Jesun's tap, and the video is held for the
January engine queue.
