# local-first-ai

A private local assistant study: fully offline local retrieval over synthetic documents, and a local against cloud comparison where the local side is measured and the cloud side is modelled from published pricing only. There is no Ollama and no language model in any level: Ollama was rechecked unavailable on the Muse VM on 2026-11-05, so the assistant is an extractive TF-IDF core, and Deep compares that measured core against cloud costs modelled from published pricing, never measured.

- Learn: TF-IDF core over 8 synthetic documents, 10 labelled questions, top-1 accuracy 1.000, recall at 3 1.000, answer sentence accuracy 1.000, privacy audit clean (2 files, 7 patterns, 0 matches). Grade 8,700 of 10,000.
- Build: chunked TF-IDF pipeline over 24 synthetic documents (72 chunks, 30 words per chunk, 10 words overlap), 24 labelled questions (20 evidence, 4 no-evidence), top-1 document accuracy 1.000, chunk recall at 3 1.000, answer sentence accuracy 1.000, refusal precision and recall 1.000 at threshold 0.30, privacy audit clean. Grade 7,100 of 10,000.
- Deep: local against cloud study. Local measured top-1 1.000, chunk recall at 3 1.000, refusal precision and recall 1.000 on the Build eval set, mean answer latency 0.3326 ms over 120 timed answers. Cloud side modelled only: 0.000031 USD per query at budget rates to 0.000621 USD at flagship rates, 3.11 USD to 62.13 USD per 100,000 queries, at 163.33 input and 29.46 output tokens per query (word based estimate). Cloud quality and latency were not measured. Grade 7,400 of 10,000.

The perfect local scores are weak evidence: the corpus is synthetic with distinct topics, so retrieval is easy. That limit is stated in every level README.

Grades on record (of 10,000): Learn 8,700, Build 7,100, Deep 7,400.

Every number above is already published in this repo (README.md, DOSSIER.md, and the three level READMEs and results files) and reproduced by the runners in this repo, checked in CI.

Releases: https://github.com/JesunAhmadUshno/local-first-ai/releases
