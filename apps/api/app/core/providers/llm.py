from __future__ import annotations

from typing import List, Dict

from app.config import load_config


def _to_lc_messages(messages: List[Dict[str, str]]):
    """Convert OpenAI-style dict messages to LangChain BaseMessage list."""
    try:
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError("LangChain core is required: 'langchain-core'") from e

    lc_msgs = []
    for m in messages:
        role = (m.get("role") or "user").lower()
        content = m.get("content") or ""
        if role == "system":
            lc_msgs.append(SystemMessage(content=content))
        elif role == "assistant":
            lc_msgs.append(AIMessage(content=content))
        else:
            lc_msgs.append(HumanMessage(content=content))
    return lc_msgs


class LLMClient:
    """LLM client backed by LangChain chat models.

    - openai: langchain_openai.ChatOpenAI
    - ollama: ChatOllama (langchain_ollama or langchain_community)
    """

    def __init__(self):
        self.cfg = load_config()
        self.provider = (self.cfg.llm_provider or "").lower()
        if self.provider == "openai":
            try:
                from langchain_openai import ChatOpenAI  # type: ignore
            except Exception as e:  # pragma: no cover
                raise RuntimeError("LangChain OpenAI integration is required: 'langchain-openai'") from e
            self._chat_cls = ChatOpenAI
            self._model = self.cfg.openai_model or "gpt-4o-mini"
        elif self.provider == "ollama":
            chat_cls = None
            err: Exception | None = None
            try:
                from langchain_ollama import ChatOllama as _ChatOllama  # type: ignore

                chat_cls = _ChatOllama
            except Exception as e1:  # pragma: no cover
                err = e1
                try:
                    from langchain_community.chat_models import ChatOllama as _ChatOllama  # type: ignore

                    chat_cls = _ChatOllama
                except Exception as e2:  # pragma: no cover
                    err = e2
            if chat_cls is None:
                raise RuntimeError(
                    "LangChain Ollama integration is required: 'langchain-ollama' or 'langchain-community'"
                ) from err
            self._chat_cls = chat_cls
            self._model = self.cfg.ollama_model or "llama3"
        else:
            raise ValueError("LLM_PROVIDER must be 'openai' or 'ollama'")

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 800) -> str:
        lc_messages = _to_lc_messages(messages)
        chat = self._chat_cls(model=self._model, temperature=temperature, max_tokens=max_tokens)
        resp = chat.invoke(lc_messages)
        content = getattr(resp, "content", None)
        return str(content) if content is not None else str(resp)
