"""
CLI entry point for Video Prompt Enhancer.

Provides a simple interface to run examples, interactive mode, or enhance a single prompt.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, Any

from pydantic_core import ValidationError

from config import get_settings
from example_usage import run_all_examples


def _clear_screen() -> None:
    """Clear terminal screen without invoking a shell.

    Uses ANSI escape sequences which are safe and fast on POSIX and modern
    Windows terminals. Falls back to printing newlines if ANSI isn't supported.
    """
    try:
        # Clear screen and move cursor to home position
        print("\033[2J\033[H", end="")
    except Exception:
        # Minimal fallback; no shell invocation
        print("\n" * 100, end="")


def check_environment() -> bool:
    try:
        get_settings()
        return True
    except ValidationError:
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("\nTo get started:")
        print("1. Get an API key from https://ai.google.dev/tutorials/setup")
        print("2. Set the environment variable:")
        print("   export GOOGLE_API_KEY='your-api-key-here'")
        return False


def display_formats(output: Dict[str, Any], format_choice: str) -> None:
    if format_choice in ["json", "all"]:
        print("\n" + "=" * 20 + " JSON FORMAT " + "=" * 20)
        import json

        print(json.dumps(output["json_prompt"], indent=2))

    if format_choice in ["xml", "all"]:
        print("\n" + "=" * 20 + " XML FORMAT " + "=" * 20)
        print(output["xml_prompt"])

    if format_choice in ["natural", "all"]:
        print("\n" + "=" * 20 + " NATURAL LANGUAGE FORMAT " + "=" * 20)
        print(output["natural_language_prompt"])

    # Always show saved location if present
    if "saved_dir" in output and output["saved_dir"]:
        print("\n" + "=" * 20 + " SAVED TO " + "=" * 20)
        print(output["saved_dir"]) 


def enhance_single_prompt(prompt: str, output_format: str, verbose: bool) -> None:
    # Lazy import to avoid heavy deps at CLI help time
    from prompt_enhancer_graph import enhance_video_prompt, PromptEnhancerWorkflow
    print(f"🎬 Enhancing prompt: {prompt}")
    print("=" * 60)

    if verbose:
        workflow = PromptEnhancerWorkflow()
        full_state = workflow.enhance_prompt_with_full_state(prompt)

        print(f"\n📝 Original Prompt:\n   {prompt}")
        print(f"\n🎯 Enhanced Concept:\n   {full_state.enhanced_concept}")
        print(f"\n🚫 Negative Prompt:\n   {full_state.negative_prompt}")
        print(f"\n📊 Quality Score: {full_state.enhancement_quality_score:.2f}")
        print(f"\n📋 Enhancement Steps:")
        for note in full_state.enhancement_notes:
            print(f"   • {note}")

        output = {
            "json_prompt": full_state.json_prompt,
            "xml_prompt": full_state.xml_prompt,
            "natural_language_prompt": full_state.natural_language_prompt,
        }
    else:
        output = enhance_video_prompt(prompt)

    display_formats(output, output_format)


def interactive_mode() -> None:
    from prompt_enhancer_graph import PromptEnhancerWorkflow
    print("🎬 Video Prompt Enhancer - Interactive Mode")
    print("=" * 50)
    print("Enter video prompts to enhance (type 'quit' to exit)")
    print("Commands:")
    print("  'help' - Show this help")
    print("  'examples' - Show example prompts")
    print("  'clear' - Clear screen")
    print("  'quit' - Exit")
    print()

    workflow = PromptEnhancerWorkflow()

    while True:
        try:
            user_input = input("🎥 Enter prompt > ").strip()
            if not user_input:
                continue
            if user_input.lower() == "quit":
                print("👋 Goodbye!")
                break
            if user_input.lower() == "help":
                print("\nCommands:")
                print("  'help' - Show this help")
                print("  'examples' - Show example prompts")
                print("  'clear' - Clear screen")
                print("  'quit' - Exit")
                continue
            if user_input.lower() == "examples":
                show_example_prompts()
                continue
            if user_input.lower() == "clear":
                _clear_screen()
                continue

            print(f"\n🔄 Enhancing: {user_input}")
            result = workflow.enhance_prompt(user_input)
            print(f"\n📊 Quality Score: {result['quality_score']:.2f}")

            format_choice = input("\nShow format (j=json, x=xml, n=natural, a=all): ").lower()
            if format_choice.startswith("j"):
                format_choice = "json"
            elif format_choice.startswith("x"):
                format_choice = "xml"
            elif format_choice.startswith("n"):
                format_choice = "natural"
            else:
                format_choice = "all"

            display_formats(result, format_choice)
            print("\n" + "-" * 50)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.")


def show_example_prompts() -> None:
    examples = [
        "A cat sitting on a windowsill watching rain",
        "Time-lapse of flowers blooming in a garden",
        "Cinematic shot of coffee being poured into a cup",
        "Magical transformation of an empty room into a cozy library",
        "Slow-motion water splash with dramatic lighting",
        "Sunrise over a mountain lake with mist",
        "Urban street scene with people walking in the rain",
        "Close-up of hands kneading bread dough",
        "Bird's eye view of traffic flowing through city intersections",
        "Underwater scene with colorful fish swimming through coral",
    ]

    print("\n💡 Example Prompts:")
    for i, example in enumerate(examples, 1):
        print(f"   {i:2d}. {example}")
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Video Prompt Enhancer - Transform basic prompts into professional video generation prompts"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            """
Examples:
  python -m langraph_agents --prompt "A cat sitting by a window"
  python -m langraph_agents --examples
  python -m langraph_agents --interactive
            """
        ),
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", "-p", type=str, help="The video prompt to enhance")
    group.add_argument("--examples", "-e", action="store_true", help="Run all example demonstrations")
    group.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")

    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "xml", "natural", "all"],
        default="all",
        help="Output format to display (default: all)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output with enhancement details")

    args = parser.parse_args(argv)

    if not check_environment():
        return 1

    try:
        if args.examples:
            # Lazy import to avoid heavy deps at CLI help time
            from example_usage import run_all_examples
            run_all_examples()
        elif args.interactive:
            interactive_mode()
        elif args.prompt:
            enhance_single_prompt(args.prompt, args.format, args.verbose)
        return 0
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


