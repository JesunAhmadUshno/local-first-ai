# 0002. Cloud side modelled from published pricing, not measured

Date: 2026-11-05 (recorded 2026-11-08 from level-3-deep/DEEP-SPEC.md)
Status: accepted

Context. The Deep cycle ran under a free-only rule: no paid API call
and no new credential without the Owner's approval.

Decision. Model cloud cost from published pricing pages (checked
2026-11-05) and a stated word-based token estimate; carry cloud
latency as one labelled assumed range; compare quality as
capabilities, not accuracy.

Consequences. No cloud number in results/results_deep.json is a
measurement. Measuring cloud cost, latency and quality needs API keys
and about 240 paid calls; it is in PROPOSAL.md Part 1 and needs the
Owner's approval.
