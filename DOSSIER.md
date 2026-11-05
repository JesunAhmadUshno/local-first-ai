# DOSSIER: local-first-ai (P15)

Written under the documentation and publishing standard (past,
present, future). Updated at Deep ship time, 2026-11-05: all
three levels are built, tested, and measured. v1.0 is the
December compressed scope; the rest of the v2 scope is the
v1.1 backlog in ROADMAP.md.

## Past

Prior art: local assistant bundles (Ollama class setups) and
hosted chat APIs. The problem is old: a person wants answers
from their own files without handing the files, or the
questions about them, to a third party. Hosted models made the
capability gap wide (generation, paraphrase, synthesis) while
making the privacy transfer routine. This project measures
that trade on one small, fully public, synthetic corpus,
instead of asserting it.

## Present

Shipped v1.0 (2026-11-05), all measured on the Muse VM,
Python 3.12, standard library only:

- Learn: TF-IDF core over 8 synthetic documents, 10 labelled
  questions, top-1 and sentence accuracy 1.000, privacy audit
  clean. Grade 8,700 of 10,000.
- Build: chunked TF-IDF pipeline over 24 synthetic documents
  (72 chunks), 24 labelled questions, top-1, recall, sentence,
  and refusal metrics all 1.000, persistent session memory,
  privacy audit clean. Grade 7,100 of 10,000.
- Deep: the local against cloud study. Local side measured
  (quality 1.000 on the Build eval set, mean answer latency
  0.3326 ms over 120 timed answers, privacy audit clean).
  Cloud side modelled from published pricing checked
  2026-11-05 (OpenAI, Anthropic, Google pricing pages):
  modelled cost per query from 0.000031 USD at budget rates
  (gpt-6-luna, claude-haiku-5.5) to 0.000621 USD at flagship
  rates (gpt-6.1-sol, claude-sonnet-5.5), at a stated token
  estimate of 163.33 input and 29.46 output tokens per query.
  Cloud quality and latency were not measured; the verdict is
  a five step decision rule (privacy and offline go local,
  synthesis and general knowledge go cloud, document lookups
  go local). Grade 7,400 of 10,000.

Honest limits that ship with v1.0: no Ollama and no language
model ran locally (Ollama rechecked unavailable on the Muse
VM, 2026-11-05); the corpus is synthetic with distinct topics,
so perfect scores are weak evidence; the cloud side is a
pricing model, not a measurement; token counts come from a
word based estimator, not provider tokenizers.

Current demand evidence: hiring value 2 of 5 (few postings,
v2 rank 16) [confirmed, fleet and scoring pass 2026-11-04].
The value of this project is positioning: a measured, public,
local first study with its failure modes written down.

## Future

The v1.1 backlog is ROADMAP.md at the repo root: the Ollama
generative local run, a real private corpus eval, provider
tokenizer counts, a free tier cloud measurement where terms
allow, total cost of ownership, a corpus scaling run, runtime
privacy monitoring, and fan-out completion. Any forecast
about this field is [unverified] unless a dated primary
source is added here.
