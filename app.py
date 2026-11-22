"""
FastAPI Web Application for the Automatic Lecture Notes Summarizer.
Provides REST API endpoints and serves the interactive UI.
"""

import os
import sys
import io
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Add current directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

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

app = FastAPI(
    title="Automatic Lecture Notes Summarizer",
    description="Transforms long lecture transcripts and PDF documents into clear bullet-point notes.",
    version="1.0.0"
)

# Mount static files and templates
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
SAMPLES_DIR = BASE_DIR / "sample_lectures"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ------------------------------------------------------------------------------
# Request Models
# ------------------------------------------------------------------------------
class SummarizeTextRequest(BaseModel):
    text: str
    provider: str = "offline"
    model: Optional[str] = None
    api_key: Optional[str] = None
    ollama_url: Optional[str] = "http://localhost:11434"
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP


# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    """Serves the primary web application interface."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "palette": COLOR_PALETTE,
        "providers": SUPPORTED_PROVIDERS
    })


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": "Lecture Notes Summarizer", "version": "1.0.0"}


@app.get("/api/providers")
async def get_providers():
    """Returns available LLM providers and default models."""
    return {
        "providers": SUPPORTED_PROVIDERS,
        "palette": COLOR_PALETTE
    }


@app.get("/api/samples/{sample_id}")
async def get_sample_lecture(sample_id: str):
    """Loads pre-packaged realistic university lecture transcripts."""
    mapping = {
        "ml_transformers": "machine_learning_transformers_lecture.txt",
        "neuro_plasticity": "neurobiology_synaptic_plasticity_lecture.txt"
    }

    filename = mapping.get(sample_id)
    if not filename:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found.")

    file_path = SAMPLES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample lecture file is missing.")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return {
        "sample_id": sample_id,
        "filename": filename,
        "text": content,
        "word_count": len(content.split())
    }


@app.post("/api/summarize-text")
async def summarize_text_endpoint(req: SummarizeTextRequest):
    """
    Summarize a raw text transcript using Map-Reduce chunking.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    cleaned_text, doc_meta = DocumentExtractor.extract_from_text(req.text)

    try:
        chunker = LectureChunker(chunk_size=req.chunk_size, chunk_overlap=req.chunk_overlap)
        llm = LLMClient(
            provider=req.provider,
            model=req.model,
            api_key=req.api_key,
            base_url=req.ollama_url
        )
        summarizer = LectureSummarizer(llm_client=llm, chunker=chunker)

        result = summarizer.summarize_document(cleaned_text)
        result["raw_text"] = cleaned_text
        result["document_metadata"] = doc_meta
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/summarize-file")
async def summarize_file_endpoint(
    file: UploadFile = File(...),
    provider: str = Form("offline"),
    model: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
    ollama_url: Optional[str] = Form("http://localhost:11434"),
    chunk_size: int = Form(DEFAULT_CHUNK_SIZE),
    chunk_overlap: int = Form(DEFAULT_CHUNK_OVERLAP)
):
    """
    Summarize an uploaded PDF, TXT, or Markdown document.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".pdf", ".txt", ".md"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Supported extensions: .pdf, .txt, .md"
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        if suffix == ".pdf":
            # Extract from PDF bytes stream
            file_stream = io.BytesIO(file_bytes)
            cleaned_text, doc_meta = DocumentExtractor.extract_from_pdf(file_stream)
        else:
            # Extract from plain text
            text_str = file_bytes.decode("utf-8", errors="replace")
            cleaned_text, doc_meta = DocumentExtractor.extract_from_text(text_str, source_name=file.filename)

        if not cleaned_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text could be extracted from the document."
            )

        chunker = LectureChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        llm = LLMClient(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=ollama_url
        )
        summarizer = LectureSummarizer(llm_client=llm, chunker=chunker)

        result = summarizer.summarize_document(cleaned_text)
        result["raw_text"] = cleaned_text
        result["document_metadata"] = doc_meta
        result["filename"] = file.filename
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("\n\033[38;2;252;147;31mStarting Automatic Lecture Notes Summarizer Server on http://127.0.0.1:8000...\033[0m\n")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
