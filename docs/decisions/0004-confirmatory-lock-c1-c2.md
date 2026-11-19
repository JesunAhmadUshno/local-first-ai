# 0004. Confirmatory lock: C1 and C2 pass lines as drafted; C3 and C4 excluded

Date: 2026-11-17
Status: accepted

Context. PROPOSAL.md Part 1 drafts a confirmatory re-run (C1 to
C4) whose pass lines were proposals until the Owner confirmed
them. The gap register (2026-11-17) carried that confirmation as
an open decision. On 2026-11-17 the Owner ruled: the C1 to C4
pass lines are locked as the confirmatory draft's own lines,
and the paid cloud calls are refused, so C3 and C4 stay unrun
under the FREE-ONLY rule. This entry records the lock in the
repo's decision record before any confirmatory run, as
PROPOSAL.md's design requires (the plan is fixed before the
runs; the proposal-v1 tag is applied to the commit carrying
this entry in the BlackBox clone, and nothing is pushed).

Decision. The locked pass lines are PROPOSAL.md Part 1's own
lines, verbatim in effect:

- C1, refusal generalises: with the threshold fitted on a
  calibration split only, refusal recall on a held-out set of
  at least 25 no-evidence questions has a Wilson 95% lower
  bound of at least 0.80, with at most 10% false refusals on
  at least 75 held-out evidence questions. The questions are
  written by someone who has not read the corpus, over a
  public, openly licensed personal-style corpus, with two
  annotators (the data the 2026-11-07 review lists as an
  Owner-supplied input).
- C2, local generation keeps the evidence: a local 7B to 8B
  instruction model (Ollama or llama.cpp) answering from the
  same top 3 chunks is judged supported by its cited chunk on
  at least 90% of evidence questions, under a blind grading
  protocol fixed before the run.
- C3 and C4: not run. The Owner refused the roughly 240 paid
  cloud calls (about USD 0.07 at the recorded modelled rates);
  the cloud side stays modelled, exactly as results_deep.json
  records it.

Pre-run state, recorded 2026-11-17 in the BlackBox window so
nobody has to guess later. C1 cannot run yet: the held-out
non-reader question set and its corpus do not exist in this
repo or on the machine (the committed question sets are the
author's own 24 Build questions and 16 hard questions, and the
0.30 threshold was tuned on them, which is the exact
contamination C1 exists to remove). C1 stays blocked on that
Owner-supplied data. C2 cannot run yet either: BlackBox has
no Ollama installation and no llama.cpp binary (verified
2026-11-17), and the only local model file on the machine is
a Qwen3.5-9B GGUF in an unrelated application's cache, which
is outside the draft's 7B to 8B band. No substitute model or
runtime was installed in this window; C2 stays blocked on a
7B to 8B instruction model served by Ollama or llama.cpp on
BlackBox. Neither block is a verdict on either hypothesis.

Consequences. The repo's verdict cap (Functional) stands until
C1 and C2 actually run under this lock. When the data and the
model exist, the runs proceed under this entry without a new
lock decision; every trial is reported, misses included, per
PROPOSAL.md's design.
