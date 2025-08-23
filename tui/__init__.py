"""
Textual TUI package for prompt generation, enhancement, and Veo3 video creation.

This package provides a standalone Textual application that integrates with
`pydantic_ai_agents` and `langraph_agents` in this repository. It includes:

- Settings management for API keys (Google, Tavily) with on-disk storage
- Prompt generation using Pydantic AI agents
- Prompt enhancement using LangGraph
- Video generation via Google's Veo3 API

Run with the CLI entrypoint `veo3-tui` or `python -m tui`.
"""

__all__ = [
    "run",
]

def run() -> int:
    from .app import main
    return main()


