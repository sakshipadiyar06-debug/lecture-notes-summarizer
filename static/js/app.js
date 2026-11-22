/**
 * Frontend Application Logic for Automatic Lecture Notes Summarizer
 * Coordinates file upload, API calls, real-time chunk progress, and markdown rendering.
 */

// Model options per provider
const PROVIDER_MODELS = {
  "offline": ["extractive-synthesizer (Zero-Setup / Local)"],
  "openai": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
  "gemini": ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
  "ollama": ["llama3.2", "llama3", "mistral", "qwen2.5", "phi4", "deepseek-r1"]
};

// Global state
let currentInputMode = "text"; // "text" or "file"
let selectedFile = null;
let lastResults = null;

document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupTextareaCounters();
  setupSampleButtons();
  setupDropzone();
  setupProviderControls();
  setupSliders();
  setupSubmit();
  setupToolbarButtons();
  setupOutputTabs();
});

// Tab Switching (Text vs File)
function setupTabs() {
  const textTabBtn = document.getElementById("tabBtnText");
  const fileTabBtn = document.getElementById("tabBtnFile");
  const textPane = document.getElementById("textInputPane");
  const filePane = document.getElementById("fileInputPane");

  textTabBtn.addEventListener("click", () => {
    currentInputMode = "text";
    textTabBtn.classList.add("active");
    fileTabBtn.classList.remove("active");
    textPane.style.display = "block";
    filePane.style.display = "none";
  });

  fileTabBtn.addEventListener("click", () => {
    currentInputMode = "file";
    fileTabBtn.classList.add("active");
    textTabBtn.classList.remove("active");
    textPane.style.display = "none";
    filePane.style.display = "block";
  });
}

// Textarea Character & Word Counters
function setupTextareaCounters() {
  const textarea = document.getElementById("lectureTextInput");
  const charCountEl = document.getElementById("charCount");
  const wordCountEl = document.getElementById("wordCount");

  const updateCounts = () => {
    const val = textarea.value.trim();
    const chars = textarea.value.length;
    const words = val ? val.split(/\s+/).length : 0;
    charCountEl.textContent = `${chars.toLocaleString()} chars`;
    wordCountEl.textContent = `${words.toLocaleString()} words`;
  };

  textarea.addEventListener("input", updateCounts);
  updateCounts();
}

// Sample Lecture Buttons
function setupSampleButtons() {
  const btnML = document.getElementById("btnSampleML");
  const btnNeuro = document.getElementById("btnSampleNeuro");
  const textarea = document.getElementById("lectureTextInput");

  const loadSample = async (sampleId) => {
    try {
      showToast(`Loading sample lecture (${sampleId})...`, "info");
      const resp = await fetch(`/api/samples/${sampleId}`);
      if (!resp.ok) throw new Error("Failed to load sample");
      const data = await resp.json();
      textarea.value = data.text;
      // Trigger counter update
      textarea.dispatchEvent(new Event("input"));
      showToast("Sample lecture loaded successfully!", "success");
    } catch (err) {
      showToast(`Error: ${err.message}`, "error");
    }
  };

  btnML.addEventListener("click", () => loadSample("ml_transformers"));
  btnNeuro.addEventListener("click", () => loadSample("neuro_plasticity"));
}

// Drag & Drop File Upload
function setupDropzone() {
  const dropzone = document.getElementById("fileDropzone");
  const fileInput = document.getElementById("fileInput");
  const fileSelectedCard = document.getElementById("fileSelectedCard");
  const fileNameEl = document.getElementById("selectedFileName");
  const fileSizeEl = document.getElementById("selectedFileSize");
  const removeFileBtn = document.getElementById("removeFileBtn");

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
      handleFile(fileInput.files[0]);
    }
  });

  removeFileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    selectedFile = null;
    fileInput.value = "";
    fileSelectedCard.style.display = "none";
    dropzone.style.display = "flex";
  });

  function handleFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!["pdf", "txt", "md"].includes(ext)) {
      showToast("Only .pdf, .txt, and .md files are supported.", "error");
      return;
    }
    selectedFile = file;
    fileNameEl.textContent = file.name;
    fileSizeEl.textContent = `${(file.size / 1024).toFixed(1)} KB`;
    dropzone.style.display = "none";
    fileSelectedCard.style.display = "flex";
    showToast(`File selected: ${file.name}`, "info");
  }
}

