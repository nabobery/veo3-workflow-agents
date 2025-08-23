from __future__ import annotations

from typing import Dict, Any
from langraph_agents import enhance_video_prompt


def enhance_prompt(prompt: str) -> Dict[str, Any]:
    if not prompt or not prompt.strip():
        raise ValueError("Prompt is required")
    return enhance_video_prompt(prompt)


