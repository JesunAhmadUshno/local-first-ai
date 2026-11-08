# Report: local-first-ai (P15)

Exploratory, not pre-registered (PROPOSAL.md says why). This file
holds the background, method, results, misses, threats and
conclusion. Sections below "Background" are the level READMEs, the
2026-11-07 research review and ROADMAP.md, moved here on 2026-11-08
with grades removed and run commands updated to the src/ layout.
Mentions of "this folder" or "this level" inside them refer to the
old level-1-learn/, level-2-build/ and level-3-deep/ folders: code is
now in src/, the Build corpus in experiments/corpus/, results in
results/, and the specs in PROPOSAL.md Part 2.

## Current state

- What ran: a standard-library, offline, extractive TF-IDF assistant
  (ingest, chunk, rank, cited answer, refusal, session memory) on a
  synthetic 24-document corpus, plus a Learn core on 8 documents. It
  ran end to end on the Muse VM (CPU, Python 3.12) on 2026-11-05 and
  the rigor add-ons on 2026-11-07; CI re-runs every runner.
- What did not run: no local language model (Ollama was unavailable
  on the study VM) and no cloud API. The cloud side of the local
  against cloud question is modelled from published pricing.
- So the original question (a local assistant against a cloud one,
  on cost, speed, quality and privacy) is answered only for cost (a
  model) and privacy (by construction); quality and speed are
  answered for the extractive local core alone.

## Questions scored

Written 2026-11-07, after the main runs (post hoc), except the hard
set. Every number below is read from results/results_rigor.json.

| Hypothesis | Result | Status |
| --- | --- | --- |
| H1. Chunk retrieval finds the gold document | 20 of 20 top-1, Wilson 95% 0.839 to 1.000 | Supported, ceiling caveat |
| H2. One threshold separates evidence from no-evidence without tuning on the test items | Leave-one-out: 4 of 4 refused, 0 false refusals; refusal recall Wilson 95% 0.510 to 1.000 | Supported on the labelled set, wide interval |
| H3. The separation survives questions that do not word-match | Hard set at 0.30: 2 of 10 paraphrases answered correctly (8 refused, 6 of 10 had the right top document), 2 of 6 distractors refused | MISS: not supported |
| H4. Chunking and the ranking function matter here | TF-IDF chunks, BM25 chunks and whole-document TF-IDF all 20 of 20; only refusal moves in the 24-point sweep | MISS: not testable, set too easy |
| H5. Latency stays interactive as the corpus grows | 0.143 ms at 72 chunks to 13.7 ms at 7,200 chunks, roughly linear (wall clock, one machine) | Supported to 7,200 chunks |
| Original Deep question: local against cloud on cost, speed, quality, privacy | Local measured; cloud cost modelled (0.000031 to 0.000621 USD per query), cloud quality and latency not measured | Partly answered |

The misses are the finding: exact token matching fails on
paraphrase, and the labelled set is too easy to rank retrieval
settings or to give tight intervals.

## Headline evidence

Each headline number regenerates from the committed corpus and code,
and is printed from the results file by:

```text
python3 src/check_results.py
python3 -c "import json; r=json.load(open('results/results_rigor.json')); print(r['intervals']['top1'])"
python3 -c "import json; r=json.load(open('results/results_rigor.json')); print(r['threshold']['leave_one_out'], r['intervals']['refusal_recall'])"
python3 -c "import json; r=json.load(open('results/results_rigor.json')); print({k: v for k, v in r['hard_set'].items() if k != 'rows'})"
```

## Compute, data and versions

- Machine: the Muse VM, CPU only, Python 3.12 (2026-11-05 runs); the
  rigor scaling block on the machine that ran src/run_rigor.py on
  2026-11-07. Not the assigned BlackBox fleet node. No GPU.
- Data: 24 synthetic text files in experiments/corpus/ (corpus
  fingerprint in results/results_build.json); 8 synthetic Learn
  documents and all question sets are defined in the code
  (src/local_first.py, src/assistant.py, src/rigor.py).
- Dependencies: Python standard library only. Pricing snapshot
  checked 2026-11-05 (sources in PROPOSAL.md Part 2, DEEP-SPEC).
- Uncertainty: Wilson 95% intervals on every count metric. Wall clock
  fields vary between runs and are excluded from the regeneration
  check (docs/decisions/0003).
- The string "(level-2-build results)" inside results_deep.json names
  the old folder; it is kept so the recorded file regenerates
  unchanged.

## Background: Learn (recorded 2026-11-05)

Status: DONE (2026-11-05). A local-first assistant core: a small
set of synthetic documents stored locally, TF-IDF retrieval, an
extractive answer with a citation, and a privacy audit, built
with the Python standard library only.

### Honest scope line

The documents are synthetic. No real private file is read, indexed,
or shown anywhere in this level. There is no Ollama, no real LLM,
no embedding model, and no network call: the answer is one sentence
copied word for word from the retrieved document, with its
citation. A real local model on Ollama over real private files is
Build level scope. The local against cloud study is Deep scope.

### Method

1. Local corpus. Eight synthetic documents, three sentences each,
   held as local data in the code (garden notes, home budget,
   japan trip plan, bicycle repair log, sourdough journal, home
   network notes, exercise routine, photography notes). Document
   ids, titles, and sentences are validated first: duplicate ids,
   empty titles, and sentences with no content tokens raise a
   named LocalFirstError.
2. Tokenizing. Text is lowercased, split into alphanumeric tokens,
   and a small fixed stopword list is removed. No stemming is done,
   so word forms must match exactly.
3. TF-IDF index. Each term gets a smoothed inverse document
   frequency, idf = log((1 + N) / (1 + df)) + 1, over the N = 8
   documents. A document vector holds (count / total tokens) times
   idf per term. Questions are vectorized with the same idf.
4. Retrieval. Documents are ranked by cosine similarity to the
   question. Ties break on document id, so ranking is fully
   deterministic, including the all-zero case.
5. Extractive answer. Inside the top document, sentences are
   scored by the same cosine measure and the best sentence is
   returned unchanged, with a citation that names the document
   and the sentence, for example [D02 S2]. One sentence, one
   citation. Nothing is generated or paraphrased.
6. Privacy audit. Two parts. First, an inventory lists every
   indexed document with its sentence, word, and character
   counts and a sha256 hash of its exact text. Second, a source
   scan counts seven network patterns in this level's own two
   source files and reports the count per pattern. The pattern
   names are built from fragments inside the audit code, so the
   scanner does not flag its own pattern list.
7. Scoring. Each labelled question carries a gold document and a
   gold sentence. Top-1 accuracy is the share whose first
   retrieved document is gold. Recall at 3 is the share whose
   gold document appears in the top 3. Sentence accuracy is the
   share whose chosen answer sentence is the gold sentence in
   the gold document.

