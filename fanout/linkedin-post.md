# LinkedIn post draft: P15 local-first-ai v1.0

Status: DRAFT NOT POSTED
Date drafted: 2026-11-05
Author: Jesun Ahmad Ushno
Rule for this platform: the link goes in the first comment, not in the
post body. The first comment line is at the end of this file.

## Post body

Your files do not have to leave your machine to be searchable.
I built the measurement for that claim, and wrote down where it
stops working.

local-first-ai v1.0 is done: Learn, Build, and Deep, all open,
all measured, Python standard library only.

The scope, up front: there is no Ollama and no language model in
this project. Ollama was unavailable, so the assistant is an
extractive TF-IDF core. Answers are cited sentences copied word
for word, never generated. The cloud side of the study is
modelled from published pricing, never measured.

Learn: 8 synthetic documents, 10 questions, top-1 1.000, recall
at 3 1.000, sentence accuracy 1.000, privacy audit clean.

Build: 24 synthetic documents, 72 chunks, 24 questions (20
evidence, 4 no-evidence), top-1 1.000, chunk recall at 3 1.000,
refusal precision and recall 1.000 at threshold 0.30.

Deep: local mean answer latency 0.3326 ms over 120 timed
answers. Modelled cloud cost: 0.000031 USD per query at budget
rates to 0.000621 USD at flagship rates, 3.11 to 62.13 USD per
100,000 queries. Local marginal API cost: 0 USD. Cloud quality
and latency were not measured.

The honest limit, in the post: the corpus is synthetic with
distinct topics, so those perfect scores are weak evidence.
Local wins cost, speed on this corpus, and privacy. Cloud wins
capability: generation, paraphrase, and synthesis.

Grades, house scale: Learn 8,700, Build 7,100, Deep 7,400 of
10,000. 62 tests in total, plus the smoke test.

When would you keep a document assistant local even if a cloud
model answers better?

## First comment (post this as the first comment, per the standing rule)

Repo, releases v0.1, v0.5, and v1.0, and the full tutorial: https://github.com/JesunAhmadUshno/local-first-ai
