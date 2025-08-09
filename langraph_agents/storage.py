"""
Storage utilities for saving prompt generations to disk.

This module creates a directory per generation and writes all relevant
artifacts: original prompt, enhanced concept, negative prompt, JSON, XML,
natural language, and metadata.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def _slugify(text: str, max_length: int = 60) -> str:
    """Create a filesystem-safe, truncated slug from text.

    - Lowercases
    - Replaces non-alphanumerics with hyphens
    - Collapses consecutive hyphens
    - Truncates to max_length preserving word boundaries when possible
    """
    text = text.strip().lower()
    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Collapse multiple hyphens
    text = re.sub(r"-+", "-", text).strip("-")
    if len(text) <= max_length:
        return text or "prompt"

    # Try to cut at last hyphen before limit
    cut = text.rfind("-", 0, max_length)
    if cut == -1:
        cut = max_length
    return (text[:cut] or text[:max_length])


def _unique_suffix(source: str) -> str:
    """Return a short deterministic suffix from a hash of the source text."""
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()  # nosec - non-crypto use
    return digest[:8]


def save_generation_outputs(
    original_prompt: str,
    full_state: Any,
    output: Dict[str, Any],
    base_dir: str = "prompt_outputs",
) -> str:
    """Persist a single generation's inputs and outputs to disk.

    Args:
        original_prompt: The user's original prompt
        full_state: The final VideoPromptState (provides enhanced fields)
        output: The WorkflowOutputState dict returned to the caller
        base_dir: Base directory where per-generation folders are stored

    Returns:
        The absolute path to the directory where files were saved.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(original_prompt)
    suffix = _unique_suffix(original_prompt)

    root = Path.cwd() / base_dir
    generation_dir = root / f"{slug}_{timestamp}_{suffix}"
    generation_dir.mkdir(parents=True, exist_ok=True)

    # Write plain-text artifacts
    (generation_dir / "original_prompt.txt").write_text(original_prompt, encoding="utf-8")
    if getattr(full_state, "enhanced_concept", None):
        (generation_dir / "enhanced_concept.txt").write_text(
            full_state.enhanced_concept, encoding="utf-8"
        )
    if getattr(full_state, "negative_prompt", None):
        (generation_dir / "negative_prompt.txt").write_text(
            full_state.negative_prompt, encoding="utf-8"
        )

    # JSON format
    if output.get("json_prompt") is not None:
        (generation_dir / "json_prompt.json").write_text(
            json.dumps(output["json_prompt"], indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # XML format
    if output.get("xml_prompt") is not None:
        (generation_dir / "xml_prompt.xml").write_text(output["xml_prompt"], encoding="utf-8")

    # Natural language format
    if output.get("natural_language_prompt") is not None:
        (generation_dir / "natural_language_prompt.txt").write_text(
            output["natural_language_prompt"], encoding="utf-8"
        )

    # Metadata and process notes
    meta: Dict[str, Any] = {
        "quality_score": output.get("quality_score"),
        "enhancement_notes": output.get("enhancement_notes", []),
    }
    # Include config if present on full_state
    config = getattr(full_state, "config", None)
    try:
        if config is not None:
            meta["config"] = config.model_dump()
    except Exception:
        pass

    (generation_dir / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return str(generation_dir.resolve())


