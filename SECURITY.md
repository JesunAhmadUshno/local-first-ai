# Security policy

Report a vulnerability privately through GitHub's "Report a
vulnerability" button on this repository's Security tab. Please do not
open a public issue for it. You will get a reply within 7 days.

Scope: the code in this repository and the dashboard in site/. The
corpus in experiments/corpus/ is synthetic; no private data, key or
credential is stored in the repo, and no code path makes a network
call (tests/test_deep_egress.py blocks every socket and runs the
pipeline end to end).
