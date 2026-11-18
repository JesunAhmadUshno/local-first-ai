"""C1 confirmatory run (decision 0005). Run from this folder.

Uses the repo's offline core unmodified (src/assistant.py):
ingest_directory + ChunkIndex.retrieve_chunks produce every
question's best-chunk score. The refusal threshold is fitted on
the calibration consensus sets only, by the rule fixed in
decision 0005 (maximise balanced accuracy over the observed
calibration scores and their midpoints; ties toward the larger
threshold), then applied once to the held-out consensus sets.

Inputs (this folder):
  questions.json          [{id, split, intended, question}]
  labels_annotator_a.json {qid: {"label": ..., "doc": ...}}
  labels_annotator_b.json {qid: {"label": ..., "doc": ...}}

Output: results_c1.json with every question's score and labels,
the fitted threshold, and the verdict under the locked lines:
refusal recall Wilson 95% lower bound >= 0.80 on >= 25 held-out
no-evidence questions; false refusals <= 10% on >= 75 held-out
evidence questions (PROPOSAL.md Part 1, decision 0004).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
from assistant import ChunkIndex, ingest_directory  # noqa: E402

Z = 1.959964


def wilson_lower(k, n, z=Z):
    if n == 0:
        return 0.0
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return centre - half


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def consensus_label(qid, la, lb):
    a, b = la.get(qid), lb.get(qid)
    if a is None or b is None:
        return None, "missing"
    if a["label"] == b["label"]:
        return a["label"], "agree"
    return None, "disagree"


def fit_threshold(cal_rows):
    """cal_rows: [(score, is_no_evidence)] on consensus labels."""
    scores = sorted({s for s, _ in cal_rows})
    grid = set(scores)
    for x, y in zip(scores, scores[1:]):
        grid.add((x + y) / 2)
    grid.add(0.0)
    best = None
    for t in sorted(grid):
        ne = [(s, lab) for s, lab in cal_rows if lab]
        ev = [(s, lab) for s, lab in cal_rows if not lab]
        recall = (sum(1 for s, _ in ne if s < t) / len(ne)) if ne else 0.0
        frr = (sum(1 for s, _ in ev if s < t) / len(ev)) if ev else 0.0
        bal = (recall + (1 - frr)) / 2
        key = (bal, t)  # ties toward the larger threshold
        if best is None or key > best[0]:
            best = (key, t, recall, frr)
    return best[1], best[2], best[3]


def score_set(rows, threshold):
    """rows: [(qid, score, is_no_evidence)] -> refusal metrics."""
    ne = [(q, s) for q, s, lab in rows if lab]
    ev = [(q, s) for q, s, lab in rows if not lab]
    refused_ne = sum(1 for _, s in ne if s < threshold)
    refused_ev = sum(1 for _, s in ev if s < threshold)
    recall = refused_ne / len(ne) if ne else 0.0
    frr = refused_ev / len(ev) if ev else 0.0
    return {
        "no_evidence_n": len(ne), "no_evidence_refused": refused_ne,
        "refusal_recall": recall,
        "refusal_recall_wilson_lower": wilson_lower(refused_ne, len(ne)),
        "evidence_n": len(ev), "evidence_refused": refused_ev,
        "false_refusal_rate": frr,
    }


def main():
    questions = load("questions.json")
    la = load("labels_annotator_a.json")
    lb = load("labels_annotator_b.json")
    docs = ingest_directory(os.path.join(HERE, "corpus"))
    index = ChunkIndex(docs)

    rows = []
    for q in questions:
        best = index.retrieve_chunks(q["question"], top_k=3)[0]
        lab, agree = consensus_label(q["id"], la, lb)
        rows.append({
            "id": q["id"], "split": q["split"],
            "intended": q["intended"], "question": q["question"],
            "best_chunk": best["chunk_id"], "best_doc": best["doc_id"],
            "best_score": best["score"],
            "label_a": la.get(q["id"], {}).get("label"),
            "label_b": lb.get(q["id"], {}).get("label"),
            "consensus": lab, "agreement": agree,
        })

    cal = [(r["best_score"], r["consensus"] == "NO-EVIDENCE")
           for r in rows if r["split"] == "calibration"
           and r["consensus"] is not None]
    threshold, cal_recall, cal_frr = fit_threshold(cal)

    held = [(r["id"], r["best_score"], r["consensus"] == "NO-EVIDENCE")
            for r in rows if r["split"] == "held_out"
            and r["consensus"] is not None]
    primary = score_set(held, threshold)

    per_annotator = {}
    for key, labels in (("annotator_a", la), ("annotator_b", lb)):
        h = [(r["id"], r["best_score"],
              labels.get(r["id"], {}).get("label") == "NO-EVIDENCE")
             for r in rows if r["split"] == "held_out"
             and labels.get(r["id"]) is not None]
        per_annotator[key] = score_set(h, threshold)

    disagreements = [r["id"] for r in rows if r["agreement"] == "disagree"]
    counts_ok = (primary["evidence_n"] >= 75
                 and primary["no_evidence_n"] >= 25)
    verdict = {
        "counts_meet_lock_minimums": counts_ok,
        "wilson_line_met": primary["refusal_recall_wilson_lower"] >= 0.80,
        "false_refusal_line_met": primary["false_refusal_rate"] <= 0.10,
    }
    verdict["c1_confirmed"] = bool(
        counts_ok and verdict["wilson_line_met"]
        and verdict["false_refusal_line_met"])

    out = {
        "study": "C1 confirmatory run, decision 0005",
        "documents": len(docs), "chunks": len(index.chunks),
        "fitted_threshold": threshold,
        "calibration": {"n": len(cal), "refusal_recall": cal_recall,
                        "false_refusal_rate": cal_frr},
        "held_out_primary_consensus": primary,
        "held_out_per_annotator": per_annotator,
        "annotator_disagreements": disagreements,
        "verdict": verdict,
        "questions": rows,
    }
    with open(os.path.join(HERE, "results_c1.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"fitted_threshold": threshold,
                      "calibration": out["calibration"],
                      "primary": primary, "verdict": verdict,
                      "disagreements": len(disagreements)}, indent=2))


if __name__ == "__main__":
    main()
