# local-first-ai

A private local assistant on Ollama, fully offline local RAG, a local against cloud study.

Status: Learn DONE (2026-11-05, ROADMAP-V3-BATCH). Level 1 is built, tested, and measured below. Build and Deep are not started.
Project: P15. Fleet node: BlackBox (GPU). Wave: Wave 7. Learn was run on the Muse VM (CPU); see the level README for the named deduction.

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

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.