### Run it

    python src/run_learn.py
    python -m unittest tests.test_learn_local_first -v
    python -m unittest tests.test_layout -v

The runner writes results/results_learn.json deterministically:
run it twice and the file is identical (verified 2026-11-05:
sha256 87978c5c087e0d4c08ae7284d653a02c0035b2715e2d5a9a243dfcd546d4c4a9
on both runs).

### Results (measured 2026-11-05, Muse VM, Python 3.12)

| Q | Question | Gold | Top 1 | Top 1 score | Top 3 | Hit at 1 | Hit at 3 | Answer | Sentence ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | tomatoes weekly watering sun | D01 S1 | D01 | 0.5371 | D01, D07, D02 | yes | yes | D01 S1 | yes |
| Q02 | emergency fund covers three months living costs | D02 S2 | D02 | 0.6153 | D02, D03, D01 | yes | yes | D02 S2 | yes |
| Q03 | train pass travel Tokyo Kyoto | D03 S1 | D03 | 0.5315 | D03, D01, D02 | yes | yes | D03 S1 | yes |
| Q04 | chain cleaning fresh lubricant | D04 S1 | D04 | 0.4625 | D04, D01, D02 | yes | yes | D04 S1 | yes |
| Q05 | starter rises feeding flour | D05 S1 | D05 | 0.5164 | D05, D01, D02 | yes | yes | D05 S1 | yes |
| Q06 | router shelf thick walls | D06 S1 | D06 | 0.4714 | D06, D01, D02 | yes | yes | D06 S1 | yes |
| Q07 | morning stretches shoulders hips | D07 S1 | D07 | 0.4754 | D07, D01, D02 | yes | yes | D07 S1 | yes |
| Q08 | tripod camera long exposures | D08 S1 | D08 | 0.4573 | D08, D04, D01 | yes | yes | D08 S1 | yes |
| Q09 | compost soil spring planting | D01 S3 | D01 | 0.4396 | D01, D02, D03 | yes | yes | D01 S3 | yes |
| Q10 | brake pads wheel rim | D04 S2 | D04 | 0.4625 | D04, D01, D02 | yes | yes | D04 S2 | yes |

Scores are rounded to 4 decimal places in this table. Full float
scores are in results_learn.json. In most rows the second and
third ranked documents score 0.0: the question shares no content
term with them, so their order is the deterministic document id
tie break, not evidence of closeness. Recall at 3 on this corpus
must be read with that fact in mind.

Document inventory (hashes shortened to 12 characters here, full
hashes in results_learn.json):

| Doc | Title | Sentences | Words | Chars | sha256 (first 12) |
| --- | --- | --- | --- | --- | --- |
| D01 | garden notes | 3 | 23 | 148 | 4d7f88db5415 |
| D02 | home budget | 3 | 25 | 150 | b2fbb2b310e4 |
| D03 | japan trip plan | 3 | 25 | 149 | dd096eb13893 |
| D04 | bicycle repair log | 3 | 25 | 146 | af6fb8c26a20 |
| D05 | sourdough journal | 3 | 26 | 142 | 544cba8c19e6 |
| D06 | home network notes | 3 | 26 | 149 | d9eeb3be71d2 |
| D07 | exercise routine | 3 | 23 | 144 | abb045ccbe69 |
| D08 | photography notes | 3 | 23 | 151 | 8b3d4a77f69c |

Privacy audit: 2 source files scanned (local_first.py and
run_learn.py), 7 patterns, 0 matches for every pattern (socket,
urllib, requests, urlopen, http.client, ftplib, smtplib), total
0, passed true, local only true.

Summary: Learn ran one deterministic local-first evaluation on the Muse VM: 8 synthetic documents (24 sentences, 196 words) indexed with TF-IDF, 10 labelled questions scored top-1 accuracy 1.000 (10 of 10), recall at 3 1.000 (10 of 10), and answer sentence accuracy 1.000 (10 of 10), with a privacy audit scanning 2 source files for 7 network patterns and finding 0 matches, and 21 unit tests passing plus the scaffold smoke test.

Hand checks: top-1 accuracy is 10 correct of 10 questions = 1.000,
and recall at 3 and sentence accuracy are the same count, 10 of
10 = 1.000. Words are 23 + 25 + 25 + 25 + 26 + 26 + 23 + 23 =
196. Characters are 148 + 150 + 149 + 146 + 142 + 149 + 144 +
151 = 1,179. Sentences are 8 documents times 3 = 24. The term
tomatoes sits in 1 of 8 documents, so its idf is log(9 / 2) + 1 =
log(4.5) + 1 = 2.504077397. The term covers sits in 2 of 8
documents (D02 and D03), so its idf is log(9 / 3) + 1 = log(3) +
1 = 2.098612289. The Q02 answer is the second sentence of D02,
so its citation is [D02 S2].

### Learn failure modes and limits

- Tiny synthetic corpus: 8 documents on 8 distinct topics, with
  almost no vocabulary overlap between topics. Perfect scores on
  this set are expected and are weak evidence: real private
  files share vocabulary, use synonyms, and ask messy questions,
  and every one of those cases is unmeasured here.
- No stemming and no synonyms: token forms must match exactly.
  A question that says watering when the document says water, or
  that uses a synonym, scores lower or fails outright. The unseen
  terms test shows the floor: a question with no corpus term
  scores 0.0 against every document and returns documents in id
  order, with no signal that nothing matched.
- Recall at 3 is inflated by the corpus shape: with only 8
  documents and mostly zero-score runners-up, appearing in the
  top 3 is a low bar. Top-1 accuracy is the honest headline here.
- One extracted sentence per answer: no multi-sentence answers,
  no combining facts across documents, no paraphrase, and no
  check that the chosen sentence actually answers in natural
  language beyond the gold sentence labels in this small set.
- The privacy audit is a source pattern scan, not a proof about
  the machine: it shows this level's code contains no network
  pattern, but it does not monitor the operating system, does
  not sandbox the process, and does not prove that other code on
  the machine stays offline.
- No real private data was evaluated, on purpose. Nothing here
  measures behaviour on real files, real file formats, or a real
  folder tree. Those are Build level scope, with real consent
  and real local files.
- This level was run on the Muse VM (CPU), not on its fleet node
  BlackBox (GPU). Learn is CPU teaching work and uses no GPU, but
  the fleet node rule still names this as a grade deduction.

### What Build adds next

A real assistant on Ollama over real local private files, fully
offline, with file format handling, chunking, and the same audit
extended to runtime network monitoring. See the root README
level map.

