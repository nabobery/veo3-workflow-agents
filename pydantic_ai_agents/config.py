from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    PYA_MODEL: str = "google:gemini-2.5-flash"
    TAVILY_API_KEY: str | None = None
    EXA_API_KEY: str | None = None
    LINKUP_API_KEY: str | None = None
    DEFAULT_NUM_IDEAS: int = 10

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()


