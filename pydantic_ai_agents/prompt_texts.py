from __future__ import annotations

from pathlib import Path


def _prompts_dir() -> Path:
    return Path(__file__).parent / "prompts"


def load_prompt_text(filename: str) -> str:
    path = _prompts_dir() / filename
    return path.read_text(encoding="utf-8")


