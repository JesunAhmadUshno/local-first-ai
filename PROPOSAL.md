# Proposal: local-first-ai (P15)

Status: NOT LOCKED. This repo is not pre-registered. Part 1 is a draft
confirmatory plan that would lift the verdict cap once the Owner
approves its compute and data and it is tagged proposal-v1 before any
run. Part 2 keeps the original plans exactly as they were written
(2026-11-04 and 2026-11-05), moved here from SPEC.md, NOVELTY.md,
DOSSIER.md, level-2-build/BUILD-SPEC.md and level-3-deep/DEEP-SPEC.md
on 2026-11-08. Only grade wording was removed from them.

## Why this repo is not pre-registered

The first commit (cb895e5, 2026-11-04) is a scaffold: SPEC.md names
the subject and acceptance criteria per level, but no hypothesis,
pass line or analysis plan. BUILD-SPEC.md says it was written before
the Build code, but it was committed in the same commit as the code
and results (04c7b51). DEEP-SPEC.md arrived in the same commit as the
Deep results (8dc2037). The hypotheses H1 to H5 in REPORT.md were
written on 2026-11-07, after the main runs; only the 16-question hard
set was written before its first run, and that is not provable from
git (it arrived with its results in 5c23976). No tag can honestly
lock a plan here, so none is added, and the verdict is capped at
Functional (portfolio METHOD section 7).

## Part 1. Confirmatory re-run (draft, not locked)

Question. On the same retrieved chunks, does a local generative model
answer private-document questions as well as hosted models, at what
measured cost and latency, and does the refusal rule hold on questions
written by someone who has not read the corpus?

Hypotheses and proposed pass lines (the Owner confirms or changes
them before the lock; nothing below has been run):

- C1, refusal generalises: with the threshold fitted on a calibration
  split only, refusal recall on a held-out set of at least 25
  no-evidence questions has a Wilson 95% lower bound of at least 0.80,
  with at most 10% false refusals on at least 75 held-out evidence
  questions.
- C2, local generation keeps the evidence: a local 7B to 8B
  instruction model (Ollama or llama.cpp) answering from the same top
  3 chunks is judged supported by its cited chunk on at least 90% of
  evidence questions, under a blind grading protocol fixed before the
  run.
- C3, local against cloud quality: on the same questions and chunks,
  the local model's supported-answer rate is within 10 percentage
  points of the best of the six recorded hosted models.
- C4, cost and latency measured, not modelled: billed cloud cost per
  query is within a factor of 2 of the modelled cost in
  results/results_deep.json, and local generative median latency on
  the named fleet node is reported with every run.

Design: the questions are written first and committed (experiments/,
dated), then this plan is tagged proposal-v1, then the runs happen;
every trial is reported, misses included; compute, model versions and
machine are recorded with each result.

What the re-run needs from the Owner (from the 2026-11-07 review):
about one GPU hour on the BlackBox node for C2; API keys and about
240 paid calls (about 0.07 USD at the recorded modelled rates) for C3
and C4; a public, openly licensed personal-style corpus with at
least 100 human-written questions and two annotators for C1.

## Part 2. Original plans, kept as written

### SPEC: local-first-ai (P15)

Phase skill: spec-driven-development (house engineering pipeline).
Status: Wave 0 scaffold spec, from Roadmap v2 text and the v3 decision pack. Scope and acceptance criteria below are the v2 section text, kept as the source of truth until the project's wave opens its own spec pass.

Fleet node: BlackBox (GPU). Wave: Wave 7.
Hiring evidence: 2 of 5 (few postings, v2 rank 16) [confirmed, fleet and scoring pass 2026-11-04, or the decision pack for P23 to P29].

#### Project section text (Roadmap v2, or the v3 candidate text for P23 to P29)

local-first-ai: KEEP

