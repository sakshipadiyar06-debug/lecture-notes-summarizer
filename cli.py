"""
Command Line Interface (CLI) for the Automatic Lecture Notes Summarizer.
Supports PDF extraction, text transcripts, chunking, and multi-provider LLM pipelines.
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    SUPPORTED_PROVIDERS,
    COLOR_PALETTE
)
from pdf_extractor import DocumentExtractor
from chunker import LectureChunker
from llm_client import LLMClient
from summarizer import LectureSummarizer


def format_status(msg: str, color_code: str = "\033[96m") -> str:
    """Helper for colorful terminal logs."""
    reset = "\033[0m"
    return f"{color_code}▶ {msg}{reset}"


def print_banner():
    banner = f"""
\033[38;2;252;147;31m╔═════════════════════════════════════════════════════════════════════════╗
║   \033[1m🎓 AI AUTOMATIC LECTURE NOTES SUMMARIZER\033[0m\033[38;2;252;147;31m                              ║
║   \033[38;2;42;157;166mTransforming long lecture transcripts & PDFs into high-yield notes\033[38;2;252;147;31m     ║
╚═════════════════════════════════════════════════════════════════════════╝\033[0m
"""
    print(banner)


def main():
    parser = argparse.ArgumentParser(
        description="Automatic Lecture Notes Summarizer using Generative AI and Map-Reduce Chunking."
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to lecture file (.txt, .md, or .pdf)."
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="Raw lecture transcript text passed directly as string."
    )
    parser.add_argument(
        "--provider", "-p",
        type=str,
        default="offline",
        choices=["openai", "gemini", "ollama", "offline"],
        help="LLM Provider to use (default: offline zero-setup mode)."
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="Model name override (e.g. gpt-4o-mini, gemini-2.5-flash, llama3.2)."
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API Key for the chosen provider (or set OPENAI_API_KEY / GEMINI_API_KEY in environment)."
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Base URL for Ollama local service."
    )
    parser.add_argument(
        "--chunk-size", "-c",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Character size per chunk (default: {DEFAULT_CHUNK_SIZE})."
    )
    parser.add_argument(
        "--chunk-overlap", "-o",
        type=int,
        default=DEFAULT_CHUNK_OVERLAP,
        help=f"Character overlap between consecutive chunks (default: {DEFAULT_CHUNK_OVERLAP})."
    )
    parser.add_argument(
        "--output", "-out",
        type=str,
        default=None,
        help="File path to save the generated Markdown lecture notes."
    )
    parser.add_argument(
        "--show-chunks",
        action="store_true",
        help="Display intermediate chunk summaries in terminal output."
    )

    args = parser.parse_args()
    print_banner()

    # 1. Acquire Input Text
    raw_text = ""
    metadata = {}

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"\033[91mError: Input file '{args.input}' does not exist.\033[0m")
            sys.exit(1)
        print(format_status(f"Loading document: {input_path.name}..."))
        raw_text, metadata = DocumentExtractor.extract_file(str(input_path))
    elif args.text:
        raw_text, metadata = DocumentExtractor.extract_from_text(args.text, source_name="cli_argument")
    else:
        # Prompt user or default to sample
        sample_path = Path(__file__).parent / "sample_lectures" / "machine_learning_transformers_lecture.txt"
        if sample_path.exists():
            print(f"\033[93mNo input file specified. Using built-in sample lecture: '{sample_path.name}'\033[0m")
            raw_text, metadata = DocumentExtractor.extract_file(str(sample_path))
        else:
            print("\033[91mError: Please provide --input <file> or --text <content>.\033[0m")
            sys.exit(1)

    print(format_status(
        f"Document loaded: {metadata.get('word_count', len(raw_text.split()))} words "
        f"({metadata.get('char_count', len(raw_text))} chars, ~{metadata.get('estimated_reading_minutes', 0)} min reading time)"
    ))

    # 2. Initialize Chunker and LLM Client
    chunker = LectureChunker(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    llm = LLMClient(
        provider=args.provider,
        model=args.model,
        api_key=args.api_key,
        base_url=args.ollama_url
    )
    summarizer = LectureSummarizer(llm_client=llm, chunker=chunker)

    # 3. Progress Reporter Callback
    def on_progress(step: str, current: int, total: int):
        bar_len = 24
        filled = int(bar_len * current / total)
        bar = "█" * filled + "░" * (bar_len - filled)
        sys.stdout.write(f"\r\033[38;2;252;147;31m[{bar}] {current}%\033[0m \033[38;2;42;157;166m{step}\033[0m")
        sys.stdout.flush()
        if current >= total:
            sys.stdout.write("\n")

    print(format_status(f"Running Map-Reduce pipeline using Provider: [{args.provider.upper()}] (Model: {llm.model})..."))
    
    try:
        results = summarizer.summarize_document(raw_text, progress_callback=on_progress)
    except Exception as e:
        print(f"\n\033[91mPipeline Execution Failed: {str(e)}\033[0m")
        sys.exit(1)

    # 4. Display Results
    if args.show_chunks:
        print("\n\033[1m" + "=" * 60)
        print("  INTERMEDIATE CHUNK SUMMARIES (MAP STAGE)")
        print("=" * 60 + "\033[0m")
        for chunk_data in results["chunk_summaries"]:
            print(f"\n\033[38;2;246;118;8m[Chunk {chunk_data['chunk_index']}/{chunk_data['total_chunks']}] ({chunk_data['word_count']} words)\033[0m")
            print(chunk_data["summary"])

    print("\n\033[1m" + "=" * 60)
    print("  FINAL SYNTHESIZED LECTURE NOTES (REDUCE STAGE)")
    print("=" * 60 + "\033[0m\n")
    print(results["master_notes"])

    # 5. Save Output if Requested
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(results["master_notes"])
        print(f"\n\033[32m✔ Lecture notes saved successfully to: {out_path.resolve()}\033[0m")

    print(f"\n\033[38;2;252;147;31mCompleted in {results['metadata']['processing_time_seconds']}s. "
          f"Summarized {results['metadata']['total_chunks']} chunks. "
          f"Compression ratio: {results['metadata']['compression_ratio']}%\033[0m\n")


if __name__ == "__main__":
    main()
