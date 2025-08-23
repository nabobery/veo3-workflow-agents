# VEO3 Workflow Agents

Workflow agents for AI video prompt enhancement and video generation using Google's Veo3 Fast API. This project combines multiple AI agents to create a comprehensive video generation pipeline:

- **Enhancement agent**: `langraph_agents/` - Technical prompt enhancement with cinematography details
- **Idea generation agents**: `pydantic_ai_agents/` - Creative prompt variations and viral content ideas
- **Veo3 Integration**: Complete notebook workflow for generating videos using Google's latest video AI
- **Interactive Interface**: Jupyter notebook with user-friendly UI for the complete workflow

## 🎬 NEW: Streamlined Veo3 Video Generation Notebook

We've created a streamlined Jupyter notebook that integrates prompt generation, enhancement, and video creation with **zero Google Cloud setup required**:

**`veo3_prompt_generation_workflow.ipynb`** - Streamlined interactive video generation pipeline

### Features:

- 🎭 Generate creative prompt variations using `pydantic_ai_agents`
- ⚡ Enhance prompts with technical details using `langraph_agents`
- 🎬 Generate high-quality videos using Veo3 Fast API
- 🎛️ Interactive UI with customizable settings (duration, aspect ratio, audio)
- 💾 Automatic video saving and playback
- 🔧 Advanced usage examples and batch processing
- ✅ **No Vertex AI or Google Cloud Project required!**

### Quick Start with Notebook:

```bash
# Install dependencies
pip install -e .

# Set up environment variable (only requirement!)
export GOOGLE_API_KEY="your-google-api-key"

# Launch Jupyter Lab
jupyter lab veo3_prompt_generation_workflow.ipynb
```

### Or try the standalone demo:

```bash
# Run the command-line demo
python notebook_demo.py "A cat playing with a ball of yarn in a sunlit room"
```

See **[NOTEBOOK_SETUP.md](NOTEBOOK_SETUP.md)** for detailed setup instructions.

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

**Streamlined Setup - Only Google API Key Required!**

Get an API key from Google AI Studio and set it:

```bash
# macOS/Linux
export GOOGLE_API_KEY="your-google-api-key"

# Windows (PowerShell)
$env:GOOGLE_API_KEY = "your-google-api-key"
```

**API Key Source:**

- Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

**Key Benefits:**

- ✅ **No Google Cloud Project required**
- ✅ **No Vertex AI setup needed**
- ✅ **Single API key for everything**
- ✅ **Simplified authentication**

**Environment Variables:**

- `GOOGLE_API_KEY`: Google API key (required)
- `VEO3_MODEL`: Veo3 model variant (optional, default: `veo-3.0-fast-generate-preview`)
- `GEMINI_MODEL`: Gemini model (optional, default: `gemini-2.5-flash`)
- `TAVILY_API_KEY`: Search enhancement (optional)
- `DEFAULT_TEMPERATURE`: AI temperature (optional, default: `0.7`)

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

### Quick validation (recommended)

```bash
# Test complete Veo3 integration
python test_veo3_integration.py
```

### Legacy validation

```bash
python langraph_agents/test_setup.py
```

### Demo the streamlined workflow

```bash
# Generate enhanced prompts and create a video (no GCP setup required!)
python notebook_demo.py "A cat playing with a ball of yarn in a sunlit room"

# Just test prompt enhancement (no video generation)
python notebook_demo.py "Sunset over mountains" --enhance-only

# Custom video settings
python notebook_demo.py "Robot dancing" --duration 6 --aspect-ratio "9:16" --no-audio
```

## Project structure

`pydantic_ai_agents/`: Idea generation agents and CLI
`langraph_agents/`: Prompt Enhancement agents and CLI
`workflow_main.py`: Orchestrator CLI combining idea generation and enhancement
`main.py`: Delegates to the orchestrator (`workflow_main.main`)
`prompt_outputs/` (created at runtime): Enhanced prompt outputs
`generated_prompts/` (created at runtime): Raw JSON idea lists

## Roadmap

- Improve package imports to support `python -m langraph_agents` and installed console script seamlessly
- Add video platform integrations and templates
- Batch processing and quality metrics
- Simple web UI

## License

MIT
