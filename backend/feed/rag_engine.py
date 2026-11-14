"""
Agricultural RAG (Retrieval-Augmented Generation) Pipeline Engine
Extracts, chunks, indexes, and retrieves authoritative agricultural documents
from Kerala Agricultural University (KAU) and ICAR publications.
"""

import os
import re
import math
from typing import List, Dict, Any, Optional


class DocumentChunk:
    def __init__(
        self,
        chunk_id: str,
        text: str,
        doc_title: str,
        institution: str,
        crop: str,
        topic: str,
        citation: str,
        source_file: str
    ):
        self.chunk_id = chunk_id
        self.text = text.strip()
        self.doc_title = doc_title
        self.institution = institution
        self.crop = crop
        self.topic = topic
        self.citation = citation
        self.source_file = source_file
        # Normalized token bag for fast pure-python cosine retrieval
        self.tokens = self._tokenize(text + " " + crop + " " + topic + " " + doc_title)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        # Support Malayalam script characters and alphanumeric English tokens
        cleaned = re.sub(r"[^\w\s\u0D00-\u0D7F]", " ", text.lower())
        return [w for w in cleaned.split() if len(w) > 1]


class RAGEngine:
    def __init__(self, docs_directory: str):
        self.docs_directory = docs_directory
        self.chunks: List[DocumentChunk] = []
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.is_indexed = False
        self.load_and_index_documents()

    def load_and_index_documents(self):
        """Loads all documents from disk and splits them into indexed chunks."""
        self.chunks = []
        if not os.path.isdir(self.docs_directory):
            return

        for filename in sorted(os.listdir(self.docs_directory)):
            if not filename.endswith((".txt", ".md", ".json")):
                continue

            file_path = os.path.join(self.docs_directory, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self._process_document(filename, content)
            except Exception as e:
                print(f"[RAG] Warning reading {filename}: {e}")

        self._build_vector_index()
        self.is_indexed = True
        print(f"[RAG] Successfully indexed {len(self.chunks)} agricultural document chunks.")

    def _process_document(self, filename: str, content: str):
        """Extracts metadata headers and splits document into semantic topic chunks."""
        lines = content.splitlines()
        doc_title = "Official Agricultural Publication"
        institution = "Kerala Agricultural University / ICAR"
        crop = "General Agriculture"
        topic = "Crop Protection & Management"

        body_lines = []
        for line in lines:
            if line.startswith("TITLE:"):
                doc_title = line.replace("TITLE:", "").strip()
            elif line.startswith("INSTITUTION:"):
                institution = line.replace("INSTITUTION:", "").strip()
            elif line.startswith("CROP:"):
                crop = line.replace("CROP:", "").strip()
            elif line.startswith("TOPIC:"):
                topic = line.replace("TOPIC:", "").strip()
            else:
                body_lines.append(line)

        full_body = "\n".join(body_lines)
        # Split by numbered sections or double newlines
        sections = re.split(r"\n(?=\d+\.\s+[A-Z])", full_body)
        for idx, sec in enumerate(sections):
            text = sec.strip()
            if len(text) < 40:
                continue

            # Extract specific citation if available in section
            citation_match = re.search(r"Citation:\s*(.+)", text)
            citation = citation_match.group(1).strip() if citation_match else f"{institution} ({doc_title})"

            chunk = DocumentChunk(
                chunk_id=f"{filename}_{idx}",
                text=text,
                doc_title=doc_title,
                institution=institution,
                crop=crop,
                topic=topic,
                citation=citation,
                source_file=filename
            )
            self.chunks.append(chunk)

    def _build_vector_index(self):
        """Builds TF-IDF frequency tables for similarity calculation."""
        doc_count = len(self.chunks)
        if doc_count == 0:
            return

        doc_freq = {}
        for chunk in self.chunks:
            unique_terms = set(chunk.tokens)
            for term in unique_terms:
                doc_freq[term] = doc_freq.get(term, 0) + 1

        self.idf = {
            term: math.log((doc_count + 1) / (df + 1)) + 1.0
            for term, df in doc_freq.items()
        }

    def retrieve(self, query: str, top_k: int = 4, crop_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant agricultural chunks matching query or crop filter.
        """
        if not self.chunks:
            return []

        query_tokens = DocumentChunk._tokenize(query)
        if not query_tokens and not crop_filter:
            # Return representative general chunks
            return [self._format_chunk(c, 1.0) for c in self.chunks[:top_k]]

        query_tf = {}
        for t in query_tokens:
            query_tf[t] = query_tf.get(t, 0) + 1

        scores = []
        for chunk in self.chunks:
            # Check crop filter
            if crop_filter:
                filter_term = crop_filter.lower().strip()
                if filter_term not in chunk.crop.lower() and filter_term not in chunk.text.lower():
                    continue

            # Compute TF-IDF dot-product cosine score
            chunk_tf = {}
            for t in chunk.tokens:
                chunk_tf[t] = chunk_tf.get(t, 0) + 1

            score = 0.0
            for term, q_count in query_tf.items():
                if term in chunk_tf:
                    weight = self.idf.get(term, 1.0)
                    score += q_count * chunk_tf[term] * (weight ** 2)

            # Boost score if query keywords match title or crop
            for term in query_tokens:
                if term in chunk.crop.lower():
                    score += 5.0
                if term in chunk.topic.lower():
                    score += 3.0

            if score > 0:
                scores.append((score, chunk))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = [self._format_chunk(chunk, score) for score, chunk in scores[:top_k]]

        # Fallback if no specific keyword matched
        if not results:
            results = [self._format_chunk(c, 0.5) for c in self.chunks[:top_k]]

        return results

    def _format_chunk(self, chunk: DocumentChunk, score: float) -> Dict[str, Any]:
        return {
            "chunk_id": chunk.chunk_id,
            "text": chunk.text,
            "doc_title": chunk.doc_title,
            "institution": chunk.institution,
            "crop": chunk.crop,
            "topic": chunk.topic,
            "citation": chunk.citation,
            "source_file": chunk.source_file,
            "relevance_score": round(score, 3)
        }
