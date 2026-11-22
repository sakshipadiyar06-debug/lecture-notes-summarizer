"""
Automated Unit and Integration Tests for Lecture Notes Summarizer.
Tests extraction, recursive chunking, multi-provider LLM abstraction,
map-reduce synthesis, and FastAPI endpoints.
"""

import unittest
from pathlib import Path
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, COLOR_PALETTE
from pdf_extractor import DocumentExtractor
from chunker import LectureChunker, TextChunk
from llm_client import LLMClient
from summarizer import LectureSummarizer
from fastapi.testclient import TestClient
from app import app


class TestDocumentExtractor(unittest.TestCase):
    def test_clean_text_hyphenation(self):
        raw = "This is a demon-\nstration of hyphenated text."
        cleaned = DocumentExtractor.clean_text(raw)
        self.assertEqual(cleaned, "This is a demonstration of hyphenated text.")

    def test_clean_text_page_numbers(self):
        raw = "First paragraph.\nPage 3 of 15\nSecond paragraph."
        cleaned = DocumentExtractor.clean_text(raw)
        self.assertIn("First paragraph.", cleaned)
        self.assertIn("Second paragraph.", cleaned)
        self.assertNotIn("Page 3 of 15", cleaned)

    def test_extract_from_text_metadata(self):
        text = "Hello world! This is a test lecture transcript with several words."
        cleaned, meta = DocumentExtractor.extract_from_text(text)
        self.assertEqual(meta["source_type"], "text")
        self.assertEqual(meta["word_count"], 11)
        self.assertGreater(meta["char_count"], 0)


class TestLectureChunker(unittest.TestCase):
    def test_single_small_chunk(self):
        text = "Short lecture note under the chunk size threshold."
        chunker = LectureChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.split_text(text)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].index, 1)
        self.assertEqual(chunks[0].total_chunks, 1)

    def test_multi_chunk_split_with_overlap(self):
        # Create a document of 2000 chars
        paragraph = "This is a comprehensive lecture on deep neural architectures. " * 30
        chunk_size = 500
        chunk_overlap = 100
        chunker = LectureChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = chunker.split_text(paragraph)

        self.assertGreater(len(chunks), 1)
        for i, c in enumerate(chunks, start=1):
            self.assertEqual(c.index, i)
            self.assertEqual(c.total_chunks, len(chunks))
            self.assertLessEqual(len(c.text), chunk_size + 150) # within bounds

    def test_empty_text_handling(self):
        chunker = LectureChunker()
        chunks = chunker.split_text("")
        self.assertEqual(len(chunks), 0)


class TestLLMClientAndSummarizer(unittest.TestCase):
    def test_offline_engine_map_and_reduce(self):
        llm = LLMClient(provider="offline")
        chunker = LectureChunker(chunk_size=400, chunk_overlap=50)
        summarizer = LectureSummarizer(llm_client=llm, chunker=chunker)

        text = (
            "Machine learning is a field of artificial intelligence. "
            "Supervised learning trains models on labeled datasets. "
            "Unsupervised learning finds hidden patterns in unlabeled data. "
            "Reinforcement learning uses reward signals to optimize policies. "
        ) * 10

        result = summarizer.summarize_document(text)
        self.assertIn("master_notes", result)
        self.assertIn("Executive Summary", result["master_notes"])
        self.assertIn("chunk_summaries", result)
        self.assertGreater(len(result["chunk_summaries"]), 0)
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["provider"], "offline")


class TestFastAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_get_providers(self):
        resp = self.client.get("/api/providers")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("providers", data)
        self.assertIn("palette", data)
        self.assertEqual(data["palette"]["amber_gold"], "#FC931F")
        self.assertEqual(data["palette"]["obsidian_dark"], "#020C0F")

    def test_get_sample_lecture(self):
        resp = self.client.get("/api/samples/ml_transformers")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("CS 229", data["text"])
        self.assertGreater(data["word_count"], 500)

    def test_summarize_text_api(self):
        payload = {
            "text": "Gradient descent minimizes the objective function by taking steps proportional to the negative gradient. " * 15,
            "provider": "offline",
            "chunk_size": 500,
            "chunk_overlap": 100
        }
        resp = self.client.post("/api/summarize-text", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("master_notes", data)
        self.assertIn("chunk_summaries", data)
        self.assertGreater(data["metadata"]["total_words"], 0)


    def test_summarize_file_upload_pdf(self):
        pdf_path = Path(__file__).parent / "sample_lectures" / "quantum_computing_lecture.pdf"
        self.assertTrue(pdf_path.exists())
        with open(pdf_path, "rb") as f:
            resp = self.client.post(
                "/api/summarize-file",
                files={"file": ("quantum_computing_lecture.pdf", f, "application/pdf")},
                data={"provider": "offline", "chunk_size": 1000, "chunk_overlap": 150}
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("master_notes", data)
        self.assertIn("chunk_summaries", data)
        self.assertEqual(data["filename"], "quantum_computing_lecture.pdf")
        self.assertGreater(data["metadata"]["total_chunks"], 0)


if __name__ == "__main__":
    unittest.main()
