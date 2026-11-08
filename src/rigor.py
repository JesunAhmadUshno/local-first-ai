"""Rigor add-ons for the local-first study, Level 3 Deep.

Cheap checks that answer the review's fixable gaps, standard
library only, all on the committed Build corpus:

- Wilson 95% score intervals for every count based metric.
- A leave-one-out refusal threshold: each question is scored
  with a threshold fitted on the other 23, so the refusal figure
  is held out instead of tuned on the set it is reported on.
- A threshold curve: refusals and false refusals per threshold.
- A BM25 baseline and a document level (unchunked) ablation.
- A chunk size and overlap sweep over the Build pipeline.
- A small hard question set written for this check: synonym
  paraphrases with a gold document, and cross topic distractors
  with no evidence that share words with the corpus.
- A corpus scaling curve: the 24 documents replicated with new
  ids, timed for index build and answer latency. Synthetic
  scaling, not a real larger corpus.
"""
import math
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from assistant import REFUSAL_THRESHOLD, ChunkIndex, chunk_all, evaluate  # noqa: E402
from local_first import tokenize  # noqa: E402

Z95 = 1.959963984540054
BM25_K1 = 1.5
BM25_B = 0.75


class RigorError(Exception):
    """Named error for invalid rigor inputs."""


def wilson(k, n, z=Z95):
    """Wilson score interval for k successes of n trials."""
    if not isinstance(n, int) or n < 1 or not isinstance(k, int) or k < 0 or k > n:
        raise RigorError("need integers with 0 <= k <= n and n >= 1")
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def fit_threshold(scores, is_evidence):
    """Midpoint between the highest no-evidence and lowest evidence score."""
    none_max = max(s for s, e in zip(scores, is_evidence) if not e)
    ev_min = min(s for s, e in zip(scores, is_evidence) if e)
    return (none_max + ev_min) / 2


def leave_one_out_threshold(scores, is_evidence):
    """Refusal counts where each item uses a threshold fitted without it."""
    tp = fp = fn = 0
    thresholds = []
    for i in range(len(scores)):
        rest_s = scores[:i] + scores[i + 1:]
        rest_e = is_evidence[:i] + is_evidence[i + 1:]
        t = fit_threshold(rest_s, rest_e)
        thresholds.append(t)
        refused = scores[i] < t
        if refused and not is_evidence[i]:
            tp += 1
        elif refused and is_evidence[i]:
            fp += 1
        elif not refused and not is_evidence[i]:
            fn += 1
    return {"refusal_true_positive": tp, "refusal_false_positive": fp,
            "refusal_false_negative": fn,
            "threshold_min": min(thresholds), "threshold_max": max(thresholds)}


def threshold_curve(scores, is_evidence, thresholds):
    """Refusal counts at each threshold (refuse when score < threshold)."""
    rows = []
    for t in thresholds:
        refused = [s < t for s in scores]
        tp = sum(1 for r, e in zip(refused, is_evidence) if r and not e)
        fp = sum(1 for r, e in zip(refused, is_evidence) if r and e)
        rows.append({"threshold": t, "refused": sum(refused),
                     "true_refusals": tp, "false_refusals": fp,
                     "missed_refusals": sum(1 for e in is_evidence if not e) - tp})
    return rows


class Bm25Index:
    """Okapi BM25 over the same chunks the Build pipeline uses."""

    def __init__(self, docs, chunk_size=30, overlap=10):
        self.chunks = chunk_all(docs, chunk_size, overlap)
        self.tokens = {c["chunk_id"]: Counter(tokenize(c["text"])) for c in self.chunks}
        self.lengths = {cid: sum(t.values()) for cid, t in self.tokens.items()}
        self.avg_len = sum(self.lengths.values()) / len(self.chunks)
        df = Counter()
        for t in self.tokens.values():
            df.update(t.keys())
        n = len(self.chunks)
        self.idf = {term: math.log((n - d + 0.5) / (d + 0.5) + 1) for term, d in df.items()}

    def retrieve_chunks(self, question, top_k=3):
        q = tokenize(question)
        scored = []
        for c in self.chunks:
            tf, length = self.tokens[c["chunk_id"]], self.lengths[c["chunk_id"]]
            score = 0.0
            for term in q:
                f = tf.get(term, 0)
                if f:
                    norm = BM25_K1 * (1 - BM25_B + BM25_B * length / self.avg_len)
                    score += self.idf[term] * f * (BM25_K1 + 1) / (f + norm)
            scored.append({"chunk_id": c["chunk_id"], "doc_id": c["doc_id"], "score": score})
        scored.sort(key=lambda e: (-e["score"], e["chunk_id"]))
        return scored[:top_k]


def evaluate_ranker(index, questions):
    """Top-1 and recall@3 (by chunk document) on the evidence questions."""
    ev = [q for q in questions if q["gold_doc"] != "NONE"]
    top1 = rec3 = 0
    for q in ev:
        docs = [e["doc_id"] for e in index.retrieve_chunks(q["question"], top_k=3)]
        top1 += docs[0] == q["gold_doc"]
        rec3 += q["gold_doc"] in docs
    return {"evidence_questions": len(ev), "top1_correct": top1, "recall_at_3_correct": rec3}


