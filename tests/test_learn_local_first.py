"""Unit tests for the Level 1 Learn local-first core. Hand-computed expectations."""
import hashlib
import math
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from local_first import (  # noqa: E402
    LocalFirstError,
    LocalIndex,
    audit_sources,
    build_documents,
    build_questions,
    compute_idf,
    cosine,
    document_inventory,
    document_text,
    evaluate,
    tfidf_vector,
    tokenize,
)


class TestTokenizeAndIdf(unittest.TestCase):
    def test_tokenize_removes_stopwords_and_punctuation(self):
        # "and" and "the" are stopwords. Case and the full stop go.
        self.assertEqual(
            tokenize("Tomatoes need full sun and weekly watering."),
            ["tomatoes", "need", "full", "sun", "weekly", "watering"])
        self.assertEqual(tokenize("The router sits."), ["router", "sits"])

    def test_tokenize_rejects_non_string(self):
        with self.assertRaises(LocalFirstError):
            tokenize(12)

    def test_idf_term_in_one_of_eight_docs(self):
        # idf = log((1 + 8) / (1 + 1)) + 1 = log(4.5) + 1 = 2.504077397.
        idf = compute_idf(build_documents())
        self.assertAlmostEqual(idf["tomatoes"], math.log(4.5) + 1.0, places=12)
        self.assertAlmostEqual(idf["tomatoes"], 2.504077397, places=9)

    def test_idf_term_in_two_of_eight_docs(self):
        # "covers" is in D02 and D03, and "weekly" is in D01 and D07.
        # idf = log(9 / 3) + 1 = log(3) + 1 = 2.098612289 for both.
        idf = compute_idf(build_documents())
        self.assertAlmostEqual(idf["covers"], math.log(3.0) + 1.0, places=12)
        self.assertAlmostEqual(idf["weekly"], 2.098612289, places=9)

    def test_tfidf_vector_hand_computed(self):
        # Corpus of 2 one-sentence docs. "cat" is in 1 of 2 docs, so
        # its idf is log(3 / 2) + 1 = 1.405465108. In "cat sat cat"
        # the term counts are cat 2 and sat 1 over 3 tokens, so the
        # weights are (2/3) x 1.405465108 = 0.936976739 and
        # (1/3) x 1.405465108 = 0.468488369.
        docs = [{"id": "A", "title": "a", "sentences": ["cat sat cat."]},
                {"id": "B", "title": "b", "sentences": ["dog ran."]}]
        idf = compute_idf(docs)
        vec = tfidf_vector("cat sat cat", idf)
        self.assertAlmostEqual(vec["cat"], 0.936976739, places=9)
        self.assertAlmostEqual(vec["sat"], 0.468488369, places=9)
        self.assertEqual(tfidf_vector("the and", idf), {})

    def test_cosine_hand_computed(self):
        # dot = 3 x 3 = 9. Norms are 5 (3-4-5 triangle) and 3.
        # Cosine = 9 / (5 x 3) = 0.6. A zero vector gives 0.0.
        self.assertAlmostEqual(cosine({"a": 3.0, "b": 4.0}, {"a": 3.0}), 0.6)
        self.assertEqual(cosine({}, {"a": 1.0}), 0.0)
        self.assertAlmostEqual(cosine({"a": 1.0}, {"a": 1.0}), 1.0)


class TestCorpusAndInventory(unittest.TestCase):
    def test_corpus_shape(self):
        docs = build_documents()
        self.assertEqual([d["id"] for d in docs],
                         ["D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08"])
        self.assertTrue(all(len(d["sentences"]) == 3 for d in docs))

    def test_inventory_d01_hand_counted(self):
        # D01 words: sentence 1 has 7, sentence 2 has 9, sentence 3
        # has 7, total 23. Its joined text has 148 characters.
        rows = {r["doc_id"]: r for r in document_inventory(build_documents())}
        row = rows["D01"]
        self.assertEqual(row["sentences"], 3)
        self.assertEqual(row["words"], 23)
        self.assertEqual(row["chars"], 148)
        self.assertEqual(
            row["sha256"],
            "4d7f88db541543f4b31c2eb7c6b35a46dba1538218f559ceb022c913a2a74d81")

    def test_inventory_hash_recomputed(self):
        docs = build_documents()
        expected = hashlib.sha256(
            document_text(docs[1]).encode("utf-8")).hexdigest()
        rows = {r["doc_id"]: r for r in document_inventory(docs)}
        self.assertEqual(rows["D02"]["sha256"], expected)
        self.assertTrue(expected.startswith("b2fbb2b310e4"))

    def test_inventory_totals_hand_counted(self):
        # Words per doc: 23 + 25 + 25 + 25 + 26 + 26 + 23 + 23 = 196.
        # Chars per doc: 148 + 150 + 149 + 146 + 142 + 149 + 144 + 151 = 1179.
        rows = document_inventory(build_documents())
        self.assertEqual(sum(r["words"] for r in rows), 196)
        self.assertEqual(sum(r["chars"] for r in rows), 1179)
        self.assertEqual(sum(r["sentences"] for r in rows), 24)

    def test_duplicate_document_rejected(self):
        docs = build_documents()
        with self.assertRaises(LocalFirstError):
            LocalIndex([docs[0], docs[0]])


