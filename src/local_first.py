"""Local-first assistant core, Level 1 Learn.

A small set of synthetic private-style documents lives in code as
local data. An index is built over them with TF-IDF weighting,
questions retrieve the best document, and an extractive answer
returns one sentence from that document with a citation.

Everything runs locally with the Python standard library only.
No network call is made, no real private file is read, and no
model is loaded. The documents are synthetic. There is no Ollama
and no real LLM in this level: those are Build level scope.

A privacy audit supports the design claim. It inventories every
document with a hash, and it scans this level's own source files
for network call patterns and reports the count per pattern.
Only the standard library is used.
"""
import hashlib
import math
import re
from collections import Counter

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for",
    "with", "without", "before", "after", "over", "between",
    "during", "until", "away", "from", "is", "are", "it", "its",
    "let", "how", "what", "does", "do", "should", "be",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")


class LocalFirstError(Exception):
    """Named error for invalid documents and questions."""


def tokenize(text):
    """Lowercase tokens with stopwords removed, order kept."""
    if not isinstance(text, str):
        raise LocalFirstError("text must be a string")
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


def document_text(doc):
    """One document as a single string: its sentences joined by spaces."""
    return " ".join(doc["sentences"])


def validate_documents(docs):
    """Check ids, titles, and sentence lists."""
    ids = set()
    for doc in docs:
        did = doc.get("id")
        if not isinstance(did, str) or not did:
            raise LocalFirstError("every document needs a non-empty string id")
        if did in ids:
            raise LocalFirstError("duplicate document id: '" + did + "'")
        ids.add(did)
        if not isinstance(doc.get("title"), str) or not doc["title"]:
            raise LocalFirstError("document '" + did + "': title must be a non-empty string")
        sentences = doc.get("sentences")
        if not isinstance(sentences, list) or not sentences:
            raise LocalFirstError("document '" + did + "': sentences must be a non-empty list")
        for sentence in sentences:
            if not isinstance(sentence, str) or not sentence:
                raise LocalFirstError(
                    "document '" + did + "': every sentence must be a non-empty string")
            if not tokenize(sentence):
                raise LocalFirstError(
                    "document '" + did + "': a sentence has no content tokens")
    return ids


def compute_idf(docs):
    """Smoothed idf per term: log((1 + N) / (1 + df)) + 1."""
    validate_documents(docs)
    n = len(docs)
    df = Counter()
    for doc in docs:
        for term in set(tokenize(document_text(doc))):
            df[term] += 1
    return {term: math.log((1 + n) / (1 + count)) + 1.0
            for term, count in df.items()}


def tfidf_vector(text, idf):
    """TF-IDF vector as a dict: (count / total tokens) times idf.

    Terms missing from idf are skipped. An empty token list gives
    an empty vector.
    """
    tokens = tokenize(text)
    if not tokens:
        return {}
    counts = Counter(tokens)
    total = len(tokens)
    return {term: (count / total) * idf[term]
            for term, count in counts.items() if term in idf}


