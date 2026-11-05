# DEEP-SPEC: local-first-ai, Level 3 Deep (compressed)

Written before any Deep code, per the task order. Date: 2026-11-05.
December Compression Protocol: compressed Deep is the single
hardest capability in SPEC.md, built, tested, benchmarked, with
failure modes written. The rest of the v2 Deep scope goes into
the repo root ROADMAP.md as the named v1.1 backlog.

## What SPEC.md asks for

Deep is a local against cloud study: cost, speed, quality, and
privacy, with numbers. Deep closes when that scope is done, the
failure modes are written, and the dossier is updated to ship
state.

## Hard rule for this level (FREE-ONLY)

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

## Environment facts, checked 2026-11-05

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

## Pricing sources (published pricing, checked 2026-11-05)

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

## The study design

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

## Acceptance

- Full test suite passes: the 42 prior tests, the scaffold
  smoke test, and new Deep tests in tests/test_deep_study.py.
- results_deep.json is deterministic across two runs once the
  named timing fields (everything under the timing key) are
  excluded, verified by hash of the canonicalised remainder.
- This level README carries method, the measured local table,
  the modelled cloud table with sources, the verdict, failure
  modes, one exact main results claim paragraph for Jev gating,
  and a grade out of 10,000 with itemised deductions.
- Root README and DOSSIER.md updated to Deep ship state, and
  ROADMAP.md at repo root carries the v1.1 backlog.
- No em dash character in any file. No paid API call, no new
  credential, no social post.
