# VEO3 Workflow Agents

Workflow agents for AI video prompt enhancement. The first implemented agent is a LangGraph-based Video Prompt Enhancer that transforms a basic prompt into JSON, XML, and natural language outputs using Google Gemini. A combined orchestrator now generates ideas with `pydantic_ai_agents` and enhances them with `langraph_agents` in one command.

- Enhancement agent: `langraph_agents/` (see `langraph_agents/README.md`)
- Idea generation agents: `pydantic_ai_agents/`

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

### Orchestrated workflow (generate ideas → enhance prompts)

Use the combined CLI to first generate ideas with `pydantic_ai_agents`, then enhance each idea using `langraph_agents`. Enhanced outputs are stored under `prompt_outputs/` automatically.

```bash
# Simple mode (topic required), generate 10, enhance first 5
workflow-agents --mode simple --topic "latest trends in technology" --n 10 --max-enhance 5

# Viral mode (topic optional), enhance all
workflow-agents --mode viral --n 10

# Variations mode (topic required)
workflow-agents --mode variations --topic "AI in healthcare" --n 8

# Subcommand style is also supported
workflow-agents simple "fitness content" --n 10 --max-enhance 5
workflow-agents viral --topic "creator economy" --n 10
workflow-agents variations "cinematic water shots" --n 6
```

You can also run the repo entrypoint which now delegates to the orchestrator:

```bash
python main.py --mode simple --topic "cozy interiors" --n 5 --max-enhance 3
```

The raw idea list is saved under `generated_prompts/`, and each enhanced prompt is saved by `langraph_agents` under `prompt_outputs/<slug>_<timestamp>_<hash>`.

### Enhancement agent only (direct)

```bash
python langraph_agents/cli.py --prompt "A cat sitting on a windowsill" --format all
# Interactive mode and examples
python langraph_agents/cli.py --interactive
python langraph_agents/cli.py --examples
```

Programmatic usage:

```python
from langraph_agents import enhance_video_prompt

result = enhance_video_prompt("A cat sitting on a windowsill")
print("Saved to:", result.get("saved_dir"))
```

## Validate setup

```bash
python langraph_agents/test_setup.py
```

## Project structure

- `langraph_agents/`: Agent package (graph, nodes, state, CLI, storage)
- `pydantic_ai_agents/`: Idea generation agents and CLI
- `prompt_outputs/`: Saved generations
- `generated_prompts/`: Saved idea lists (raw JSON) from `pydantic_ai_agents`
- `workflow_main.py`: Orchestrator CLI combining idea generation and enhancement
- `main.py`: Delegates to the orchestrator (`workflow_main.main`)

## Roadmap

- Improve package imports to support `python -m langraph_agents` and installed console script seamlessly
- Add video platform integrations and templates
- Batch processing and quality metrics
- Simple web UI

## License

MIT
