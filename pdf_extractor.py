"""
PDF and Document Text Extractor for the Lecture Notes Summarizer.
Extracts clean, normalized text from PDF files, Markdown, and plain text transcripts.
"""

import re
import os
from typing import Dict, Any, Tuple
from pathlib import Path


class DocumentExtractor:
    """Handles extracting and cleaning text from PDF and text documents."""

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """
        Cleans lecture transcript and PDF text:
        - Unifies line breaks
        - Merges hyphenated words across lines (e.g. 'struc-\nture' -> 'structure')
        - Removes page number banners and repeated headers/footers
        - Collapses excess whitespace while preserving paragraph breaks
        """
        if not raw_text:
            return ""

        # Normalize line endings
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

        # Merge hyphenated words broken across line breaks
        text = re.sub(r'(\b\w+)-\n(\w+\b)', r'\1\2', text)

        # Remove common PDF page number artifacts (e.g., "Page 3 of 12", "- 12 -", "[Page 5]")
        text = re.sub(r'(?i)\n?\s*(?:page\s+\d+(?:\s+of\s+\d+)?|-?\s*\d+\s*-?|\[page\s+\d+\])\s*\n', '\n', text)

        # Normalize multiple spaces and tabs to a single space
        text = re.sub(r'[ \t]+', ' ', text)

        # Normalize excessive blank lines (more than 2 consecutive newlines -> 2 newlines)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    @classmethod
    def extract_from_pdf(cls, file_path_or_bytes) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text from a PDF file path or bytes using pypdf.
        Returns cleaned text and metadata dict.
        """
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError(
                "The 'pypdf' package is required for PDF parsing. Install it using 'pip install pypdf'."
            )

        reader = PdfReader(file_path_or_bytes)
        total_pages = len(reader.pages)
        page_texts = []

        for idx, page in enumerate(reader.pages):
            page_content = page.extract_text() or ""
            if page_content.strip():
                page_texts.append(f"[Page {idx + 1}]\n" + page_content.strip())

        raw_combined = "\n\n".join(page_texts)
        cleaned_text = cls.clean_text(raw_combined)

        word_count = len(cleaned_text.split())
        metadata = {
            "source_type": "pdf",
            "page_count": total_pages,
            "char_count": len(cleaned_text),
            "word_count": word_count,
            "estimated_reading_minutes": round(word_count / 200, 1),
        }

        return cleaned_text, metadata

    @classmethod
    def extract_from_text(cls, content: str, source_name: str = "raw_text") -> Tuple[str, Dict[str, Any]]:
        """
        Process raw string or transcript text.
        Returns cleaned text and metadata dict.
        """
        cleaned_text = cls.clean_text(content)
        word_count = len(cleaned_text.split())
        metadata = {
            "source_type": "text",
            "source_name": source_name,
            "char_count": len(cleaned_text),
            "word_count": word_count,
            "estimated_reading_minutes": round(word_count / 200, 1),
        }
        return cleaned_text, metadata

    @classmethod
    def extract_file(cls, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Dispatch extraction based on file extension (.pdf, .txt, .md, etc.).
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return cls.extract_from_pdf(str(path))
        else:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return cls.extract_from_text(content, source_name=path.name)