def cosine(vec_a, vec_b):
    """Cosine similarity of two sparse vectors. Zero norm gives 0.0."""
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(value * vec_b.get(term, 0.0) for term, value in vec_a.items())
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class LocalIndex:
    """TF-IDF index over a fixed local document set."""

    def __init__(self, docs):
        validate_documents(docs)
        self.docs = list(docs)
        self.idf = compute_idf(docs)
        self.vectors = {doc["id"]: tfidf_vector(document_text(doc), self.idf)
                        for doc in docs}

    def retrieve(self, question, top_k=3):
        """Ranked documents for a question: best score first.

        Ties break on document id, so ranking is deterministic.
        Each entry has doc_id, title, and a rounded-free float score.
        """
        if not isinstance(top_k, int) or top_k < 1:
            raise LocalFirstError("top_k must be a positive integer")
        query_vec = tfidf_vector(question, self.idf)
        scored = [{"doc_id": doc["id"], "title": doc["title"],
                   "score": cosine(query_vec, self.vectors[doc["id"]])}
                  for doc in self.docs]
        scored.sort(key=lambda entry: (-entry["score"], entry["doc_id"]))
        return scored[:top_k]

    def best_sentence(self, doc, question):
        """Best sentence inside one document for a question.

        Sentences are scored by cosine against the question, using
        the corpus idf. Ties break on the lowest sentence index.
        Returns the sentence id (for example S2), its text, and score.
        """
        query_vec = tfidf_vector(question, self.idf)
        best = None
        for idx, sentence in enumerate(doc["sentences"]):
            score = cosine(query_vec, tfidf_vector(sentence, self.idf))
            key = (-score, idx)
            if best is None or key < best[0]:
                best = (key, idx, sentence, score)
        _, idx, sentence, score = best
        return {"sentence_id": "S%d" % (idx + 1), "text": sentence, "score": score}

    def answer(self, question):
        """Extractive answer: one cited sentence from the top document.

        The answer text is copied word for word from the document.
        The citation names the document and the sentence, for
        example [D01 S1]. Nothing is generated.
        """
        top = self.retrieve(question, top_k=1)[0]
        doc = next(d for d in self.docs if d["id"] == top["doc_id"])
        chosen = self.best_sentence(doc, question)
        citation = "[%s %s]" % (doc["id"], chosen["sentence_id"])
        return {"doc_id": doc["id"], "title": doc["title"],
                "doc_score": top["score"],
                "sentence_id": chosen["sentence_id"],
                "sentence_score": chosen["score"],
                "sentence": chosen["text"], "citation": citation,
                "answer_text": chosen["text"] + " " + citation}


def document_inventory(docs):
    """Inventory rows: counts and a sha256 hash per document.

    The hash is over the document text (sentences joined by one
    space), encoded as UTF-8. It proves which exact synthetic
    text was indexed, without exposing any real file.
    """
    validate_documents(docs)
    rows = []
    for doc in docs:
        text = document_text(doc)
        rows.append({
            "doc_id": doc["id"], "title": doc["title"],
            "sentences": len(doc["sentences"]),
            "words": len(text.split()),
            "chars": len(text),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        })
    return rows


def forbidden_patterns():
    """Network pattern names, built from fragments on purpose.

    The audit scans source text for these strings. Building each
    name from two fragments keeps the audit code itself free of
    the literal strings, so the scan does not flag its own list.
    """
    fragments = [("sock", "et"), ("url", "lib"), ("req", "uests"),
                 ("url", "open"), ("http", ".client"),
                 ("ft", "plib"), ("sm", "tplib")]
    return [left + right for left, right in fragments]


def audit_sources(source_texts):
    """Count forbidden network patterns in named source texts.

    source_texts maps a file name to its full text. Returns one
    row per pattern with its total count, the grand total, and
    whether the audit passed (total is zero).
    """
    rows = []
    for pattern in forbidden_patterns():
        count = sum(text.count(pattern) for text in source_texts.values())
        rows.append({"pattern": pattern, "count": count})
    total = sum(row["count"] for row in rows)
    return {"patterns": rows, "total_matches": total,
            "files_scanned": sorted(source_texts),
            "passed": total == 0, "local_only": total == 0}


def build_documents():
    """The Learn corpus: 8 synthetic documents, 3 sentences each."""
    return [
        {"id": "D01", "title": "garden notes", "sentences": [
            "Tomatoes need full sun and weekly watering.",
            "Basil grows beside tomatoes and helps repel garden pests.",
            "Compost feeds the soil before spring planting."]},
        {"id": "D02", "title": "home budget", "sentences": [
            "The monthly budget lists rent and grocery spending.",
            "The emergency fund covers three months of living costs.",
            "Receipts stay in a folder for tax records."]},
        {"id": "D03", "title": "japan trip plan", "sentences": [
            "The train pass covers travel between Tokyo and Kyoto.",
            "A small suitcase fits the hotel luggage rack.",
            "The museum opens early on quiet weekday mornings."]},
        {"id": "D04", "title": "bicycle repair log", "sentences": [
            "A loose chain needs cleaning and fresh lubricant.",
            "The front brake pads rub against the wheel rim.",
            "Tyre pressure is checked before every long ride."]},
        {"id": "D05", "title": "sourdough journal", "sentences": [
            "The starter rises after feeding with flour and water.",
            "Dough rests covered until it doubles in size.",
            "The loaf bakes in a hot oven until golden."]},
        {"id": "D06", "title": "home network notes", "sentences": [
            "The router sits on a shelf away from thick walls.",
            "A strong password protects the home wifi signal.",
            "Firmware updates fix bugs and close security gaps."]},
        {"id": "D07", "title": "exercise routine", "sentences": [
            "Morning stretches loosen stiff shoulders and hips.",
            "The weekly run builds stamina over flat routes.",
            "Rest days let tired muscles recover and grow."]},
        {"id": "D08", "title": "photography notes", "sentences": [
            "A tripod steadies the camera during long exposures.",
            "Soft window light flatters portraits without flash.",
            "Raw files keep more detail for careful editing."]},
    ]