def chunk_sweep(docs, questions, grid):
    """Build evaluation at each (chunk_size, overlap); invalid pairs skipped."""
    rows = []
    for size, overlap in grid:
        if overlap >= size:
            continue
        s = evaluate(ChunkIndex(docs, size, overlap), questions)["summary"]
        rows.append({"chunk_size": size, "overlap": overlap, "chunks": s["chunks"],
                     "top1_correct": s["top1_correct"],
                     "chunk_recall_at_3_correct": s["chunk_recall_at_3_correct"],
                     "sentence_correct": s["sentence_correct"],
                     "refusal_true_positive": s["refusal_true_positive"],
                     "refusal_false_positive": s["refusal_false_positive"]})
    return rows


def hard_questions():
    """16 harder questions written for this check (2026-11-07).

    Paraphrases avoid the document's own wording where possible;
    distractors share words with the corpus but have no answer in it.
    """
    para = [
        ("HQ01", "How frequently should I irrigate plants when it is hot and dry?", "B01"),
        ("HQ02", "How do I sharpen a blunt blade?", "B09"),
        ("HQ03", "Why does my bike brake drag on the rim?", "B04"),
        ("HQ04", "How long should an espresso pull last?", "B17"),
        ("HQ05", "What keeps my internet connection secure from neighbours?", "B06"),
        ("HQ06", "How do I unclog a sink?", "B23"),
        ("HQ07", "When should the automobile battery be checked?", "B11"),
        ("HQ08", "How do I keep my canine from chewing the sofa?", "B20"),
        ("HQ09", "How do I stop black clothes losing colour?", "B19"),
        ("HQ10", "Where should I store coffee so it stays fresh?", "B17"),
    ]
    distract = [
        ("HQ11", "How much water should a dog drink in summer?"),
        ("HQ12", "Which weekly train runs from the garden centre?"),
        ("HQ13", "What password protects the tax clinic portal?"),
        ("HQ14", "Why does the fish tank heater keep tripping the fuse?"),
        ("HQ15", "Which coffee filter fits an aquarium pump?"),
        ("HQ16", "What telescope is best for photographing birds in daylight?"),
    ]
    out = [{"id": i, "question": q, "gold_doc": d, "kind": "synonym_paraphrase"} for i, q, d in para]
    out += [{"id": i, "question": q, "gold_doc": "NONE", "kind": "cross_topic_distractor"} for i, q in distract]
    return out


def evaluate_hard(index, questions):
    """Per question outcome on the hard set with the Build pipeline."""
    rows = []
    for q in questions:
        res = index.answer(q["question"])
        top = index.retrieve_chunks(q["question"], top_k=1)[0]
        if q["gold_doc"] == "NONE":
            ok = res["refused"]
        else:
            ok = (not res["refused"]) and res["doc_id"] == q["gold_doc"]
        rows.append({"id": q["id"], "kind": q["kind"], "question": q["question"],
                     "gold_doc": q["gold_doc"], "top1_doc": top["doc_id"],
                     "top1_score": top["score"], "refused": res["refused"], "correct": ok})
    para = [r for r in rows if r["kind"] == "synonym_paraphrase"]
    dis = [r for r in rows if r["kind"] == "cross_topic_distractor"]
    return {"rows": rows, "threshold": REFUSAL_THRESHOLD,
            "paraphrase_questions": len(para),
            "paraphrase_answered_correctly": sum(r["correct"] for r in para),
            "paraphrase_top1_correct": sum(r["top1_doc"] == r["gold_doc"] for r in para),
            "paraphrase_refused": sum(r["refused"] for r in para),
            "distractor_questions": len(dis),
            "distractor_refused": sum(r["refused"] for r in dis)}


def replicate(docs, factor):
    """The corpus copied factor times, each copy with new document ids."""
    out = []
    for k in range(factor):
        for d in docs:
            out.append({"id": d["id"] if k == 0 else "%sx%d" % (d["id"], k + 1),
                        "title": d["title"], "sentences": list(d["sentences"])})
    return out


def scaling_curve(docs, questions, factors):
    """Wall clock index build and mean answer latency per corpus size."""
    rows = []
    for factor in factors:
        corpus = replicate(docs, factor)
        start = time.perf_counter()
        index = ChunkIndex(corpus)
        build_ms = (time.perf_counter() - start) * 1000.0
        start = time.perf_counter()
        for q in questions:
            index.answer(q["question"])
        answer_ms = (time.perf_counter() - start) * 1000.0 / len(questions)
        rows.append({"factor": factor, "documents": len(corpus), "chunks": len(index.chunks),
                     "index_build_ms": build_ms, "answer_latency_ms_mean": answer_ms})
    return rows
