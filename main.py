"""
Compatibility shim: orchestrator entry point for backwards compatibility.
Delegates to the combined workflow CLI (workflow_main) so existing scripts
and external runners can still invoke this module directly via 'python main.py'.
For new integrations, use the 'workflow-agents' CLI command instead.
"""

import sys

try:
    from workflow_main import main
except ImportError as e:
    print(f"Error: Failed to import workflow_main module: {e}", file=sys.stderr)
    raise SystemExit(1) from e


if __name__ == "__main__":
    raise SystemExit(main())