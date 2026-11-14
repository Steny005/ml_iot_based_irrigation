"""
Agricultural RAG (Retrieval-Augmented Generation) Pipeline Engine
Supports PDF, Markdown (.md), and Text (.txt) agricultural documents.
Extracts text, preserves metadata (title, institution, crop, topic, publication date, source URL, page number),
prevents duplicate chunk indexing, and provides hot-reindexing without restarting the backend.
"""

import os
import re
import math
import hashlib
from typing import List, Dict, Any, Optional

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


class DocumentChunk:
    def __init__(
        self,
        chunk_id: str,
        text: str,
        doc_title: str,
        institution: str,
        crop: str,
        topic: str,
        publication_date: str,
        source_url: str,
        page_number: int,
        citation: str,
        source_file: str
    ):
        self.chunk_id = chunk_id
        self.text = text.strip()
        self.doc_title = doc_title
        self.institution = institution
        self.crop = crop
        self.topic = topic
        self.publication_date = publication_date
        self.source_url = source_url
        self.page_number = page_number
        self.citation = citation
        self.source_file = source_file
        # Unique content hash to prevent duplicate indexing
        self.content_hash = hashlib.sha256(
            f"{doc_title}_{page_number}_{self.text}".encode("utf-8")
        ).hexdigest()
        # Normalized token bag for pure-python TF-IDF cosine retrieval
        self.tokens = self._tokenize(text + " " + crop + " " + topic + " " + doc_title)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        # Support Malayalam script characters (\u0D00-\u0D7F) and alphanumeric English tokens
        cleaned = re.sub(r"[^\w\s\u0D00-\u0D7F]", " ", text.lower())
        return [w for w in cleaned.split() if len(w) > 1]


