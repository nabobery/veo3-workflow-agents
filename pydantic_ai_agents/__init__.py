"""
Pydantic AI Agents for generating seed video prompt ideas.

Provides three modes:

- simple: Use web search (DuckDuckGo, optionally Tavily) + LLM to generate 10 ideas
- viral: Let the LLM pick trending topics and research via web tools (Tavily/others) to produce 10 viral ideas
- variations: Given a user topic/idea, produce 10 interesting variations/prompts

These seed ideas are intended to be fed into the LangGraph-based enhancement pipeline in
`langraph_agents/` in subsequent steps.
"""

from .config import Settings, get_settings
from .agents import (
    generate_video_prompt_ideas_simple,
    generate_video_prompt_ideas_viral,
    generate_variations_for_topic,
)

__all__ = [
    "Settings",
    "get_settings",
    "generate_video_prompt_ideas_simple",
    "generate_video_prompt_ideas_viral",
    "generate_variations_for_topic",
]

