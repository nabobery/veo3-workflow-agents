# Video Prompt Enhancer Agent 🎬

A LangGraph-based agent that transforms basic video prompts into three enhanced formats using Google Gemini models. Ideal for producing professional-quality AI video generation prompts.

## Features ✨

- **Three Output Formats**: JSON, XML, and Natural Language
- **Professional Enhancement**: Adds technical details, camera settings, and cinematic elements
- **Google Gemini Integration**: Default model `gemini-2.5-flash`
- **Structured State Management**: Pydantic models for type safety
- **Parallel Processing**: JSON, XML, and Natural Language are generated in parallel
- **Fallback Handling**: Robust error handling with graceful degradation

## Quick Start 🚀

### 1) Install

From the repository root:

```bash
# Using pip
pip install -e .

# Or with uv
uv pip install -e .
```

### 2) Configure environment

Get an API key from [Google AI Studio](https://ai.google.dev/tutorials/setup) and set it:

```bash
# macOS/Linux (bash/zsh)
export GOOGLE_API_KEY="your-google-api-key"

# Windows (PowerShell)
$env:GOOGLE_API_KEY = "your-google-api-key"
```

Optional overrides:

- `GOOGLE_MODEL` (default: `gemini-2.5-flash`)
- `DEFAULT_TEMPERATURE` (default: `0.7`)

### 3) Run the CLI

Current version is best invoked from inside the package folder:

```bash
cd langraph_agents
python cli.py --prompt "A cat sitting on a windowsill" --format all

# Interactive mode
python cli.py --interactive

# Examples
python cli.py --examples
```

Artifacts are saved under `prompt_outputs/<slug>_<timestamp>_<hash>`.

### 4) Use from Python

```python
from langraph_agents import enhance_video_prompt

result = enhance_video_prompt("A cat sitting on a windowsill")
print("Saved to:", result.get("saved_dir"))
```

## Output Examples 📋

### Input Prompt

```bash
"A magical transformation scene where furniture appears in an empty room"
```

### JSON Output (shape)

```json
{
  "prompt": "A pristine, sterile white living room with polished hardwood floors and floor-to-ceiling windows. A single cardboard box sits center frame. The box suddenly explodes with magical energy as furniture materializes instantly - a modern sofa, coffee tables, bookshelves, and decorative elements appear in perfect choreography over 2-3 seconds.",
  "negative_prompt": "blurry, low resolution, distorted furniture, poor lighting, incomplete transformation, floating objects",
  "config": {
    "duration_seconds": 8,
    "aspect_ratio": "16:9",
    "generate_audio": true,
    "camera": {
      "movement": "slight_zoom_in",
      "angle": "wide_establishing_shot",
      "lens": "35mm_equivalent"
    },
    "style": {
      "aesthetic": "clean_modern_commercial",
      "rendering": "photorealistic_high_quality"
    }
  }
}
```

### XML Output (actual generator structure)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt>
  <description>A richly described enhanced concept...</description>
  <negative>blurry, low quality, distorted</negative>
  <camera movement="..." angle="..." lens="...">Standard camera setup with natural framing</camera>
  <style aesthetic="..." rendering="...">Clean, professional visual style with natural lighting</style>
  
</prompt>
```

### Natural Language Output

```bash
The scene opens in a pristine, sterile white living room with polished hardwood floors reflecting soft, diffused natural light streaming through large floor-to-ceiling windows. The space is completely empty except for a single, modest brown cardboard box positioned precisely in the center of the room. The camera begins with a wide establishing shot at eye level, slowly pushing in with a gentle movement, creating anticipation.

At the 2-second mark, the cardboard box begins to vibrate slightly, its corners lifting as if pressurized from within. The lighting shifts to a warmer, golden tone as the box suddenly erupts in a spectacular burst of motion - not violent, but magical and choreographed. Furniture pieces emerge in perfect synchronization: a sleek modern sofa materializes horizontally, a coffee table slides smoothly into place, and bookshelves unfold vertically against the walls.

The transformation continues as decorative elements cascade through the air in graceful arcs - throw pillows, plants, and warm lighting fixtures clicking on mid-flight before settling into their perfect positions. By the 6-second mark, the magical chaos settles into a perfectly curated, warm living space complete with soft LED lighting creating pools of illumination throughout the now-furnished room.
```

## Advanced Usage 🔧

### Using the Workflow Class

```python
from langraph_agents import PromptEnhancerWorkflow

# Create workflow instance
workflow = PromptEnhancerWorkflow()

# Enhanced control
result = workflow.enhance_prompt("Your prompt here")

# Access full state for debugging
full_state = workflow.enhance_prompt_with_full_state("Your prompt here")
print("Enhancement notes:", full_state.enhancement_notes)
print("Quality score:", full_state.enhancement_quality_score)
```

### Custom Configuration

```python
from langraph_agents import VideoPromptState, ConfigSettings, CameraConfig, StyleConfig

# Create custom initial state
custom_config = ConfigSettings(
    duration_seconds=12,
    aspect_ratio="21:9",
    camera=CameraConfig(
        movement="dynamic_tracking",
        angle="low_angle",
        lens="wide_angle"
    ),
    style=StyleConfig(
        aesthetic="cinematic",
        rendering="ultra_high_quality",
        color_palette="warm_golden_hour"
    )
)

# Use in workflow...
```

## Architecture 🏗️

```bash
START
  ↓
generate_concept (LLM)
  ↓
enhance_details (LLM)
  ↓
┌─────────────────┬────────────────┬─────────────────────────┐
│ generate_json   │ generate_xml   │ generate_natural_language │
└─────────────────┴────────────────┴─────────────────────────┘
  ↓
finalize
  ↓
END
```

### Key Components

- **State**: `prompt_enhancer_state.py`
- **Nodes**: `prompt_enhancer_nodes.py`
- **Graph**: `prompt_enhancer_graph.py`
- **CLI**: `cli.py`
- **Storage**: `storage.py` (writes artifacts to `prompt_outputs/`)

## Configuration ⚙️

- Required: `GOOGLE_API_KEY`
- Optional: `GOOGLE_MODEL` (default `gemini-2.5-flash`), `DEFAULT_TEMPERATURE` (default `0.7`)
- `.env` is supported via pydantic-settings

## Troubleshooting 🔧

- **API key missing**: Set `GOOGLE_API_KEY` as shown above
- **Import errors when using CLI**: Run from inside `langraph_agents/` for now
- **Empty outputs**: Check network/API key; fallbacks will still persist minimal artifacts

## Roadmap 🗺️

- [ ] **Video Platform Integration**: Direct API connections to video generators
- [ ] **Custom Model Support**: Integration with other LLM providers
- [ ] **Template System**: Pre-built templates for common video types
- [ ] **Batch Processing**: Handle multiple prompts efficiently
- [ ] **Quality Metrics**: Enhanced scoring and validation
- [ ] **Web Interface**: Simple web UI for non-technical users

## Troubleshooting 🔧

### Common Issues

**1. API Key Error**

```bash
Error: Environment not properly configured
```

**Solution**: Set `GOOGLE_API_KEY` environment variable

**2. Import Error**

```bash
ModuleNotFoundError: No module named 'langraph_agents'
```

**Solution**: Install dependencies with `pip install -r requirements.txt`

**3. Empty Responses**

```bash
Warning: Missing outputs: ['json', 'xml']
```

**Solution**: Check API key validity and internet connection

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- **LangGraph**: For the excellent graph-based workflow framework
- **Google Gemini**: For powerful language model capabilities
- **Pydantic**: For robust data validation and type safety
- **The AI Video Community**: For inspiration and examples

---

— Created with ❤️ for the AI video generation community
