<div align="center">

# 🎓 AI Automatic Lecture Notes Summarizer
### *Transforming Long Academic Lectures & PDF Textbooks into High-Yield Bullet-Point Study Guides*

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash%20%2F%20Pro-8E75C2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o%20%2F%20mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLMs-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-FC931F?style=for-the-badge)](LICENSE)

<br/>

[Key Features](#-key-features) •
[UI/UX Color Theme](#-uiux-color-palette) •
[System Architecture](#-system-architecture) •
[Quickstart](#-quickstart) •
[Web Application](#-interactive-web-application) •
[CLI Usage](#-command-line-interface-cli) •
[Testing](#-automated-testing)

</div>

---

## 📖 Overview

Standard Large Language Models (LLMs) struggle with long lectures, seminar transcripts, and multi-page textbook chapters due to context degradation, hallucination over long sequences, and prompt size limits. 

The **AI Automatic Lecture Notes Summarizer** solves this with a robust **hierarchical Map-Reduce pipeline**:
1. **Intelligent Recursive Chunking**: Long documents and extracted PDFs are split into context-aware, overlapping semantic segments (paragraphs and sentences are never cut in half).
2. **Map Stage**: Each segment is independently processed by an LLM to extract granular facts, technical terminology, and arguments.
3. **Reduce Stage**: Segment notes are synthesized into a coherent master study guide that eliminates redundancies, groups ideas by conceptual themes, and generates active-recall self-test questions.
4. **Multi-Engine Agnostic**: Works out-of-the-box with **Google Gemini**, **OpenAI**, **Local Ollama**, or the zero-setup **Offline Extractive Engine**.

---

## 🎨 UI/UX Color Palette

The user interface is engineered with a custom, high-tech dark theme adhering strictly to this palette:

| Color Swatch | Hex Code | Role in UI/UX |
| :---: | :---: | :--- |
| ![#FC931F](https://via.placeholder.com/15/FC931F/000000?text=+) | **`#FC931F`** | **Warm Amber** &bull; Primary CTA Buttons (`✨ Generate Lecture Notes`), Glowing Titles, Key Takeaway Cards |
| ![#F67608](https://via.placeholder.com/15/F67608/000000?text=+) | **`#F67608`** | **Fiery Orange** &bull; Button Gradients, Chunk Segment Badges, Active Progress Bar Accents |
| ![#020C0F](https://via.placeholder.com/15/020C0F/000000?text=+) | **`#020C0F`** | **Obsidian Base** &bull; Viewport Background, Terminal Codeblocks, Markdown Reading Surface |
| ![#053A41](https://via.placeholder.com/15/053A41/000000?text=+) | **`#053A41`** | **Deep Teal Surface** &bull; Elevated Cards, Form Containers, Header Navigation Gradient |
| ![#044F58](https://via.placeholder.com/15/044F58/000000?text=+) | **`#044F58`** | **Border Teal** &bull; Panel Outlines, Subtle Dividers, Drag-and-Drop Zone Borders |
| ![#1C7C84](https://via.placeholder.com/15/1C7C84/000000?text=+) | **`#1C7C84`** | **Muted Cyan** &bull; Secondary Action Buttons, Sliders, Metadata Counters (`chars`, `words`) |
| ![#2A9DA6](https://via.placeholder.com/15/2A9DA6/000000?text=+) | **`#2A9DA6`** | **Bright Cyan Accent** &bull; Active Tab Indicators, Live Progress Bar Glow, Hyperlinks & Badges |

---

## ✨ Key Features

- 📑 **Universal Ingestion**: Paste transcripts with speaker timestamps or drag-and-drop `.pdf`, `.txt`, and `.md` files.
- 🧹 **Automated Text Sanitization**: Cleans PDF noise, merges hyphenated line-breaks (`trans-\nformer` &rarr; `transformer`), and removes repetitive page headers/footers.
- 🧩 **Sliding-Window Chunker**: Preserves paragraph and sentence integrity with configurable overlap (50–1000 characters) to prevent lost thoughts between chunks.
- ⚡ **Map-Reduce Parallelism**: Scales efficiently across arbitrarily long documents without hitting single-prompt context limits.
- 🎓 **Structured Academic Output Format**:
  - 📌 **Executive Summary**: 2–3 paragraph high-level thesis of the lecture.
  - 🧠 **Thematic Modular Notes**: Deep conceptual breakdown with clear subheadings.
  - 📖 **Terminology & Formulas Glossary**: Precise, contextual definitions.
  - 💡 **High-Yield Takeaways**: Top exam-critical principles and rules of thumb.
  - ❓ **Active Recall Questions**: Flashcard-style self-test questions with answers.
- 🖥️ **Interactive Web Application**: Responsive single-page interface with real-time progress bars, metric cards, chunk inspection accordion, copy-to-clipboard, and print/PDF export.
- 💻 **Complete CLI**: Headless command-line tool for terminal workflows and batch scripts.
- 🔒 **Privacy & Local-First**: Run 100% locally with Ollama or the built-in Offline Engine without sending data to external APIs.

---

## 🏛️ System Architecture

```
                                  ┌──────────────────────────────┐
                                  │   Raw Lecture Input Source   │
                                  │ (PDF / Transcript / Text)    │
                                  └──────────────┬───────────────┘
                                                 │
                                  ┌──────────────▼───────────────┐
                                  │    Document Sanitizer        │
                                  │ • Linebreak hyphen repair    │
                                  │ • Page number noise removal  │
                                  └──────────────┬───────────────┘
                                                 │
                                  ┌──────────────▼───────────────┐
                                  │   Recursive Semantic Chunker │
                                  │  (Sliding Window + Overlap)  │
                                  └──────────────┬───────────────┘
                                                 │
                   ┌─────────────────────────────┼─────────────────────────────┐
                   ▼                             ▼                             ▼
             ┌───────────┐                 ┌───────────┐                 ┌───────────┐
             │  Chunk 1  │                 │  Chunk 2  │                 │  Chunk N  │
             └─────┬─────┘                 └─────┬─────┘                 └─────┬─────┘
                   │                             │                             │
                   │ [MAP STAGE: Extract points, theories, terminology, steps] │
                   ▼                             ▼                             ▼
             ┌───────────┐                 ┌───────────┐                 ┌───────────┐
             │ Summary 1 │                 │ Summary 2 │                 │ Summary N │
             └─────┬─────┘                 └─────┬─────┘                 └─────┬─────┘
                   │                             │                             │
                   └─────────────────────────────┼─────────────────────────────┘
                                                 │
                                  ┌──────────────▼───────────────┐
                                  │    REDUCE SYNTHESIS STAGE    │
                                  │  • Eliminate redundancies    │
                                  │  • Harmonize narrative arc   │
                                  │  • Generate self-test Q&As   │
                                  └──────────────┬───────────────┘
                                                 │
                                  ┌──────────────▼───────────────┐
                                  │  Master Study Guide (Notes)  │
                                  │  • Executive Summary         │
                                  │  • Thematic Concept Modules  │
                                  │  • Terminology Glossary      │
                                  │  • Active Recall Q&A Cards   │
                                  └──────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/sakshipadiyar06-debug/lecture-notes-summarizer.git
cd lecture-notes-summarizer

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Create a `.env` file (or set environment variables) if you wish to use cloud providers:

```bash
# OpenAI (Optional)
OPENAI_API_KEY=sk-...

# Google Gemini (Optional)
GEMINI_API_KEY=AIzaSy...

# Local Ollama (Optional - default is http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434
```

> **Note**: You don't need any API key to start! The built-in **Offline Engine** runs locally out-of-the-box.

---

## 🖥️ Interactive Web Application

Launch the local web server:

```bash
python app.py
```

Then open your browser at **[http://localhost:8000](http://localhost:8000)**.

### Web UI Features:
- **Two Input Modes**: Toggle between **Paste Transcript** and **Upload PDF / File**.
- **1-Click Sample Demos**: Load realistic university lectures with one click:
  - `🤖 ML Transformers` (1,150-word lecture on Self-Attention and Vaswani et al.)
  - `🧠 Synaptic Plasticity` (950-word neurobiology lecture on LTP and NMDA receptors)
- **Live Progress Tracking**: Watch real-time stage transitions from chunking &rarr; map summarization &rarr; reduce synthesis.
- **Three-Way Output Viewer**:
  - `🎓 Master Notes`: Rendered study guide with executive summary, bullets, and quiz questions.
  - `🧩 Map Stage (Chunks)`: Expandable accordion showing individual chunk context and segment summaries.
  - `📄 Extracted Text`: Cleaned text extracted from the source document.
- **Export Toolbar**: `📋 Copy Markdown`, `💾 Save .md`, and `🖨️ Print / Save to PDF`.

---

## 💻 Command Line Interface (CLI)

The CLI tool allows quick batch processing directly in your terminal:

```bash
# 1. Quick run on built-in sample lecture with offline engine
python cli.py --show-chunks

# 2. Summarize a PDF file and save output to markdown
python cli.py --input sample_lectures/quantum_computing_lecture.pdf --output notes.md

# 3. Summarize using Google Gemini
python cli.py --input lecture.txt --provider gemini --model gemini-2.5-flash

# 4. Summarize using OpenAI GPT-4o-mini
python cli.py --input lecture.pdf --provider openai --model gpt-4o-mini --api-key sk-...

# 5. Summarize using local Ollama (LLaMA-3.2)
python cli.py --input lecture.txt --provider ollama --model llama3.2 --chunk-size 2500
```

### CLI Options:

| Flag | Description | Default |
| :--- | :--- | :--- |
| `--input, -i` | Path to `.pdf`, `.txt`, or `.md` file | Built-in sample |
| `--text, -t` | Raw transcript passed as inline text | `None` |
| `--provider, -p` | LLM backend: `gemini`, `openai`, `ollama`, `offline` | `offline` |
| `--model, -m` | Model name override | Provider default |
| `--api-key` | API key override | Read from environment |
| `--chunk-size, -c` | Character size per chunk window | `3200` |
| `--chunk-overlap, -o` | Overlap character count between chunks | `350` |
| `--output, -out` | Path to save output Markdown file | `None` (prints to stdout) |
| `--show-chunks` | Show intermediate chunk notes (Map Stage) | `False` |

---

## 🧪 Automated Testing

The project includes an automated test suite verifying extraction, chunking, providers, and REST endpoints:

```bash
python test_summarizer.py
```

```
............
----------------------------------------------------------------------
Ran 12 tests in 1.14s

OK
```

### Test Coverage:
- Text sanitization, line-break hyphen repair, and page header removal
- Edge cases in recursive splitting (single small chunks, oversized text, empty text)
- Map-Reduce execution in offline mode
- REST API endpoints (`/api/health`, `/api/providers`, `/api/samples`)
- Multi-part file upload with real PDF document extraction (`/api/summarize-file`)

---

## 📁 Repository Structure

```
lecture-notes-summarizer/
├── app.py                      # FastAPI server & REST API
├── cli.py                      # Command Line Interface (CLI)
├── config.py                   # System prompts, defaults, and color palette
├── chunker.py                  # Recursive paragraph/sentence text chunker
├── pdf_extractor.py            # PDF & text extraction and sanitization engine
├── llm_client.py               # Multi-provider LLM interface (Gemini, OpenAI, Ollama, Offline)
├── summarizer.py               # Hierarchical Map-Reduce summarization pipeline
├── test_summarizer.py          # Unit and integration test suite
├── create_sample_pdf.py        # ReportLab script generating sample test PDFs
├── requirements.txt            # Python dependencies
├── .env.example                # Template for API keys
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── static/
│   ├── css/
│   │   └── styles.css          # Styled strictly with custom hex color palette
│   └── js/
│       └── app.js              # Real-time progress, drag-and-drop, markdown rendering
├── templates/
│   └── index.html              # Responsive single-page web UI
└── sample_lectures/
    ├── machine_learning_transformers_lecture.txt
    ├── neurobiology_synaptic_plasticity_lecture.txt
    └── quantum_computing_lecture.pdf
```

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute it for academic or commercial purposes.
