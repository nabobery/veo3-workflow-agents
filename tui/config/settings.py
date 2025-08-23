"""
Unified configuration settings for the Veo3 Workflow Agents TUI.

This module combines and extends the configuration from both pydantic_ai_agents 
and langraph_agents packages, providing a unified interface for all settings.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

from pydantic import Field, SecretStr, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Unified configuration for Veo3 Workflow Agents TUI.
    
    This class merges settings from both pydantic_ai_agents and langraph_agents,
    adding TUI-specific configuration options.
    """
    
    # === API Keys ===
    GOOGLE_API_KEY: Optional[SecretStr] = Field(
        None, 
        description="Google API key for Gemini models and Video Generation"
    )
    TAVILY_API_KEY: Optional[SecretStr] = Field(
        None, 
        description="Tavily API key for web search functionality"
    )
    EXA_API_KEY: Optional[SecretStr] = Field(
        None, 
        description="Exa API key for enhanced search capabilities"
    )
    LINKUP_API_KEY: Optional[SecretStr] = Field(
        None, 
        description="LinkUp API key for additional search options"
    )
    
    # === Model Configuration ===
    # Pydantic AI Models
    PYA_MODEL: str = Field(
        "gemini-2.5-flash",
        pattern=r"^gemini-[a-z0-9._\-]+$",
        description="Pydantic AI Gemini model identifier"
    )
    
    # LangGraph Models  
    GOOGLE_MODEL: str = Field(
        "gemini-2.5-flash",
        description="LangGraph Google model identifier"
    )
    
    # Video Generation Model
    VEO3_MODEL: str = Field(
        "video-generation-001",
        description="Veo3 video generation model identifier"
    )
    
    # === Model Settings ===
    DEFAULT_TEMPERATURE: float = Field(
        0.7, 
        ge=0.0, 
        le=2.0, 
        description="Default temperature for model inference"
    )
    DEFAULT_NUM_IDEAS: int = Field(
        10, 
        ge=1, 
        le=100, 
        description="Default number of ideas to generate"
    )
    PYA_RETRIES: int = Field(
        3, 
        ge=0, 
        le=10, 
        description="Maximum retry attempts for Pydantic AI agents"
    )
    PYA_RETRY_BACKOFF_S: float = Field(
        1.0, 
        ge=0.0, 
        le=30.0, 
        description="Backoff delay between retries in seconds"
    )
    
    # === TUI Configuration ===
    TUI_THEME: str = Field(
        "dark",
        description="TUI color theme (dark/light)"
    )
    TUI_AUTO_SAVE: bool = Field(
        True,
        description="Automatically save generated content"
    )
    TUI_MAX_HISTORY: int = Field(
        100,
        ge=1,
        le=1000,
        description="Maximum number of items to keep in history"
    )
    
    # === Storage Configuration ===
    OUTPUT_DIR: Path = Field(
        default_factory=lambda: Path.cwd() / "outputs",
        description="Directory for saving generated content"
    )
    CONFIG_DIR: Path = Field(
        default_factory=lambda: Path.home() / ".veo3-tui",
        description="Directory for TUI configuration files"
    )
    
    # === Video Generation Settings ===
    VIDEO_QUALITY: str = Field(
        "high",
        description="Default video quality (low/medium/high)"
    )
    VIDEO_DURATION: int = Field(
        30,
        ge=1,
        le=300,
        description="Default video duration in seconds"
    )
    VIDEO_ASPECT_RATIO: str = Field(
        "16:9",
        description="Default video aspect ratio"
    )
    
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="VEO3_",
    )
    
    @validator("OUTPUT_DIR", "CONFIG_DIR", pre=True)
    def ensure_path_exists(cls, v):
        """Ensure that directories exist."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    def get_google_api_key(self) -> Optional[str]:
        """Get the Google API key as a string."""
        if self.GOOGLE_API_KEY:
            return self.GOOGLE_API_KEY.get_secret_value()
        return None
    
    def get_tavily_api_key(self) -> Optional[str]:
        """Get the Tavily API key as a string."""
        if self.TAVILY_API_KEY:
            return self.TAVILY_API_KEY.get_secret_value()
        return None
    
    def get_exa_api_key(self) -> Optional[str]:
        """Get the Exa API key as a string."""
        if self.EXA_API_KEY:
            return self.EXA_API_KEY.get_secret_value()
        return None
    
    def get_linkup_api_key(self) -> Optional[str]:
        """Get the LinkUp API key as a string."""
        if self.LINKUP_API_KEY:
            return self.LINKUP_API_KEY.get_secret_value()
        return None
    
    def has_required_keys(self) -> bool:
        """Check if all required API keys are present."""
        return self.GOOGLE_API_KEY is not None
    
    def get_missing_keys(self) -> list[str]:
        """Get a list of missing required API keys."""
        missing = []
        if not self.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        return missing
    
    def to_pydantic_ai_settings(self) -> dict:
        """Convert to pydantic_ai_agents compatible settings."""
        return {
            "PYA_MODEL": self.PYA_MODEL,
            "GOOGLE_API_KEY": self.GOOGLE_API_KEY,
            "TAVILY_API_KEY": self.TAVILY_API_KEY,
            "EXA_API_KEY": self.EXA_API_KEY,
            "LINKUP_API_KEY": self.LINKUP_API_KEY,
            "DEFAULT_NUM_IDEAS": self.DEFAULT_NUM_IDEAS,
            "PYA_RETRIES": self.PYA_RETRIES,
            "PYA_RETRY_BACKOFF_S": self.PYA_RETRY_BACKOFF_S,
        }
    
    def to_langraph_settings(self) -> dict:
        """Convert to langraph_agents compatible settings."""
        return {
            "GOOGLE_API_KEY": self.get_google_api_key(),
            "GOOGLE_MODEL": self.GOOGLE_MODEL,
            "DEFAULT_TEMPERATURE": self.DEFAULT_TEMPERATURE,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get the singleton settings instance."""
    return Settings()


def reload_settings() -> Settings:
    """Reload settings from environment/config files."""
    get_settings.cache_clear()
    return get_settings()
