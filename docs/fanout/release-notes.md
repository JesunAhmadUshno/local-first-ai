# Release notes: local-first-ai (P15)

One section per release line. Every number below comes from the
level README of that release and the release text on GitHub,
verified with gh release list on 2026-11-05. There is no Ollama
and no language model in any release, and the Deep cloud side is
modelled from published pricing, never measured. The full
release text lives on the GitHub releases page:
https://github.com/JesunAhmadUshno/local-first-ai/releases

## v0.1, Learn (2026-11-05)

- What shipped: a TF-IDF core over 8 synthetic documents with
  cited extractive answers and a privacy audit, standard library
  only, plus 21 unit tests and the scaffold smoke test.
- Measured result: 10 labelled questions, top-1 1.000, recall
  at 3 1.000, answer sentence accuracy 1.000, privacy audit
  clean (2 files, 7 patterns, 0 matches).
- Release: https://github.com/JesunAhmadUshno/local-first-ai/releases/tag/v0.1

## v0.5, Build (2026-11-05)

- What shipped: a chunked assistant pipeline over 24 synthetic
  documents (72 chunks), multi-sentence cited answers, refusal
  at threshold 0.30, and persistent session memory, plus 21 new
  tests (42 unit tests in total with Learn).
- Measured result: 24 questions (20 evidence, 4 no-evidence),
  top-1 1.000, chunk recall at 3 1.000, sentence 1.000, refusal
  precision and recall 1.000, privacy audit clean, session
  memory 3 entries reloaded identically.
- Release: https://github.com/JesunAhmadUshno/local-first-ai/releases/tag/v0.5

## v1.0, Learn, Build, and Deep (2026-11-05)

- What shipped: the local against cloud study on top of Learn
  and Build, plus 20 new tests (62 unit tests in total, plus
  the scaffold smoke test). The rest of the v2 scope is named
  in ROADMAP.md as the v1.1 backlog.
- Measured and modelled result: local top-1 1.000, chunk recall
  at 3 1.000, refusal precision and recall 1.000, mean answer
  latency 0.3326 ms over 120 timed answers; modelled cloud cost
  0.000031 USD per query at budget rates to 0.000621 USD at
  flagship rates (3.11 to 62.13 USD per 100,000 queries) at
  163.33 input and 29.46 output tokens per query. Cloud quality
  and latency not measured.
- Release: https://github.com/JesunAhmadUshno/local-first-ai/releases/tag/v1.0

## Held channels

- Social posts for every release above: HELD under the standing
  platform rules. The loop prepares drafts and never posts;
  Threads needs Jesun's one tap per post.
- The v1.1 backlog lives in ROADMAP.md: Ollama generative run,
  real private corpus eval, provider tokenizer counts, free tier
  cloud measurement, total cost of ownership, corpus scaling,
  and runtime privacy monitoring.
