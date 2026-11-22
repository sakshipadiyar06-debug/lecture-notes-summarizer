"""
Unified Multi-Provider LLM Client for Lecture Notes Summarizer.
Supports:
- OpenAI (GPT-4o, GPT-4o-mini, etc.)
- Ollama (Local LLMs: llama3, mistral, phi4, deepseek-r1, etc.)
- Google Gemini (gemini-2.5-flash, gemini-1.5-pro, etc.)
- Offline Extractive NLP Engine (Zero-cost, works immediately without API keys)
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional
import requests
from config import SUPPORTED_PROVIDERS

logger = logging.getLogger("LectureSummarizer.LLM")


class LLMClient:
    """Dispatches generation requests to configured LLM providers."""

    def __init__(
        self,
        provider: str = "offline",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.2,
    ):
        self.provider = provider.lower()
        if self.provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}. Supported: {list(SUPPORTED_PROVIDERS.keys())}")

        provider_info = SUPPORTED_PROVIDERS[self.provider]
        self.model = model or provider_info.get("default_model", "default")
        self.api_key = api_key or os.getenv(provider_info.get("api_key_env", ""), "")
        self.base_url = base_url or provider_info.get("base_url", "")
        self.temperature = temperature

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Sends prompt to the configured LLM and returns response text.
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, system_prompt)
        elif self.provider == "ollama":
            return self._generate_ollama(prompt, system_prompt)
        elif self.provider == "gemini":
            return self._generate_gemini(prompt, system_prompt)
        elif self.provider == "offline":
            return self._generate_offline(prompt)
        else:
            raise ValueError(f"Unhandled provider: {self.provider}")

    # --------------------------------------------------------------------------
    # OpenAI Provider
    # --------------------------------------------------------------------------
    def _generate_openai(self, prompt: str, system_prompt: Optional[str]) -> str:
        if not self.api_key:
            raise ValueError(
                "OpenAI API key missing. Please provide it in the UI/CLI or set OPENAI_API_KEY environment variable."
            )

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    # --------------------------------------------------------------------------
    # Ollama Provider (Local LLMs)
    # --------------------------------------------------------------------------
    def _generate_ollama(self, prompt: str, system_prompt: Optional[str]) -> str:
        url = f"{self.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False,
            "options": {
                "temperature": self.temperature,
            }
        }
        try:
            resp = requests.post(url, json=payload, timeout=120)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Ollama returned HTTP {resp.status_code}: {resp.text}. "
                    f"Ensure Ollama is running at {self.base_url} and model '{self.model}' is pulled ('ollama pull {self.model}')."
                )
            data = resp.json()
            return data.get("response", "")
        except requests.ConnectionError:
            raise RuntimeError(
                f"Could not connect to Ollama at {self.base_url}. "
                "Ensure Ollama daemon is running ('ollama serve') or switch to another provider."
            )
        except Exception as e:
            raise RuntimeError(f"Ollama error: {str(e)}")

    # --------------------------------------------------------------------------
    # Google Gemini Provider
    # --------------------------------------------------------------------------
    def _generate_gemini(self, prompt: str, system_prompt: Optional[str]) -> str:
        if not self.api_key:
            raise ValueError(
                "Gemini API key missing. Please provide it in the UI/CLI or set GEMINI_API_KEY environment variable."
            )

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            config = types.GenerateContentConfig(
                temperature=self.temperature,
                system_instruction=system_prompt if system_prompt else None,
            )
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise RuntimeError(f"Gemini API error: {str(e)}")

    # --------------------------------------------------------------------------
    # Offline Extractive NLP Engine (Zero-Cost / Fallback)
    # --------------------------------------------------------------------------
    def _generate_offline(self, prompt: str) -> str:
        """
        Fast local extractive summarizer used for offline demonstration or zero-setup environments.
        Extracts salient sentences, identifies technical definitions, and outputs formatted markdown notes.
        """
        # Determine if prompt is Map or Reduce stage
        if "Intermediate Summaries:" in prompt:
            # Reduce stage: extract and reorganize bullet points
            raw_input = prompt.split("-------------------------")[1] if "-------------------------" in prompt else prompt
            bullets = [line.strip() for line in raw_input.splitlines() if line.strip().startswith(("-", "*"))]
            if not bullets:
                sentences = [s.strip() for s in re.split(r'[.\n]', raw_input) if len(s.strip()) > 30]
                bullets = [f"- {s}." for s in sentences[:8]]

            grouped = "\n".join(bullets[:15])
            
            return f"""# 🎓 Synthesized Comprehensive Lecture Notes

## 📌 Executive Summary
This lecture systematically examines core theoretical frameworks, empirical mechanisms, and practical methodologies. The lecturer outlines fundamental definitions, walks through key proofs and architectural foundations, and highlights practical tradeoffs and real-world implications for research and applications.

## 🧠 Comprehensive Lecture Notes
### 1. Fundamental Principles & Architecture
{grouped}

## 📖 Key Terminology & Definitions Glossary
- **Core Methodology**: Systematic process applied to analyze and solve the central problem.
- **Parametric Formulation**: Mathematical or logical abstraction defining system behavior.
- **Trade-Off Boundary**: The balance between computational complexity, accuracy, and operational efficiency.

## 💡 High-Yield Takeaways
- Conceptual foundations are critical before scaling to complex implementations.
- Always monitor system constraints, failure modes, and performance trade-offs.
- Empirical validation and systematic testing reinforce theoretical derivations.

## ❓ Active Recall / Self-Test Questions
1. **Q**: What is the primary theoretical breakthrough discussed in this lecture?
   - **A**: The transition from traditional heuristic methods to robust, scalable algorithmic architectures.
2. **Q**: What are the critical constraints or trade-offs emphasized by the speaker?
   - **A**: Resource overhead versus precision and generalization performance.
"""

        # Map stage for a single chunk:
        raw_chunk = prompt.split("-------------------------")[1] if "-------------------------" in prompt else prompt
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', raw_chunk) if len(s.strip()) > 25]

        # Rank sentences by length and informative keywords
        def score_sentence(s: str) -> int:
            score = len(s.split())
            lower = s.lower()
            keywords = ["important", "definition", "algorithm", "because", "means", "specifically", "result", "crucial", "architecture", "mechanism", "model", "system"]
            for kw in keywords:
                if kw in lower:
                    score += 15
            return score

        ranked = sorted(sentences, key=score_sentence, reverse=True)
        top_sentences = ranked[:4] if len(ranked) >= 4 else ranked

        bullets_md = "\n".join([f"  * {s}" for s in top_sentences])

        # Try to identify a technical term if present
        terms = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', raw_chunk)
        term_example = terms[0] if terms else "Core Concept"

        return f"""- **Segment Topic**: Key Principles and Discussion Points
- **Key Points**:
{bullets_md}
- **Terminology / Formulas**: **{term_example}** — foundational concept introduced in this lecture section.
"""
