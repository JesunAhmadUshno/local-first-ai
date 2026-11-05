# Level 3, Deep: local-first-ai

Status: DONE (2026-11-05). The local against cloud study from
SPEC.md: cost, speed, quality, and privacy, with numbers. The
local side is measured with the Build pipeline on this machine.
The cloud side is modelled from published pricing and stated
assumptions only: no API was called, no key was used, and no
cloud number in this file is a measurement. The spec, written
before the code, is DEEP-SPEC.md in this folder.

## Honest scope line

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

## Method

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

## Run it

    python level-3-deep/run_deep.py
    python -m unittest discover -s tests -v
    python tests/test_smoke.py

The runner writes level-3-deep/results_deep.json. The
deterministic part (quality, token model, modelled costs,
privacy, verdict) is identical across two runs: canonicalised
sha256 541abbed0e30284b (first 16) on both runs, verified
2026-11-05, computed after removing the timing key. The timing
key (index build and answer latency, wall clock) varies
between runs and is the named exclusion from that check.

## Results, local side (measured 2026-11-05, Muse VM)

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

## Results, cloud side (MODELLED from published pricing)

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

## Quality comparison (measured local, capability cloud)

| Capability | Local (measured or observed) | Cloud generative (capability, not measured) |
| --- | --- | --- |
| Lookup inside the documents | 1.000 top-1 and sentence accuracy on the eval set | Expected strong, not measured here |
| Refusal with no evidence | 1.000 precision and recall at threshold 0.30 | No built in refusal rule; can answer anyway |
| Paraphrase and synonyms | Fails: exact token matching only | Handles rewording as a core capability |
| Combining facts across documents | Cannot: one document per answer | Can synthesise across the full prompt |
| General knowledge | None: documents only | Broad, with fluent error risk |
| Answer form | Verbatim cited sentences only | Fluent written answers, citations on request |
| Hallucination surface | None by construction (copied text or refusal) | Present: fluent text can outrun the evidence |

## Verdict

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

## Main results claim (exact paragraph for Jev gating)

Deep ran one local against cloud study on the Muse VM on 2026-11-05: the local side was measured with the Build pipeline on its 24 labelled questions and scored top-1 document accuracy 1.000 (20 of 20 evidence questions), first answer sentence accuracy 1.000 (20 of 20), and refusal precision 1.000 and recall 1.000 (4 of 4 no-evidence questions refused), with a mean answer latency of 0.3326 ms over 120 timed answers and a privacy audit over 2 Deep source files finding 0 matches for 7 network patterns; the cloud side was modelled, not measured, from published pricing checked on 2026-11-05 and a stated token estimate (mean 163.33 input tokens and 29.46 output tokens per query), giving a modelled cost per query of 0.000031 USD on gpt-6-luna and claude-haiku-5.5, 0.000123 USD on gemini-3.5-flash-lite, 0.000233 USD on gemini-3.8-flash, and 0.000621 USD on gpt-6.1-sol and claude-sonnet-5.5, or 3.11, 12.26, 23.30, and 62.13 USD per 100,000 queries at the budget, flash-lite, flash, and flagship rates; no cloud API was called, cloud quality and cloud latency were not measured, and Ollama was rechecked unavailable on the Muse VM on 2026-11-05 so the local core stayed extractive; and 62 unit tests passed in total, 20 of them new Deep tests, plus the scaffold smoke test.

Jev gate on the paragraph above: model jev-1.13.0, 1,812 input
tokens, supported noul 0.72, route REVIEW (clear at 0.85 or
above, block at 0.10 or below). The claim therefore stands as
reviewed, not cleared, and its numbers rest on the measured
and modelled evidence in results_deep.json, not on the gate.

## Failure modes and limits

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

## Grade

Grade: 7,400 of 10,000 for this Deep level.

Deductions (they sum to 2,600):
- Cloud side modelled from published pricing, never measured:
  no API run under FREE-ONLY, so no observed cloud cost,
  latency, or billing behaviour: minus 600.
- Cloud quality not measured: the quality comparison is a
  capability table, not a head to head accuracy result:
  minus 500.
- Local quality inherited from the synthetic 24 document
  corpus on distinct topics, so the perfect scores are weak
  evidence for either side of the comparison: minus 500.
- Local core still extractive with no Ollama and no language
  model (rechecked unavailable), so the local side of the
  study is a retrieval core, not the SPEC assistant: minus 400.
- Cloud latency is a stated assumed range and local latency
  is a tiny corpus, shared VM measurement with visible cross
  run spread: minus 250.
- Token counts come from a documented word based estimator,
  not from provider tokenizers: minus 150.
- Run on the Muse VM, not the assigned BlackBox fleet node:
  minus 100.
- Pricing is a dated snapshot that decays: one rate in the
  table is already announced to double on 2027-01-01:
  minus 100.

## What v1.1 adds next

The rest of the v2 Deep scope sits in the repo root ROADMAP.md
as the named v1.1 backlog: the Ollama backed generative local
run on a machine where Ollama is installed, a real private
corpus eval, provider tokenizer counts, a free tier cloud
measurement where terms allow it, and a total cost of ownership
comparison that includes hardware and electricity.
