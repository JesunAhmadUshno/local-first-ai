"""Unit tests for the Level 2 Build local-first pipeline.

Hand-computed expectations for chunking and chunk IDF, plus
refusal, session persistence, ingest, and privacy guard tests.
"""
import hashlib
import json
import math
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from assistant import (  # noqa: E402
    ANSWER_SENTENCES,
    CHUNK_OVERLAP_WORDS,
    CHUNK_SIZE_WORDS,
    REFUSAL_THRESHOLD,
    BuildError,
    ChunkIndex,
    Session,
    audit_build_sources,
    build_questions,
    chunk_document,
    corpus_fingerprint,
    corpus_inventory,
    evaluate,
    ingest_directory,
    split_sentences,
)

DATA = os.path.join(ROOT, "experiments", "corpus")


class TestChunkingHandComputed(unittest.TestCase):
    def test_chunk_windows_hand_computed(self):
        # Words: one two three four five. / six seven eight nine ten.
        # That is 10 whitespace words. Chunk size 4, overlap 1, so
        # the step is 3. Windows: [0,4), [3,7), [6,10). The last
        # window reaches the end, so chunking stops there: 3 chunks.
        doc = {"id": "T01", "title": "t", "sentences": [
            "one two three four five.", "six seven eight nine ten."]}
        chunks = chunk_document(doc, chunk_size=4, overlap=1)
        self.assertEqual(len(chunks), 3)
        self.assertEqual([(c["start_word"], c["end_word"]) for c in chunks],
                         [(0, 4), (3, 7), (6, 10)])
        self.assertEqual(chunks[0]["text"], "one two three four")
        self.assertEqual(chunks[1]["text"], "four five. six seven")
        self.assertEqual(chunks[2]["text"], "seven eight nine ten.")
        self.assertEqual([c["chunk_id"] for c in chunks],
                         ["T01-C1", "T01-C2", "T01-C3"])

    def test_chunk_overlap_must_be_smaller_than_size(self):
        doc = {"id": "T01", "title": "t", "sentences": ["one two three."]}
        with self.assertRaises(BuildError):
            chunk_document(doc, chunk_size=3, overlap=3)

    def test_named_chunk_constants(self):
        self.assertEqual(CHUNK_SIZE_WORDS, 30)
        self.assertEqual(CHUNK_OVERLAP_WORDS, 10)
        self.assertEqual(REFUSAL_THRESHOLD, 0.30)
        self.assertEqual(ANSWER_SENTENCES, 2)

    def test_real_corpus_chunk_count(self):
        # Each of the 24 documents has 58 to 66 words. With size 30
        # and step 20 the windows start at 0, 20, and 40, and the
        # third window reaches the end: 3 chunks per document,
        # 24 times 3 = 72 chunks in total.
        docs = ingest_directory(DATA)
        index = ChunkIndex(docs)
        self.assertEqual(len(index.chunks), 72)

    def test_chunk_idf_hand_computed(self):
        # Two one-chunk documents, so N = 2 chunks. The term cat
        # sits in 1 of 2 chunks, so its smoothed idf is
        # log((1 + 2) / (1 + 1)) + 1 = log(1.5) + 1 = 1.405465108.
        docs = [{"id": "A", "title": "a", "sentences": ["cat sat."]},
                {"id": "B", "title": "b", "sentences": ["dog ran."]}]
        index = ChunkIndex(docs)
        self.assertEqual(len(index.chunks), 2)
        self.assertAlmostEqual(index.idf["cat"], math.log(1.5) + 1.0,
                               places=12)
        self.assertAlmostEqual(index.idf["cat"], 1.405465108, places=9)

    def test_split_sentences(self):
        self.assertEqual(split_sentences("One here. Two there! Three?"),
                         ["One here.", "Two there!", "Three?"])


class TestIngestAndInventory(unittest.TestCase):
    def setUp(self):
        self.docs = ingest_directory(DATA)

    def test_ingest_shape(self):
        self.assertEqual([d["id"] for d in self.docs],
                         ["B%02d" % n for n in range(1, 25)])
        self.assertTrue(all(len(d["sentences"]) == 6 for d in self.docs))
        self.assertEqual(self.docs[0]["title"], "garden notes")

    def test_inventory_totals_hand_summed(self):
        # Words and characters are the sums printed by the runner
        # and re-summed by hand from the inventory rows in the
        # level README: 1,472 words, 9,290 characters, 144 sentences.
        rows = corpus_inventory(self.docs)
        self.assertEqual(sum(r["words"] for r in rows), 1472)
        self.assertEqual(sum(r["chars"] for r in rows), 9290)
        self.assertEqual(sum(r["sentences"] for r in rows), 144)

    def test_inventory_hash_recomputed(self):
        doc = self.docs[0]
        expected = hashlib.sha256(
            " ".join(doc["sentences"]).encode("utf-8")).hexdigest()
        rows = {r["doc_id"]: r for r in corpus_inventory(self.docs)}
        self.assertEqual(rows["B01"]["sha256"], expected)
        self.assertTrue(expected.startswith("ddb9126a1ca4"))

    def test_fingerprint_is_stable(self):
        self.assertEqual(corpus_fingerprint(self.docs),
                         corpus_fingerprint(ingest_directory(DATA)))
        self.assertEqual(len(corpus_fingerprint(self.docs)), 64)

    def test_missing_directory_rejected(self):
        with self.assertRaises(BuildError):
            ingest_directory(os.path.join(DATA, "does-not-exist"))


