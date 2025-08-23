from __future__ import annotations

import json
import os
from typing import Optional


CONFIG_DIR_ENV = "VEO3_TUI_CONFIG_DIR"
DEFAULT_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "veo3-tui")
CONFIG_FILENAME = "keys.json"


def _config_dir() -> str:
    return os.environ.get(CONFIG_DIR_ENV) or DEFAULT_CONFIG_DIR


def _config_path() -> str:
    return os.path.join(_config_dir(), CONFIG_FILENAME)


class KeyStore:
    def __init__(self, google_api_key: Optional[str], tavily_api_key: Optional[str]):
        self.google_api_key = google_api_key
        self.tavily_api_key = tavily_api_key

    @classmethod
    def load(cls) -> "KeyStore":
        # Prefer environment variables
        google = os.environ.get("GOOGLE_API_KEY")
        tavily = os.environ.get("TAVILY_API_KEY")
        # Then fall back to persisted file
        if not google or not tavily:
            try:
                with open(_config_path(), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    google = google or data.get("GOOGLE_API_KEY")
                    tavily = tavily or data.get("TAVILY_API_KEY")
            except FileNotFoundError:
                pass
        return cls(google, tavily)

    @staticmethod
    def google_api_key_preview() -> str:
        key = os.environ.get("GOOGLE_API_KEY")
        if key:
            return "*" * 8
        try:
            with open(_config_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("GOOGLE_API_KEY"):
                    return "*" * 8
        except FileNotFoundError:
            pass
        return ""

    @staticmethod
    def tavily_api_key_preview() -> str:
        key = os.environ.get("TAVILY_API_KEY")
        if key:
            return "*" * 8
        try:
            with open(_config_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("TAVILY_API_KEY"):
                    return "*" * 8
        except FileNotFoundError:
            pass
        return ""

    @staticmethod
    def save_masked(google_api_key: str, tavily_api_key: str) -> None:
        # If inputs look like masked previews, do not overwrite stored values
        current = {}
        try:
            with open(_config_path(), "r", encoding="utf-8") as f:
                current = json.load(f)
        except FileNotFoundError:
            pass

        new_google = (
            current.get("GOOGLE_API_KEY") if google_api_key.strip().startswith("*") else google_api_key.strip() or None
        )
        new_tavily = (
            current.get("TAVILY_API_KEY") if tavily_api_key.strip().startswith("*") else tavily_api_key.strip() or None
        )

        os.makedirs(_config_dir(), exist_ok=True)
        with open(_config_path(), "w", encoding="utf-8") as f:
            json.dump({
                "GOOGLE_API_KEY": new_google,
                "TAVILY_API_KEY": new_tavily,
            }, f, indent=2)

        # Also set environment for current process
        if new_google:
            os.environ["GOOGLE_API_KEY"] = new_google
        if new_tavily:
            os.environ["TAVILY_API_KEY"] = new_tavily


