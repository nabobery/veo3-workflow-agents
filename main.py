"""
Compatibility shim: delegate to package CLI so external runners can still invoke this repo root script.
"""

from langraph_agents.cli import main


if __name__ == "__main__":
    raise SystemExit(main())