"""
Farmer Feed Storage and Caching Manager
Maintains cached knowledge cards, handles topic filtering, and interfaces with RAG.
"""

import os
import json
from typing import List, Dict, Any, Optional
from .rag_engine import RAGEngine
from .generator import generate_feed_cards_from_rag, DEFAULT_VERIFIED_CARDS


class FeedStore:
    def __init__(self, data_file: str, rag_engine: RAGEngine):
        self.data_file = data_file
        self.rag_engine = rag_engine
        self.cards: List[Dict[str, Any]] = []
        self._load_or_initialize()

    def _load_or_initialize(self):
        """Loads cached cards from disk or initializes with verified knowledge."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.cards = json.load(f)
                if self.cards:
                    print(f"[FEED STORE] Loaded {len(self.cards)} cached cards from disk.")
                    return
            except Exception as e:
                print(f"[FEED STORE] Error reading cached cards: {e}")

        # Initialize with verified cards
        self.cards = generate_feed_cards_from_rag([])
        self.save()

    def save(self):
        """Persists cards to JSON storage."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.cards, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[FEED STORE] Error saving cards: {e}")

    def get_cards(
        self,
        category: Optional[str] = None,
        crop: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Returns cards with optional category or crop filtering."""
        filtered = self.cards
        if category and category.lower() != "all":
            cat_lower = category.lower().strip()
            filtered = [c for c in filtered if cat_lower in c.get("category", "").lower()]

        if crop and crop.lower() != "all":
            crop_lower = crop.lower().strip()
            filtered = [c for c in filtered if crop_lower in c.get("crop", "").lower()]

        return filtered[:limit]

    def query_rag_feed(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieves relevant knowledge chunks using RAG and returns matching feed cards.
        """
        chunks = self.rag_engine.retrieve(query, top_k=top_k)
        if not chunks:
            return {
                "status": "warning",
                "message": "No specific document matched this query. Showing general verified advisories.",
                "cards": self.get_cards(limit=top_k),
                "retrieved_sources": []
            }

        # Check existing cards for keyword matches
        q_lower = query.lower()
        matched_cards = []
        for card in self.cards:
            full_card_text = (
                card.get("title", "") + " " +
                card.get("title_en", "") + " " +
                card.get("explanation", "") + " " +
                card.get("crop", "") + " " +
                card.get("category", "")
            ).lower()
            if any(term in full_card_text for term in q_lower.split() if len(term) > 2):
                matched_cards.append(card)

        # If not enough existing cards matched, synthesize from RAG
        if len(matched_cards) < 2 and chunks:
            new_cards = generate_feed_cards_from_rag(chunks)
            for nc in new_cards:
                if not any(c.get("id") == nc.get("id") for c in self.cards):
                    self.cards.insert(0, nc)
                    matched_cards.append(nc)
            self.save()

        return {
            "status": "success",
            "query": query,
            "cards": matched_cards if matched_cards else self.cards[:top_k],
            "retrieved_sources": [
                {
                    "citation": c["citation"],
                    "crop": c["crop"],
                    "topic": c["topic"],
                    "relevance_score": c["relevance_score"]
                }
                for c in chunks
            ]
        }

    def refresh(self) -> int:
        """Re-indexes documents and refreshes feed cards."""
        self.rag_engine.load_and_index_documents()
        chunks = self.rag_engine.retrieve("agriculture pest disease fertilizer management", top_k=6)
        fresh_cards = generate_feed_cards_from_rag(chunks)
        # Merge ensuring no duplicates
        existing_ids = {c["id"] for c in self.cards}
        for fc in fresh_cards:
            if fc["id"] not in existing_ids:
                self.cards.insert(0, fc)
        self.save()
        return len(self.cards)
