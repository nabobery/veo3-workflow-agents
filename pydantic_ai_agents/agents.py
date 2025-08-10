from __future__ import annotations

from typing import List, Optional

import json
import contextlib
from pydantic_ai import Agent

from .config import get_settings
from .tools import build_default_search_tools
from .schemas import IdeaList
from .storage import save_ideas_output
from .prompt_texts import load_prompt_text


def _build_agent(system_prompt: str, extra_tools: Optional[List[object]] = None) -> Agent:
    settings = get_settings()
    tools = build_default_search_tools()
    if extra_tools:
        tools.extend(extra_tools)

    agent = Agent(
        settings.PYA_MODEL,
        tools=tools,
        system_prompt=system_prompt,
    )
    return agent


def _parse_ideas_output(raw_output: object) -> IdeaList:
    """Parse agent output into IdeaList regardless of whether it's a JSON string or Python object.

    Expects a JSON object with shape {"ideas": [...]}.
    """
    if isinstance(raw_output, str):
        return IdeaList.model_validate_json(raw_output)
    if isinstance(raw_output, dict):
        return IdeaList.model_validate(raw_output)
    # Fallback: attempt JSON serialization if the object isn't directly valid
    return IdeaList.model_validate_json(json.dumps(raw_output))


def generate_video_prompt_ideas_simple(topic: str, num_ideas: Optional[int] = None) -> IdeaList:
    """Generate N creative video prompt ideas using general web search + LLM creativity.

    Args:
        topic: Query or area of interest, e.g., "Latest trends in technology".
        num_ideas: Desired idea count (defaults to settings.DEFAULT_NUM_IDEAS)
    """

    settings = get_settings()
    n = settings.DEFAULT_NUM_IDEAS if num_ideas is None else num_ideas

    template = load_prompt_text("simple_search_prompt.txt")
    system_prompt = template.replace("{n}", str(n))

    agent = _build_agent(system_prompt)
    result = agent.run_sync(topic)
    ideas = _parse_ideas_output(result.output)
    with contextlib.suppress(Exception):
        save_ideas_output(mode="simple", context=topic, ideas=ideas)
    return ideas


def generate_video_prompt_ideas_viral(query: Optional[str] = None, num_ideas: Optional[int] = None) -> IdeaList:
    """Generate N viral-oriented video prompt ideas by selecting trendy topics and researching them.

    The agent can pick topics itself if none provided, then uses available search tools
    to find evidence and produce ideas with an estimated trend_score.
    """

    settings = get_settings()
    n = settings.DEFAULT_NUM_IDEAS if num_ideas is None else num_ideas

    base_instruction = load_prompt_text("viral_topic_prompt.txt").replace("{n}", str(n))

    if query and query.strip():
        user_context = f"User context/topic: {query.strip()}\nPrioritize trends related to this context."
    else:
        user_context = "No specific user topic provided. Select high-signal trends yourself."

    system_prompt = base_instruction + "\n" + user_context
    agent = _build_agent(system_prompt)
    result = agent.run_sync("Find viral topics and propose video prompt ideas")
    ideas = _parse_ideas_output(result.output)
    with contextlib.suppress(Exception):
        save_ideas_output(mode="viral", context=(query or ""), ideas=ideas)
    return ideas


def generate_variations_for_topic(topic: str, num_ideas: Optional[int] = None) -> IdeaList:
    """Given a user-provided topic/idea, generate diverse, interesting prompt variations.

    Emphasizes variety in tone, scale, genre, camera treatment, style, and constraints
    while staying faithful to the core concept.
    """

    settings = get_settings()
    n = settings.DEFAULT_NUM_IDEAS if num_ideas is None else num_ideas

    system_prompt = load_prompt_text("topic_variation_prompt.txt").replace("{n}", str(n))

    agent = _build_agent(system_prompt)
    result = agent.run_sync(topic)
    ideas = _parse_ideas_output(result.output)
    with contextlib.suppress(Exception):
        save_ideas_output(mode="variations", context=topic, ideas=ideas)
    return ideas


