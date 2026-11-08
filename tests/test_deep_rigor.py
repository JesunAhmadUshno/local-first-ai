"""Tests for the rigor add-ons: intervals, held-out threshold, BM25,
chunk sweep, hard question set, and corpus scaling."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import rigor  # noqa: E402
from assistant import build_questions, ingest_directory  # noqa: E402
from local_first import audit_sources  # noqa: E402

DATA = os.path.join(ROOT, "experiments", "corpus")


class WilsonTest(unittest.TestCase):
    def test_all_correct_lower_bound(self):
        # k = n gives a lower bound of n / (n + z^2)
        lo, hi = rigor.wilson(20, 20)
        self.assertAlmostEqual(lo, 20 / (20 + rigor.Z95 ** 2), places=12)
        self.assertEqual(hi, 1.0)

    def test_four_of_four(self):
        lo, _ = rigor.wilson(4, 4)
        self.assertAlmostEqual(lo, 4 / (4 + rigor.Z95 ** 2), places=12)

    def test_half(self):
        lo, hi = rigor.wilson(5, 10)
        self.assertAlmostEqual(lo + hi, 1.0, places=12)
        self.assertTrue(0.2 < lo < 0.25)

    def test_rejects_bad_counts(self):
        with self.assertRaises(rigor.RigorError):
            rigor.wilson(3, 2)
        with self.assertRaises(rigor.RigorError):
            rigor.wilson(0, 0)


class ThresholdTest(unittest.TestCase):
    def test_midpoint_between_bands(self):
        t = rigor.fit_threshold([0.1, 0.2, 0.5, 0.6], [False, False, True, True])
        self.assertAlmostEqual(t, 0.35)

    def test_leave_one_out_on_separable_scores(self):
        out = rigor.leave_one_out_threshold([0.1, 0.2, 0.5, 0.6], [False, False, True, True])
        self.assertEqual(out["refusal_true_positive"], 2)
        self.assertEqual(out["refusal_false_positive"], 0)
        self.assertEqual(out["refusal_false_negative"], 0)

    def test_leave_one_out_catches_a_lone_outlier(self):
        # The held-out no-evidence score 0.7 sits above every evidence score
        # seen in training, so it is answered: one false negative.
        out = rigor.leave_one_out_threshold([0.1, 0.7, 0.5, 0.6], [False, False, True, True])
        self.assertEqual(out["refusal_false_negative"], 1)

    def test_threshold_curve_counts(self):
        curve = rigor.threshold_curve([0.1, 0.5], [False, True], [0.0, 0.3, 0.6])
        self.assertEqual([c["refused"] for c in curve], [0, 1, 2])
        self.assertEqual(curve[2]["false_refusals"], 1)


class Bm25Test(unittest.TestCase):
    def test_bm25_ranks_the_matching_chunk_first(self):
        docs = [{"id": "X1", "title": "a", "sentences": ["Red apples grow on tall trees."]},
                {"id": "X2", "title": "b", "sentences": ["Blue boats float on calm water."]}]
        index = rigor.Bm25Index(docs)
        self.assertEqual(index.retrieve_chunks("calm water boats")[0]["doc_id"], "X2")

    def test_bm25_on_real_corpus(self):
        docs = ingest_directory(DATA)
        result = rigor.evaluate_ranker(rigor.Bm25Index(docs), build_questions())
        self.assertEqual(result["evidence_questions"], 20)
        self.assertGreaterEqual(result["top1_correct"], 18)


class SweepTest(unittest.TestCase):
    def test_default_point_reproduces_build(self):
        docs = ingest_directory(DATA)
        rows = rigor.chunk_sweep(docs, build_questions(), [(30, 10)])
        self.assertEqual(rows[0]["chunks"], 72)
        self.assertEqual(rows[0]["top1_correct"], 20)
        self.assertEqual(rows[0]["refusal_true_positive"], 4)

    def test_sweep_skips_invalid_overlap(self):
        docs = ingest_directory(DATA)
        rows = rigor.chunk_sweep(docs, build_questions(), [(10, 10), (20, 5)])
        self.assertEqual([(r["chunk_size"], r["overlap"]) for r in rows], [(20, 5)])


class HardSetTest(unittest.TestCase):
    def test_hard_set_shape(self):
        qs = rigor.hard_questions()
        self.assertEqual(len(qs), 16)
        kinds = {q["kind"] for q in qs}
        self.assertEqual(kinds, {"synonym_paraphrase", "cross_topic_distractor"})
        for q in qs:
            self.assertEqual(q["gold_doc"] == "NONE", q["kind"] == "cross_topic_distractor")


class ScalingTest(unittest.TestCase):
    def test_replicate_corpus_renames_ids(self):
        docs = ingest_directory(DATA)
        big = rigor.replicate(docs, 3)
        self.assertEqual(len(big), 72)
        self.assertEqual(len({d["id"] for d in big}), 72)


class RigorAuditTest(unittest.TestCase):
    def test_rigor_sources_pass_the_network_audit(self):
        texts = {}
        for name in ("rigor.py", "run_rigor.py"):
            with open(os.path.join(ROOT, "src", name), encoding="utf-8") as f:
                texts[name] = f.read()
        self.assertTrue(audit_sources(texts)["passed"])


if __name__ == "__main__":
    unittest.main()
