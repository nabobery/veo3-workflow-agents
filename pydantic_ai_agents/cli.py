from __future__ import annotations

import argparse
import json
import sys

from .agents import (
    generate_video_prompt_ideas_simple,
    generate_video_prompt_ideas_viral,
    generate_variations_for_topic,
)
from .config import get_settings
from .storage import save_ideas_to_contents


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pydantic AI Agents: Generate seed video prompt ideas",
    )

    # Support either --mode or subcommands for ergonomics
    parser.add_argument("--mode", choices=["simple", "viral", "variations"], help="Agent mode")
    parser.add_argument("--topic", type=str, help="Topic or user context (required for simple/variations)")
    parser.add_argument("--n", type=int, help="Number of ideas (default: 10)")

    sub = parser.add_subparsers(dest="command")

    # simple
    p_simple = sub.add_parser("simple", help="Use general web search + LLM creativity")
    p_simple.add_argument("topic", type=str, help="Topic or query to explore")
    p_simple.add_argument("--n", type=int, default=None, help="Number of ideas (default: 10)")

    # viral
    p_viral = sub.add_parser("viral", help="Research viral/trending topics and propose ideas")
    p_viral.add_argument("--topic", type=str, default=None, help="Optional user context/topic")
    p_viral.add_argument("--n", type=int, default=None, help="Number of ideas (default: 10)")

    # variations
    p_var = sub.add_parser("variations", help="Generate variations based on a user-provided topic")
    p_var.add_argument("topic", type=str, help="The user's topic or seed idea")
    p_var.add_argument("--n", type=int, default=None, help="Number of ideas (default: 10)")

    args = parser.parse_args(argv)

    try:
        # Touch settings early to surface any configuration errors
        get_settings()

        # Resolve mode
        mode = args.mode or args.command

        # Consolidate arguments from either root or subparser
        topic = getattr(args, "topic", None)
        n = getattr(args, "n", None)

        if mode == "simple":
            if not topic:
                parser.error("'simple' mode requires --topic or a positional topic in the subcommand form")
            result = generate_video_prompt_ideas_simple(topic, n)
        elif mode == "viral":
            result = generate_video_prompt_ideas_viral(topic, n)
        elif mode == "variations":
            if not topic:
                parser.error("'variations' mode requires --topic or a positional topic in the subcommand form")
            result = generate_variations_for_topic(topic, n)
        else:
            parser.print_help()
            return 2

        # Persist JSON to the `contents` directory and print the saved path
        saved_path = save_ideas_to_contents(mode or "unknown", topic, result)
        print(saved_path)
        return 0

    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


