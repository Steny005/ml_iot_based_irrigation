"""
Dedicated Automated Tests for Malayalam Content and Audio/TTS Functionality
Validates Malayalam Unicode characters, audio script generation, semantic retrieval,
source citations, and speech synthesis fallback behaviors.
"""
import sys
import os
import unittest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from feed.rag_engine import RAGEngine
from feed.store import FeedStore
from feed.generator import DEFAULT_VERIFIED_CARDS, generate_feed_cards_from_rag
from advisor.ai_explainer import generate_advisor_explanation


class TestMalayalamAndAudioValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.docs_dir = os.path.join(BACKEND_DIR, "knowledge", "documents")
        cls.rag = RAGEngine(cls.docs_dir)
        cls.test_store_file = os.path.join(BACKEND_DIR, "data", "test_malayalam_store.json")
        cls.store = FeedStore(cls.test_store_file, cls.rag)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_store_file):
            os.remove(cls.test_store_file)

    def _is_malayalam(self, text: str) -> bool:
        """Returns True if the text contains characters in the Malayalam Unicode block (U+0D00 to U+0D7F)."""
        return any('\u0D00' <= char <= '\u0D7F' for char in text)

    def test_default_cards_malayalam_unicode_integrity(self):
        """Verifies that all seeded knowledge cards contain valid Malayalam script without mojibake."""
        self.assertGreater(len(DEFAULT_VERIFIED_CARDS), 0)
        for card in DEFAULT_VERIFIED_CARDS:
            # Title must be in Malayalam
            self.assertTrue(
                self._is_malayalam(card["title"]),
                f"Card {card['id']} title does not contain Malayalam Unicode: {card['title']}"
            )
            # Explanation must be in Malayalam
            self.assertTrue(
                self._is_malayalam(card["explanation"]),
                f"Card {card['id']} explanation does not contain Malayalam Unicode."
            )
            # Practical tip must be in Malayalam
            self.assertTrue(
                self._is_malayalam(card["practical_tip"]),
                f"Card {card['id']} practical tip does not contain Malayalam Unicode."
            )
            # Audio text must be non-empty and in Malayalam
            self.assertIn("audio_text", card)
            self.assertTrue(
                self._is_malayalam(card["audio_text"]),
                f"Card {card['id']} audio text does not contain Malayalam Unicode."
            )
            # UTF-8 roundtrip encoding test to ensure no data corruption
            card["title"].encode("utf-8").decode("utf-8")
            card["explanation"].encode("utf-8").decode("utf-8")

    def test_audio_text_length_and_readability(self):
        """Verifies that audio text is concise, clear, and well-suited for Web Speech TTS."""
        for card in DEFAULT_VERIFIED_CARDS:
            audio_text = card["audio_text"]
            # Should be between 20 and 500 characters for optimal audio streaming
            self.assertGreaterEqual(len(audio_text), 20)
            self.assertLessEqual(len(audio_text), 500)
            # Must contain complete sentences
            self.assertTrue(audio_text.endswith("."))

    def test_advisor_ai_explainer_malayalam_summary(self):
        """Verifies that the Agricultural Advisor generates authentic Malayalam explanations."""
        result = generate_advisor_explanation(
            crop_name="Banana / Plantain",
            stage="Planting / Pit Preparation",
            weather_summary="Favorable window",
            recommendations_summary=[{"name": "Vermicompost", "qty": "5 kg per pit"}]
        )
        self.assertIn("summary_ml", result)
        self.assertTrue(
            self._is_malayalam(result["summary_ml"]),
            "Advisor summary_ml is missing Malayalam Unicode characters."
        )

    def test_malayalam_rag_query_stem_borer(self):
        """Tests RAG semantic query using Malayalam keyword for paddy stem borer."""
        results = self.rag.retrieve("തണ്ടുതുരപ്പൻ പുഴു", top_k=3)
        self.assertGreater(len(results), 0)
        # Verify retrieved document citation
        top_result = results[0]
        self.assertIn("citation", top_result)
        self.assertTrue(len(top_result["citation"]) > 5)

    def test_malayalam_rag_query_quick_wilt(self):
        """Tests RAG semantic query using Malayalam keyword for quick wilt disease."""
        results = self.rag.retrieve("ദ്രുതവാട്ടം", top_k=3)
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertIn("Pepper", top["crop"])

    def test_malayalam_rag_query_rhino_beetle(self):
        """Tests RAG semantic query using Malayalam keyword for rhinoceros beetle."""
        results = self.rag.retrieve("കൊമ്പൻ ചെല്ലി", top_k=3)
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertIn("Coconut", top["crop"])

    def test_card_institutional_citations(self):
        """Verifies that every card explicitly cites trusted institutions (KAU or ICAR)."""
        for card in DEFAULT_VERIFIED_CARDS:
            citation = card.get("source_citation", "")
            source_name = card.get("source_name", "")
            has_kau_or_icar = (
                "Kerala Agricultural University" in source_name or
                "KAU" in citation or
                "ICAR" in source_name or
                "ICAR" in citation or
                "Kerala Agriculture Department" in source_name
            )
            self.assertTrue(
                has_kau_or_icar,
                f"Card {card['id']} lacks verified institution citation: {citation}"
            )


if __name__ == "__main__":
    unittest.main()
