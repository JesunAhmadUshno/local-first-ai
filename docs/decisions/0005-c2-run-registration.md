# 0005. C2 run registration: model, prompt, and blind grading protocol fixed before the run

Date: 2026-11-17
Status: accepted (registered before any C2 run, as decision 0004 requires)

Context. Decision 0004 locked the C2 pass line (a local 7B to 8B
instruction model, Ollama or llama.cpp, answering from the same
top 3 chunks, judged supported by its cited chunk on at least 90%
of evidence questions, under a blind grading protocol fixed
before the run) and recorded C2 as blocked: BlackBox had no
Ollama and no model in the band. On 2026-11-17 the Owner ordered
the block resolved and all work finished rigorously. This entry
fixes the run's remaining choices before anything runs. C1 is
untouched by this entry and stays blocked on its Owner-supplied
data. C3 and C4 stay unrun under FREE-ONLY.

Fixed choices.

- Runtime: Ollama for Windows, installed in the user context
  from the official ollama.com installer, no elevation.
- Model: llama3.1:8b (Meta Llama 3.1 8B instruct, inside the
  locked 7B to 8B band), pulled from the Ollama library. The
  exact manifest digest served is recorded in the results file.
  The 9B GGUF in the OpenWhispr cache is not used; it is
  outside the band.
- Question set: the 20 evidence questions of the Build labelled
  set, build_questions() in src/assistant.py (BQ01 to BQ20).
  The 4 no-evidence questions are not part of C2, whose pass
  line is stated over evidence questions.
- Retrieval: the repo's own ChunkIndex over experiments/corpus,
  top_k = 3, unchanged. The model receives exactly the same top
  3 chunks the offline core retrieves for each question.
- Prompt, fixed verbatim: the instruction "Answer the question
  using only the context below. Cite the source for each fact.
  If the context does not contain the answer, say you do not
  know.", then the three chunks each headed by their chunk id,
  then the question, then the instruction to answer briefly and
  to end with the line "Citation: " followed by the single
  chunk id that supports the answer.
- Generation: Ollama chat API on localhost, temperature 0,
  seed 20261117, one generation per question, per-question
  latency recorded.
- Cited chunk: the first chunk id named in the answer's
  Citation line that is one of the three retrieved chunks. If
  no valid id is named, the item is NO_CITATION and counts as
  not supported.

Blind grading protocol, fixed before the run.

- Grading is a separate pass after all 20 generations exist.
- The grading file carries, per item, only the answer text and
  the full text of its cited chunk, under a random code, in
  shuffled order. It carries no question id, no gold document
  or sentence, no other chunks, and no model name.
- Rubric: SUPPORTED if every factual claim in the answer is
  stated in, or directly follows from, the cited chunk text;
  NOT_SUPPORTED otherwise. NO_CITATION items are graded
  NOT_SUPPORTED without a grading file entry.
- The grader is the visiting agent, a single grader. Named
  limitation: decision 0004 names no grader for C2 and no
  second grader is available on this visit; the two-annotator
  requirement in the record belongs to C1's data, not to C2.
- A deterministic secondary signal (content-token overlap
  between the answer and its cited chunk) is computed and
  reported beside the grades. It is not the verdict.

Pass line (from decision 0004, unchanged): SUPPORTED on at
least 90% of the 20 evidence questions, that is at least 18
of 20.

Outputs, new files only: src/run_c2.py (the runner),
results/results_c2.json (the full run record),
results/c2_blind_grading.json (the grading record). The
outcome is recorded as a new dated decision entry after the
run. Nothing is pushed.
