"""Run the Build evaluation and write deterministic results.

Run: python level-2-build/run_build.py
Writes level-2-build/results_build.json. No timestamps, no
randomness, no wall clock values, so two runs produce an
identical file. The run also exercises the session memory: it
records three questions into a fresh session file, reloads the
file in a new Session object, and reports the reload check.
The privacy audit reads every Python source file in this level
and scans it for the network patterns defined in Learn.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from assistant import (  # noqa: E402
    ChunkIndex, Session, audit_build_sources, build_questions,
    corpus_fingerprint, corpus_inventory, evaluate, ingest_directory,
)

SOURCE_FILES = ("assistant.py", "run_build.py")


def main():
    docs = ingest_directory(os.path.join(HERE, "data"))
    index = ChunkIndex(docs)
    inventory = corpus_inventory(docs)
    result = evaluate(index, build_questions())
    source_texts = {}
    for name in SOURCE_FILES:
        with open(os.path.join(HERE, name), encoding="utf-8") as f:
            source_texts[name] = f.read()
    audit = audit_build_sources(source_texts)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "session_memory.json")
        session = Session(path)
        demo = ["How often do tomatoes need watering in dry summer weather?",
                "What is the capital of Norway and its population?",
                "What checksum verifies a copied file matches the original exactly?"]
        for question in demo:
            session.record(question, index.answer(question))
        reloaded = Session(path)
        session_check = {
            "entries_recorded": len(session.entries),
            "entries_after_reload": len(reloaded.entries),
            "reload_matches": reloaded.entries == session.entries,
            "cited_doc_ids": reloaded.cited_doc_ids(),
            "refused_count": sum(1 for e in reloaded.entries if e["refused"]),
        }
    for row in result["questions"]:
        print(f"{row['question_id']}: gold={row['gold_doc']} top1={row['top1_doc']} "
              f"score={row['top1_score']:.4f} hit1={row['hit_at_1']} "
              f"chunk3={row['chunk_hit_at_3']} refused={row['refused']} "
              f"sentence_ok={row['sentence_correct']}")
    s = result["summary"]
    print(f"Summary: {s['documents']} documents, {s['chunks']} chunks, "
          f"{s['questions']} questions; top1 {s['top1_correct']}/"
          f"{s['evidence_questions']} = {s['top1_accuracy']}; chunk recall@3 "
          f"{s['chunk_recall_at_3_correct']}/{s['evidence_questions']} = "
          f"{s['chunk_recall_at_3']}; sentence {s['sentence_correct']}/"
          f"{s['evidence_questions']} = {s['sentence_accuracy']}; refusal "
          f"precision {s['refusal_precision']}, recall {s['refusal_recall']}; "
          f"audit passed={audit['passed']} total={audit['total_matches']}; "
          f"session reload={session_check['reload_matches']}")
    out = {"scenario": "local-first assistant pipeline, 24 synthetic documents "
                       "ingested from local files, overlapping word chunks, "
                       "TF-IDF chunk index, multi-sentence extractive cited "
                       "answers, threshold refusal, persistent session memory, "
                       "privacy audit, no language model",
           "summary": s, "questions": result["questions"],
           "inventory": inventory,
           "corpus_fingerprint_sha256": corpus_fingerprint(docs),
           "audit": audit, "session_check": session_check}
    path = os.path.join(HERE, "results_build.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("Wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
