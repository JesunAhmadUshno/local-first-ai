"""Runtime egress test: the full Build pipeline runs with networking disabled.

The privacy audit elsewhere is a static scan of source text. This test
adds a runtime check: every socket constructor and name lookup in the
standard library is replaced with a function that raises, then ingest,
indexing, answering, refusal, evaluation and session memory all run.
Any attempt to open a connection would fail the test.
"""
import os
import socket
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))
from assistant import ChunkIndex, Session, build_questions, evaluate, ingest_directory  # noqa: E402


class EgressBlocked(AssertionError):
    pass


def _blocked(*args, **kwargs):
    raise EgressBlocked("network access attempted during an offline run")


class RuntimeEgressTest(unittest.TestCase):
    NAMES = ("socket", "create_connection", "getaddrinfo", "gethostbyname", "socketpair")

    def setUp(self):
        self.saved = {n: getattr(socket, n) for n in self.NAMES}
        for n in self.NAMES:
            setattr(socket, n, _blocked)

    def tearDown(self):
        for n, f in self.saved.items():
            setattr(socket, n, f)

    def test_guard_is_live(self):
        with self.assertRaises(EgressBlocked):
            socket.create_connection(("127.0.0.1", 9))

    def test_full_pipeline_runs_offline(self):
        docs = ingest_directory(os.path.join(ROOT, "level-2-build", "data"))
        index = ChunkIndex(docs)
        summary = evaluate(index, build_questions())["summary"]
        self.assertEqual(summary["top1_correct"], 20)
        self.assertEqual(summary["refusal_true_positive"], 4)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "session.json")
            session = Session(path)
            q = "What checksum verifies a copied file matches the original exactly?"
            session.record(q, index.answer(q))
            self.assertEqual(Session(path).cited_doc_ids(), ["B18"])

    def test_rigor_runs_offline(self):
        import rigor
        docs = ingest_directory(os.path.join(ROOT, "level-2-build", "data"))
        hard = rigor.evaluate_hard(ChunkIndex(docs), rigor.hard_questions())
        self.assertEqual(hard["paraphrase_questions"], 10)


if __name__ == "__main__":
    unittest.main()
