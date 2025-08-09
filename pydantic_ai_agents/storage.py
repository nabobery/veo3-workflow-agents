from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .schemas import IdeaList


def _slugify(text: str, max_length: int = 60) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    if len(text) <= max_length:
        return text or "ideas"
    cut = text.rfind("-", 0, max_length)
    if cut == -1:
        cut = max_length
    return text[:cut] or text[:max_length]


def _unique_suffix(source: str) -> str:
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()  # nosec - non-crypto use
    return digest[:8]


def save_ideas_output(
    mode: str,
    context: Optional[str],
    ideas: IdeaList,
    base_dir: str = "generated_prompts",
) -> str:
    """Persist a generation's idea list to disk under `generated_prompts`.

    Creates a timestamped directory using a slug of the context (or mode),
    writes the context, full JSON, and a per-idea text file for readability.

    Returns absolute directory path.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug_source = (context or mode or "ideas").strip()
    slug = _slugify(slug_source)
    suffix = _unique_suffix(slug_source)

    root = Path.cwd() / base_dir
    generation_dir = root / f"{slug}_{timestamp}_{suffix}"
    generation_dir.mkdir(parents=True, exist_ok=True)

    # Write context
    context_text = context or f"mode={mode}"
    (generation_dir / "context.txt").write_text(context_text, encoding="utf-8")

    # Write full JSON
    (generation_dir / "ideas.json").write_text(
        json.dumps(ideas.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Write per-idea txt files
    ideas_dir = generation_dir / "ideas"
    ideas_dir.mkdir(parents=True, exist_ok=True)
    for idx, idea in enumerate(ideas.ideas, start=1):
        rank = f"{idx:03d}"
        title_slug = _slugify(idea.title, max_length=50)
        file_path = ideas_dir / f"{rank}_{title_slug or 'idea'}.txt"
        lines = [
            f"Title: {idea.title}",
            "",
            f"Description:\n{idea.description}",
        ]
        if idea.sources:
            lines.append("")
            lines.append("Sources:")
            for s in idea.sources:
                lines.append(f"- {s}")
        if idea.trend_score is not None:
            lines.append("")
            lines.append(f"Trend Score: {idea.trend_score:.2f}")
        file_path.write_text("\n".join(lines), encoding="utf-8")

    return str(generation_dir.resolve())


