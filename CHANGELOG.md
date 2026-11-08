# Changelog

All notable changes to this project. Format: Keep a Changelog 1.1.
Versions follow Semantic Versioning. The tags v0.1, v0.5 and v1.0 were
cut before portfolio standard v2 and are kept as they are; under the
standard no release has been made yet.

## [Unreleased]

### Changed
- 2026-11-08: Restructured to the portfolio standard v2. README is the
  abstract (question, headline with its interval, field, job family,
  verdict). Verdict: Functional, not pre-registered. PROPOSAL.md
  replaces SPEC.md, NOVELTY.md, DOSSIER.md and the Build and Deep
  specs, and adds a confirmatory re-run plan (draft, not locked).
  REPORT.md replaces the three level READMEs, the old README body,
  ROADMAP.md (now "Future work") and docs/research-review.md. Code
  moved to src/, the Build corpus to experiments/corpus/, recorded
  results to results/ (unchanged; they regenerate from the code).
  fanout/ and PUBLICITY.md moved to docs/fanout/. docs/index.md
  removed (its text duplicated the README).
- 2026-11-08: Grades and review scores removed from public files,
  including the dashboard's grade tiles, which now show the README
  verdict; grades are kept internally.
- 2026-11-08: CI runs with read-only permissions, adds the layout test
  and src/check_results.py, which fails if results/ does not regenerate
  (wall clock fields excluded, decision 0003). CodeQL covers Python and
  JavaScript; Dependabot watches the site's npm packages.

### Added
- 2026-11-08: docs/decisions 0001 to 0003, CITATION.cff, SECURITY.md,
  tests/test_layout.py (required files, README abstract, no public
  grade).
- 2026-11-07: Rigor add-ons: Wilson intervals, leave-one-out
  threshold, BM25 and whole-document baselines, chunk sweep, a
  16-question hard set and a scaling curve (results_rigor.json); a
  runtime egress test with every socket constructor blocked.
- 2026-11-07: Live dashboard on GitHub Pages: a browser port of the
  Build pipeline, with a build-time parity check against the recorded
  results; vite pinned to 6.4.5.
- 2026-11-07: Research review (now in REPORT.md).

## [1.0] - 2026-11-05 (pre-standard tag)

### Added
- Deep: local against cloud study, local side measured with the Build
  pipeline, cloud side modelled from published pricing (no API call);
  20 tests (62 total). ROADMAP.md with the v1.1 backlog.
- Actions pack (CI matrix with ruff, CodeQL, Dependabot, release,
  labeler, greetings, stale) and the written fan-out set.

## [0.5] - 2026-11-05 (pre-standard tag)

### Added
- Build: chunked TF-IDF assistant over 24 synthetic documents with
  cited multi-sentence answers, refusal at 0.30 and session memory,
  measured on 24 labelled questions; 21 tests.

## [0.1] - 2026-11-05 (pre-standard tag)

### Added
- Learn: TF-IDF core with cited extractive answers over 8 synthetic
  documents, 10 labelled questions, and a source privacy audit; 21
  tests.
