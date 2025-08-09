from __future__ import annotations

from typing import List, Optional

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
        try:
            tools.append(_duckduckgo_search_tool())
        except Exception:
            # Non-fatal: continue without DDG
            pass

    if settings.TAVILY_API_KEY and _tavily_search_tool is not None:
        try:
            tools.append(_tavily_search_tool(settings.TAVILY_API_KEY))
        except Exception:
            # Non-fatal: continue if Tavily cannot be constructed
            pass

    return tools


