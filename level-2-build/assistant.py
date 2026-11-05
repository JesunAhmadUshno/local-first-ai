"""Local-first assistant pipeline, Level 2 Build.

End to end, fully offline, standard library only: ingest a
directory of local text documents, chunk them into overlapping
word chunks, index the chunks with TF-IDF reused from the Learn
level, answer questions with multi-sentence extractive answers
carrying a citation per sentence, refuse when retrieval is below
a named threshold, and keep a persistent JSON session memory.

Honest scope: there is no Ollama and no language model in this
level. Ollama was checked on 2026-11-05 and is not available on
the machine this was built on (see BUILD-SPEC.md). The assistant
core is extractive: answer sentences are copied word for word
from the retrieved document. The corpus is synthetic data files
committed in the data folder, standing in for a private folder.
No call leaves the machine: this module imports only local file,
text, math, and data helpers, and a test enforces that.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEARN_DIR = os.path.join(os.path.dirname(HERE), "level-1-learn")
sys.path.insert(0, LEARN_DIR)
from local_first import (  # noqa: E402
    LocalFirstError,
    audit_sources,
    compute_idf,
    cosine,
    document_inventory,
    tfidf_vector,
)

CHUNK_SIZE_WORDS = 30
CHUNK_OVERLAP_WORDS = 10
REFUSAL_THRESHOLD = 0.30
ANSWER_SENTENCES = 2
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]")


class BuildError(LocalFirstError):
    """Named error for Build level failures."""


def split_sentences(text):
    """Split text into sentences, keeping the ending punctuation."""
    if not isinstance(text, str):
        raise BuildError("text must be a string")
    return [s.strip() for s in SENTENCE_RE.findall(text) if s.strip()]


def ingest_directory(data_dir):
    """Read every .txt document in a local directory, sorted by name.

    The first line of each file is 'Title: <title>'. The document
    id is the file name without the .txt suffix. The remaining
    text is split into sentences. Returns Learn style documents.
    """
    if not os.path.isdir(data_dir):
        raise BuildError("data directory not found: " + str(data_dir))
    names = sorted(n for n in os.listdir(data_dir) if n.endswith(".txt"))
    if not names:
        raise BuildError("no .txt documents in: " + str(data_dir))
    docs = []
    for name in names:
        with open(os.path.join(data_dir, name), encoding="utf-8") as f:
            raw = f.read()
        lines = raw.splitlines()
        if not lines or not lines[0].startswith("Title: "):
            raise BuildError(name + ": first line must be 'Title: <title>'")
        title = lines[0][len("Title: "):].strip()
        body = " ".join(line.strip() for line in lines[1:] if line.strip())
        sentences = split_sentences(body)
        if not title or not sentences:
            raise BuildError(name + ": title and sentences are required")
        docs.append({"id": name[:-len(".txt")], "title": title,
                     "sentences": sentences})
    return docs


def chunk_document(doc, chunk_size=CHUNK_SIZE_WORDS,
                   overlap=CHUNK_OVERLAP_WORDS):
    """Split one document into overlapping word chunks.

    Words are the whitespace split of the full document text.
    Chunk n covers words [start, start + chunk_size), and the
    next chunk starts chunk_size minus overlap words later.
    The last chunk may be shorter. Each chunk records its word
    offsets so a reader can find the exact span in the document.
    """
    if not isinstance(chunk_size, int) or chunk_size < 1:
        raise BuildError("chunk_size must be a positive integer")
    if not isinstance(overlap, int) or overlap < 0 or overlap >= chunk_size:
        raise BuildError("overlap must be an integer in [0, chunk_size)")
    words = " ".join(doc["sentences"]).split()
    step = chunk_size - overlap
    chunks = []
    start = 0
    index = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append({
            "chunk_id": "%s-C%d" % (doc["id"], index + 1),
            "doc_id": doc["id"], "title": doc["title"],
            "chunk_index": index, "start_word": start, "end_word": end,
            "text": " ".join(words[start:end]),
        })
        index += 1
        if end == len(words):
            break
        start += step
    return chunks


def chunk_all(docs, chunk_size=CHUNK_SIZE_WORDS,
              overlap=CHUNK_OVERLAP_WORDS):
    """Chunk every document, preserving document order."""
    chunks = []
    for doc in docs:
        chunks.extend(chunk_document(doc, chunk_size, overlap))
    return chunks


def chunk_as_doc(chunk):
    """A chunk in the shape the Learn TF-IDF helpers expect."""
    return {"id": chunk["chunk_id"], "title": chunk["title"],
            "sentences": [chunk["text"]]}


class ChunkIndex:
    """TF-IDF index over chunks, built with the Learn helpers."""

    def __init__(self, docs, chunk_size=CHUNK_SIZE_WORDS,
                 overlap=CHUNK_OVERLAP_WORDS):
        self.docs = list(docs)
        self.chunks = chunk_all(self.docs, chunk_size, overlap)
        pseudo = [chunk_as_doc(c) for c in self.chunks]
        self.idf = compute_idf(pseudo)
        self.vectors = {c["chunk_id"]: tfidf_vector(c["text"], self.idf)
                        for c in self.chunks}
        self.docs_by_id = {d["id"]: d for d in self.docs}

    def retrieve_chunks(self, question, top_k=3):
        """Ranked chunks for a question, best score first.

        Ties break on chunk id, so ranking is deterministic.
        """
        if not isinstance(top_k, int) or top_k < 1:
            raise BuildError("top_k must be a positive integer")
        query_vec = tfidf_vector(question, self.idf)
        scored = [{"chunk_id": c["chunk_id"], "doc_id": c["doc_id"],
                   "score": cosine(query_vec, self.vectors[c["chunk_id"]])}
                  for c in self.chunks]
        scored.sort(key=lambda e: (-e["score"], e["chunk_id"]))
        return scored[:top_k]

    def best_sentences(self, doc, question, count=ANSWER_SENTENCES):
        """Best distinct sentences inside one document.

        Sentences are scored by cosine against the question with
        the chunk idf. Ties break on the lowest sentence index.
        Returns up to count entries, best first.
        """
        query_vec = tfidf_vector(question, self.idf)
        scored = []
        for idx, sentence in enumerate(doc["sentences"]):
            score = cosine(query_vec, tfidf_vector(sentence, self.idf))
            scored.append({"sentence_id": "S%d" % (idx + 1),
                           "text": sentence, "score": score, "index": idx})
        scored.sort(key=lambda e: (-e["score"], e["index"]))
        return scored[:count]

    def answer(self, question):
        """Answer one question, or refuse below the threshold.

        A refusal states plainly that the local documents hold no
        evidence for the question. An answer carries one entry per
        sentence, each with its own citation, and an answer_text
        that joins each sentence with its citation.
        """
        ranked = self.retrieve_chunks(question, top_k=3)
        best = ranked[0]
        if best["score"] < REFUSAL_THRESHOLD:
            return {"question": question, "refused": True,
                    "reason": "no_evidence_below_threshold",
                    "best_chunk": best["chunk_id"],
                    "best_score": best["score"],
                    "threshold": REFUSAL_THRESHOLD,
                    "cited_doc_ids": [], "sentences": [],
                    "answer_text": "No evidence in the local documents "
                                   "for this question."}
        doc = self.docs_by_id[best["doc_id"]]
        chosen = self.best_sentences(doc, question)
        sentences = []
        for entry in chosen:
            citation = "[%s %s]" % (doc["id"], entry["sentence_id"])
            sentences.append({"doc_id": doc["id"],
                              "sentence_id": entry["sentence_id"],
                              "text": entry["text"], "score": entry["score"],
                              "citation": citation})
        answer_text = " ".join(s["text"] + " " + s["citation"]
                               for s in sentences)
        return {"question": question, "refused": False,
                "reason": "answered", "best_chunk": best["chunk_id"],
                "best_score": best["score"],
                "threshold": REFUSAL_THRESHOLD,
                "doc_id": doc["id"],
                "cited_doc_ids": sorted({s["doc_id"] for s in sentences}),
                "sentences": sentences, "answer_text": answer_text}


class Session:
    """Persistent session memory in one local JSON file.

    The file stores one entry per asked question: the question,
    whether it was refused, and the cited document ids. Loading
    an existing file restores its entries, so memory survives
    across runs. A missing file starts empty.
    """

    def __init__(self, path):
        self.path = path
        self.entries = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or not isinstance(
                    data.get("entries"), list):
                raise BuildError("session file has the wrong shape: " + path)
            self.entries = data["entries"]

    def record(self, question, result):
        """Append one answer or refusal and save the file."""
        self.entries.append({
            "question": question, "refused": result["refused"],
            "cited_doc_ids": list(result["cited_doc_ids"]),
        })
        self.save()

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"entries": self.entries}, f, indent=2,
                      sort_keys=True)
            f.write("\n")

    def cited_doc_ids(self):
        """Every cited document id so far, in first seen order."""
        seen = []
        for entry in self.entries:
            for doc_id in entry["cited_doc_ids"]:
                if doc_id not in seen:
                    seen.append(doc_id)
        return seen


def build_questions():
    """The Build labelled set: 24 questions, 20 evidence, 4 none."""
    evidence = [
        ("BQ01", "How often do tomatoes need watering in dry summer weather?", "B01", "S1"),
        ("BQ02", "How many months of living costs does the emergency fund covers in total?", "B02", "S2"),
        ("BQ03", "Which train pass lets me travel between Tokyo and Kyoto?", "B03", "S1"),
        ("BQ04", "Why do the front brake pads rub against the wheel rim?", "B04", "S2"),
        ("BQ05", "What makes the starter rises after feeding with flour?", "B05", "S1"),
        ("BQ06", "Where does the router sits on a shelf away from thick walls?", "B06", "S1"),
        ("BQ07", "What morning stretches loosen stiff shoulders and hips?", "B07", "S1"),
        ("BQ08", "How does a tripod steadies the camera during long exposures?", "B08", "S1"),
        ("BQ09", "What whetstone sharpens a dull kitchen knife at a steady angle?", "B09", "S1"),
        ("BQ10", "Why do yellow leaves signal overwatering in indoor houseplants?", "B10", "S3"),
        ("BQ11", "When is the car battery tested before the first hard frost?", "B11", "S2"),
        ("BQ12", "What primer coat helps new paint adhere to patched drywall?", "B12", "S2"),
        ("BQ13", "How is water filtered or boiled before drinking from mountain streams?", "B13", "S3"),
        ("BQ14", "What notice of assessment confirms the tax return was processed?", "B14", "S3"),
        ("BQ15", "What bandages antiseptic and sterile gauze pads does the kit holds?", "B15", "S1"),
        ("BQ16", "What filter cycles beneficial bacteria that break down fish waste?", "B16", "S2"),
        ("BQ17", "When are fresh coffee beans ground just before brewing for aroma?", "B17", "S1"),
        ("BQ18", "What checksum verifies a copied file matches the original exactly?", "B18", "S6"),
        ("BQ19", "How does cold water washing protects dark fabrics from fading?", "B19", "S1"),
        ("BQ20", "What metronome keeps tempo steady during difficult passage practice?", "B21", "S2"),
    ]
    questions = [{"id": qid, "question": q, "gold_doc": doc,
                  "gold_sentence": sent} for qid, q, doc, sent in evidence]
    questions += [
        {"id": "BQ21", "question": "How do I renew a passport for travel abroad?",
         "gold_doc": "NONE", "gold_sentence": "NONE"},
        {"id": "BQ22", "question": "What is the best treatment for a migraine headache?",
         "gold_doc": "NONE", "gold_sentence": "NONE"},
        {"id": "BQ23", "question": "How much does a flight to Paris cost this year?",
         "gold_doc": "NONE", "gold_sentence": "NONE"},
        {"id": "BQ24", "question": "What is the capital of Norway and its population?",
         "gold_doc": "NONE", "gold_sentence": "NONE"},
    ]
    return questions


def evaluate(index, questions):
    """Run the labelled set and score retrieval, answers, refusal.

    Evidence metrics use the 20 evidence questions. Refusal
    precision and recall use all 24, with refusal as the positive
    class and no-evidence as the positive truth.
    """
    rows = []
    for item in questions:
        ranked = index.retrieve_chunks(item["question"], top_k=3)
        top_docs = [e["doc_id"] for e in ranked]
        result = index.answer(item["question"])
        is_evidence = item["gold_doc"] != "NONE"
        rows.append({
            "question_id": item["id"], "question": item["question"],
            "gold_doc": item["gold_doc"],
            "gold_sentence": item["gold_sentence"],
            "is_evidence": is_evidence,
            "top1_doc": top_docs[0], "top3_chunk_docs": top_docs,
            "top1_score": ranked[0]["score"],
            "hit_at_1": is_evidence and top_docs[0] == item["gold_doc"],
            "chunk_hit_at_3": is_evidence and item["gold_doc"] in top_docs,
            "refused": result["refused"],
            "answer_doc": result.get("doc_id"),
            "answer_sentence": (result["sentences"][0]["sentence_id"]
                                if result["sentences"] else None),
            "sentence_correct": bool(
                is_evidence and result["sentences"]
                and result["sentences"][0]["sentence_id"] == item["gold_sentence"]
                and result["sentences"][0]["doc_id"] == item["gold_doc"]),
            "answer_text": result["answer_text"],
        })
    ev = [r for r in rows if r["is_evidence"]]
    tp = sum(1 for r in rows if r["refused"] and not r["is_evidence"])
    fp = sum(1 for r in rows if r["refused"] and r["is_evidence"])
    fn = sum(1 for r in rows if not r["refused"] and not r["is_evidence"])
    summary = {
        "documents": len(index.docs), "chunks": len(index.chunks),
        "questions": len(rows), "evidence_questions": len(ev),
        "no_evidence_questions": len(rows) - len(ev),
        "top1_correct": sum(1 for r in ev if r["hit_at_1"]),
        "chunk_recall_at_3_correct": sum(1 for r in ev if r["chunk_hit_at_3"]),
        "sentence_correct": sum(1 for r in ev if r["sentence_correct"]),
        "refusal_true_positive": tp, "refusal_false_positive": fp,
        "refusal_false_negative": fn,
        "threshold": REFUSAL_THRESHOLD,
    }
    summary["top1_accuracy"] = summary["top1_correct"] / len(ev)
    summary["chunk_recall_at_3"] = summary["chunk_recall_at_3_correct"] / len(ev)
    summary["sentence_accuracy"] = summary["sentence_correct"] / len(ev)
    summary["refusal_precision"] = tp / (tp + fp) if (tp + fp) else 0.0
    summary["refusal_recall"] = tp / (tp + fn) if (tp + fn) else 0.0
    return {"questions": rows, "summary": summary}


def corpus_inventory(docs):
    """Per document inventory with sha256, from the Learn helper."""
    return document_inventory(docs)


def corpus_fingerprint(docs):
    """One sha256 over the sorted per document hashes."""
    hashes = sorted(r["sha256"] for r in document_inventory(docs))
    return hashlib.sha256("\n".join(hashes).encode("utf-8")).hexdigest()


def audit_build_sources(source_texts):
    """Privacy scan over Build sources, reusing the Learn audit."""
    return audit_sources(source_texts)
