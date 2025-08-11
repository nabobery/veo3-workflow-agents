# Pydantic AI Agents — Video Prompt Idea Generator 🎥

A lightweight set of Pydantic AI agents that generate seed video prompt ideas in three modes. These ideas are intended to be fed into the `langraph_agents` enhancement workflow later.

## Features ✨

- **Three Modes**
  - **simple**: Web search + LLM creativity → diverse ideas
  - **viral**: Selects trending topics and researches with web tools → viral-leaning ideas with `trend_score`
  - **variations**: Given a user topic → distinct variations/prompts
- **Gemini-only**: Uses Google's Gemini via `GoogleProvider` (GLA or Vertex). Default `gemini-2.5-flash`.
- **Web Tools**: Built-in DuckDuckGo; optional Tavily via `TAVILY_API_KEY`
- **Structured Output**: Returns a validated `IdeaList` schema

## Quick Start 🚀

### 1) Install

```bash
# From repository root
pip install -e .
# Or
uv pip install -e .
```

### 2) Configure environment

Set your Google API key and choose the Gemini model:

```bash
# macOS/Linux (bash/zsh)
export GOOGLE_API_KEY="your-google-api-key"
export PYA_MODEL="gemini-2.5-flash"  # or gemini-2.5-pro

# Windows (PowerShell)
$env:GOOGLE_API_KEY = "your-google-api-key"
$env:PYA_MODEL = "gemini-2.5-flash"  # or gemini-2.5-pro

# To use Vertex AI instead of the Generative Language API (optional):
export GOOGLE_VERTEX=true
# optionally set project/location (or rely on GOOGLE_CLOUD_PROJECT/GOOGLE_CLOUD_LOCATION)
export GOOGLE_PROJECT="your-gcp-project"
export GOOGLE_LOCATION="us-central1"
```

Optional search provider key:

```bash
# Tavily (optional)
export TAVILY_API_KEY="your-tavily-api-key"
# PowerShell
$env:TAVILY_API_KEY = "your-tavily-api-key"
```

### 3) Run the CLI

```bash
# Simple mode (topic required)
pydantic-ai-agents simple "latest trends in technology" --n 10

# Viral mode (topic optional)
pydantic-ai-agents viral --topic "fitness content" --n 10

# Variations mode (topic required)
pydantic-ai-agents variations "AI in healthcare" --n 10
```

By default, runs persist results under a timestamped directory in `generated_prompts/`
(including full JSON and per-idea text files).

Outputs a JSON object with this shape:

```json
{
  "ideas": [
    {
      "title": "Catchy idea title",
      "description": "2-4 sentence description of the video prompt",
      "sources": ["https://example.com/..."],
      "trend_score": 0.82
    }
  ]
}
```

- `trend_score` is only present in viral mode.

### 4) Use from Python

```python
from pydantic_ai_agents import (
    generate_video_prompt_ideas_simple,
    generate_video_prompt_ideas_viral,
    generate_variations_for_topic,
)

ideas = generate_video_prompt_ideas_simple("latest trends in technology", num_ideas=10)
for idea in ideas.ideas:
    print(idea.title)

viral_ideas = generate_video_prompt_ideas_viral("fitness content", num_ideas=10)

variations = generate_variations_for_topic("AI in healthcare", num_ideas=10)
```

## Integrate with LangGraph Enhancer 🔗

Pipe each seed idea into the LangGraph-based enhancer later:

```python
from langraph_agents import enhance_video_prompt
from pydantic_ai_agents import generate_video_prompt_ideas_simple

ideas = generate_video_prompt_ideas_simple("cozy living spaces")
for idea in ideas.ideas:
    enhanced = enhance_video_prompt(idea.description)
    print(enhanced["quality_score"], enhanced["saved_dir"])  # Example fields
```

## Troubleshooting 🔧

- Ensure `GOOGLE_API_KEY` is set and valid (GLA) or Vertex credentials are configured.
- Without Tavily, DuckDuckGo will still provide search signals.
- Outputs must be valid JSON; agents enforce the `{ "ideas": [...] }` shape.

## Reference 📚

- Model selector: `PYA_MODEL` (default `gemini-2.5-flash`, or `gemini-2.5-pro`)
- Optional keys: `TAVILY_API_KEY`

## License 📄

MIT License
