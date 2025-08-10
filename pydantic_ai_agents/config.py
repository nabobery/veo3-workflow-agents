from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field, SecretStr


class Settings(BaseSettings):
    """Configuration for Pydantic AI agents.

    Environment variables:
    - GOOGLE_API_KEY: used by Google Gemini via pydantic-ai GoogleProvider (GLA)
    - PYA_MODEL: Gemini model identifier, e.g., 'gemini-2.5-flash'
    - TAVILY_API_KEY: optional, enables Tavily search tool
    - EXA_API_KEY: optional, enables Exa search tool (not required)
    - LINKUP_API_KEY: optional, enables LinkUp search tool (not required)
    - DEFAULT_NUM_IDEAS: default number of ideas to generate (default 10)
    """

    # Gemini-only model selection
    # Valid examples: 'gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash'
    PYA_MODEL: str = Field(
        "gemini-2.5-flash",
        pattern=r"^gemini-[a-z0-9._\-]+$",
        description="Gemini model id, e.g., 'gemini-2.5-pro'",
    )
    GOOGLE_API_KEY: SecretStr | None = None
    TAVILY_API_KEY: SecretStr | None = None
    EXA_API_KEY: SecretStr | None = None
    LINKUP_API_KEY: SecretStr | None = None
    DEFAULT_NUM_IDEAS: int = Field(10, ge=1, le=100, description="Default number of ideas to generate")

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


