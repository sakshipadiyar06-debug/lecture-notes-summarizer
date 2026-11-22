"""
Configuration module for the Automatic Lecture Notes Summarizer.
Includes system prompts, chunking defaults, LLM provider settings,
and the brand color palette.
"""

import os
from typing import Dict, Any

# ==============================================================================
# UI UX Color Palette (Strictly Enforced)
# ==============================================================================
COLOR_PALETTE: Dict[str, str] = {
    "amber_gold": "#FC931F",     # Warm vibrant amber
    "vibrant_orange": "#F67608", # Deep fiery orange accent
    "obsidian_dark": "#020C0F",  # Deepest background base
    "deep_teal": "#053A41",      # Surface / card background
    "border_teal": "#044F58",    # Panel borders & divider lines
    "muted_cyan": "#1C7C84",     # Muted interactive / secondary controls
    "bright_cyan": "#2A9DA6",    # Active badges, highlights, links
}

# ==============================================================================
# Chunking Defaults
# ==============================================================================
DEFAULT_CHUNK_SIZE: int = 3200       # ~600-800 words / tokens
DEFAULT_CHUNK_OVERLAP: int = 350     # ~70 words context carry-over
MIN_CHUNK_SIZE: int = 500
MAX_CHUNK_SIZE: int = 12000

# ==============================================================================
# LLM Providers & Models
# ==============================================================================
SUPPORTED_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "default_model": "gpt-4o-mini",
        "available_models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        "api_key_env": "OPENAI_API_KEY",
        "requires_key": True,
    },
    "gemini": {
        "name": "Google Gemini",
        "default_model": "gemini-2.5-flash",
        "available_models": ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        "api_key_env": "GEMINI_API_KEY",
        "requires_key": True,
    },
    "ollama": {
        "name": "Ollama (Local)",
        "default_model": "llama3.2",
        "available_models": ["llama3.2", "llama3", "mistral", "qwen2.5", "phi4", "deepseek-r1"],
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "requires_key": False,
    },
    "offline": {
        "name": "Offline Engine (Zero-Setup / Local NLP)",
        "default_model": "extractive-synthesizer",
        "available_models": ["extractive-synthesizer"],
        "requires_key": False,
    }
}

# ==============================================================================
# Prompts for Map & Reduce Stages
# ==============================================================================
MAP_CHUNK_PROMPT = """You are an expert academic scribe and university teaching assistant.
Your task is to analyze this lecture excerpt and extract clear, concise, highly informative bullet-point notes.

Focus on:
1. Core Concepts & Theories introduced
2. Key Arguments, Mechanisms, or Steps
3. Definitions of essential technical terms
4. Concrete examples, case studies, or analogies used by the lecturer

Excerpt ({chunk_index}/{total_chunks}):
-------------------------
{chunk_text}
-------------------------

Produce your response in Markdown with:
- **Segment Topic**: Short 3-6 word title
- **Key Points**:
  * Bullet point 1 (crisp and factual)
  * Bullet point 2
  * Bullet point 3
- **Terminology / Formulas** (if any): Definition or formula
"""

REDUCE_SYNTHESIS_PROMPT = """You are an elite academic professor preparing the definitive, high-yield study guide and lecture notes.
Below are intermediate bullet-point summaries extracted from sequential segments of a full lecture.

Synthesize these segment summaries into a single, comprehensive, beautifully structured set of lecture notes.
Eliminate redundancies, harmonize the narrative arc, and format with high visual clarity.

Intermediate Summaries:
-------------------------
{all_summaries}
-------------------------

Output your final notes in the following Markdown format:

# 🎓 [Insert Master Lecture Title]

## 📌 Executive Summary
A 2-3 paragraph synthesis capturing the central thesis, purpose, and overall narrative of the lecture.

## 🧠 Comprehensive Lecture Notes
Group the notes into 3 to 5 logical conceptual modules or themes with subheadings:
### 1. [First Major Conceptual Theme]
- **[Concept/Mechanism]**: Detailed explanation and significance.
- **[Key Insight]**: Explanation with concrete examples.

### 2. [Second Major Conceptual Theme]
- ...

## 📖 Key Terminology & Definitions Glossary
- **[Term]**: Concise, exact definition as used in context.

## 💡 High-Yield Takeaways
- Top 3-5 critical insights or rules of thumb for exams or practical application.

## ❓ Active Recall / Self-Test Questions
Provide 3-5 thought-provoking review questions with expandable or concise answers for student revision:
1. **Q**: [Question]?
   - **A**: [Concise answer].
"""
