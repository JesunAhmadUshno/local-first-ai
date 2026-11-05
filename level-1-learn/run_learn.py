"""Run the Learn evaluation and write deterministic results.

Run: python level-1-learn/run_learn.py
Writes level-1-learn/results_learn.json. No timestamps, no
randomness, no wall clock values, so two runs produce an
identical file. The privacy audit reads this level's own two
source files as local text and scans them for network patterns.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from local_first import (  # noqa: E402
    LocalIndex, audit_sources, build_documents, build_questions,
    document_inventory, evaluate,
)


def main():
    docs = build_documents()
    questions = build_questions()
    index = LocalIndex(docs)
    inventory = document_inventory(docs)
    result = evaluate(index, questions)
    source_texts = {}
    for name in ("local_first.py", "run_learn.py"):
        with open(os.path.join(HERE, name), encoding="utf-8") as f:
            source_texts[name] = f.read()
    audit = audit_sources(source_texts)
    for row in result["questions"]:
        print(f"{row['question_id']}: gold={row['gold_doc']} top1={row['top1_doc']} "
              f"top3={','.join(row['top3_docs'])} hit1={row['hit_at_1']} "
              f"hit3={row['hit_at_3']} answer={row['answer_doc']} "
              f"{row['answer_sentence']} sentence_ok={row['sentence_correct']}")
    s = result["summary"]
    print(f"Summary: {s['documents']} documents, {s['questions']} questions; "
          f"top1 {s['top1_correct']}/{s['questions']} = {s['top1_accuracy']}; "
          f"recall@3 {s['recall_at_3_correct']}/{s['questions']} = {s['recall_at_3']}; "
          f"sentence {s['sentence_correct']}/{s['questions']} = {s['sentence_accuracy']}; "
          f"audit passed={audit['passed']} total_matches={audit['total_matches']}")
    out = {"scenario": "local-first assistant core, 8 synthetic documents, "
                       "10 labelled questions, TF-IDF retrieval, "
                       "extractive cited answers, privacy audit",
           "summary": s, "questions": result["questions"],
           "inventory": inventory, "audit": audit}
    path = os.path.join(HERE, "results_learn.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("Wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
