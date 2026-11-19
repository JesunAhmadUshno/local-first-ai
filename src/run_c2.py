"""C2 confirmatory run (DECISIONS 0004 lock, 0005 registration).

A local 7B to 8B instruction model (Ollama) answers the 20
Build evidence questions from the same top 3 chunks the
offline core retrieves, and cites the single chunk that
supports its answer. This script only generates and records;
grading happens in a separate blind pass from
results/c2_blind_grading.json, which carries no gold labels.

Run: python src/run_c2.py
Writes results/results_c2.json and results/c2_blind_grading.json.
Standard library only.
"""
import json
import os
import platform
import random
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from assistant import ChunkIndex, build_questions, ingest_directory  # noqa: E402

MODEL = "llama3.1:8b"
SEED = 20261117
OLLAMA = "http://localhost:11434"
INSTRUCTION = ("Answer the question using only the context below. "
               "Cite the source for each fact. If the context does "
               "not contain the answer, say you do not know.")
CLOSING = ("Answer briefly, using only the context above. End your "
           "answer with a line of the form \"Citation: \" followed "
           "by the single chunk id that supports your answer.")
STOPWORDS = set("""a an the is are was were be been of to in on for
with by at from as it its this that these those and or but if then
so such into about above below during before after how what when
where why which who whom do does did can could should would may
might must shall will you your yours i we they he she them his
her their our my me him us not no yes only just also very""".split())


def http_json(url, payload=None, timeout=600):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_prompt(ranked, chunk_texts, question):
    parts = [INSTRUCTION, "Context:"]
    for entry in ranked:
        parts.append("[%s]\n%s" % (entry["chunk_id"],
                                   chunk_texts[entry["chunk_id"]]))
    parts.append("Question: " + question)
    parts.append(CLOSING)
    return "\n".join(parts)


def parse_citation(answer, valid_ids):
    """First valid chunk id named in the answer's Citation line."""
    cite_lines = [ln for ln in answer.splitlines()
                  if "citation" in ln.lower()]
    if not cite_lines:
        return None
    line = cite_lines[-1]
    hits = [(line.find(cid), cid) for cid in valid_ids if cid in line]
    hits = [(pos, cid) for pos, cid in hits if pos >= 0]
    if not hits:
        return None
    hits.sort()
    return hits[0][1]


def content_tokens(text):
    toks = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in toks if t not in STOPWORDS and len(t) > 2}


def main():
    version = http_json(OLLAMA + "/api/version")
    tags = http_json(OLLAMA + "/api/tags")
    digest = None
    for m in tags.get("models", []):
        if m.get("name", "").startswith(MODEL):
            digest = m.get("digest")
    docs = ingest_directory(os.path.join(ROOT, "experiments", "corpus"))
    index = ChunkIndex(docs)
    chunk_texts = {c["chunk_id"]: c["text"] for c in index.chunks}
    questions = [q for q in build_questions()
                 if q["gold_doc"] != "NONE"]
    print("evidence questions: %d" % len(questions), flush=True)

    rng = random.Random(SEED)
    codes = ["G%02d" % (i + 1) for i in range(len(questions))]
    rng.shuffle(codes)

    rows = []
    grading = []
    for item, code in zip(questions, codes):
        ranked = index.retrieve_chunks(item["question"], top_k=3)
        prompt = build_prompt(ranked, chunk_texts, item["question"])
        payload = {"model": MODEL,
                   "messages": [{"role": "user", "content": prompt}],
                   "stream": False,
                   "options": {"temperature": 0, "seed": SEED}}
        t0 = time.perf_counter()
        resp = http_json(OLLAMA + "/api/chat", payload)
        latency = time.perf_counter() - t0
        answer = resp.get("message", {}).get("content", "")
        valid_ids = [e["chunk_id"] for e in ranked]
        cited = parse_citation(answer, valid_ids)
        overlap = None
        if cited is not None:
            at = content_tokens(answer)
            ct = content_tokens(chunk_texts[cited])
            overlap = (len(at & ct) / len(at)) if at else 0.0
            grading.append({"code": code, "answer": answer,
                            "cited_chunk_text": chunk_texts[cited]})
        rows.append({
            "question_id": item["id"],
            "question": item["question"],
            "gold_doc": item["gold_doc"],
            "gold_sentence": item["gold_sentence"],
            "top3": [{"chunk_id": e["chunk_id"], "doc_id": e["doc_id"],
                      "score": e["score"]} for e in ranked],
            "prompt": prompt,
            "answer": answer,
            "latency_s": round(latency, 3),
            "eval_count": resp.get("eval_count"),
            "cited_chunk_id": cited,
            "answer_token_overlap_with_cited_chunk": overlap,
            "blind_code": code,
        })
        print("%s: cited=%s latency=%.1fs" % (item["id"],
                                              cited, latency),
              flush=True)

    rng.shuffle(grading)
    record = {
        "study": "C2 confirmatory run (decisions 0004 and 0005)",
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "machine": platform.node(),
        "ollama_version": version.get("version"),
        "model": MODEL,
        "model_digest": digest,
        "options": {"temperature": 0, "seed": SEED},
        "n_evidence_questions": len(rows),
        "questions": rows,
    }
    out = os.path.join(ROOT, "results", "results_c2.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, sort_keys=True)
        f.write("\n")
    gout = os.path.join(ROOT, "results", "c2_blind_grading.json")
    with open(gout, "w", encoding="utf-8") as f:
        json.dump({"items": grading}, f, indent=2, sort_keys=True)
        f.write("\n")
    n_cited = sum(1 for r in rows if r["cited_chunk_id"] is not None)
    print("wrote %s and %s; cited %d/%d" % (out, gout, n_cited,
                                           len(rows)), flush=True)


if __name__ == "__main__":
    main()