class TestRetrievalAndAnswers(unittest.TestCase):
    def setUp(self):
        self.index = LocalIndex(build_documents())
        self.result = evaluate(self.index, build_questions())
        self.by_id = {r["question_id"]: r for r in self.result["questions"]}

    def test_summary_counts(self):
        # All 10 gold documents are top 1, all 10 are in the top 3,
        # and all 10 chosen sentences are the gold sentences.
        s = self.result["summary"]
        self.assertEqual(s["documents"], 8)
        self.assertEqual(s["questions"], 10)
        self.assertEqual(s["top1_correct"], 10)
        self.assertEqual(s["top1_accuracy"], 1.0)
        self.assertEqual(s["recall_at_3_correct"], 10)
        self.assertEqual(s["recall_at_3"], 1.0)
        self.assertEqual(s["sentence_correct"], 10)
        self.assertEqual(s["sentence_accuracy"], 1.0)

    def test_top1_for_each_question(self):
        expected = {"Q01": "D01", "Q02": "D02", "Q03": "D03", "Q04": "D04",
                    "Q05": "D05", "Q06": "D06", "Q07": "D07", "Q08": "D08",
                    "Q09": "D01", "Q10": "D04"}
        for qid, doc_id in expected.items():
            self.assertEqual(self.by_id[qid]["top1_doc"], doc_id)
            self.assertTrue(self.by_id[qid]["hit_at_1"])
            self.assertTrue(self.by_id[qid]["hit_at_3"])

    def test_q01_top1_score_measured(self):
        self.assertAlmostEqual(
            self.by_id["Q01"]["top1_score"], 0.5371146121646176, places=12)

    def test_answer_citation_exact(self):
        result = self.index.answer("emergency fund covers three months living costs")
        self.assertEqual(result["doc_id"], "D02")
        self.assertEqual(result["sentence_id"], "S2")
        self.assertEqual(result["citation"], "[D02 S2]")
        self.assertEqual(
            result["answer_text"],
            "The emergency fund covers three months of living costs. [D02 S2]")

    def test_answer_picks_third_sentence_for_compost(self):
        result = self.index.answer("compost soil spring planting")
        self.assertEqual(result["doc_id"], "D01")
        self.assertEqual(result["sentence_id"], "S3")
        self.assertEqual(result["sentence"],
                         "Compost feeds the soil before spring planting.")

    def test_unseen_terms_retrieve_zero_scores_in_id_order(self):
        # No query term is in the corpus, so every score is 0.0 and
        # the deterministic tie break returns ids in sorted order.
        ranked = self.index.retrieve("zebra quantum waffle", top_k=3)
        self.assertEqual([r["doc_id"] for r in ranked], ["D01", "D02", "D03"])
        self.assertTrue(all(r["score"] == 0.0 for r in ranked))

    def test_determinism(self):
        again = evaluate(LocalIndex(build_documents()), build_questions())
        self.assertEqual(again, self.result)


class TestPrivacyAudit(unittest.TestCase):
    def test_audit_flags_a_network_pattern(self):
        bad = audit_sources({"x.py": "import socket\n"})
        row = {r["pattern"]: r["count"] for r in bad["patterns"]}
        self.assertEqual(row["socket"], 1)
        self.assertEqual(bad["total_matches"], 1)
        self.assertFalse(bad["passed"])
        self.assertFalse(bad["local_only"])

    def test_audit_passes_clean_text(self):
        clean = audit_sources({"x.py": "print('local only')\n"})
        self.assertEqual(clean["total_matches"], 0)
        self.assertTrue(clean["passed"])

    def test_audit_of_real_level_sources_passes(self):
        here = os.path.join(ROOT, "src")
        texts = {}
        for name in ("local_first.py", "run_learn.py"):
            with open(os.path.join(here, name), encoding="utf-8") as f:
                texts[name] = f.read()
        audit = audit_sources(texts)
        self.assertEqual(audit["files_scanned"], ["local_first.py", "run_learn.py"])
        self.assertEqual(audit["total_matches"], 0)
        self.assertTrue(audit["passed"])
        self.assertEqual(len(audit["patterns"]), 7)


if __name__ == "__main__":
    unittest.main()
