# Video Prompt Enhancer Agent 🎬

A sophisticated LangGraph-based agent that transforms basic video prompts into three enhanced formats using Google Gemini models. Perfect for creating professional-quality AI video generation prompts.

## Features ✨

- **Three Output Formats**: JSON, XML, and Natural Language
- **Professional Enhancement**: Adds technical details, camera settings, and cinematic elements
- **Google Gemini Integration**: Uses latest Gemini 2.0 Flash model for intelligent enhancement
- **Structured State Management**: Built with Pydantic for type safety and validation
- **Parallel Processing**: Efficient workflow with parallel format generation
- **Fallback Handling**: Robust error handling with graceful degradation

## Quick Start 🚀

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install langgraph langchain-google-genai langchain-core pydantic typing-extensions
```

### 2. Environment Setup

```bash
# Set your Google API key
export GOOGLE_API_KEY="your-google-api-key-here"
```

Get your API key from [Google AI Studio](https://ai.google.dev/tutorials/setup).

### 3. Basic Usage

```python
from langraph_agents import enhance_video_prompt

result = enhance_video_prompt("A cat sitting on a windowsill")
print("JSON Format:", result["json_prompt"])
print("XML Format:", result["xml_prompt"])
print("Natural Language:", result["natural_language_prompt"])
```

## Output Examples 📋

### Input Prompt

```
"A magical transformation scene where furniture appears in an empty room"
```

### JSON Output

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

### XML Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt>
    <description>
        A pristine white living room transforms as furniture magically materializes from an exploding cardboard box, creating a fully furnished space in seconds.
    </description>

    <negative>
        blurry, low resolution, distorted furniture, poor lighting, incomplete transformation
    </negative>

    <camera movement="slight_zoom_in" angle="wide_establishing" lens="35mm">
        Static wide shot that slowly moves closer to capture the dramatic transformation
    </camera>

    <lighting mood="bright_commercial" time="day" quality="studio">
        Clean, bright lighting with soft shadows emphasizing the modern aesthetic
    </lighting>

    <style aesthetic="commercial" rendering="photorealistic">
        Clean, modern commercial aesthetic with high-quality rendering
    </style>
</prompt>
```

### Natural Language Output

```
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

The agent follows a structured workflow:

```
START
  ↓
generate_concept (Enhance basic prompt)
  ↓
enhance_details (Add technical specifications)
  ↓
┌─────────────┬─────────────┬─────────────┐
│ JSON Format │ XML Format  │ Natural Lang│
└─────────────┴─────────────┴─────────────┘
  ↓
finalize (Validate and complete)
  ↓
END
```

### Key Components

- **State Management**: Pydantic-based state schema for type safety
- **Node Functions**: Specialized LLM-powered enhancement nodes
- **Graph Workflow**: LangGraph manages execution flow
- **Error Handling**: Graceful fallbacks for robust operation

## Best Practices 💡

### Prompt Engineering Tips

1. **Be Specific**: Include key visual elements you want enhanced
2. **Set Context**: Mention the mood, setting, or style preferences
3. **Technical Hints**: Include camera movement or lighting preferences
4. **Temporal Elements**: Describe what happens over time

### Good Input Examples

```python
# ✅ Good: Specific with visual details
"A time-lapse of cherry blossoms blooming in a Japanese garden at sunrise"

# ✅ Good: Includes mood and technical elements
"Cinematic slow-motion shot of raindrops on glass with dramatic backlighting"

# ❌ Too vague
"Something cool"

# ❌ Too complex for single prompt
"A 10-minute documentary about climate change with multiple scenes and characters"
```

## Configuration ⚙️

### Environment Variables

```bash
export GOOGLE_API_KEY="your-google-api-key"

# Optional - for debugging
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="your-langsmith-key"
```

### Model Settings

The agent uses `gemini-2.0-flash` with optimized settings:

- **Temperature**: 0.7 (balanced creativity/consistency)
- **Max Tokens**: 2048 (sufficient for detailed outputs)
- **Top P**: 0.9 (diverse but focused responses)

## Error Handling 🛡️

The agent includes comprehensive error handling:

- **Validation Errors**: Graceful fallbacks for invalid responses
- **API Failures**: Retry logic and fallback content
- **Format Errors**: Automatic format cleaning and validation
- **Environment Issues**: Clear error messages for setup problems

## Contributing 🤝

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with proper tests
4. **Follow the coding standards** (Black, isort, type hints)
5. **Submit a pull request**

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black langraph_agents/
isort langraph_agents/

# Type checking
mypy langraph_agents/
```

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

```
Error: Environment not properly configured
```

**Solution**: Set `GOOGLE_API_KEY` environment variable

**2. Import Error**

```
ModuleNotFoundError: No module named 'langraph_agents'
```

**Solution**: Install dependencies with `pip install -r requirements.txt`

**3. Empty Responses**

```
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

**Created with ❤️ for the AI video generation community**