Subject: private, local AI. v1 levels carry over: a full assistant on a local machine with Ollama, no data leaves the machine; local RAG over private files, fully offline; Deep is a local against cloud study (cost, speed, quality, privacy, with numbers). Posting fit is thin and this file keeps the career documentation's honest read: the value is positioning, his differentiator, not posting counts [confirmed, career documentation Section D rank 16]. Trend support for on-prem and regulated use sits in Section 7.
Fan-out: Book chapter "AI That Stays Home". Paper angle: the local against cloud study itself. Course module: P15-local-first-ai.

#### Acceptance criteria (scaffold level)

- Learn closes when the level-1-learn code runs, its README teaches the idea, and a fresh-eyes reader can follow it.
- Build closes when the system runs end to end, tests pass, and one benchmark or result table with method is in the README.
- Deep closes when the Deep scope in the section text is done, the failure modes are written, and the dossier is updated to ship state.
- No level closes on a claim. Evidence only: code, tests, numbers, links.

### BUILD-SPEC: local-first-ai, Level 2 Build

Written before any Build code, per the task order. Date: 2026-11-05.

#### What SPEC.md asks for

A full assistant on a local machine with Ollama, no data leaves
the machine; local RAG over private files, fully offline. Build
closes when the system runs end to end, tests pass, and one
benchmark or result table with method is in the README.

#### Environment facts, checked 2026-11-05

- Ollama: NOT available on the Muse VM. Check: `which ollama`
  returned nothing, and a probe of localhost port 11434 returned
  no server response. This is stated plainly, not worked around
  in wording.
- BlackBox (the assigned fleet GPU node): unreachable in this
  cycle, recorded as NEEDS-BLACKBOX-ON by the coordinator. Build
  therefore runs on the Muse VM on CPU. That is a named grade
  deduction, as it was at Learn.
- Python 3.12, standard library only. numpy is present on the VM
  but prior levels are standard library only, so Build stays
  standard library only and runs anywhere Python 3 runs.

#### Substitutions, named plainly

1. Extractive assistant core, not an LLM. Because Ollama is not
   available, there is no local language model in this level.
   Answers are sentences copied word for word from the retrieved
   documents, with a citation per sentence. Nothing is generated,
   paraphrased, or summarised by a model. Swapping in Ollama
   later means replacing only the answer selection step; ingest,
   chunking, indexing, refusal, session memory, and the privacy
   guard do not change.
2. Synthetic corpus, not real private files. The corpus is 24
   synthetic documents committed as data files, standing in for a
   private folder. No real private file is read. The ingest path
   is the real path a private folder would take: a directory of
   text files on local disk.
3. TF-IDF chunk index, reused from Learn. Retrieval reuses the
   Learn level functions (tokenize, TF-IDF, cosine) by import,
   applied to chunks instead of whole documents. No embeddings.

#### The system, end to end

1. Ingest: read every .txt file in level-2-build/data/ in sorted
   file name order. First line is `Title: <title>`. The rest is
   split into sentences. Document ids come from file names
   (B01 to B24). Each document is inventoried with sentence,
   word, and character counts and a sha256 hash of its text.
2. Chunk: each document is split into overlapping word chunks.
   Chunk size: 30 words. Overlap: 10 words. Step: 20 words.
   A chunk keeps its document id, chunk index, and word offsets.
3. Index: TF-IDF over chunks, using the Learn smoothed idf,
   idf = log((1 + N) / (1 + df)) + 1, with N = chunk count.
4. Retrieve: a question is vectorised with the same idf, chunks
   are ranked by cosine, ties break on chunk id. The top chunk
   decides the top document.
5. Answer: inside the top document, sentences are scored by the
   same cosine measure and the best two distinct sentences are
   returned, each unchanged, each with its own citation in the
   form [B07 S1]. Multi-sentence, extractive, cited per sentence.
