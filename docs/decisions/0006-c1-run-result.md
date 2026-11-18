# 0006. C1 confirmatory run: executed, NOT CONFIRMED

Date: 2026-11-17
Status: run complete; verdict recorded. Supersedes nothing;
decision 0004's lock and decision 0005's personnel amendment
stand as the protocol of record.

## The run

Under the Owner's blanket permission of 2026-11-17 21:59 EST,
C1 was run exactly as locked (decision 0004, PROPOSAL.md
Part 1), with the personnel arrangement of decision 0005:
independent AI question writers that never opened the corpus
files (titles and topic list only) and two independent AI
annotators. Every element is recorded in
experiments/c1-2026-11-17/: corpus-source.md (Emerson essays,
Project Gutenberg eBook #16643, public domain; 11 documents,
67,633 words, 3,387 chunks), questions.json and
questions-note.md (189 questions, one recorded drop),
labels_annotator_a.txt and labels_annotator_b.txt with parsed
JSON (agreement 183 of 189, 96.8%; 6 disagreements excluded
from the primary sets, no adjudication invented), run_c1.py,
results_c1.json and results_c1.md. The questions were
committed before the run and the plan tagged proposal-v1 in
this clone, per the Part 1 design order. src/ is unmodified.
Test suite: 84 passed before, 84 passed after.

## The verdict

C1 is NOT CONFIRMED.

- Held-out consensus counts meet the lock's minimums: 85
  evidence (line: at least 75), 40 no-evidence (line: at
  least 25).
- Threshold fitted on the calibration consensus sets only,
  by the rule registered in decision 0005: 0.1220, at which
  the calibration balanced accuracy reaches its grid maximum
  of 0.5000 (chance). No calibration threshold separates the
  classes.
- Refusal recall on the held-out no-evidence set: 0 of 40,
  recall 0.0000, Wilson 95% lower bound 0.0000. Locked line:
  at least 0.80. FAILED.
- False refusals on the held-out evidence set: 0 of 85,
  rate 0.0000. Locked line: at most 10%. Passed trivially,
  because the fitted threshold refuses nothing.

The measured reason: best-chunk TF-IDF scores for
no-evidence questions sit systematically above those for
evidence questions (held-out medians 0.2509 against 0.1889),
so no threshold on this score refuses the unanswerable while
answering the answerable. At the shipped constant of 0.30 the
same sets give recall 0.7000 with a false refusal rate of
0.9765. The full distributions are in results_c1.md.

## Consequences

- The refusal rule does not generalise beyond the set it was
  tuned on. Any future claim about refusal must carry this
  result beside the Build level's same-set scores.
- The repo's verdict cap (Functional) is not lifted by C1.
- Disclosure, restated for any paper version: the C1
  questions were written by AI agents working from the
  corpus's titles only, and the labels are two AI annotators'
  independent judgements. They may not be described as
  human-written questions or human annotations (decision
  0005, point c).
- C2 is untouched by this run and stays blocked on its own
  named input (no Ollama or llama.cpp and no 7B to 8B model
  on the BlackBox node). C3 and C4 stay unrun under the
  FREE-ONLY ruling.
