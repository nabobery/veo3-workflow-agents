from __future__ import annotations

from typing import List, Optional

import json
import contextlib
import re
import time
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.output import PromptedOutput

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

    # Build a GoogleProvider (GLA only) and a GoogleModel for Gemini-only usage
    api_key = settings.GOOGLE_API_KEY.get_secret_value()
    provider = GoogleProvider(api_key=api_key) if api_key else GoogleProvider()

    model = GoogleModel(
        settings.PYA_MODEL,
        provider=provider,
        settings=GoogleModelSettings(temperature=0.4, google_thinking_config={"thinking_budget": 2048}),
    )

    # Set retries to improve resilience to transient errors
    agent = Agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        output_type=PromptedOutput(
            IdeaList,
            name="IdeaList",
            description="Return { ideas: [ {title, description, sources, trend_score?} ] }."
        ),
        retries=settings.PYA_RETRIES,
        output_retries=None,
    )
    return agent


def _strip_code_fences(text: str) -> str:
    # Extract inner content of a fenced block if present
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # Remove stray backticks if the whole string is fenced without closing/newlines
    return text.strip().strip('`').strip()


def _extract_json_object(text: str) -> str:
    # Grab the substring from the first '{' to the last '}'
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def _parse_ideas_output(raw_output: object) -> IdeaList:
    """Parse agent output into IdeaList regardless of whether it's a JSON string or Python object.

    Expects a JSON object with shape {"ideas": [...]}.
    """
    if isinstance(raw_output, IdeaList):
        return raw_output
    if isinstance(raw_output, str):
        text = raw_output.strip()
        # Attempt direct parse
        try:
            return IdeaList.model_validate_json(text)
        except Exception:
            pass
        # Strip code fences and retry
        try:
            return IdeaList.model_validate_json(_strip_code_fences(text))
        except Exception:
            pass
        # Extract best-effort JSON object and retry
        cleaned = _extract_json_object(_strip_code_fences(text))
        return IdeaList.model_validate_json(cleaned)
    if isinstance(raw_output, dict):
        return IdeaList.model_validate(raw_output)
    # Pydantic models in general
    if hasattr(raw_output, "model_dump"):
        return IdeaList.model_validate(raw_output.model_dump())  # type: ignore[attr-defined]
    # Fallback: attempt JSON serialization if the object isn't directly valid
    return IdeaList.model_validate_json(json.dumps(raw_output))


def _run_agent_with_retries(agent: Agent, user_prompt: str) -> IdeaList:
    settings = get_settings()
    last_err: Exception | None = None
    attempts = max(1, settings.PYA_RETRIES)
    for i in range(attempts):
        try:
            result = agent.run_sync(user_prompt)
            # If structured output is enabled, this is already an IdeaList
            if isinstance(result.output, IdeaList):
                return result.output
            return _parse_ideas_output(result.output)
        except Exception as e:
            last_err = e
            if i < attempts - 1 and settings.PYA_RETRY_BACKOFF_S > 0:
                time.sleep(settings.PYA_RETRY_BACKOFF_S)
    assert last_err is not None
    raise last_err


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
    ideas = _run_agent_with_retries(agent, topic)
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
    ideas = _run_agent_with_retries(agent, "Find viral topics and propose video prompt ideas")
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
    ideas = _run_agent_with_retries(agent, topic)
    return ideas