class TestAnswersAndRefusal(unittest.TestCase):
    def setUp(self):
        self.index = ChunkIndex(ingest_directory(DATA))

    def test_multi_sentence_answer_with_citation_per_sentence(self):
        result = self.index.answer(
            "How often do tomatoes need watering in dry summer weather?")
        self.assertFalse(result["refused"])
        self.assertEqual(len(result["sentences"]), 2)
        self.assertEqual(result["sentences"][0]["citation"], "[B01 S1]")
        for entry in result["sentences"]:
            self.assertIn(entry["citation"], result["answer_text"])
            self.assertIn(entry["text"], result["answer_text"])
        self.assertEqual(result["cited_doc_ids"], ["B01"])

    def test_refusal_for_zero_evidence_question(self):
        result = self.index.answer(
            "What is the capital of Norway and its population?")
        self.assertTrue(result["refused"])
        self.assertEqual(result["best_score"], 0.0)
        self.assertEqual(result["cited_doc_ids"], [])
        self.assertEqual(result["sentences"], [])
        self.assertEqual(result["answer_text"],
                         "No evidence in the local documents for this "
                         "question.")

    def test_refusal_for_single_common_term_question(self):
        # This no-evidence question shares the term travel with the
        # corpus, so its best chunk score is a measured 0.2253,
        # above zero but below the 0.30 threshold: it must refuse.
        result = self.index.answer("How do I renew a passport for travel abroad?")
        self.assertAlmostEqual(result["best_score"], 0.225316109, places=9)
        self.assertLess(result["best_score"], REFUSAL_THRESHOLD)
        self.assertTrue(result["refused"])

    def test_evidence_questions_are_not_refused(self):
        result = evaluate(self.index, build_questions())
        refused_evidence = [r["question_id"] for r in result["questions"]
                            if r["is_evidence"] and r["refused"]]
        self.assertEqual(refused_evidence, [])

    def test_summary_counts(self):
        s = evaluate(self.index, build_questions())["summary"]
        self.assertEqual(s["documents"], 24)
        self.assertEqual(s["chunks"], 72)
        self.assertEqual(s["questions"], 24)
        self.assertEqual(s["evidence_questions"], 20)
        self.assertEqual(s["no_evidence_questions"], 4)
        self.assertEqual(s["top1_correct"], 20)
        self.assertEqual(s["top1_accuracy"], 1.0)
        self.assertEqual(s["chunk_recall_at_3_correct"], 20)
        self.assertEqual(s["sentence_correct"], 20)
        self.assertEqual(s["refusal_true_positive"], 4)
        self.assertEqual(s["refusal_false_positive"], 0)
        self.assertEqual(s["refusal_false_negative"], 0)
        self.assertEqual(s["refusal_precision"], 1.0)
        self.assertEqual(s["refusal_recall"], 1.0)

    def test_determinism(self):
        again = evaluate(ChunkIndex(ingest_directory(DATA)),
                         build_questions())
        first = evaluate(self.index, build_questions())
        self.assertEqual(again, first)


class TestSessionPersistence(unittest.TestCase):
    def test_session_round_trip_through_json_file(self):
        index = ChunkIndex(ingest_directory(DATA))
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "session_memory.json")
            session = Session(path)
            self.assertEqual(session.entries, [])
            session.record("How often do tomatoes need watering in dry "
                           "summer weather?",
                           index.answer("How often do tomatoes need "
                                        "watering in dry summer weather?"))
            session.record("What is the capital of Norway and its population?",
                           index.answer("What is the capital of Norway and "
                                        "its population?"))
            with open(path, encoding="utf-8") as f:
                stored = json.load(f)
            self.assertEqual(len(stored["entries"]), 2)
            self.assertEqual(stored["entries"][0]["cited_doc_ids"], ["B01"])
            self.assertTrue(stored["entries"][1]["refused"])
            reloaded = Session(path)
            self.assertEqual(reloaded.entries, session.entries)
            self.assertEqual(reloaded.cited_doc_ids(), ["B01"])
            reloaded.record(
                "What checksum verifies a copied file matches the original "
                "exactly?",
                index.answer("What checksum verifies a copied file matches "
                             "the original exactly?"))
            third = Session(path)
            self.assertEqual(len(third.entries), 3)
            self.assertEqual(third.cited_doc_ids(), ["B01", "B18"])

    def test_session_rejects_wrong_shape_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(["not", "a", "session"], f)
            with self.assertRaises(BuildError):
                Session(path)


class TestPrivacyGuard(unittest.TestCase):
    def test_pipeline_module_has_no_network_import(self):
        # Pattern names are built from fragments, as in Learn, so
        # this test does not flag its own pattern list.
        fragments = [("sock", "et"), ("url", "lib"), ("req", "uests"),
                     ("url", "open"), ("http", ".client"),
                     ("ft", "plib"), ("sm", "tplib")]
        patterns = [a + b for a, b in fragments]
        path = os.path.join(ROOT, "src", "assistant.py")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for pattern in patterns:
            self.assertEqual(text.count(pattern), 0, pattern)
        import_lines = [line for line in text.splitlines()
                        if line.startswith(("import ", "from "))]
        self.assertTrue(import_lines)
        for line in import_lines:
            for pattern in patterns:
                self.assertNotIn(pattern, line)

    def test_audit_of_all_build_sources_passes(self):
        here = os.path.join(ROOT, "src")
        texts = {}
        for name in ("assistant.py", "run_build.py"):
            with open(os.path.join(here, name), encoding="utf-8") as f:
                texts[name] = f.read()
        audit = audit_build_sources(texts)
        self.assertEqual(audit["files_scanned"],
                         ["assistant.py", "run_build.py"])
        self.assertEqual(audit["total_matches"], 0)
        self.assertTrue(audit["passed"])
        self.assertEqual(len(audit["patterns"]), 7)


if __name__ == "__main__":
    unittest.main()