## Method and results: Build (recorded 2026-11-05)

Status: DONE (2026-11-05). A full local assistant pipeline, end
to end, on local files: ingest a directory of documents, chunk
them, index the chunks with TF-IDF, answer with multi-sentence
extractive answers cited per sentence, refuse below a named
threshold, and keep a persistent session memory. Standard
library only. The build spec, written before the code, is
BUILD-SPEC.md in this folder.

### Honest scope line

There is no Ollama and no language model in this level. Ollama
was checked on 2026-11-05 on the Muse VM: no ollama binary was
found and no server answered on localhost port 11434, so the
SPEC assistant is built as an extractive core instead of an LLM,
and that substitution is named in BUILD-SPEC.md, not hidden.
The corpus is synthetic: 24 documents committed as data files,
standing in for a private folder. No real private file is read.
Answers are sentences copied word for word from the retrieved
document, never generated. This level ran on the Muse VM on
CPU, not on the assigned BlackBox fleet node, which was
unreachable this cycle (NEEDS-BLACKBOX-ON).

### Method

1. Ingest. Every .txt file in data/ is read in sorted file name
   order. The first line is a Title line, the document id is the
   file name (B01 to B24), and the body is split into sentences.
   The 24 documents cover 24 named topics: garden, budget, Japan
   travel, bicycle repair, sourdough, home network, exercise,
   photography, knife care, houseplants, winter car care,
   painting, camping, tax records, first aid, aquarium, coffee,
   laptop backup, laundry, dog training, piano, astronomy,
   plumbing, and sewing. Each document has 6 sentences.
2. Inventory. Each document is counted (sentences, words,
   characters) and hashed with sha256 over its exact text, using
   the Learn helper. The corpus totals 144 sentences, 1,472
   words, and 9,290 characters. One fingerprint hash over the 24
   sorted document hashes is
   11964044d39406c51d767be94aa057c6dfc2f077ef97fa2dc6199b267e96c866.
3. Chunk. Documents are split into overlapping word chunks:
   chunk size 30 words, overlap 10 words, step 20 words. Every
   document here makes exactly 3 chunks, so the index holds 72
   chunks. Each chunk records its word offsets.
4. Index. TF-IDF over chunks, reusing the Learn functions by
   import (tokenize, compute_idf, tfidf_vector, cosine), with
   the Learn smoothed idf, log((1 + N) / (1 + df)) + 1, at
   N = 72 chunks.
5. Answer. The top chunk decides the top document. Inside that
   document, sentences are scored by the same cosine measure
   and the best two distinct sentences are returned unchanged,
   each with its own citation, for example [B01 S1]. The first
   sentence is the scored answer; the second is supporting
   context from the same document and can be weakly related
   (named under failure modes).
6. Refuse. If the best chunk score is below the named constant
   REFUSAL_THRESHOLD = 0.30, the answer is a refusal stating
   that the local documents hold no evidence for the question.
   Calibration: a first value of 0.10 failed in testing, because
   no-evidence questions sharing one common term with the corpus
   score up to 0.2321, while the weakest evidence question
   scores 0.4447. The 0.30 value sits between those bands. It
   was tuned on the same set it is reported on; that is a limit.
7. Session memory. A Session class stores each asked question,
   its refusal flag, and its cited document ids in one JSON
   file, saves after each question, and reloads the entries in
   a later run. The runner exercises this in a temporary
   directory: 3 entries recorded, 3 reloaded, reload identical,
   1 of the 3 refused, cited document ids [B01, B18].
8. Privacy. Two parts, extended from Learn. The source scan now
   covers every Python source file in this level (assistant.py
   and run_build.py) for the same 7 network patterns, and a
   separate test enforces that the pipeline module contains no
   network import at all, with the pattern names built from
   fragments so the test does not flag its own list.

### Run it

    python src/run_build.py
    python -m unittest discover -s tests -v
    python -m unittest tests.test_layout -v

The runner writes results/results_build.json
deterministically: run it twice and the file is identical
(verified 2026-11-05: sha256
11078552a37bf56878b2db4ab1cd8afb80a18414cc6c7401b02bb595366f41e0
on both runs). One committing note: the scaffold .gitignore
carried an unscoped data/ rule that would have silently
excluded the committed corpus, so the rule now has a named
exception for this level's data folder, verified with git
status before the commit.

### Results (measured 2026-11-05, Muse VM, Python 3.12)

| Test | Result |
| --- | --- |
| Build corpus | 24 synthetic documents, 144 sentences, 1,472 words, 9,290 characters |
| Chunks | 72 chunks, 30 words per chunk, 10 words overlap |
| Labelled questions | 24 questions: 20 evidence, 4 no-evidence |
| Top-1 document accuracy | 1.000 (20 of 20 evidence) |
| Chunk recall at 3 | 1.000 (20 of 20 evidence) |
| Answer sentence accuracy (first sentence) | 1.000 (20 of 20 evidence) |
| Refusal precision | 1.000 (4 refused, all truly no-evidence) |
| Refusal recall | 1.000 (4 of 4 no-evidence refused, 0 evidence refused) |
| Privacy audit | 2 source files scanned, 7 network patterns, 0 matches, passed |
| Session memory | 3 entries recorded, 3 reloaded identically, 1 refusal |
| Unit tests | 42 passed in total (21 Learn, 21 new Build), plus the scaffold smoke test |
| Determinism | results_build.json identical across two runs (hash above) |

Per question (scores rounded to 4 decimal places; full floats
are in results_build.json; Top-3 docs are the distinct documents
of the top 3 chunks):

| Q | Gold | Top 1 | Score | Top-3 chunk docs | Refused | Sentence ok |
| --- | --- | --- | --- | --- | --- | --- |
| BQ01 | B01 | B01 | 0.5542 | B01, B10 | no | yes |
| BQ02 | B02 | B02 | 0.4809 | B02, B06 | no | yes |
| BQ03 | B03 | B03 | 0.5685 | B03 | no | yes |
| BQ04 | B04 | B04 | 0.5874 | B04, B15, B23 | no | yes |
| BQ05 | B05 | B05 | 0.4974 | B05 | no | yes |
| BQ06 | B06 | B06 | 0.4447 | B03, B06, B12 | no | yes |
| BQ07 | B07 | B07 | 0.5384 | B01, B07, B21 | no | yes |
| BQ08 | B08 | B08 | 0.4825 | B08, B16, B21 | no | yes |
| BQ09 | B09 | B09 | 0.6346 | B04, B05, B09 | no | yes |
| BQ10 | B10 | B10 | 0.4846 | B06, B10 | no | yes |
| BQ11 | B11 | B11 | 0.5267 | B11, B16, B17 | no | yes |
| BQ12 | B12 | B12 | 0.5707 | B12, B24 | no | yes |
| BQ13 | B13 | B13 | 0.5008 | B13, B17 | no | yes |
| BQ14 | B14 | B14 | 0.6315 | B14 | no | yes |
| BQ15 | B15 | B15 | 0.6292 | B15, B16 | no | yes |
| BQ16 | B16 | B16 | 0.6926 | B07, B16 | no | yes |
| BQ17 | B17 | B17 | 0.6322 | B04, B17 | no | yes |
| BQ18 | B18 | B18 | 0.7188 | B14, B18 | no | yes |
| BQ19 | B19 | B19 | 0.5508 | B13, B19 | no | yes |
| BQ20 | B21 | B21 | 0.5223 | B01, B21 | no | yes |
| BQ21 | NONE | B03 | 0.2253 | B01, B03 | yes | n/a |
| BQ22 | NONE | B22 | 0.2321 | B01, B22 | yes | n/a |
| BQ23 | NONE | B01 | 0.2037 | B01 | yes | n/a |
| BQ24 | NONE | B01 | 0.0000 | B01 | yes | n/a |

