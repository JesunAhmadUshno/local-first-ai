# local-first-ai

A private local assistant on Ollama, fully offline local RAG, a local against cloud study.

Status: Build DONE (2026-11-05, ROADMAP-V3-BATCH). Levels 1 and 2 are built, tested, and measured below. Deep is not started.
Project: P15. Fleet node: BlackBox (GPU). Wave: Wave 7. Learn and Build were run on the Muse VM (CPU); see the level READMEs for the named deduction. Build has no Ollama and no language model: Ollama was not available on the Muse VM when checked on 2026-11-05, so Build is an extractive assistant core, named plainly in level-2-build/BUILD-SPEC.md.

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

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