6. Refuse: if the best chunk score is below the named refusal
   threshold of 0.30, the assistant refuses and states that it
   has no evidence in the local documents, instead of returning
   an unrelated sentence. The threshold is a named constant,
   REFUSAL_THRESHOLD = 0.30, and the refusal rule is tested.
   Calibration note, recorded during the build: a first value of
   0.10 failed, because no-evidence questions that share one
   common term with the corpus (for example travel, best) score
   up to 0.2321 on a single chunk, while the weakest evidence
   question scores 0.4447. The 0.30 value sits between those two
   measured bands. It was tuned on the same labelled set it is
   reported on, which the level README names as a limit.
7. Session memory: a JSON file stores every asked question, its
   refusal flag, and its cited document ids. It is loaded on
   start, appended on each question, saved after each question,
   and reloaded correctly in a later run.

#### Privacy proof, extended from Learn

- Source scan: every Python source file in level-2-build/ is
  scanned for the same 7 network patterns as Learn. Zero matches
  are expected and reported in results_build.json.
- Runtime guard: the pipeline module (assistant.py) must contain
  no network import of any kind. A test parses its source text
  using pattern names built from fragments, as in Learn, so the
  test does not flag its own pattern list, and asserts the count
  is zero.
- No network call is made anywhere in the pipeline. All inputs
  are local files, all outputs are local files.

#### Benchmark

- Question set: 24 labelled questions in assistant.py, larger
  than the Learn set of 10. 20 carry a gold document and a gold
  first answer sentence. 4 are no-evidence questions with gold
  document NONE, written to have no answer in the corpus.
- Paraphrase style: evidence questions are written as natural
  questions, not keyword lists as in Learn. They still share
  content terms with the corpus, because TF-IDF matches exact
  token forms only; that limit is named in the level README.
- Metrics: top-1 document accuracy (over the 20 evidence
  questions), chunk recall at 3 (gold document among the
  documents of the top 3 chunks), answer sentence accuracy
  (first returned sentence is the gold sentence), and for the
  refusal rule, no-evidence precision and recall over all 24
  questions (a refusal is the positive class).
- Determinism: run_build.py writes results_build.json with no
  timestamps or randomness. Two runs must produce an identical
  file, verified by hash.

#### Acceptance

- Full test suite passes (Learn tests, smoke test, new Build
  tests in tests/test_build_*.py).
- results_build.json is deterministic across two runs.
- Root README carries Status Build DONE and the measured table.
- This level README carries method, results, failure modes, one
  exact main results claim paragraph for Jev gating.

### DEEP-SPEC: local-first-ai, Level 3 Deep (compressed)

Written before any Deep code, per the task order. Date: 2026-11-05.
December Compression Protocol: compressed Deep is the single
hardest capability in SPEC.md, built, tested, benchmarked, with
failure modes written. The rest of the v2 Deep scope goes into
the repo root ROADMAP.md as the named v1.1 backlog.

#### What SPEC.md asks for

Deep is a local against cloud study: cost, speed, quality, and
privacy, with numbers. Deep closes when that scope is done, the
failure modes are written, and the dossier is updated to ship
state.

#### Hard rule for this level (FREE-ONLY)

The cloud side comes from published pricing and stated
assumptions only. No paid API run is made, no API key is used,
and no cloud model is called. Every cloud cost number is
modelled from published pricing, never measured, and is labelled
that way wherever it appears. Cloud quality and cloud latency
are not measured either: quality is compared as capability (what
each side can and cannot do, from the measured local behaviour
and the documented model class), and cloud latency is a stated
assumed planning range, labelled unverified. The local side is
measured on this machine with the Build pipeline.

#### Environment facts, checked 2026-11-05

- Ollama: rechecked this cycle on the Muse VM. No ollama binary
  was found on PATH and no server answered on localhost port
  11434 (connection refused). Ollama is still unavailable, stated
  plainly. The local core therefore stays extractive, exactly as
  at Build: TF-IDF retrieval over chunks, cited extracted
  sentences, threshold refusal. No language model runs locally
  in this study.