Document inventory (hashes shortened to 12 characters here,
full hashes in results_build.json):

| Doc | Title | Words | Chars | sha256 (first 12) |
| --- | --- | --- | --- | --- |
| B01 | garden notes | 60 | 389 | ddb9126a1ca4 |
| B02 | home budget | 61 | 373 | d62bf16abcf9 |
| B03 | japan trip plan | 62 | 378 | 444e92198d34 |
| B04 | bicycle repair log | 65 | 382 | df7b46ed8b0b |
| B05 | sourdough journal | 66 | 375 | ef609b657876 |
| B06 | home network notes | 60 | 383 | b622a0be7438 |
| B07 | exercise routine | 58 | 379 | e65237bbb680 |
| B08 | photography notes | 59 | 383 | fb0d3d46e7ac |
| B09 | kitchen knife care | 63 | 375 | 2fd28deb5a1c |
| B10 | houseplant care | 59 | 392 | 49ed8990dd1c |
| B11 | winter car care | 62 | 388 | d5a601f7399e |
| B12 | home painting | 59 | 384 | fef0be9537f6 |
| B13 | camping gear | 62 | 401 | ca7aac58bd40 |
| B14 | tax records | 63 | 408 | 90a9cfe3de36 |
| B15 | first aid kit | 62 | 383 | 9332e807f3cf |
| B16 | aquarium care | 60 | 388 | 441ea80791a1 |
| B17 | coffee brewing | 63 | 399 | de66419f4162 |
| B18 | laptop backup | 60 | 396 | 39ca2a5fdf56 |
| B19 | laundry care | 62 | 386 | 291a424ba49b |
| B20 | dog training | 62 | 387 | 11ec9868e312 |
| B21 | piano practice | 61 | 418 | 5ebf529c1366 |
| B22 | astronomy notes | 60 | 389 | 1e84127377d3 |
| B23 | plumbing fixes | 61 | 381 | b2fc057f20c0 |
| B24 | sewing repairs | 62 | 373 | 98313167b0f1 |

Every document has 6 sentences, so sentences total 24 times 6
= 144. Hand checks: words sum to 1,472 and characters sum to
9,290 across the rows above, matching the runner. Top-1
accuracy is 20 correct of 20 evidence questions = 1.000, and
chunk recall at 3 and first sentence accuracy are the same
count. Refusal precision is 4 true refusals of 4 refusals =
1.000, and refusal recall is 4 of 4 no-evidence questions =
1.000.

### Main results claim (exact paragraph for Jev gating)

Build ran one deterministic local-first evaluation on the Muse VM on 2026-11-05: 24 synthetic documents (144 sentences, 1,472 words) were ingested from local text files, split into 72 overlapping chunks of 30 words with 10 words of overlap, and indexed with TF-IDF; on 24 labelled questions the pipeline scored top-1 document accuracy 1.000 (20 of 20 evidence questions), chunk recall at 3 1.000 (20 of 20), first answer sentence accuracy 1.000 (20 of 20), and refusal precision 1.000 and recall 1.000 (4 of 4 no-evidence questions refused, 0 evidence questions refused) at a refusal threshold of 0.30; the privacy audit scanned 2 Build source files for 7 network patterns and found 0 matches; the session memory check recorded 3 entries and reloaded all 3 correctly; and 42 unit tests passed in total, 21 of them new Build tests, plus the scaffold smoke test.

Jev gate on the paragraph above: model jev-1.13.0, 1,143 input
tokens, supported noul 0.31, route REVIEW (clear at 0.85 or
above, block at 0.10 or below). The claim therefore stands as
reviewed, not cleared, and its numbers rest on the measured
evidence in results_build.json, not on the gate.

### Build failure modes and limits

- Synthetic corpus, distinct topics: the 24 documents sit on 24
  mostly separate topics, so perfect scores are expected and are
  weak evidence. Real private files share vocabulary across
  topics, use synonyms, and ask messy questions; none of that is
  measured here.
- No real LLM and no Ollama: the assistant extracts sentences,
  it does not generate, paraphrase, summarise, or reason. A
  question whose answer needs two facts combined, or wording
  the documents do not contain, is outside what this core can
  do. The Ollama swap is future work, gated on Ollama being
  installed on a local machine.
- TF-IDF only, exact token forms: no stemming, no synonyms, no
  embeddings. The paraphrase style questions in this set still
  share content terms and even exact verb forms with the
  documents, because a true synonym paraphrase would score near
  zero under exact matching. That is the honest ceiling of this
  retrieval method, not a hidden pass.
- The refusal threshold was tuned on the same labelled set it
  is reported on. The measured bands (no-evidence up to 0.2321,
  evidence from 0.4447) are wide here, but on a real corpus the
  bands will overlap and a single threshold will trade false
  refusals against false answers. That trade is unmeasured.
- The second answer sentence is the best remaining sentence in
  the same document, and it can be weakly related: for BQ01 it
  scores 0.1416 against the first sentence score of 0.8080.
  Only the first sentence is scored for accuracy. Read the
  second sentence as context, not as a second scored answer.
- Chunk recall at 3 is a low bar on this corpus: several top-3
  lists contain zero score chunks from other documents, ordered
  only by the deterministic chunk id tie break. Top-1 accuracy
  is the honest headline metric here.
- Plain text only: ingest reads .txt files with a Title first
  line. Real private folders hold PDFs, mail, notes in other
  formats, and files without titles; none of that is handled.
- The privacy proof is a source scan plus an import guard. It
  shows this level's code holds no network pattern and no
  network import, but it does not monitor the operating system,
  does not sandbox the process, and does not prove other code
  on the machine stays offline.
