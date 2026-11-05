# Local First, Measured: What a Tiny Offline Assistant Can and Cannot Do

By Jesun Ahmad Ushno
Date: 2026-11-05
Status: DRAFT, written fan-out for P15 local-first-ai v1.0. Not posted.

## The problem

A person wants answers from their own files without handing the
files, or the questions about them, to a third party. Hosted models
made the capability gap wide (generation, paraphrase, synthesis)
while making the privacy transfer routine. This project measures
that trade on one small, fully public, synthetic corpus, instead
of asserting it.

Repository: https://github.com/JesunAhmadUshno/local-first-ai

## Honest scope, stated first

There is no Ollama and no language model in any level. Ollama was
rechecked unavailable on the Muse VM on 2026-11-05, so the
assistant is an extractive TF-IDF core: answers are sentences copied
word for word from the retrieved document, with a citation, never
generated. The cloud side of the Deep study is modelled only from
published pricing checked 2026-11-05, never measured: no API was
called. The corpus is synthetic with distinct topics, so perfect
scores are weak evidence.

## What was built

Learn: a TF-IDF core over 8 synthetic documents (24 sentences,
196 words), 10 labelled questions. Top-1 accuracy 1.000, recall
at 3 1.000, answer sentence accuracy 1.000, privacy audit clean
(2 files, 7 network patterns, 0 matches). Grade 8,700 of 10,000.

Build: a chunked pipeline over 24 synthetic documents (144
sentences, 72 chunks at 30 words per chunk with 10 words overlap),
24 labelled questions (20 evidence, 4 no-evidence), persistent
session memory (3 entries recorded, 3 reloaded identically), and
a refusal rule at threshold 0.30. Grade 7,100 of 10,000.

Deep: the local against cloud study. Local side measured with the
Build pipeline. Cloud side modelled from published pricing only.
Grade 7,400 of 10,000.

## The main result

On the Build eval set the local core measured top-1 1.000, chunk recall at 3 1.000, and refusal precision and recall 1.000, on a synthetic distinct-topic corpus where those perfect scores are weak evidence.

Local answer latency was 0.3326 ms mean over 120 timed answers
(median 0.3528 ms), and local index build time was 3.6389 ms mean
over 5 builds. At a stated token estimate of 163.33 input and
29.46 output tokens per query (word based estimator, not provider
tokenizers), modelled cloud cost per query is 0.000031 USD at
budget rates (gpt-6-luna, claude-haiku-5.5) to 0.000621 USD at
flagship rates (gpt-6.1-sol, claude-sonnet-5.5), or 3.11 USD to
62.13 USD per 100,000 queries. Local marginal API cost is 0 USD.
Cloud quality and latency were not measured; cloud latency is one
labelled assumed range of 1,000 to 3,000 ms.

## The verdict

Local wins cost, speed on this corpus, eval set quality, and
privacy. Cloud wins capability: generation, paraphrase, synthesis,
and general knowledge, none of which the local core does. The Deep
README gives a five step decision rule: privacy and offline go
local, synthesis and general knowledge go cloud, document lookups
go local.

## Limits

- No Ollama, no LLM: the local side is a retrieval core, not the
  full SPEC assistant.
- Synthetic distinct-topic corpus: perfect scores are weak
  evidence for either side.
- Cloud side modelled, not measured: no observed cost, latency,
  or quality.
- Refusal threshold 0.30 was tuned on the same set it is reported
  on.
- All levels ran on the Muse VM (CPU), not the assigned BlackBox
  fleet node.

## Future

The v1.1 backlog is ROADMAP.md in the repo: the Ollama generative
local run, a real private corpus eval, provider tokenizer counts,
a free tier cloud measurement where terms allow, total cost of
ownership, a corpus scaling run, and runtime privacy monitoring.
None of that is claimed as done.

Tests: 62 in total, plus the scaffold smoke test.
