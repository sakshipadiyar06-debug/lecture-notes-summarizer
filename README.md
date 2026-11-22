# 🎓 Automatic Lecture Notes Summarizer

A high-performance Generative AI system that converts long university lecture transcripts and PDF textbooks into structured, concise, and high-yield bullet-point study notes using a scalable **Map-Reduce** hierarchical chunking architecture.

---

## 🎨 UI/UX Color Palette Specification

The web application is designed with the custom, high-contrast dark theme requested:

| Color Hex | Name | UI Component / Role |
| :--- | :--- | :--- |
| **`#FC931F`** | Warm Amber | Primary Action CTA Buttons, Glowing Badges, Header Highlights |
| **`#F67608`** | Fiery Orange | Button Gradients, Chunk Badges, Active Progress Bar Accents |
| **`#020C0F`** | Obsidian Base | Viewport Background, Terminal Blocks, Markdown Container |
| **`#053A41`** | Deep Teal | Elevated Cards, Input Containers, Navigation Header Base |
| **`#044F58`** | Border Teal | Panel Borders, Divider Lines, Drag-and-Drop Zone Borders |
| **`#1C7C84`** | Muted Cyan | Secondary Controls, Metadata Counters, Subdued Labeling |
| **`#2A9DA6`** | Bright Cyan | Active Tab Highlights, Progress Bar Glows, Hyperlinks |

---

## 🌟 Key Architecture & Capabilities

```
  ┌──────────────────────────────────────────────────────────────┐
  │                   Input Lecture Document                     │
  │     (Long Transcript / PDF / Textbook Chapter / Audio TXT)   │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │   Recursive Semantic Chunker  │
                 │ (Sliding Window with Overlap) │
                 └───────────────┬───────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
   ┌───────────┐           ┌───────────┐           ┌───────────┐
   │  Chunk 1  │           │  Chunk 2  │           │  Chunk N  │
   └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
         │                       │                       │
         │ (MAP STAGE: Prompt per chunk)                 │
         ▼                       ▼                       ▼
   ┌───────────┐           ┌───────────┐           ┌───────────┐
   │ Summary 1 │           │ Summary 2 │           │ Summary N │
   └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │  REDUCE STAGE: Synthesis LLM  │
                 │   (Global Redundancy Removal) │
                 └───────────────┬───────────────┘
                                 │
                 ┌───────────────▼───────────────┐
                 │  Structured Study Master Note │
                 │  - Executive Summary          │
                 │  - Thematic Bullet Points     │
                 │  - Terminology Glossary       │
                 │  - High-Yield Takeaways       │
                 │  - Active Recall Questions    │
                 └───────────────────────────────┘
```

1. **Smart Recursive Chunker**:
   - Preserves paragraph transitions, sentence structures, and speaker tags.
   - Configurable `chunk_size` (1,000 to 8,000 characters) and `chunk_overlap` (50 to 1,000 characters) to avoid context clipping across boundaries.

2. **Hierarchical Map-Reduce Processing**:
   - **Map Step**: Each chunk is analyzed independently to extract technical definitions, empirical arguments, and key points.
   - **Reduce Step**: Combines all intermediate notes into a harmonized, formatted study guide.

3. **Multi-Provider LLM Engine**:
   - **Google Gemini**: `gemini-2.5-flash`, `gemini-1.5-pro` (via `google-genai` SDK or REST)
   - **OpenAI**: `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`
   - **Ollama**: Local models (`llama3.2`, `mistral`, `qwen2.5`, `phi4`, `deepseek-r1`) with zero API costs
   - **Offline Extractive Engine**: Local extractive graph-ranking summarizer for zero-setup offline demos.

4. **Multi-Format Ingestion**:
   - Directly paste long raw text / transcripts.
   - Drag-and-drop or upload `.pdf`, `.txt`, and `.md` files.
   - Automated cleaning: joins broken hyphenated linebreaks, strips repetitive page number footers, and normalizes spacing.

5. **Export Options**:
   - One-click copy Markdown to clipboard.
   - Download `.md` file.
   - Print or export to PDF directly from browser.

---

## 🚀 Quick Start Guide

### 1. Requirements & Installation

```bash
# Navigate to the project directory
cd C:\Users\saksh\.gemini\antigravity\scratch\lecture_notes_summarizer

# Install required dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional)

Copy `.env.example` to `.env` or set environment variables:

```bash
# For OpenAI
set OPENAI_API_KEY=sk-...

