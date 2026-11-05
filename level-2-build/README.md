# Level 2, Build: local-first-ai

Status: DONE (2026-11-05). A full local assistant pipeline, end
to end, on local files: ingest a directory of documents, chunk
them, index the chunks with TF-IDF, answer with multi-sentence
extractive answers cited per sentence, refuse below a named
threshold, and keep a persistent session memory. Standard
library only. The build spec, written before the code, is
BUILD-SPEC.md in this folder.

## Honest scope line

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

## Method

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

## Run it

    python level-2-build/run_build.py
    python -m unittest discover -s tests -v
    python tests/test_smoke.py

The runner writes level-2-build/results_build.json
deterministically: run it twice and the file is identical
(verified 2026-11-05: sha256
11078552a37bf56878b2db4ab1cd8afb80a18414cc6c7401b02bb595366f41e0
on both runs). One committing note: the scaffold .gitignore
carried an unscoped data/ rule that would have silently
excluded the committed corpus, so the rule now has a named
exception for this level's data folder, verified with git
status before the commit.

## Results (measured 2026-11-05, Muse VM, Python 3.12)

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

## Main results claim (exact paragraph for Jev gating)

Build ran one deterministic local-first evaluation on the Muse VM on 2026-11-05: 24 synthetic documents (144 sentences, 1,472 words) were ingested from local text files, split into 72 overlapping chunks of 30 words with 10 words of overlap, and indexed with TF-IDF; on 24 labelled questions the pipeline scored top-1 document accuracy 1.000 (20 of 20 evidence questions), chunk recall at 3 1.000 (20 of 20), first answer sentence accuracy 1.000 (20 of 20), and refusal precision 1.000 and recall 1.000 (4 of 4 no-evidence questions refused, 0 evidence questions refused) at a refusal threshold of 0.30; the privacy audit scanned 2 Build source files for 7 network patterns and found 0 matches; the session memory check recorded 3 entries and reloaded all 3 correctly; and 42 unit tests passed in total, 21 of them new Build tests, plus the scaffold smoke test.

Jev gate on the paragraph above: model jev-1.13.0, 1,143 input
tokens, supported noul 0.31, route REVIEW (clear at 0.85 or
above, block at 0.10 or below). The claim therefore stands as
reviewed, not cleared, and its numbers rest on the measured
evidence in results_build.json, not on the gate.

## Failure modes and limits

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

## Grade

Grade: 7,100 of 10,000 for this Build level.

Deductions (they sum to 2,900):
- No real LLM and no Ollama: the SPEC assistant is an extractive
  core, so generation, paraphrase, and synthesis are absent:
  minus 800.
- Synthetic corpus of 24 documents on 24 distinct topics, so
  the perfect measured scores are weak evidence: minus 700.
- TF-IDF retrieval only, exact token matching, with no
  embeddings, no stemming, and no synonym handling: minus 400.
- Plain text ingest only, with no real private files and no
  other file formats evaluated: minus 200.
- Run on the Muse VM, not the assigned BlackBox fleet node:
  minus 200.
- Refusal threshold tuned on the same labelled set it is
  reported on, so its generalisation is unproven: minus 200.
- Multi-sentence answers pair one scored sentence with a second
  sentence that can be weakly related and is not scored:
  minus 200.
- Privacy proof is a source scan and an import guard only, with
  no operating system level monitoring and no sandbox: minus 100.
- Session memory is a flat JSON list with no search, editing,
  or expiry: minus 100.

## What Deep adds next

The local against cloud study in SPEC.md: cost, speed, quality,
and privacy with numbers, plus the Ollama backed assistant on a
machine where Ollama is installed. See the root README level map.
