from __future__ import annotations

from typing import List, Dict

from app.config import load_config


class LLMClient:
    def __init__(self):
        self.cfg = load_config()
        self.provider = (self.cfg.llm_provider or "").lower()
        if self.provider == "openai":
            try:
                from openai import OpenAI  # type: ignore
            except Exception as e:
                raise RuntimeError("openai package is required for OpenAI LLM") from e
            self._openai = OpenAI()
            self._model = self.cfg.openai_model or "gpt-4o-mini"
        elif self.provider == "ollama":
            try:
                import ollama  # type: ignore
            except Exception as e:
                raise RuntimeError("ollama package is required for Ollama LLM") from e
            self._ollama = ollama
            self._model = self.cfg.ollama_model or "llama3"
        else:
            raise ValueError("LLM_PROVIDER must be 'openai' or 'ollama'")

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 800) -> str:
        if self.provider == "openai":
            resp = self._openai.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        else:
            r = self._ollama.chat(model=self._model, messages=messages, options={"temperature": temperature})
            return r["message"]["content"]  # type: ignore[index]
