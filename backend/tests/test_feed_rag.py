"""
Unit tests for RAG pipeline and Malayalam Farmer Feed
"""
import sys
import os
import unittest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from feed.rag_engine import RAGEngine
from feed.store import FeedStore


class TestFarmerFeedRAG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        docs_dir = os.path.join(BACKEND_DIR, "knowledge", "documents")
        cls.rag = RAGEngine(docs_dir)
        cls.test_store_file = os.path.join(BACKEND_DIR, "data", "test_feed_cards.json")
        cls.store = FeedStore(cls.test_store_file, cls.rag)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_store_file):
            os.remove(cls.test_store_file)

    def test_document_indexing(self):
        self.assertTrue(self.rag.is_indexed)
        self.assertGreaterEqual(len(self.rag.chunks), 10)

    def test_retrieval_by_keyword(self):
        # Query for stem borer in paddy
        results = self.rag.retrieve("stem borer dead heart paddy", top_k=3)
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertIn("Paddy", top["crop"])
        self.assertIn("citation", top)

    def test_retrieval_by_malayalam_keyword(self):
        # Query for Malayalam keyword "കുരുമുളക്" (pepper)
        results = self.rag.retrieve("കുരുമുളക് ദ്രുതവാട്ടം", top_k=3)
        self.assertGreater(len(results), 0)
        self.assertTrue(any("Pepper" in r["crop"] or "കുരുമുളക്" in r["text"] for r in results))

    def test_feed_store_cards_malayalam_fields(self):
        cards = self.store.get_cards(limit=10)
        self.assertGreaterEqual(len(cards), 5)
        for c in cards:
            self.assertIn("title", c)
            self.assertIn("explanation", c)
            self.assertIn("practical_tip", c)
            self.assertIn("category", c)
            self.assertIn("source_citation", c)
            self.assertIn("audio_text", c)
            # Ensure Malayalam script exists in title
            self.assertTrue(any('\u0D00' <= char <= '\u0D7F' for char in c["title"]))

    def test_feed_query_rag(self):
        response = self.store.query_rag_feed("വാഴ തണ്ടുതുരപ്പൻ", top_k=3)
        self.assertEqual(response["status"], "success")
        self.assertGreater(len(response["cards"]), 0)


if __name__ == "__main__":
    unittest.main()
