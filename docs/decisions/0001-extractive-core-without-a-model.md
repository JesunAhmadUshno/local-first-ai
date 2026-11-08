# 0001. Extractive core, standard library only, no language model

Date: 2026-11-05 (recorded 2026-11-08 from level-2-build/BUILD-SPEC.md)
Status: accepted

Context. The plan called for an assistant on Ollama. Ollama was not
installed on the Muse VM where the work ran (checked 2026-11-05: no
binary, nothing on localhost port 11434), and installing a model
runtime and weights was out of scope for the cycle.

Decision. Build the assistant as an extractive core: TF-IDF retrieval
over chunks, answers copied verbatim from the top document with a
citation, a refusal below a named threshold. Python standard library
only, so the privacy audit and the egress test cover every line.

Consequences. No generation, paraphrase or synthesis; the hard set
shows the cost (2 of 10 paraphrases answered). The local against
cloud question is answered for an extractive core, not for a local
language model; that comparison is PROPOSAL.md Part 1.