- Session memory is a flat JSON list: no search, no editing,
  no expiry, and no protection if the file itself is shared.
  It proves persistence across runs, nothing more.
- This level was run on the Muse VM (CPU), not on its fleet
  node BlackBox (GPU). The work is CPU work and uses no GPU,
  but the fleet node rule still names this as a deduction.

### What Deep adds next

The local against cloud study in SPEC.md: cost, speed, quality,
and privacy with numbers, plus the Ollama backed assistant on a
machine where Ollama is installed. See the root README level map.

## Method and results: Deep (recorded 2026-11-05)

Status: DONE (2026-11-05). The local against cloud study from
SPEC.md: cost, speed, quality, and privacy, with numbers. The
local side is measured with the Build pipeline on this machine.
The cloud side is modelled from published pricing and stated
assumptions only: no API was called, no key was used, and no
cloud number in this file is a measurement. The spec, written
before the code, is DEEP-SPEC.md in this folder.

### Honest scope line

Ollama was rechecked on 2026-11-05 on the Muse VM: no ollama
binary was found and no server answered on localhost port
11434, so Ollama is still unavailable and the local core stays
extractive, exactly as at Build. There is no local language
model in this study. Cloud quality is not measured and no cloud
accuracy figure appears anywhere in this level: the quality
comparison is measured local scores on the Build eval set plus
a capability comparison. Cloud latency is not measured either:
one labelled assumed range is carried for an order of magnitude
comparison only. This level ran on the Muse VM on CPU, not on
the assigned BlackBox fleet node.

### Method

1. Local measurement. The Build pipeline (24 synthetic
   documents, 72 chunks, TF-IDF index) answers its 24 labelled
   questions. Quality is the Build evaluation rerun inside this
   study. Latency is wall clock per answer call, 5 rounds over
   24 questions, 120 timed answers, plus the index build time.
2. Cloud prompt shape. For the same question, a cloud answer
   would send an instruction line, the top 3 retrieved chunk
   texts (the same chunks the local pipeline retrieved), and
   the question. The study builds that prompt locally, counts
   its words, and sends nothing anywhere.
3. Token estimate (stated assumption). Estimated tokens equal
   ceil(words divided by 0.75). Input tokens come from the
   prompt word count. Output tokens use the local answer word
   count for the same question as the length proxy (a refusal
   counts its fixed refusal sentence, 9 words, 12 tokens).
   Means over the 24 questions: 163.33 input tokens and 29.46
   output tokens per query.
4. Cost model (computed in code, arithmetic shown). For each
   model: cost per query = (mean input tokens / 1,000,000)
   times the input rate + (mean output tokens / 1,000,000)
   times the output rate. Worked example, gpt-6-luna: 163.33
   input tokens at 0.10 USD per million = 0.0000163 USD, plus
   29.46 output tokens at 0.50 USD per million = 0.0000147 USD,
   total 0.000031 USD per query. Volumes scale linearly.
5. Pricing sources. Published pricing, Standard tier, USD per
   1 million tokens, checked 2026-11-05: OpenAI pricing at
   https://developers.openai.com/api/docs/pricing (gpt-6-luna
   0.10 in, 0.50 out; gpt-6.1-sol 2.00 in, 10.00 out),
   Anthropic pricing at
   https://platform.claude.com/docs/en/about-claude/pricing
   (claude-haiku-5.5 0.10 in, 0.50 out for prompts up to
   100,000 tokens; claude-sonnet-5.5 2.00 in, 10.00 out), and
   Google pricing at https://ai.google.dev/gemini-api/docs/pricing
   (gemini-3.5-flash-lite 0.30 in, 2.50 out; gemini-3.8-flash
   0.75 in, 3.75 out, a rate the same page says doubles on
   2027-01-01). Local marginal API cost is 0 USD by
   construction; electricity and hardware are excluded.
6. Privacy. Local: the Build audit (2 source files, 7 network
   patterns, 0 matches) plus a Deep audit over this level's 2
   source files with the same result. Cloud: the prompt and
   the retrieved private chunks leave the machine to the
   provider by construction. The Google pricing page states
   the tier split directly: free tier content is used to
   improve products, paid tier content is not.

### Run it

    python src/run_deep.py
    python -m unittest discover -s tests -v
    python -m unittest tests.test_layout -v

The runner writes results/results_deep.json. The
deterministic part (quality, token model, modelled costs,
privacy, verdict) is identical across two runs: canonicalised
sha256 541abbed0e30284b (first 16) on both runs, verified
2026-11-05, computed after removing the timing key. The timing
key (index build and answer latency, wall clock) varies
between runs and is the named exclusion from that check.

### Results, local side (measured 2026-11-05, Muse VM)

| Test | Result |
| --- | --- |
| Eval set | 24 questions: 20 evidence, 4 no-evidence |
| Top-1 document accuracy | 1.000 (20 of 20) |
| Chunk recall at 3 | 1.000 (20 of 20) |
| Answer sentence accuracy | 1.000 (20 of 20) |
| Refusal precision / recall | 1.000 / 1.000 (4 of 4 refused) |
| Answer latency, mean | 0.3326 ms over 120 timed answers |
| Answer latency, median / max | 0.3528 ms / 0.7189 ms |
| Index build time, mean | 3.6389 ms over 5 builds |
| Privacy audit, Deep sources | 2 files, 7 patterns, 0 matches, passed |
| Unit tests | 62 passed in total (42 prior, 20 new Deep), plus smoke |

Latency varies with machine load: a second full run measured
a mean of 0.6998 ms with one 7.64 ms outlier. Read local
latency as well under 1 ms on this corpus, not as a precise
constant. Per query token rows (prompt words include the
instruction and the top 3 chunk texts):

| Q | Prompt words | Input tokens est | Output words | Output tokens est | Refused |
| --- | --- | --- | --- | --- | --- |
| BQ01 | 118 | 158 | 25 | 34 | no |
| BQ02 | 122 | 163 | 24 | 32 | no |
| BQ03 | 121 | 162 | 24 | 32 | no |
| BQ04 | 130 | 174 | 26 | 35 | no |
| BQ05 | 124 | 166 | 26 | 35 | no |
| BQ06 | 131 | 175 | 26 | 35 | no |
| BQ07 | 127 | 170 | 23 | 31 | no |
| BQ08 | 110 | 147 | 23 | 31 | no |
| BQ09 | 121 | 162 | 26 | 35 | no |
| BQ10 | 128 | 171 | 23 | 31 | no |
| BQ11 | 123 | 164 | 25 | 34 | no |
| BQ12 | 121 | 162 | 24 | 32 | no |
| BQ13 | 123 | 164 | 24 | 32 | no |
| BQ14 | 122 | 163 | 24 | 32 | no |
| BQ15 | 120 | 160 | 25 | 34 | no |
| BQ16 | 117 | 156 | 24 | 32 | no |
| BQ17 | 123 | 164 | 25 | 34 | no |
| BQ18 | 112 | 150 | 24 | 32 | no |
| BQ19 | 129 | 172 | 25 | 34 | no |
| BQ20 | 118 | 158 | 24 | 32 | no |
| BQ21 | 128 | 171 | 9 | 12 | yes |
| BQ22 | 128 | 171 | 9 | 12 | yes |
| BQ23 | 119 | 159 | 9 | 12 | yes |
| BQ24 | 118 | 158 | 9 | 12 | yes |

