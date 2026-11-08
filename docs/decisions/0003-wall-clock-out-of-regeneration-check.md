# 0003. Wall clock fields are left out of the results regeneration check

Date: 2026-11-08
Status: accepted

Context. results_learn.json and results_build.json regenerate byte
for byte. results_deep.json and results_rigor.json also hold timing
(answer latency, index build time) measured on the study VM, which
differs on every run and every machine.

Decision. src/check_results.py re-runs all four runners and compares
every field except keys containing "latency_ms" or "build_ms", then
restores the committed files, so the recorded study-VM timings stay
as recorded. A self-check in the script fails if the filter drops any
other key.

Consequences. Timing numbers are evidence of one machine on one day,
not reproducible results; REPORT.md says so wherever they appear.
