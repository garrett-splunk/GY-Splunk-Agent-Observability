"""
LLM helper — chat model factory with readable span names.

INSTRUMENTATION (Exercise 5):
  Pass name="IT Helpdesk Assistant" to ChatOllama / ChatOpenAI so LLM spans
  are labeled clearly in Galileo.
  Reference: ~/Desktop/galileo-golden-demo/helpers/llm_utils.py
"""
import os
from typing import Literal, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

LLMProvider = Literal["local", "hosted"]
SPAN_NAME = "IT Helpdesk Assistant"


def get_chat_model(
    model: Optional[str] = None,
    *,
    temperature: float = 0.1,
    provider: LLMProvider = "local",
    name: str = SPAN_NAME,
) -> BaseChatModel:
    if provider == "hosted":
        resolved = model or os.environ.get("OPENAI_DEFAULT_CHAT_MODEL", "gpt-4o")
        # INSTRUMENTATION (Exercise 5): ensure `name=` is set for Galileo LLM spans
        return ChatOpenAI(
            model=resolved,
            temperature=temperature,
            api_key=os.environ.get("OPENAI_API_KEY"),
            name=name,
        )

    resolved = model or os.environ.get("OLLAMA_DEFAULT_CHAT_MODEL", "gemma4")
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    # INSTRUMENTATION (Exercise 5): ensure `name=` is set for Galileo LLM spans
    return ChatOllama(
        model=resolved,
        temperature=temperature,
        base_url=base_url,
        name=name,
    )
