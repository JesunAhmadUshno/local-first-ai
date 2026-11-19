# 0005. C1 confirmatory run: amendment on personnel (AI writers and annotators)

Date: 2026-11-17
Status: accepted under the Owner's blanket permission of
2026-11-17 21:59 EST ("i give you every permission do everything
anyhow possible"), given after the Owner was told C1 was blocked
on an owner-supplied non-reader question set.

## What this amendment carries forward, unchanged

Decision 0004 (registered 2026-11-17 in the BlackBox clone of
record, local tag proposal-v1) locked PROPOSAL.md Part 1. The C1
pass lines are NOT changed by this amendment. They are, verbatim
in substance from PROPOSAL.md Part 1:

- C1, refusal generalises: with the threshold fitted on a
  calibration split only, refusal recall on a held-out set of at
  least 25 no-evidence questions has a Wilson 95% lower bound of
  at least 0.80, with at most 10% false refusals on at least 75
  held-out evidence questions.

The design order also stands: questions are written first and
committed (experiments/, dated), then the plan is tagged, then
the runs happen; every trial is reported, misses included.

## What this amendment changes: personnel only

(a) Authority. The Owner's blanket permission of 2026-11-17
21:59 EST authorises this run, including the personnel
arrangement below.

(b) Writers and annotators are independent AI agents. The
question writers are AI agents that never open the corpus files.
Each writer receives only the corpus's document titles and topic
list, never its text, and writes questions from the titles alone.
The two annotators are AI agents working independently of each
other; unlike the writers, the annotators DO read the corpus,
because their task is to judge whether the corpus contains
evidence that answers each question. Neither annotator sees the
writers' intended labels or the other annotator's labels.

(c) Disclosure. This arrangement, and the AI identity of the
writers and annotators, must be disclosed in any paper version
that reports C1, exactly as this record states it. The original
Part 1 needs list asked for "at least 100 human-written
questions"; under this amendment the questions are AI-written
under a non-reader constraint, and no report may describe them
as human-written.

(d) Pass lines unchanged. See above. Nothing in this amendment
moves a number, a count, or a verdict rule from the lock.

## Clarifications the lock leaves open, fixed here before any run

1. Corpus. A public, openly licensed, personal-style corpus:
   Ralph Waldo Emerson, Essays: First Series (1841) and Essays:
   Second Series (1844), public domain, fetched from Project
   Gutenberg (ebook 16643 and the Second Series companion text).
   Each essay becomes one document in the repo's ingest format
   (first line "Title: <essay title>"). Source and licence are
   recorded in experiments/c1-2026-11-17/corpus-source.md.

2. Splits and counts. Writers produce, by construction and in
   separate batches: a calibration split (40 intended-evidence
   and 20 intended-no-evidence questions) and a held-out split
   (90 intended-evidence and 40 intended-no-evidence questions).
   Intended labels are the writers' design intent only; the
   labels of record come from the annotators (point 3).

3. Labels of record. Each annotator independently labels every
   question EVIDENCE (the corpus contains a passage that answers
   the question) or NO-EVIDENCE (it does not), citing the
   document id for every EVIDENCE label. The primary scoring
   sets are the consensus sets: questions both annotators label
   the same way, within each split. The lock names no
   adjudication rule, so none is invented here: disagreements
   are counted and reported, the disagreed questions are
   excluded from the primary sets, and the full-set numbers
   under each annotator's own labels are reported beside the
   primary numbers. If a consensus held-out set falls below the
   lock's minimum counts (75 evidence, 25 no-evidence), that
   element of C1 is reported as not testable at the locked
   counts, not quietly re-based.

4. Threshold fitting rule (the lock says "fitted on a
   calibration split only" and names no rule). The fitted
   threshold is the value, over the grid of the calibration
   questions' observed best-chunk scores and their midpoints,
   that maximises balanced accuracy on the calibration consensus
   sets: (refusal recall on calibration no-evidence + (1 minus
   false refusal rate) on calibration evidence) / 2. Ties break
   toward the larger threshold. Best-chunk scores come from the
   repo's own offline core, unmodified (src/assistant.py
   ChunkIndex.retrieve_chunks); the fitted value is applied at
   study level in the run script. src/ is not edited.

5. Refusal rule at the fitted threshold: a question is refused
   if and only if its best-chunk score is below the fitted
   threshold, the same comparison the core makes against its
   named constant.

6. Wilson bound: the standard Wilson score interval for a
   binomial proportion, z = 1.959964, lower bound only, computed
   on the held-out consensus no-evidence set.

## Consequences

C1 can now be run tonight. Its evidence is weaker than the
human-writer design in one named way: AI writers working from
titles may write questions whose phrasing differs from human
questions, and AI annotators replace human annotators. Both
facts travel with the result wherever it is reported (point c).
C2, C3 and C4 are untouched by this amendment.
