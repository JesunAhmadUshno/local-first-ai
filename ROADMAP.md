# ROADMAP: local-first-ai (P15), v1.1 backlog

Written 2026-11-05 at Deep ship time, per the December
Compression Protocol: compressed Deep (v1.0) is the single
hardest capability in SPEC.md, the local against cloud study.
Everything else in the v2 Deep scope is named here as the
v1.1 backlog. Nothing in this file is built or measured yet.

## v1.1 items

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

## Held items (not v1.1 work)

- P19 style multi-GPU scope does not apply to this project.
- Any paid API run stays out of scope under FREE-ONLY unless
  Jesun rules otherwise on a named proposal.
