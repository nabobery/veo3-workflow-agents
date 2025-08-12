from __future__ import annotations

import argparse
import sys
from typing import Optional, List

from pydantic_core import ValidationError

# Pydantic AI agents: idea generation and storage
from pydantic_ai_agents.agents import (
    generate_video_prompt_ideas_simple,
    generate_video_prompt_ideas_viral,
    generate_variations_for_topic,
)
from pydantic_ai_agents.storage import save_ideas_to_directory
from pydantic_ai_agents.config import get_settings as get_pyai_settings
from pydantic_ai_agents.schemas import IdeaList

# LangGraph agents: enhancement workflow
from langraph_agents import enhance_video_prompt
from langraph_agents.config import get_settings as get_lang_settings


def _generate_ideas(mode: str, topic: Optional[str], n: Optional[int]) -> IdeaList:
    """Dispatch to the appropriate idea generator based on mode."""
    if mode == "simple":
        if not topic or not str(topic).strip():
            raise ValueError("'simple' mode requires a topic")
        return generate_video_prompt_ideas_simple(topic, n)
    if mode == "viral":
        return generate_video_prompt_ideas_viral(topic, n)
    if mode == "variations":
        if not topic or not str(topic).strip():
            raise ValueError("'variations' mode requires a topic")
        return generate_variations_for_topic(topic, n)
    raise ValueError(f"Unknown mode: {mode}")


def _run_pipeline(mode: str, topic: Optional[str], n: Optional[int], max_enhance: Optional[int]) -> int:
    # Touch settings early to surface configuration issues
    get_pyai_settings()
    try:
        # LangGraph requires GOOGLE_API_KEY; surface error early
        get_lang_settings()
    except ValidationError:
        print("Error: GOOGLE_API_KEY environment variable not set for langraph_agents", file=sys.stderr)
        return 1

    # 1) Generate ideas using Pydantic AI agents
    ideas = _generate_ideas(mode, topic, n)

    # Persist the raw ideas JSON for reference
    try:
        saved_file = save_ideas_to_directory(mode or "unknown", topic, ideas)
        print(f"Saved generated ideas to: {saved_file}")
    except Exception as e:
        print(f"Warning: failed to save generated ideas JSON: {e}", file=sys.stderr)

    # 2) Enhance each idea using LangGraph workflow (saves under prompt_outputs/)
    enhanced_dirs: List[str] = []
    items = ideas.ideas
    if max_enhance is not None and max_enhance > 0:
        items = items[:max_enhance]

    for idx, idea in enumerate(items, start=1):
        try:
            print(f"Enhancing idea {idx}/{len(items)}: {idea.title}")
            result = enhance_video_prompt(idea.description)
            saved_dir = result.get("saved_dir") or ""
            if saved_dir:
                enhanced_dirs.append(saved_dir)
                print(f"  → Saved to: {saved_dir}")
        except KeyboardInterrupt:
            print("\nCancelled by user", file=sys.stderr)
            return 130
        except Exception as e:
            print(f"  ! Enhancement failed: {e}", file=sys.stderr)

    if enhanced_dirs:
        print("\nAll enhanced outputs are under 'prompt_outputs/'.")
    else:
        print("\nNo enhanced outputs were saved.", file=sys.stderr)

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate video prompt ideas using pydantic_ai_agents, then enhance them with langraph_agents "
            "and save results under prompt_outputs/."
        )
    )

    # Support either --mode or subcommands (mirror pydantic_ai_agents CLI ergonomics)
    parser.add_argument("--mode", choices=["simple", "viral", "variations"], help="Idea generation mode")
    parser.add_argument("--topic", type=str, help="Topic or user context (required for simple/variations)")
    parser.add_argument("--n", type=int, help="Number of ideas to generate (defaults to settings)")
    parser.add_argument(
        "--max-enhance",
        type=int,
        default=None,
        help="Only enhance the first N generated ideas (default: enhance all)",
    )

    sub = parser.add_subparsers(dest="command")

    p_simple = sub.add_parser("simple", help="Generate ideas with general web search + creativity")
    p_simple.add_argument("topic", type=str, help="Topic or query to explore")
    p_simple.add_argument("--n", type=int, default=None, help="Number of ideas (default: from settings)")
    p_simple.add_argument("--max-enhance", type=int, default=None, help="Only enhance first N ideas")

    p_viral = sub.add_parser("viral", help="Research trending topics and propose ideas")
    p_viral.add_argument("--topic", type=str, default=None, help="Optional user context/topic")
    p_viral.add_argument("--n", type=int, default=None, help="Number of ideas (default: from settings)")
    p_viral.add_argument("--max-enhance", type=int, default=None, help="Only enhance first N ideas")

    p_var = sub.add_parser("variations", help="Generate variations based on a user-provided topic")
    p_var.add_argument("topic", type=str, help="The user's topic or seed idea")
    p_var.add_argument("--n", type=int, default=None, help="Number of ideas (default: from settings)")
    p_var.add_argument("--max-enhance", type=int, default=None, help="Only enhance first N ideas")

    args = parser.parse_args(argv)

    # Resolve mode and parameters regardless of invocation style
    mode = args.mode or args.command
    if mode not in {"simple", "viral", "variations"}:
        parser.print_help()
        return 2

    # Gather topic/n from either root or subparser
    topic = getattr(args, "topic", None)
    n = getattr(args, "n", None)
    max_enhance = getattr(args, "max_enhance", None)

    # Validate numeric inputs
    if n is not None and n <= 0:
        parser.error("'n' must be a positive integer")
    if max_enhance is not None and max_enhance <= 0:
        parser.error("'--max-enhance' must be a positive integer")

    try:
        return _run_pipeline(mode, topic, n, max_enhance)
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


