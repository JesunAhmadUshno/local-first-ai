# Tutorial: P15 local-first-ai, course module

Module: P15-local-first-ai
By Jesun Ahmad Ushno
Date: 2026-11-05
Paths updated 2026-11-08 for the portfolio standard v2 layout (code in src/, results in results/, corpus in experiments/corpus/).
License for this tutorial: CC BY 4.0. Code in the repo: Apache-2.0.

## What you will do

You will clone the local-first-ai repo, run all three levels, run
the test suite for each level, and read your own results against
the recorded v1.0 numbers. Every command below was verified by
running it in this fan-out cycle. The project needs Python 3.11
or 3.12 and uses the standard library only. No model, no API, no
Ollama, and no credential are needed.

Two scope facts govern every step. First, there is no Ollama and
no language model: answers are extracted sentences, copied word
for word, with a citation. Second, the corpus is synthetic with
distinct topics, so the perfect scores below are weak evidence,
and the cloud side of Deep is modelled from published pricing,
never measured.

## Step 0: Clone and enter the repo

```text
git clone https://github.com/JesunAhmadUshno/local-first-ai.git
cd local-first-ai
```

Optional smoke check, before the levels:

```text
python -m unittest tests.test_layout -v
```

Expected: scaffold smoke test: PASS, 8 files present.

## Step 1: Level 1, Learn, TF-IDF core with privacy audit

Read the Learn section of REPORT.md first.

```text
python src/run_learn.py
python -m unittest tests.test_learn_local_first -v
```

Expected: 8 documents, 10 questions; top1 10 of 10 = 1.0;
recall at 3 10 of 10 = 1.0; sentence 10 of 10 = 1.0; audit
passed with 0 matches. The runner writes
results/results_learn.json deterministically.

## Step 2: Level 2, Build, chunked assistant pipeline

Read the Build sections of REPORT.md and PROPOSAL.md.

```text
python src/run_build.py
python -m unittest tests.test_build_assistant -v
```

Expected: 24 documents, 72 chunks, 24 questions; top1 20 of 20
= 1.0; chunk recall at 3 20 of 20 = 1.0; sentence 20 of 20 =
1.0; refusal precision 1.0, recall 1.0 (4 of 4 no-evidence
refused at threshold 0.30); audit passed; session reload true.
The runner writes results/results_build.json.

## Step 3: Level 3, Deep, local against cloud study

Read the Deep sections of REPORT.md and PROPOSAL.md.

```text
python src/run_deep.py
python -m unittest tests.test_deep_study -v
```

Expected: local quality top1 20 of 20 = 1.0, sentence 20 of 20
= 1.0, refusal precision and recall 1.0; token estimates mean
input 163.33, mean output 29.46; modelled costs per query from
0.000031 USD (budget) to 0.000621 USD (flagship), and 3.11 USD
to 62.13 USD per 100,000 queries. Timing fields vary between
runs and are excluded from the determinism check. Cloud quality
and latency are not measured in this step.

## Step 4: Full suite

```text
python -m unittest discover -s tests -v
python -m unittest tests.test_layout -v
```

Expected: 62 tests, all passing, plus the scaffold smoke test.

## If your numbers differ

Check the results files (results_learn.json, results_build.json,
results_deep.json) first. For Deep, ignore timing fields when
comparing: they vary by machine load. Every other field should
match the recorded v1.0 values on the same code.
