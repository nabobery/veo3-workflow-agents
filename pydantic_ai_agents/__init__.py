"""
Pydantic AI Agents for generating seed video prompt ideas.

Provides three modes:

- simple: Use web search (DuckDuckGo, optionally Tavily) + LLM to generate N ideas (default per Settings.DEFAULT_NUM_IDEAS)
- viral: Let the LLM pick trending topics and research via web tools (DuckDuckGo, optionally Tavily) to produce N viral ideas
- variations: Given a user topic/idea, produce N interesting variations/prompts

These seed ideas are intended to be fed into the LangGraph-based enhancement pipeline in
`langraph_agents/` in subsequent steps.
"""

from .config import Settings, get_settings
from .agents import (
    generate_video_prompt_ideas_simple,
    generate_video_prompt_ideas_viral,
    generate_variations_for_topic,
)
from .schemas import IdeaList

__all__ = [
    "Settings",
    "get_settings",
    "IdeaList",
    "generate_video_prompt_ideas_simple",
    "generate_video_prompt_ideas_viral",
    "generate_variations_for_topic",
]

