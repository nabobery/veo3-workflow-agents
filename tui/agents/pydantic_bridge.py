from __future__ import annotations

from typing import Optional

from pydantic_ai_agents.agents import (
    generate_video_prompt_ideas_simple,
    generate_video_prompt_ideas_viral,
    generate_variations_for_topic,
)
from pydantic_ai_agents.schemas import IdeaList


def generate_ideas(mode: str, topic: Optional[str], n: Optional[int]) -> IdeaList:
    mode = (mode or "").strip().lower()
    if mode == "simple":
        if not topic or not topic.strip():
            raise ValueError("'simple' mode requires a topic")
        return generate_video_prompt_ideas_simple(topic, n)
    if mode == "viral":
        return generate_video_prompt_ideas_viral(topic, n)
    if mode == "variations":
        if not topic or not topic.strip():
            raise ValueError("'variations' mode requires a topic")
        return generate_variations_for_topic(topic, n)
    raise ValueError("Unknown mode. Choose simple, viral, or variations.")


