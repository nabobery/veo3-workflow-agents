from __future__ import annotations

from pathlib import Path
from importlib.resources import files as pkg_files


def _prompts_dir():
    # Return a Traversable for zip-safe resource access
    return pkg_files(__package__) / "prompts"


def load_prompt_text(filename: str) -> str:
    # Prevent directory traversal and ensure we only access known files
    safe_name = Path(filename).name
    path = _prompts_dir() / safe_name
    return path.read_text(encoding="utf-8")