# For Google Gemini
set GEMINI_API_KEY=AIzaSy...

# For Ollama (Local)
# Just ensure Ollama is running:
ollama run llama3.2
```

*(Note: If no API keys are provided, the built-in **Offline Engine** runs automatically!)*

---

## 🖥️ Running the Interactive Web Application

Launch the FastAPI web server:

```bash
python app.py
```

Then open your browser at **[http://localhost:8000](http://localhost:8000)**.

### Features in the Web App:
- **Sample Loader Buttons**: Click `🤖 ML Transformers` or `🧠 Synaptic Plasticity` to instantly load realistic 1,200+ word university lectures.
- **PDF Upload**: Drag and drop any lecture slides or PDF paper (e.g. `sample_lectures/quantum_computing_lecture.pdf`).
- **Interactive Tabs**:
  - `Master Notes`: Rendered Markdown with executive summary, categorized bullets, definitions, and self-test questions.
  - `Map Stage (Chunks)`: Expandable accordion to inspect each chunk and its individual segment summary.
  - `Extracted Text`: View raw extracted content with word and character counters.
- **Progress Tracking**: Real-time progress bar with live stage indicators.

---

## 💻 Running via Command Line (CLI)

The CLI script `cli.py` allows command-line batch processing and terminal usage:

```bash
# 1. Quick run on built-in sample lecture
python cli.py --show-chunks

# 2. Summarize a PDF file
python cli.py --input sample_lectures/quantum_computing_lecture.pdf --output notes.md

# 3. Use Google Gemini
python cli.py --input sample_lectures/machine_learning_transformers_lecture.txt --provider gemini --model gemini-2.5-flash

# 4. Use OpenAI GPT-4o-mini
python cli.py --input lecture.pdf --provider openai --model gpt-4o-mini --api-key sk-...

# 5. Use Ollama with local LLaMA-3.2
python cli.py --input lecture.txt --provider ollama --model llama3.2 --chunk-size 2500
```

### CLI Arguments:

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--input, -i` | Path to `.pdf`, `.txt`, or `.md` lecture file | Sample ML lecture |
| `--text, -t` | Raw transcript passed directly as text string | None |
| `--provider, -p` | LLM backend: `offline`, `gemini`, `openai`, `ollama` | `offline` |
| `--model, -m` | Model name override | Provider default |
| `--api-key` | API key override | Read from environment |
| `--chunk-size, -c` | Character size per chunk | `3200` |
| `--chunk-overlap, -o` | Overlap between consecutive chunks | `350` |
| `--output, -out` | Path to save output Markdown file | None (stdout) |
| `--show-chunks` | Print intermediate chunk summaries | False |

---

## 🧪 Automated Test Suite

Run the comprehensive unit and integration test suite:

```bash
python test_summarizer.py
```

### Verified Test Cases:
- `test_clean_text_hyphenation`: Validates joining words split across lines.
- `test_clean_text_page_numbers`: Validates stripping header/footer noise.
- `test_single_small_chunk` & `test_multi_chunk_split_with_overlap`: Validates recursive split logic.
- `test_offline_engine_map_and_reduce`: Validates Map-Reduce pipeline synthesis.
- `test_health_check` & `test_get_providers`: Validates REST endpoints.
- `test_summarize_file_upload_pdf`: Validates end-to-end PDF file upload and extraction.

---

## 📂 Project Structure

```
lecture_notes_summarizer/
├── app.py                      # FastAPI web server and REST API
├── cli.py                      # Command line interface
├── config.py                   # Settings, color palette, and prompt templates
├── chunker.py                  # Recursive sentence/paragraph chunker
├── pdf_extractor.py            # PDF and transcript text extraction engine
├── llm_client.py               # Unified multi-provider LLM client
├── summarizer.py               # Hierarchical Map-Reduce summarization pipeline
├── test_summarizer.py          # Unit & integration test suite (12 tests)
├── create_sample_pdf.py        # Generates test lecture PDFs using ReportLab
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── static/
│   ├── css/
│   │   └── styles.css          # Styled strictly with requested color palette
│   └── js/
│       └── app.js              # Drag-and-drop, real-time progress, markdown parsing
├── templates/
│   └── index.html              # Modern, responsive single-page application
└── sample_lectures/
    ├── machine_learning_transformers_lecture.txt
    ├── neurobiology_synaptic_plasticity_lecture.txt
    └── quantum_computing_lecture.pdf
```