- Machine: the Muse VM, Python 3.12, CPU only. The assigned
  fleet node is BlackBox (GPU); this study is CPU work and ran
  on the Muse VM, which prior levels name as a grade deduction.
- Standard library only, as at Learn and Build.

#### Pricing sources (published pricing, checked 2026-11-05)

All rates are Standard tier, USD per 1 million tokens, input and
output priced separately, read from the provider pricing pages
on 2026-11-05:

| Model | Input | Output | Source |
| --- | --- | --- | --- |
| gpt-6-luna (OpenAI) | 0.10 | 0.50 | https://developers.openai.com/api/docs/pricing |
| claude-haiku-5.5 (Anthropic, prompts up to 100,000 tokens) | 0.10 | 0.50 | https://platform.claude.com/docs/en/about-claude/pricing |
| gemini-3.5-flash-lite (Google) | 0.30 | 2.50 | https://ai.google.dev/gemini-api/docs/pricing |
| gemini-3.8-flash (Google, rate through 2026-12-31) | 0.75 | 3.75 | https://ai.google.dev/gemini-api/docs/pricing |
| gpt-6.1-sol (OpenAI) | 2.00 | 10.00 | https://developers.openai.com/api/docs/pricing |
| claude-sonnet-5.5 (Anthropic) | 2.00 | 10.00 | https://platform.claude.com/docs/en/about-claude/pricing |

Dated caveat, from the Google page itself: the gemini-3.8-flash
rate doubles to 1.50 input and 7.50 output on 2027-01-01. Every
modelled number in this level is a snapshot at the rates above
and decays when a provider changes a rate.

#### The study design

1. Local measurement. The Build pipeline (level-2-build) is run
   over its own 24 labelled questions. Per query, the study
   records the answer latency (wall clock, repeated rounds), and
   reuses the Build evaluation for quality: top-1 document
   accuracy, chunk recall at 3, first answer sentence accuracy,
   refusal precision and recall. Index build time is measured
   once per round. Latency values are timing fields: they vary
   between runs and are the named exclusion from the determinism
   check. Everything else in results_deep.json is deterministic.
2. Cloud prompt shape. A cloud retrieval answer for the same
   question would send one instruction line, the top 3 retrieved
   chunk texts (the same chunks the local pipeline retrieved),
   and the question, and would return a short answer. The study
   builds that exact prompt text locally for each of the 24
   questions and counts its words. No prompt is sent anywhere.
3. Token estimate (stated assumption). Tokens are estimated from
   words with the rule 1 token is about 0.75 words, so estimated
   tokens = ceil(words times 4 divided by 3). Input tokens come
   from the prompt word count. Output tokens come from the local
   answer word count for the same question (a refusal counts its
   fixed refusal sentence), used as the length proxy for a cloud
   answer of the same shape. This estimator is not a provider
   tokenizer; that gap is a named deduction.
4. Cost model (pre-computed in code). For each cloud model:
   cost per query = (input tokens / 1,000,000) times input rate
   plus (output tokens / 1,000,000) times output rate, using the
   mean token counts over the 24 questions. The study reports
   cost per query, per 1,000 queries, per 100,000 queries, and
   per 1,000,000 queries. Local marginal cost per query is 0 USD
   in API fees by construction (no API is called); electricity
   and hardware are excluded and that exclusion is stated.
5. Speed comparison. Local: measured latency per query (mean,
   median, minimum, maximum over all rounds). Cloud: not
   measured. The study carries one labelled assumption, a
   planning range of 1,000 to 3,000 ms per query for a hosted
   API answer (network round trip plus generation), marked
   unverified, used only to state the order of magnitude gap on
   this tiny corpus, never as a measured result.
6. Quality comparison. Local quality is measured (Build eval).
   Cloud quality is not measured and no cloud accuracy number
   is stated anywhere. The comparison is a capability table:
   the local core answers only with sentences present in the
   documents, refuses below threshold, and cannot paraphrase,
   use synonyms, combine facts, or answer from general
   knowledge; a hosted generative model can do those things and
   can also answer without evidence and be wrong fluently. Both
   halves of that sentence are the finding, not a score.