// Provider & Model Selection
function setupProviderControls() {
  const providerSelect = document.getElementById("providerSelect");
  const modelSelect = document.getElementById("modelSelect");
  const apiKeyGroup = document.getElementById("apiKeyGroup");
  const ollamaGroup = document.getElementById("ollamaUrlGroup");

  const updateModels = () => {
    const provider = providerSelect.value;
    const models = PROVIDER_MODELS[provider] || [];

    modelSelect.innerHTML = "";
    models.forEach(m => {
      const opt = document.createElement("option");
      opt.value = m.split(" ")[0];
      opt.textContent = m;
      modelSelect.appendChild(opt);
    });

    if (provider === "openai" || provider === "gemini") {
      apiKeyGroup.style.display = "block";
      ollamaGroup.style.display = "none";
    } else if (provider === "ollama") {
      apiKeyGroup.style.display = "none";
      ollamaGroup.style.display = "block";
    } else {
      apiKeyGroup.style.display = "none";
      ollamaGroup.style.display = "none";
    }
  };

  providerSelect.addEventListener("change", updateModels);
  updateModels();
}

// Sliders
function setupSliders() {
  const chunkSizeSlider = document.getElementById("chunkSizeSlider");
  const chunkSizeVal = document.getElementById("chunkSizeVal");
  const chunkOverlapSlider = document.getElementById("chunkOverlapSlider");
  const chunkOverlapVal = document.getElementById("chunkOverlapVal");

  chunkSizeSlider.addEventListener("input", () => {
    chunkSizeVal.textContent = `${chunkSizeSlider.value} ch`;
  });

  chunkOverlapSlider.addEventListener("input", () => {
    chunkOverlapVal.textContent = `${chunkOverlapSlider.value} ch`;
  });
}

// Main Submit / Summarization Call
function setupSubmit() {
  const btn = document.getElementById("btnGenerate");
  const progressCard = document.getElementById("progressCard");
  const progressBar = document.getElementById("progressBarFill");
  const progressStep = document.getElementById("progressStep");
  const progressPct = document.getElementById("progressPct");

  btn.addEventListener("click", async () => {
    const provider = document.getElementById("providerSelect").value;
    const model = document.getElementById("modelSelect").value;
    const apiKey = document.getElementById("apiKeyInput").value.trim();
    const ollamaUrl = document.getElementById("ollamaUrlInput").value.trim();
    const chunkSize = parseInt(document.getElementById("chunkSizeSlider").value, 10);
    const chunkOverlap = parseInt(document.getElementById("chunkOverlapSlider").value, 10);

    // Validation
    if (currentInputMode === "text") {
      const text = document.getElementById("lectureTextInput").value.trim();
      if (!text) {
        showToast("Please enter or paste a lecture transcript first.", "error");
        return;
      }
    } else {
      if (!selectedFile) {
        showToast("Please upload a PDF or text file first.", "error");
        return;
      }
    }

    // Set UI loading state
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner">⏳</span> Summarizing Lecture...`;
    progressCard.style.display = "block";
    updateProgress(15, "Chunking document & parsing text...");

    try {
      let response;
      if (currentInputMode === "text") {
        const payload = {
          text: document.getElementById("lectureTextInput").value.trim(),
          provider,
          model,
          api_key: apiKey,
          ollama_url: ollamaUrl,
          chunk_size: chunkSize,
          chunk_overlap: chunkOverlap
        };

        updateProgress(40, "Sending chunks to LLM (Map Stage)...");
        response = await fetch("/api/summarize-text", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
      } else {
        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("provider", provider);
        formData.append("model", model);
        formData.append("api_key", apiKey);
        formData.append("ollama_url", ollamaUrl);
        formData.append("chunk_size", chunkSize);
        formData.append("chunk_overlap", chunkOverlap);

        updateProgress(35, "Extracting text from document & splitting chunks...");
        response = await fetch("/api/summarize-file", {
          method: "POST",
          body: formData
        });
      }

      updateProgress(85, "Synthesizing master lecture notes (Reduce Stage)...");

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Summarization failed");
      }

      const data = await response.json();
      lastResults = data;

      updateProgress(100, "Done!");
      renderResults(data);
      showToast("Lecture notes generated successfully!", "success");

      setTimeout(() => {
        progressCard.style.display = "none";
      }, 1200);

    } catch (err) {
      showToast(`Error: ${err.message}`, "error");
      progressCard.style.display = "none";
    } finally {
      btn.disabled = false;
      btn.innerHTML = `✨ Generate Lecture Notes`;
    }
  });

  function updateProgress(pct, msg) {
    progressBar.style.width = `${pct}%`;
    progressPct.textContent = `${pct}%`;
    progressStep.textContent = msg;
  }
}

