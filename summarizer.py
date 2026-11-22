"""
Hierarchical Map-Reduce Summarization Engine for Lecture Notes.
Coordinates chunking, intermediate chunk summarization, and master note synthesis.
"""

import time
from typing import List, Dict, Any, Optional, Callable
from chunker import LectureChunker, TextChunk
from llm_client import LLMClient
from config import MAP_CHUNK_PROMPT, REDUCE_SYNTHESIS_PROMPT


class LectureSummarizer:
    """
    Coordinates Map-Reduce summarization for long lecture documents.
    1. Chunking: breaks documents into semantic windows.
    2. Map Stage: generates focused bullet-point summaries for each chunk.
    3. Reduce Stage: synthesizes all chunk notes into structured master lecture notes.
    """

    def __init__(self, llm_client: LLMClient, chunker: Optional[LectureChunker] = None):
        self.llm = llm_client
        self.chunker = chunker or LectureChunker()

    def summarize_chunk(self, chunk: TextChunk, total_chunks: int) -> str:
        """
        Map step: Summarizes a single chunk into atomic bullet points.
        """
        prompt = MAP_CHUNK_PROMPT.format(
            chunk_index=chunk.index,
            total_chunks=total_chunks,
            chunk_text=chunk.text
        )
        return self.llm.generate(prompt)

    def synthesize_summaries(self, intermediate_summaries: List[Dict[str, Any]]) -> str:
        """
        Reduce step: Combines all intermediate segment notes into high-level lecture notes.
        """
        formatted_inputs = []
        for item in intermediate_summaries:
            formatted_inputs.append(
                f"### Segment {item['chunk_index']} of {item['total_chunks']}:\n{item['summary']}\n"
            )
        all_summaries_text = "\n".join(formatted_inputs)

        prompt = REDUCE_SYNTHESIS_PROMPT.format(all_summaries=all_summaries_text)
        return self.llm.generate(prompt)

    def summarize_document(
        self,
        text: str,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Full end-to-end pipeline:
        - Splits text into chunks
        - Iterates over chunks with status reporting
        - Synthesizes final master notes
        - Returns structured payload with all details
        """
        start_time = time.time()
        
        # 1. Chunking
        if progress_callback:
            progress_callback("chunking", 0, 100)
            
        chunks = self.chunker.split_text(text)
        total_chunks = len(chunks)

        if total_chunks == 0:
            elapsed = round(time.time() - start_time, 2)
            return {
                "master_notes": "No readable content provided.",
                "chunk_summaries": [],
                "metadata": {
                    "total_words": 0,
                    "total_chars": 0,
                    "total_chunks": 0,
                    "chunk_size_configured": self.chunker.chunk_size,
                    "chunk_overlap_configured": self.chunker.chunk_overlap,
                    "provider": self.llm.provider,
                    "model": self.llm.model,
                    "processing_time_seconds": elapsed,
                    "compression_ratio": 0.0,
                    "error": "Empty text provided"
                }
            }

        intermediate_results: List[Dict[str, Any]] = []

        # 2. Map Stage (Chunk-by-chunk summarization)
        for i, chunk in enumerate(chunks, start=1):
            if progress_callback:
                pct = int(10 + (i / total_chunks) * 70)
                progress_callback(f"summarizing_chunk_{i}", pct, 100)

            summary = self.summarize_chunk(chunk, total_chunks)
            intermediate_results.append({
                "chunk_index": chunk.index,
                "total_chunks": total_chunks,
                "word_count": chunk.word_count,
                "char_count": chunk.char_count,
                "preview": chunk.preview,
                "summary": summary
            })

        # 3. Reduce Stage (Master Synthesis)
        if progress_callback:
            progress_callback("synthesizing_master_notes", 85, 100)

        # If there's only 1 small chunk, we can refine or directly structure it
        if total_chunks == 1:
            prompt = REDUCE_SYNTHESIS_PROMPT.format(
                all_summaries=f"### Single Lecture Segment:\n{intermediate_results[0]['summary']}"
            )
            master_notes = self.llm.generate(prompt)
        else:
            master_notes = self.synthesize_summaries(intermediate_results)

        if progress_callback:
            progress_callback("complete", 100, 100)

        elapsed = round(time.time() - start_time, 2)
        total_words = len(text.split())

        return {
            "master_notes": master_notes,
            "chunk_summaries": intermediate_results,
            "metadata": {
                "total_words": total_words,
                "total_chars": len(text),
                "total_chunks": total_chunks,
                "chunk_size_configured": self.chunker.chunk_size,
                "chunk_overlap_configured": self.chunker.chunk_overlap,
                "provider": self.llm.provider,
                "model": self.llm.model,
                "processing_time_seconds": elapsed,
                "compression_ratio": round(len(master_notes.split()) / max(1, total_words) * 100, 1)
            }
        }
