"""Single source of truth for all configuration and URLs (env-loaded via Pydantic Settings)."""
import logging
from pathlib import Path

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_file = Path(__file__).resolve().parent / ".env"
_logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """All app configuration; loaded from .env at project root."""

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_provider: str = "ollama"
    llm_model: str = "ministral-3:3b"
    llm_temperature: float = 0.0
    ollama_base_url: str = "http://localhost:11434"
    google_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    )

    # SQLite
    sqlite_database: str = "chinook.db"

    # LangSmith (optional)
    langsmith_api_key: str = ""
    langsmith_tracing: str = "false"
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_project: str = ""

    # Logging
    log_level: str = "INFO"

    @model_validator(mode="after")
    def gemini_requires_api_key(self) -> "Settings":
        if self.llm_provider == "gemini" and not (self.google_api_key or "").strip():
            _logger.error(
                "GOOGLE_API_KEY (or GEMINI_API_KEY) is required when LLM_PROVIDER=gemini"
            )
            raise ValueError(
                "GOOGLE_API_KEY (or GEMINI_API_KEY) is required when LLM_PROVIDER=gemini"
            )
        return self


settings = Settings()
_logger.debug("Configuration loaded from %s", _env_file)


def get_sqlite_connection_uri() -> str:
    """Build SQLite connection URI for SQLAlchemy."""
    db_path = Path(__file__).resolve().parent / settings.sqlite_database
    return f"sqlite:///{db_path}"