Hand checks: the 24 input token estimates sum to 3,920, and
3,920 divided by 24 = 163.33, the reported mean. The output
estimates sum to 707, and 707 divided by 24 = 29.46.

### Results, cloud side (MODELLED from published pricing)

Modelled, not measured. Rates checked 2026-11-05, sources in
the method section. Token means: 163.33 in, 29.46 out.

| Model | In / Out per 1M | Per query | Per 1k | Per 100k | Per 1M |
| --- | --- | --- | --- | --- | --- |
| gpt-6-luna | 0.10 / 0.50 | 0.000031 | 0.03 | 3.11 | 31.06 |
| claude-haiku-5.5 | 0.10 / 0.50 | 0.000031 | 0.03 | 3.11 | 31.06 |
| gemini-3.5-flash-lite | 0.30 / 2.50 | 0.000123 | 0.12 | 12.26 | 122.65 |
| gemini-3.8-flash | 0.75 / 3.75 | 0.000233 | 0.23 | 23.30 | 232.97 |
| gpt-6.1-sol | 2.00 / 10.00 | 0.000621 | 0.62 | 62.13 | 621.25 |
| claude-sonnet-5.5 | 2.00 / 10.00 | 0.000621 | 0.62 | 62.13 | 621.25 |

All figures USD, rounded to the places shown; full floats are
in results_deep.json. Chart, modelled cost per 100,000 queries
(bar length proportional to cost, flagship = 40 characters):

    budget (luna, haiku)      3.11 | ##
    gemini-3.5-flash-lite    12.26 | ########
    gemini-3.8-flash         23.30 | ###############
    flagship (sol, sonnet)   62.13 | ########################################
    local (measured setup)    0.00 | (no API fee)

Speed chart (local measured, cloud ASSUMED and unverified):

    local mean (measured)     0.33 ms | (invisible at this scale)
    cloud range (assumed)  1000 to 3000 ms | ####################

The honest reading of the speed chart: on a 24 document corpus
the local answer is about three to four orders of magnitude
faster than the assumed cloud range, and that gap is a property
of this tiny corpus and a same machine call against a network
call, not a general law. The cost reading: at lookup shape the
cloud fee is small in absolute terms (3.11 USD per 100,000
queries at budget rates) and exactly zero locally; cost alone
rarely decides this comparison. Privacy and capability decide
it, in opposite directions.

### Quality comparison (measured local, capability cloud)

| Capability | Local (measured or observed) | Cloud generative (capability, not measured) |
| --- | --- | --- |
| Lookup inside the documents | 1.000 top-1 and sentence accuracy on the eval set | Expected strong, not measured here |
| Refusal with no evidence | 1.000 precision and recall at threshold 0.30 | No built in refusal rule; can answer anyway |
| Paraphrase and synonyms | Fails: exact token matching only | Handles rewording as a core capability |
| Combining facts across documents | Cannot: one document per answer | Can synthesise across the full prompt |
| General knowledge | None: documents only | Broad, with fluent error risk |
| Answer form | Verbatim cited sentences only | Fluent written answers, citations on request |
| Hallucination surface | None by construction (copied text or refusal) | Present: fluent text can outrun the evidence |

### Verdict

Axis winners: cost, local (zero marginal API fee against a
modelled fee on every cloud query). Speed, local on this
corpus (measured under 1 ms against an assumed 1,000 to 3,000
ms range, order of magnitude only). Quality on the eval set,
local (measured perfect scores; cloud quality not measured).
Quality capability, cloud (generation, paraphrase, synthesis,
general knowledge; the local core does none of these). Privacy,
local (no transfer by construction against a prompt transfer
by construction).

Decision rule, in order:
1. If the data must not leave the device, or the work must run
   offline, use local. The cloud prompt carries the question
   and the retrieved private chunks to the provider.
2. If the question needs paraphrase, synonyms, facts combined
   across documents, or general knowledge, use cloud. The
   local core refuses or misses on all of these.
3. If the question is a lookup whose answer is a sentence in
   the local documents, use local at any volume: measured
   quality is perfect on the eval set and the fee is zero.
4. If the corpus is large, messy, or beyond plain text, use
   cloud, and pay the modelled price with the transfer named.
5. If a fluent written answer matters more than a verbatim
   cited sentence, use cloud, and keep a human or a checker
   on the evidence, because fluency is not evidence.

### Main results claim (exact paragraph for Jev gating)

Deep ran one local against cloud study on the Muse VM on 2026-11-05: the local side was measured with the Build pipeline on its 24 labelled questions and scored top-1 document accuracy 1.000 (20 of 20 evidence questions), first answer sentence accuracy 1.000 (20 of 20), and refusal precision 1.000 and recall 1.000 (4 of 4 no-evidence questions refused), with a mean answer latency of 0.3326 ms over 120 timed answers and a privacy audit over 2 Deep source files finding 0 matches for 7 network patterns; the cloud side was modelled, not measured, from published pricing checked on 2026-11-05 and a stated token estimate (mean 163.33 input tokens and 29.46 output tokens per query), giving a modelled cost per query of 0.000031 USD on gpt-6-luna and claude-haiku-5.5, 0.000123 USD on gemini-3.5-flash-lite, 0.000233 USD on gemini-3.8-flash, and 0.000621 USD on gpt-6.1-sol and claude-sonnet-5.5, or 3.11, 12.26, 23.30, and 62.13 USD per 100,000 queries at the budget, flash-lite, flash, and flagship rates; no cloud API was called, cloud quality and cloud latency were not measured, and Ollama was rechecked unavailable on the Muse VM on 2026-11-05 so the local core stayed extractive; and 62 unit tests passed in total, 20 of them new Deep tests, plus the scaffold smoke test.

Jev gate on the paragraph above: model jev-1.13.0, 1,812 input
tokens, supported noul 0.72, route REVIEW (clear at 0.85 or
above, block at 0.10 or below). The claim therefore stands as
reviewed, not cleared, and its numbers rest on the measured
and modelled evidence in results_deep.json, not on the gate.

