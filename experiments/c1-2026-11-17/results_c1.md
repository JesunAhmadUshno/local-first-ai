# C1 confirmatory run: results

Run 2026-11-17 under decision 0004 (the lock) as amended on
personnel by decision 0005. Full per-question record:
results_c1.json (every question's best-chunk score, both
annotators' labels, the consensus label, and the fitted
threshold). Script: run_c1.py. Core: src/assistant.py,
unmodified.

## Verdict: C1 NOT CONFIRMED

The locked lines (PROPOSAL.md Part 1) and the outcome:

- Counts: held-out consensus sets are 85 evidence and 40
  no-evidence questions. Both meet the lock's minimums (75 and
  25). PASS on counts.
- Refusal recall: 0 of 40 held-out no-evidence questions
  refused at the fitted threshold. Recall 0.0000, Wilson 95%
  lower bound 0.0000, against the locked line of at least 0.80.
  FAIL.
- False refusals: 0 of 85 held-out evidence questions refused.
  Rate 0.0000, against the locked line of at most 10%. PASS,
  trivially: at the fitted threshold the system refuses
  nothing, which is exactly why the recall line fails.

## How the threshold was fitted

On the calibration consensus sets (38 evidence, 20
no-evidence), the registered fitting rule (maximise balanced
accuracy over the observed scores and their midpoints, ties
toward the larger threshold) reaches its maximum, balanced
accuracy 0.5000, at threshold 0.1220, the lowest calibration
score, where nothing is refused. No calibration threshold does
better than chance: 0.5000 is the ceiling over the whole grid.
The fitted value was applied once to the held-out sets, as
registered. It was not adjusted after the held-out scores were
seen.

## Why: the score does not separate the classes

Best-chunk TF-IDF scores (repo's core, unmodified), consensus
labels:

- Calibration evidence (n 38): median 0.1909, range 0.1220 to
  0.3354. Calibration no-evidence (n 20): median 0.2458, range
  0.1627 to 0.4947.
- Held-out evidence (n 85): median 0.1889, range 0.1472 to
  0.4117. Held-out no-evidence (n 40): median 0.2509, range
  0.1722 to 0.4033.

The no-evidence questions score systematically HIGHER than the
evidence questions, the reverse of what a refusal threshold
needs. For scale, at the core's own shipped constant of 0.30
the held-out sets would give refusal recall 0.7000 with a
false refusal rate of 0.9765 (83 of 85 evidence questions
refused): unusable in the other direction. There is no
threshold on this score, on this corpus, that refuses the
unanswerable questions while answering the answerable ones.

## Personnel and labels (decision 0005 disclosure)

Questions: 189, written by five independent AI writer agents
that received only the corpus's title and topic list and never
opened the corpus files (39 calibration evidence, 20
calibration no-evidence, 90 held-out evidence, 40 held-out
no-evidence, after one recorded drop; see questions-note.md).
Labels: two independent AI annotator agents read the corpus
and labelled all 189 questions blind (shuffled, no intended
labels shown). Agreement 183 of 189 (96.8%). The 6
disagreements (CAL-E27, HO-E033, HO-E058, HO-E075, HO-E078,
HO-E082; annotator A EVIDENCE, annotator B NO-EVIDENCE in each
case) were excluded from the primary sets, as registered; no
adjudication rule was invented. Under each annotator's own
labels the held-out result is the same: refusal recall 0.0
(annotator A: 0 of 40 no-evidence refused, 90 evidence;
annotator B: 0 of 45, 85 evidence).

## Corpus

Emerson's essays, 11 documents, 67,633 words, 3,387 chunks;
source and licence in corpus-source.md; fingerprint
7ce2deb4397a61694350425c11a25bd64c4fd4092a32e35d7df76e287822183b.

## What this means

C1 asked whether the refusal rule generalises to questions
written by someone who has not read the corpus. On this real,
public corpus it does not: the best-chunk score carries no
usable separation, so a threshold fitted on calibration data
cannot make the rule work. The Build level's perfect refusal
scores were measured on the same labelled set the 0.30
threshold was tuned on, over a small synthetic corpus; this
run is the measurement that limit called for, and the answer
is negative. The repo's verdict cap (Functional) is not lifted
by C1.
