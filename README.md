# VEO3 Workflow Agents

Workflow agents for AI video prompt enhancement. The first implemented agent is a LangGraph-based Video Prompt Enhancer that transforms a basic prompt into JSON, XML, and natural language outputs using Google Gemini.

- Agent code and detailed docs: `langraph_agents/` (see `langraph_agents/README.md`)

## Requirements

- Python >= 3.11

## Install

```bash
# From repository root
pip install -e .

# Or with uv
uv pip install -e .
```

## Configure environment

Get an API key from Google AI Studio and set it:

```bash
# macOS/Linux
export GOOGLE_API_KEY="your-google-api-key"

# Windows (PowerShell)
$env:GOOGLE_API_KEY = "your-google-api-key"
```

Optional overrides via env:

- `GOOGLE_MODEL` (default: `gemini-2.5-flash`)
- `DEFAULT_TEMPERATURE` (default: `0.7`)

## Quick start

Run the CLI from the package folder (recommended for now due to import paths):

```bash
python langraph_agents/cli.py --prompt "A cat sitting on a windowsill" --format all
```

Interactive mode and examples:

```bash
python langraph_agents/cli.py --interactive
python langraph_agents/cli.py --examples
```

Programmatic usage:

```python
from langraph_agents import enhance_video_prompt

result = enhance_video_prompt("A cat sitting on a windowsill")
print("Saved to:", result.get("saved_dir"))
```

Outputs (JSON, XML, narrative) and metadata are saved under `prompt_outputs/`.

## Validate setup

```bash
python langraph_agents/test_setup.py
```

## Project structure

- `langraph_agents/`: Agent package (graph, nodes, state, CLI, storage)
- `prompt_outputs/`: Saved generations
- `main.py`: Thin wrapper that delegates to the CLI

## Roadmap

- Improve package imports to support `python -m langraph_agents` and installed console script seamlessly
- Add video platform integrations and templates
- Batch processing and quality metrics
- Simple web UI

## License

MIT