def build_questions():
    """The labelled set: 10 questions with gold document and sentence."""
    return [
        {"id": "Q01", "question": "tomatoes weekly watering sun",
         "gold_doc": "D01", "gold_sentence": "S1"},
        {"id": "Q02", "question": "emergency fund covers three months living costs",
         "gold_doc": "D02", "gold_sentence": "S2"},
        {"id": "Q03", "question": "train pass travel Tokyo Kyoto",
         "gold_doc": "D03", "gold_sentence": "S1"},
        {"id": "Q04", "question": "chain cleaning fresh lubricant",
         "gold_doc": "D04", "gold_sentence": "S1"},
        {"id": "Q05", "question": "starter rises feeding flour",
         "gold_doc": "D05", "gold_sentence": "S1"},
        {"id": "Q06", "question": "router shelf thick walls",
         "gold_doc": "D06", "gold_sentence": "S1"},
        {"id": "Q07", "question": "morning stretches shoulders hips",
         "gold_doc": "D07", "gold_sentence": "S1"},
        {"id": "Q08", "question": "tripod camera long exposures",
         "gold_doc": "D08", "gold_sentence": "S1"},
        {"id": "Q09", "question": "compost soil spring planting",
         "gold_doc": "D01", "gold_sentence": "S3"},
        {"id": "Q10", "question": "brake pads wheel rim",
         "gold_doc": "D04", "gold_sentence": "S2"},
    ]


def evaluate(index, questions):
    """Run every labelled question and score the retrieval.

    Top-1 accuracy is the share whose first retrieved document is
    the gold document. Recall at 3 is the share whose gold document
    appears anywhere in the top 3. Sentence accuracy is the share
    whose chosen answer sentence is the gold sentence, counted
    only as an answer measure, on the top retrieved document.
    """
    rows = []
    for item in questions:
        ranked = index.retrieve(item["question"], top_k=3)
        top_ids = [entry["doc_id"] for entry in ranked]
        result = index.answer(item["question"])
        rows.append({
            "question_id": item["id"], "question": item["question"],
            "gold_doc": item["gold_doc"], "gold_sentence": item["gold_sentence"],
            "top1_doc": top_ids[0], "top3_docs": top_ids,
            "top1_score": ranked[0]["score"],
            "hit_at_1": top_ids[0] == item["gold_doc"],
            "hit_at_3": item["gold_doc"] in top_ids,
            "answer_doc": result["doc_id"],
            "answer_sentence": result["sentence_id"],
            "sentence_correct": result["sentence_id"] == item["gold_sentence"]
            and result["doc_id"] == item["gold_doc"],
            "answer_text": result["answer_text"],
        })
    total = len(rows)
    summary = {
        "documents": len(index.docs),
        "questions": total,
        "top1_correct": sum(1 for r in rows if r["hit_at_1"]),
        "recall_at_3_correct": sum(1 for r in rows if r["hit_at_3"]),
        "sentence_correct": sum(1 for r in rows if r["sentence_correct"]),
    }
    summary["top1_accuracy"] = summary["top1_correct"] / total
    summary["recall_at_3"] = summary["recall_at_3_correct"] / total
    summary["sentence_accuracy"] = summary["sentence_correct"] / total
    return {"questions": rows, "summary": summary}