### Deep failure modes and limits

- The cloud side is a model, not a measurement. No cloud query
  was run, so no cloud latency, quality, or billed cost was
  observed. A provider can bill differently (caching, minimums,
  tokenizer differences) and can change any rate after the
  2026-11-05 check date; the gemini-3.8-flash rate is already
  announced to double on 2027-01-01.
- Cloud quality is unmeasured by design (FREE-ONLY). The
  capability table compares what each class of system can do,
  from the measured local behaviour and the documented model
  class. It is not a head to head accuracy result, and any
  reader who needs one must run a paid or free tier eval,
  which this level does not do.
- The token estimator is a word rule, not a tokenizer. Real
  provider tokenizers split text differently (Anthropic notes
  its newer tokenizer yields about 30 percent more tokens for
  the same text), so real input counts, and therefore real
  costs, can run above the modelled figures.
- The output token proxy assumes a cloud answer as short as
  the local extractive answer. Generative answers usually run
  longer, and output tokens are the expensive side (up to 5
  times the input rate here), so the modelled costs are a
  floor for this prompt shape, not a typical bill.
- Local latency is measured on a tiny corpus on a shared VM.
  It grows with corpus size, it says nothing about a local
  generative model (none ran), and the cross run spread (mean
  0.33 ms against 0.70 ms, one 7.64 ms outlier) shows the
  noise floor. The cloud latency range is an assumption.
- Local quality inherits the Build limits in full: synthetic
  documents on distinct topics, perfect scores that are weak
  evidence, exact token matching, a refusal threshold tuned on
  the set it is reported on, and plain text ingest only.
- The privacy comparison is asymmetric by necessity: the local
  side has a source audit, the cloud side has a construction
  argument and one pricing page data use note. Retention,
  subprocessors, and regional processing on the cloud side are
  policy questions this study does not audit.
- Local cost excludes electricity and hardware. At very high
  volume on owned hardware that exclusion is small; for a
  reader pricing a new machine against API fees it is the
  whole question, and it is v1.1 scope in ROADMAP.md.

### What v1.1 adds next

The rest of the v2 Deep scope sits in the repo root ROADMAP.md
as the named v1.1 backlog: the Ollama backed generative local
run on a machine where Ollama is installed, a real private
corpus eval, provider tokenizer counts, a free tier cloud
measurement where terms allow it, and a total cost of ownership
comparison that includes hardware and electricity.

## Review findings (2026-11-07)

Reviewed 2026-11-07 against a doctoral-level research rubric. This review assessed the study as research (its scores are kept internally), lists what was fixed in this change, and names the exact compute or data each remaining gap needs. Every number below comes from a committed results file: `results/results_learn.json`, `results/results_build.json`, `results/results_deep.json`, or the new `results/results_rigor.json` (written by `level-3-deep/run_rigor.py`, rerun in CI).

The engineering is strong: standard library only, deterministic hashed results, a CI matrix, and honest limits written in every level README. The research is held back by one thing above all: the central question (a local language model against a cloud one) is not answered, because no local generative model ran and the cloud side is modelled from pricing, not measured. This change does not and cannot fix that without a GPU and paid API calls. What it does fix is the measurable rigor of the local side: uncertainty, a held-out threshold, baselines, a sensitivity sweep, a harder question set, a scaling curve and a runtime egress test.

### Criteria

| Criterion | What was missing | Fixed in this change |
| --- | --- | --- |
| Research question | The stated question (local LLM against cloud) is broader than what was run (extractive TF-IDF against modelled cloud cost). | Not fixable cheaply; scope stated plainly on the dashboard banner and here. |
| Hypotheses | No written hypotheses or falsification rules. | Hypotheses stated below, each with its test and result. They are written after the original runs, so they are post hoc for the labelled set; the hard set was written before its first run. |
| Method | Clear, deterministic, but parameters (chunk size, overlap, threshold) never varied. | Chunk size and overlap sweep (24 settings), threshold curve (17 thresholds). |
| Baselines and ablations | No baseline at all. | BM25 over the same chunks, and TF-IDF over whole documents (no chunking) as an ablation. |
| Statistics and uncertainty | Point estimates only on n = 20 and n = 4. | Wilson 95% intervals for every count metric, recorded and shown on the dashboard. |
| Threshold validity | REFUSAL_THRESHOLD 0.30 tuned on the set it is reported on. | Leave-one-out threshold: each question scored with a threshold fitted on the other 23. |
| Construct validity | 24 synthetic documents on 24 topics, questions reuse document wording, perfect scores are a ceiling. | A 16-question hard set: 10 synonym paraphrases and 6 cross-topic distractors. The drop is reported. |
| Reproducibility | Already strong. | The rigor run joins CI; the dashboard build fails if the browser port drifts from the recorded results. |
| Threats to validity | Listed honestly in each README. | The hard set and threshold curve turn two listed threats into measured ones. |
| Related work | NOVELTY.md is an unfilled draft with "NO MEASUREMENT YET". | A short related-work section below. A measured comparison against real local tools still needs compute (see remaining gaps). |
| Limitations | Already candid. | Carried onto every dashboard panel next to the numbers it qualifies. |

### Hypotheses and results

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

### What changed in this branch

- `level-3-deep/rigor.py` and `level-3-deep/run_rigor.py`: Wilson intervals, leave-one-out threshold, threshold curve, BM25 baseline, whole-document ablation, chunk sweep, hard question set, scaling curve. Standard library only, under one second. Deterministic except the labelled scaling block.
- `tests/test_deep_rigor.py`: tests for each helper, including hand-computed Wilson bounds and a network-pattern audit of the new sources.
- `tests/test_deep_egress.py`: a runtime egress test. Every socket constructor and name lookup is replaced with a function that raises, then ingest, indexing, answering, refusal, evaluation and session memory run end to end. Before this, the privacy claim rested on a static source scan.
- `site/`: the live dashboard. Its `engine.check.mjs` runs inside `npm run build` and asserts that the in-browser port reproduces every recorded top-1 document, score (to 1e-9; the observed difference is 0), refusal, answer sentence and answer text in `results_build.json`, the Learn results in `results_learn.json`, all 24 sweep rows, the threshold curve, the leave-one-out result, all 16 hard-set rows, the Wilson intervals, and all six modelled cost rows in `results_deep.json`.

### Related work (positioning, not measured)

