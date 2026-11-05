# Level 1, Learn: local-first-ai

Status: DONE (2026-11-05). A local-first assistant core: a small
set of synthetic documents stored locally, TF-IDF retrieval, an
extractive answer with a citation, and a privacy audit, built
with the Python standard library only.

## Honest scope line

The documents are synthetic. No real private file is read, indexed,
or shown anywhere in this level. There is no Ollama, no real LLM,
no embedding model, and no network call: the answer is one sentence
copied word for word from the retrieved document, with its
citation. A real local model on Ollama over real private files is
Build level scope. The local against cloud study is Deep scope.

## Method

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

## Run it

    python level-1-learn/run_learn.py
    python -m unittest tests.test_learn_local_first -v
    python tests/test_smoke.py

The runner writes level-1-learn/results_learn.json deterministically:
run it twice and the file is identical (verified 2026-11-05:
sha256 87978c5c087e0d4c08ae7284d653a02c0035b2715e2d5a9a243dfcd546d4c4a9
on both runs).

## Results (measured 2026-11-05, Muse VM, Python 3.12)

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

## Failure modes and limits

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

## Grade

Grade: 8,700 of 10,000 for this Learn level.

Deductions (they sum to 1,300):
- Small synthetic corpus, 8 documents and 10 labelled questions
  with distinct topic vocabulary, so the perfect scores are weak
  evidence: minus 500.
- TF-IDF retrieval and single-sentence extraction only, with no
  embeddings, no real LLM, and no Ollama in this level: minus 400.
- Run on the Muse VM, not the assigned BlackBox fleet node:
  minus 200.
- Privacy audit is a source pattern scan only, with no operating
  system level network monitoring and no sandbox proof: minus 100.
- Answers are one extracted sentence, with no multi-sentence or
  cross-document synthesis and no real private files evaluated:
  minus 100.

## What Build adds next

A real assistant on Ollama over real local private files, fully
offline, with file format handling, chunking, and the same audit
extended to runtime network monitoring. See the root README
level map.
