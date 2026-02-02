"""LLM factory: returns the chat model based on root config (Ollama or Gemini)."""
from langchain_core.language_models.chat_models import BaseChatModel

from config import settings
from logging_config import get_logger

logger = get_logger(__name__)


def get_llm() -> BaseChatModel:
    """Return the configured chat model (Ollama or Gemini)."""
    if settings.llm_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        logger.info(
            "Using LLM provider: %s, model: %s",
            settings.llm_provider,
            settings.llm_model,
        )
        return ChatGoogleGenerativeAI(
            model=settings.llm_model,
            api_key=settings.google_api_key or None,
            temperature=settings.llm_temperature,
        )
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama

        logger.info(
            "Using LLM provider: %s, model: %s",
            settings.llm_provider,
            settings.llm_model,
        )
        return ChatOllama(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            temperature=settings.llm_temperature,
        )
    logger.error(
        "Unknown LLM_PROVIDER=%r; use 'ollama' or 'gemini'",
        settings.llm_provider,
    )
    raise ValueError(
        f"Unknown LLM_PROVIDER={settings.llm_provider!r}; use 'ollama' or 'gemini'"
    )