7. Privacy comparison. Local: the Build privacy audit result
   (source scan, 0 network pattern matches, no data leaves the
   machine by construction) plus the Deep source scan over this
   level. Cloud: by construction, the prompt and the retrieved
   private chunks leave the machine to the provider. The Google
   pricing page states the data use split directly: on the free
   tier content is used to improve products, on the paid tier it
   is not. Retention and training policy beyond what the pricing
   pages state is out of scope and is not claimed.
8. Verdict. A written decision rule closes the study: which
   side wins on each axis, and a rule a reader can apply (data
   must not leave the device, question needs synthesis or
   general knowledge, volume and lookup shape, offline need).

#### Acceptance

- Full test suite passes: the 42 prior tests, the scaffold
  smoke test, and new Deep tests in tests/test_deep_study.py.
- results_deep.json is deterministic across two runs once the
  named timing fields (everything under the timing key) are
  excluded, verified by hash of the canonicalised remainder.
- This level README carries method, the measured local table,
  the modelled cloud table with sources, the verdict, failure
  modes, and one exact main results claim paragraph for Jev gating.
- Root README and DOSSIER.md updated to Deep ship state, and
  ROADMAP.md at repo root carries the v1.1 backlog.
- No em dash character in any file. No paid API call, no new
  credential, no social post.

### NOVELTY: local-first-ai (P15)

Status: DRAFT, PROPOSED. Not verified. This text does not move into any public post, paper, or profile until the Jev claim_check gate passes on the exact text.

#### Proposed claim

Against local assistant bundles (Ollama class setups): this project aims to differ in the way its SPEC.md section text defines (a from-zero or self-hosted build, measured in public, on a named home fleet, with the failure modes written down). The exact difference is stated at the project's wave, after the prior art is re-read.

#### Prior art table

| Prior art | What it does | What this project does differently | Measured difference |
| --- | --- | --- | --- |
| local assistant bundles (Ollama class setups) | See DOSSIER.md, Past | PROPOSED, see the claim above | NO MEASUREMENT YET |

#### Honest size

If the novelty proves small, this file will say so and name the real value instead (a cleaner reproduction, a better benchmark, a first public dataset). No novelty is invented to fill this section.

### DOSSIER: local-first-ai (P15)

Written under the documentation and publishing standard (past,
present, future). Updated at Deep ship time, 2026-11-05: all
three levels are built, tested, and measured. v1.0 is the
December compressed scope; the rest of the v2 scope is the
v1.1 backlog in ROADMAP.md.

#### Past

Prior art: local assistant bundles (Ollama class setups) and
hosted chat APIs. The problem is old: a person wants answers
from their own files without handing the files, or the
questions about them, to a third party. Hosted models made the
capability gap wide (generation, paraphrase, synthesis) while
making the privacy transfer routine. This project measures
that trade on one small, fully public, synthetic corpus,
instead of asserting it.

#### Present

Shipped v1.0 (2026-11-05), all measured on the Muse VM,
Python 3.12, standard library only:

- Learn: TF-IDF core over 8 synthetic documents, 10 labelled
  questions, top-1 and sentence accuracy 1.000, privacy audit
  clean.
- Build: chunked TF-IDF pipeline over 24 synthetic documents
  (72 chunks), 24 labelled questions, top-1, recall, sentence,
  and refusal metrics all 1.000, persistent session memory,
  privacy audit clean.
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
  go local).

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

#### Future

The v1.1 backlog is ROADMAP.md at the repo root: the Ollama
generative local run, a real private corpus eval, provider
tokenizer counts, a free tier cloud measurement where terms
allow, total cost of ownership, a corpus scaling run, runtime
privacy monitoring, and fan-out completion. Any forecast
about this field is [unverified] unless a dated primary
source is added here.
