from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field, SecretStr


class Settings(BaseSettings):
    """Configuration for Pydantic AI agents.

    Environment variables:
    - OPENAI_API_KEY: used by OpenAI models via pydantic-ai
    - PYA_MODEL: model identifier, e.g., 'openai:gpt-4o-mini'
    - TAVILY_API_KEY: optional, enables Tavily search tool
    - EXA_API_KEY: optional, enables Exa search tool (not required)
    - LINKUP_API_KEY: optional, enables LinkUp search tool (not required)
    - DEFAULT_NUM_IDEAS: default number of ideas to generate (default 10)
    """

    # Prefer Gemini models, aligning with credits availability
    # Valid examples: 'google:gemini-2.5-flash', 'google:gemini-2.5-pro'
    PYA_MODEL: str = Field(
        "google:gemini-2.5-flash",
        pattern=r"^(google|openai|anthropic|groq):[a-z0-9._\-]+$",
        description="Provider-prefixed model id, e.g., 'google:gemini-2.5-pro'",
    )
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