- Sparse retrieval: TF-IDF weighting (Salton and Buckley, 1988, "Term-weighting approaches in automatic text retrieval") and BM25 (Robertson and Zaragoza, 2009, "The Probabilistic Relevance Framework: BM25 and Beyond"). This study uses the first and now reports the second as a baseline.
- Retrieval-augmented generation: Lewis et al., 2020, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks". This study implements only the retrieval half and returns extracted sentences instead of generated text.
- Local model runtimes and local document question-answering tools such as llama.cpp, Ollama, GPT4All and PrivateGPT pair a local generative model with retrieval over personal files. This study ran none of them (Ollama was unavailable on the study VM, see `results/results_deep.json`), so it makes no measured claim against them.
- Interval estimation for small samples: Wilson, 1927, "Probable inference, the law of succession, and statistical inference", the interval used here.

The honest novelty, at present, is not the retrieval method. It is a fully reproducible, standard-library, offline baseline with a privacy audit and a live browser replica that is checked against its own recorded results.

### Remaining gaps and what each one needs

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

## Future work: the v1.1 backlog (written 2026-11-05)

Written 2026-11-05 at Deep ship time, per the December
Compression Protocol: compressed Deep (v1.0) is the single
hardest capability in SPEC.md, the local against cloud study.
Everything else in the v2 Deep scope is named here as the
v1.1 backlog. Nothing in this file is built or measured yet.

### v1.1 items

1. Ollama backed generative local run. Install Ollama on a
   local machine (the BlackBox fleet node or Jesun's own
   machine), swap the answer step from extraction to a local
   model over the same retrieved chunks, and rerun the study:
   generative local latency, quality, and cost against the
   extractive baseline in level-3-deep.
2. Real private corpus eval. A consented set of real private
   files (mixed formats, shared vocabulary, messy questions)
   replacing the synthetic corpus, with the refusal threshold
   calibrated on a held out split, not on the reported set.
3. Provider tokenizer counts. Replace the word based token
   estimator with each provider's published tokenizer or
   counting endpoint documentation, and restate the modelled
   costs with the spread named per provider.
4. Free tier cloud measurement, where terms allow. If a
   provider free tier permits eval use without a payment
   method, measure cloud latency and answer quality on the
   same 24 questions and replace the assumed latency range
   and the capability table with measured rows, labelled by
   tier. Any step that asks for a card or a paid key stops
   and goes to Jesun (FREE-ONLY, no new credentials).
5. Total cost of ownership. Add hardware and electricity to
   the local side (a named machine, a named power draw, a
   named local electricity rate with its source and date)
   and find the volume where local ownership and cloud fees
   cross, per model tier.
6. Larger corpus scaling run. Grow the local corpus by 10x
   and 100x with generated documents, and measure how local
   latency, index build time, and accuracy move, so the speed
   verdict carries a scaling curve instead of one point.
7. Runtime privacy monitoring. Extend the source scan with
   an operating system level check during a live run (open
   sockets observed while the pipeline answers), closing the
   gap the Learn, Build, and Deep READMEs all name.
8. Fan-out completion. The written fan-out set for the Deep
   level (blog, tutorial, website page copy, LinkedIn draft,
   release notes) graded on the publicity rubric, with every
   channel outcome logged in PUBLICITY.md.

### Held items (not v1.1 work)

- P19 style multi-GPU scope does not apply to this project.
- Any paid API run stays out of scope under FREE-ONLY unless
  Jesun rules otherwise on a named proposal.

## Pre-standard README (as of 2026-11-07)

The repo README before the 2026-11-08 migration, kept here with its
grade rows removed. Its "Start here" files now live in PROPOSAL.md
(SPEC, DOSSIER, NOVELTY) and in this report (the level READMEs); the
fan-out set is in docs/fanout/.

A private local assistant on Ollama, fully offline local RAG, a local against cloud study.

Live dashboard: https://jesunahmadushno.github.io/local-first-ai/ (the Build pipeline ported to run in your browser, checked at build time against results_build.json, plus the evaluation, refusal threshold, chunking, modelled cost, speed and privacy results). Source in site/; research review in docs/research-review.md.

Status: Deep DONE, v1.0 SHIPPED (2026-11-05, ROADMAP-V3-BATCH). All three levels are built, tested, and measured below. The v1.1 backlog is ROADMAP.md at the repo root.
Project: P15. Fleet node: BlackBox (GPU). Wave: Wave 7. All levels were run on the Muse VM (CPU); see the level READMEs for the named deduction. There is no Ollama and no language model in any level: Ollama was rechecked unavailable on the Muse VM on 2026-11-05, so the assistant is an extractive core, named plainly in level-2-build/BUILD-SPEC.md, and Deep compares that measured local core against cloud costs modelled from published pricing only.

### Start here

1. Read SPEC.md for scope and acceptance criteria.
2. Read DOSSIER.md for the past, present, and future of this problem (v1).
3. Read NOVELTY.md for the proposed novelty (DRAFT, pending the Jev claim_check gate).
4. Start at level-1-learn/README.md, then level-2-build, then level-3-deep.

### Level map

- Level 1, Learn: the core idea, built small and clean, with a teaching path.
- Level 2, Build: a real working system other people can run.
- Level 3, Deep: benchmarks, optimization, evaluation, hard cases.

### Benchmarks

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
| Verdict | Local wins cost, speed on this corpus, eval set quality, and privacy; cloud wins capability (generation, paraphrase, synthesis). Full decision rule in level-3-deep/README.md |

### Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

### License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.

### Fan-out

Written fan-out set for v1.0 in fanout/: blog-post.md,
tutorial.md (every command verified by running it),
website-page.md, linkedin-post.md (DRAFT NOT POSTED, link as
the first-comment line), paper-candidate.md (submission is
Jesun's tap), and release-notes.md covering v0.1, v0.5, and
v1.0. The full channel log is in PUBLICITY.md.
Social posting is held under the standing platform rules:
Threads awaits Jesun's tap, and the video is held for the
January engine queue.

## Threats to validity

- Construct: 24 synthetic documents on distinct topics; questions
  reuse document wording. Perfect labelled-set scores are a ceiling,
  and the hard set shows the drop.
- Small n: 20 evidence and 4 no-evidence questions; the refusal
  interval runs from 0.510 to 1.000.
- Post hoc: the hypotheses were written after the runs; the 0.30
  threshold was tuned on the reported set (leave-one-out is the
  check).
- External: no real private files, one VM, no local generative
  model, cloud side modelled.

## Conclusion

A fully offline, standard-library retrieval core with cited answers
and a refusal rule works end to end and is reproducible, and the
browser replica on the dashboard is checked against its recorded
results. On easy synthetic questions it is perfect within wide
intervals; on paraphrases it mostly fails. The question that gives
the project its value, a local language model against hosted ones on
measured quality, speed and cost, is still open; PROPOSAL.md Part 1
is the plan for it.