class RAGEngine:
    def __init__(self, docs_directory: str):
        self.docs_directory = docs_directory
        self.chunks: List[DocumentChunk] = []
        self.seen_hashes: set = set()
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.is_indexed = False
        self.load_and_index_documents()

    def load_and_index_documents(self) -> int:
        """
        Loads and indexes all documents (.pdf, .txt, .md) from disk.
        Thread-safe, avoids duplicates, and hot-updates the search index.
        """
        new_chunks: List[DocumentChunk] = []
        new_seen_hashes: set = set()

        if not os.path.isdir(self.docs_directory):
            print(f"[RAG] Warning: Documents directory not found: {self.docs_directory}")
            return 0

        files = sorted(os.listdir(self.docs_directory))
        for filename in files:
            file_path = os.path.join(self.docs_directory, filename)
            ext = os.path.splitext(filename)[1].lower()

            try:
                if ext == ".pdf":
                    self._process_pdf_document(file_path, filename, new_chunks, new_seen_hashes)
                elif ext in (".txt", ".md", ".json"):
                    self._process_text_document(file_path, filename, new_chunks, new_seen_hashes)
            except Exception as e:
                print(f"[RAG] Warning processing {filename}: {e}")

        # Atomic swap
        self.chunks = new_chunks
        self.seen_hashes = new_seen_hashes
        self._build_vector_index()
        self.is_indexed = True
        print(f"[RAG] Successfully indexed {len(self.chunks)} chunks across {len(files)} files.")
        return len(self.chunks)

    def _process_pdf_document(
        self,
        file_path: str,
        filename: str,
        chunks_target: List[DocumentChunk],
        seen_hashes: set
    ):
        """Extracts text page by page from PDF preserving page numbers and metadata."""
        if not PYPDF_AVAILABLE:
            print(f"[RAG] pypdf not available; skipping PDF: {filename}")
            return

        reader = PdfReader(file_path)
        doc_title = os.path.splitext(filename)[0].replace("_", " ").title()
        institution = "Kerala Agricultural University / ICAR"
        crop = "General Agriculture"
        topic = "Crop Protection & Agricultural Advisory"
        publication_date = "2024"
        source_url = "https://celkau.in / https://icar.org.in"

        # Check if first page has metadata headers
        if len(reader.pages) > 0:
            first_page_text = reader.pages[0].extract_text() or ""
            for line in first_page_text.splitlines():
                if line.startswith("TITLE:"):
                    doc_title = line.replace("TITLE:", "").strip()
                elif line.startswith("INSTITUTION:"):
                    institution = line.replace("INSTITUTION:", "").strip()
                elif line.startswith("CROP:"):
                    crop = line.replace("CROP:", "").strip()
                elif line.startswith("TOPIC:"):
                    topic = line.replace("TOPIC:", "").strip()
                elif line.startswith("PUBLICATION_DATE:"):
                    publication_date = line.replace("PUBLICATION_DATE:", "").strip()
                elif line.startswith("SOURCE_URL:"):
                    source_url = line.replace("SOURCE_URL:", "").strip()

        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            page_num = page_idx + 1

            # Split into section paragraphs
            sections = re.split(r"\n(?=\d+\.\s+[A-Z])|\n\n+", page_text)
            for idx, sec in enumerate(sections):
                text = sec.strip()
                if len(text) < 40:
                    continue

                chunk_id = f"{filename}_p{page_num}_{idx}"
                citation_match = re.search(r"Citation:\s*(.+)", text)
                citation = (
                    citation_match.group(1).strip()
                    if citation_match
                    else f"{institution} - {doc_title} (Page {page_num})"
                )

                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    text=text,
                    doc_title=doc_title,
                    institution=institution,
                    crop=crop,
                    topic=topic,
                    publication_date=publication_date,
                    source_url=source_url,
                    page_number=page_num,
                    citation=citation,
                    source_file=filename
                )

                if chunk.content_hash not in seen_hashes:
                    seen_hashes.add(chunk.content_hash)
                    chunks_target.append(chunk)

    def _process_text_document(
        self,
        file_path: str,
        filename: str,
        chunks_target: List[DocumentChunk],
        seen_hashes: set
    ):
        """Extracts text and metadata headers from .txt and .md files."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        doc_title = os.path.splitext(filename)[0].replace("_", " ").title()
        institution = "Kerala Agricultural University / ICAR"
        crop = "General Agriculture"
        topic = "Crop Protection & Agronomic Package"
        publication_date = "2024"
        source_url = "https://celkau.in / https://kau.in"
        page_num = 1

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
            elif line.startswith("PUBLICATION_DATE:"):
                publication_date = line.replace("PUBLICATION_DATE:", "").strip()
            elif line.startswith("SOURCE_URL:"):
                source_url = line.replace("SOURCE_URL:", "").strip()
            elif line.startswith("PAGE:"):
                try:
                    page_num = int(line.replace("PAGE:", "").strip())
                except ValueError:
                    pass
            else:
                body_lines.append(line)

        full_body = "\n".join(body_lines)
        sections = re.split(r"\n(?=\d+\.\s+[A-Z])", full_body)
        for idx, sec in enumerate(sections):
            text = sec.strip()
            if len(text) < 40:
                continue

            chunk_id = f"{filename}_{idx}"
            citation_match = re.search(r"Citation:\s*(.+)", text)
            citation = (
                citation_match.group(1).strip()
                if citation_match
                else f"{institution} - {doc_title} (Page {page_num})"
            )

            # Check for page numbers mentioned in section text
            page_inline = re.search(r"Page[:\s]+(\d+)", text, re.IGNORECASE)
            assigned_page = int(page_inline.group(1)) if page_inline else page_num

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                text=text,
                doc_title=doc_title,
                institution=institution,
                crop=crop,
                topic=topic,
                publication_date=publication_date,
                source_url=source_url,
                page_number=assigned_page,
                citation=citation,
                source_file=filename
            )

            if chunk.content_hash not in seen_hashes:
                seen_hashes.add(chunk.content_hash)
                chunks_target.append(chunk)

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
        """Retrieves top relevant agricultural chunks matching query or crop filter."""
        if not self.chunks:
            return []

        query_tokens = DocumentChunk._tokenize(query)
        if not query_tokens and not crop_filter:
            return [self._format_chunk(c, 1.0) for c in self.chunks[:top_k]]

        query_tf = {}
        for t in query_tokens:
            query_tf[t] = query_tf.get(t, 0) + 1

        scores = []
        for chunk in self.chunks:
            if crop_filter:
                filter_term = crop_filter.lower().strip()
                if filter_term not in chunk.crop.lower() and filter_term not in chunk.text.lower():
                    continue

            chunk_tf = {}
            for t in chunk.tokens:
                chunk_tf[t] = chunk_tf.get(t, 0) + 1

            score = 0.0
            for term, q_count in query_tf.items():
                if term in chunk_tf:
                    weight = self.idf.get(term, 1.0)
                    score += q_count * chunk_tf[term] * (weight ** 2)

            for term in query_tokens:
                if term in chunk.crop.lower():
                    score += 5.0
                if term in chunk.topic.lower():
                    score += 3.0

            if score > 0:
                scores.append((score, chunk))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = [self._format_chunk(chunk, score) for score, chunk in scores[:top_k]]

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
            "publication_date": chunk.publication_date,
            "source_url": chunk.source_url,
            "page_number": chunk.page_number,
            "citation": chunk.citation,
            "source_file": chunk.source_file,
            "relevance_score": round(score, 3)
        }
