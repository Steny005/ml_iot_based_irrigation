"""
Unit tests for RAG pipeline and Malayalam Farmer Feed
Includes PDF, Markdown, Text ingestion, metadata preservation, and duplicate prevention.
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
        self.assertGreaterEqual(len(self.rag.chunks), 15)

    def test_pdf_document_parsing_and_metadata(self):
        """Verifies that PDF documents are parsed with page numbers and full metadata."""
        pdf_chunks = [c for c in self.rag.chunks if c.source_file.endswith(".pdf")]
        self.assertGreater(len(pdf_chunks), 0, "No PDF chunks found in RAG index.")
        for chunk in pdf_chunks:
            self.assertGreater(chunk.page_number, 0)
            self.assertIn("Kerala Agricultural University", chunk.institution)
            self.assertIn("Page", chunk.citation)
            self.assertTrue(len(chunk.text) > 30)

    def test_duplicate_chunk_prevention(self):
        """Verifies that duplicate content hashes are not added to chunks."""
        hashes = [c.content_hash for c in self.rag.chunks]
        self.assertEqual(len(hashes), len(set(hashes)), "Duplicate chunk hashes detected in index!")

    def test_hot_reindex_without_restart(self):
        """Verifies that load_and_index_documents() can be re-run dynamically."""
        initial_count = len(self.rag.chunks)
        new_count = self.rag.load_and_index_documents()
        self.assertEqual(initial_count, new_count)

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
            self.assertTrue(any('\u0D00' <= char <= '\u0D7F' for char in c["title"]))

    def test_feed_query_rag(self):
        response = self.store.query_rag_feed("വാഴ തണ്ടുതുരപ്പൻ", top_k=3)
        self.assertEqual(response["status"], "success")
        self.assertGreater(len(response["cards"]), 0)


if __name__ == "__main__":
    unittest.main()