// Render Results into UI
function renderResults(data) {
  // Update Metrics
  document.getElementById("metricWords").textContent = data.metadata.total_words?.toLocaleString() || "0";
  document.getElementById("metricChunks").textContent = data.metadata.total_chunks || "1";
  document.getElementById("metricTime").textContent = `${data.metadata.processing_time_seconds || 0}s`;
  document.getElementById("metricRatio").textContent = `${data.metadata.compression_ratio || 0}%`;

  // Render Master Markdown Notes
  const container = document.getElementById("masterNotesBody");
  container.innerHTML = parseMarkdownToHtml(data.master_notes);

  // Render Intermediate Chunks (Map Stage)
  const chunksList = document.getElementById("chunksAccordion");
  chunksList.innerHTML = "";

  if (data.chunk_summaries && data.chunk_summaries.length > 0) {
    data.chunk_summaries.forEach((chunk) => {
      const item = document.createElement("div");
      item.className = "chunk-item";
      item.innerHTML = `
        <div class="chunk-header" onclick="toggleChunkAccordion(this)">
          <div class="chunk-title">
            <span class="chunk-badge">Chunk ${chunk.chunk_index}/${chunk.total_chunks}</span>
            <span>${chunk.word_count} words (${chunk.char_count} chars)</span>
          </div>
          <div class="chunk-meta">▼ Click to inspect</div>
        </div>
        <div class="chunk-body" style="display: none;">
          <div class="chunk-preview-box">
            <strong>Original Context Preview:</strong><br/>
            ${escapeHtml(chunk.preview)}
          </div>
          <div class="chunk-summary-content">
            ${parseMarkdownToHtml(chunk.summary)}
          </div>
        </div>
      `;
      chunksList.appendChild(item);
    });
  }

  // Render Raw Extracted Text
  const rawTextContainer = document.getElementById("rawExtractedText");
  rawTextContainer.textContent = data.raw_text || "(Text available during processing)";
}

// Toggle Chunk Item Accordion
window.toggleChunkAccordion = function(headerEl) {
  const body = headerEl.nextElementSibling;
  const isHidden = body.style.display === "none";
  body.style.display = isHidden ? "block" : "none";
  const meta = headerEl.querySelector(".chunk-meta");
  if (meta) meta.textContent = isHidden ? "▲ Collapse" : "▼ Click to inspect";
};

// Output Tab Switcher
function setupOutputTabs() {
  const tabs = document.querySelectorAll(".output-tab");
  const panes = {
    "tabMaster": document.getElementById("paneMasterNotes"),
    "tabChunks": document.getElementById("paneChunks"),
    "tabRaw": document.getElementById("paneRawText")
  };

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const target = tab.getAttribute("data-target");
      Object.keys(panes).forEach(k => {
        if (panes[k]) panes[k].style.display = (k === target) ? "block" : "none";
      });
    });
  });
}

// Toolbar Action Buttons (Copy, Download, Print)
function setupToolbarButtons() {
  const btnCopy = document.getElementById("btnCopyMarkdown");
  const btnDownload = document.getElementById("btnDownloadMd");
  const btnPrint = document.getElementById("btnPrintNotes");

  btnCopy.addEventListener("click", () => {
    if (!lastResults || !lastResults.master_notes) {
      showToast("No notes to copy yet.", "error");
      return;
    }
    navigator.clipboard.writeText(lastResults.master_notes).then(() => {
      showToast("Copied Markdown to clipboard!", "success");
    });
  });

  btnDownload.addEventListener("click", () => {
    if (!lastResults || !lastResults.master_notes) {
      showToast("No notes to download yet.", "error");
      return;
    }
    const blob = new Blob([lastResults.master_notes], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `lecture_notes_${new Date().toISOString().slice(0, 10)}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast("Downloaded lecture notes .md file!", "success");
  });

  btnPrint.addEventListener("click", () => {
    const container = document.getElementById("masterNotesBody");
    if (!container || !lastResults) {
      showToast("No notes to print yet.", "error");
      return;
    }
    window.print();
  });
}

// Lightweight Markdown to HTML Converter
function parseMarkdownToHtml(md) {
  if (!md) return "<p>No content.</p>";

  let html = md;
  // Escape script tags
  html = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "");

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Bold & Italic
  html = html.replace(/\*\*\*(.*?)\*\*\*/gim, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

  // Code
  html = html.replace(/`([^`]+)`/gim, '<code>$1</code>');

  // Unordered list items
  html = html.replace(/^\s*[\*\-]\s+(.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>[\s\S]*?<\/li>)/gim, '<ul>$1</ul>');
  // Clean nested duplicate UL tags
  html = html.replace(/<\/ul>\s*<ul>/gim, '');

  // Blockquotes
  html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');

  // Paragraphs
  html = html.split('\n\n').map(p => {
    p = p.trim();
    if (!p) return '';
    if (p.startsWith('<h') || p.startsWith('<ul') || p.startsWith('<block')) return p;
    return `<p>${p.replace(/\n/g, '<br/>')}</p>`;
  }).join('\n');

  return `<div class="markdown-body">${html}</div>`;
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Toast Notifications
function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = "toast";
  
  let icon = "ℹ️";
  if (type === "success") icon = "✅";
  if (type === "error") icon = "⚠️";

  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = "opacity 0.3s ease, transform 0.3s ease";
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
