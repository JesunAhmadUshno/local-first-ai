"""Run the rigor add-ons and write results_rigor.json.

Run: python src/run_rigor.py

Everything except the "scaling" block is deterministic. The
scaling block is wall clock timing and varies between runs.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rigor  # noqa: E402
from assistant import build_questions, ingest_directory  # noqa: E402
from rigor import ChunkIndex, evaluate  # noqa: E402

SWEEP_GRID = [(size, overlap) for size in (10, 15, 20, 30, 40, 60, 100) for overlap in (0, 5, 10, 20)]
SCALING_FACTORS = (1, 10, 50, 100)


def interval(k, n):
    lo, hi = rigor.wilson(k, n)
    return {"k": k, "n": n, "point": k / n, "wilson95": [lo, hi]}


def main():
    docs = ingest_directory(os.path.join(os.path.dirname(HERE), "experiments", "corpus"))
    questions = build_questions()
    build = evaluate(ChunkIndex(docs), questions)
    s = build["summary"]
    scores = [r["top1_score"] for r in build["questions"]]
    is_ev = [r["is_evidence"] for r in build["questions"]]
    loo = rigor.leave_one_out_threshold(scores, is_ev)
    refused = s["refusal_true_positive"] + s["refusal_false_positive"]
    no_ev = s["no_evidence_questions"]
    hard = rigor.evaluate_hard(ChunkIndex(docs), rigor.hard_questions())
    doc_level = rigor.evaluate_ranker(ChunkIndex(docs, 1000, 0), questions)
    out = {
        "scenario": "rigor add-ons on the Build corpus and labelled set: Wilson intervals, "
                    "leave-one-out refusal threshold, threshold curve, BM25 and document "
                    "level baselines, chunk sweep, a hard question set, corpus scaling",
        "intervals": {
            "top1": interval(s["top1_correct"], s["evidence_questions"]),
            "sentence": interval(s["sentence_correct"], s["evidence_questions"]),
            "refusal_recall": interval(s["refusal_true_positive"], no_ev),
            "refusal_precision": interval(s["refusal_true_positive"], refused),
        },
        "threshold": {
            "tuned": s["threshold"],
            "fitted_on_all_24": rigor.fit_threshold(scores, is_ev),
            "leave_one_out": loo,
            "curve": rigor.threshold_curve(scores, is_ev, [round(i * 0.05, 2) for i in range(17)]),
        },
        "baselines": {
            "tfidf_chunks_30_10": {"evidence_questions": s["evidence_questions"],
                                   "top1_correct": s["top1_correct"],
                                   "recall_at_3_correct": s["chunk_recall_at_3_correct"]},
            "bm25_chunks_30_10": rigor.evaluate_ranker(rigor.Bm25Index(docs), questions),
            "tfidf_whole_documents": doc_level,
        },
        "chunk_sweep": rigor.chunk_sweep(docs, questions, SWEEP_GRID),
        "hard_set": hard,
        "scaling": {"label": "synthetic scaling: the 24 documents replicated with new ids; "
                             "wall clock, varies between runs",
                    "rows": rigor.scaling_curve(docs, questions, SCALING_FACTORS)},
    }
    print("LOO refusal:", loo)
    print("Hard set: paraphrase %d/%d correct, distractors refused %d/%d" % (
        hard["paraphrase_answered_correctly"], hard["paraphrase_questions"],
        hard["distractor_refused"], hard["distractor_questions"]))
    print("BM25:", out["baselines"]["bm25_chunks_30_10"], "doc level:", doc_level)
    for row in out["scaling"]["rows"]:
        print("scaling:", row)
    path = os.path.join(os.path.dirname(HERE), "results", "results_rigor.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("Wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
