"""
Compatibility shim: orchestrator entry. Delegates to combined workflow CLI so
external runners can still invoke this repo root script.
"""

from workflow_main import main


if __name__ == "__main__":
    raise SystemExit(main())