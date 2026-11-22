"""
Smart Recursive Text Chunker for Long Lecture Transcripts and Documents.
Preserves paragraph, sentence, and speaker boundary integrity while maintaining
sliding-window context overlap.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import re
from config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


@dataclass
class TextChunk:
    index: int
    total_chunks: int
    text: str
    char_count: int
    word_count: int
    start_char_idx: int
    end_char_idx: int
    preview: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LectureChunker:
    """
    Splits long lecture documents into overlapping, semantically coherent chunks.
    Uses hierarchical split separators:
    1. Paragraph / speaker transitions ("\\n\\n")
    2. Line breaks ("\\n")
    3. Sentence terminators (". ", "? ", "! ")
    4. Clause delimiters ("; ", ", ")
    5. Word spaces (" ")
    """

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
        if chunk_overlap >= chunk_size:
            chunk_overlap = max(0, chunk_size // 4)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[TextChunk]:
        """
        Chunks the input text into a list of TextChunk objects.
        """
        text = text.strip()
        if not text:
            return []

        # If text is already smaller than or equal to chunk_size, return single chunk
        if len(text) <= self.chunk_size:
            return [
                TextChunk(
                    index=1,
                    total_chunks=1,
                    text=text,
                    char_count=len(text),
                    word_count=len(text.split()),
                    start_char_idx=0,
                    end_char_idx=len(text),
                    preview=text[:80].replace("\n", " ") + ("..." if len(text) > 80 else "")
                )
            ]

        # Break text into atomic units based on paragraphs and sentences
        raw_units = self._recursive_split(text, self.chunk_size)

        # Merge units into chunks with overlap
        chunks_text = []
        current_chunk_parts = []
        current_len = 0

        for unit in raw_units:
            unit_len = len(unit)
            if current_len + unit_len > self.chunk_size and current_chunk_parts:
                # Store the current chunk
                full_chunk = "".join(current_chunk_parts).strip()
                if full_chunk:
                    chunks_text.append(full_chunk)

                # Prepare overlap for next chunk
                overlap_parts = []
                overlap_len = 0
                for part in reversed(current_chunk_parts):
                    if overlap_len + len(part) <= self.chunk_overlap:
                        overlap_parts.insert(0, part)
                        overlap_len += len(part)
                    else:
                        break

                current_chunk_parts = overlap_parts
                current_len = overlap_len

            current_chunk_parts.append(unit)
            current_len += unit_len

        # Append trailing chunk
        if current_chunk_parts:
            full_chunk = "".join(current_chunk_parts).strip()
            if full_chunk and (not chunks_text or full_chunk != chunks_text[-1]):
                chunks_text.append(full_chunk)

        # Build TextChunk metadata
        total = len(chunks_text)
        result: List[TextChunk] = []
        current_pos = 0

        for idx, c_text in enumerate(chunks_text, start=1):
            char_count = len(c_text)
            word_count = len(c_text.split())
            preview = c_text[:80].replace("\n", " ") + ("..." if char_count > 80 else "")
            
            result.append(
                TextChunk(
                    index=idx,
                    total_chunks=total,
                    text=c_text,
                    char_count=char_count,
                    word_count=word_count,
                    start_char_idx=current_pos,
                    end_char_idx=current_pos + char_count,
                    preview=preview
                )
            )
            # Advance position taking overlap into account
            current_pos += max(1, char_count - self.chunk_overlap)

        return result

    def _recursive_split(self, text: str, max_size: int) -> List[str]:
        """
        Recursively splits oversized text using progressively finer separators.
        """
        separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", " "]
        
        def _split(subtext: str, sep_idx: int) -> List[str]:
            if len(subtext) <= max_size or sep_idx >= len(separators):
                return [subtext]

            sep = separators[sep_idx]
            if sep not in subtext:
                return _split(subtext, sep_idx + 1)

            # Split while preserving separator with the preceding segment
            splits = subtext.split(sep)
            reconstructed = []
            for i, piece in enumerate(splits):
                if i < len(splits) - 1:
                    reconstructed.append(piece + sep)
                else:
                    if piece:
                        reconstructed.append(piece)

            result = []
            for item in reconstructed:
                if len(item) > max_size:
                    result.extend(_split(item, sep_idx + 1))
                else:
                    result.append(item)
            return result

        return _split(text, 0)
