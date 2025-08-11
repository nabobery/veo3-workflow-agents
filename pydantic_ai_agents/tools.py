from __future__ import annotations

from typing import List
import contextlib

try:
    from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool as _duckduckgo_search_tool
except Exception:  # pragma: no cover - optional import shim
    _duckduckgo_search_tool = None  # type: ignore[assignment]

try:
    from pydantic_ai.common_tools.tavily import tavily_search_tool as _tavily_search_tool
except Exception:  # pragma: no cover - optional import shim
    _tavily_search_tool = None  # type: ignore[assignment]

from .config import get_settings


def build_default_search_tools() -> List[object]:
    """Return a list of enabled search tools based on available API keys.

    - Always tries to include DuckDuckGo (no API key required)
    - Optionally includes Tavily if `TAVILY_API_KEY` is set
    """

    settings = get_settings()
    tools: List[object] = []

    if _duckduckgo_search_tool is not None:
        with contextlib.suppress(Exception):
            tools.append(_duckduckgo_search_tool())

    if settings.TAVILY_API_KEY and _tavily_search_tool is not None:
        # unwrap SecretStr if provided
        api_key = (
            settings.TAVILY_API_KEY.get_secret_value()
            if hasattr(settings.TAVILY_API_KEY, "get_secret_value")
            else settings.TAVILY_API_KEY
        )
        with contextlib.suppress(Exception):
            tools.append(_tavily_search_tool(api_key))

    return tools


