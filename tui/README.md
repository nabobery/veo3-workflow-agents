# Veo3 Workflow Agents TUI

A professional Terminal User Interface (TUI) for AI-powered video content creation using Veo3, built with Textual, Pydantic AI, and LangGraph.

## Features

### 🎯 Core Capabilities

- **Prompt Generation**: Generate creative video prompt ideas using Pydantic AI agents
- **Prompt Enhancement**: Enhance prompts using sophisticated LangGraph workflows
- **Video Creation**: Generate videos using Google's Veo3 models
- **Configuration Management**: Secure API key storage and settings management

### 🖥️ User Interface

- **Modern TUI Design**: Built with Textual for a responsive, terminal-based interface
- **Tabbed Navigation**: Easy switching between different workflows
- **Real-time Status**: Live updates on system status and operation progress
- **Error Handling**: Comprehensive error reporting with suggested actions
- **Responsive Layout**: Adapts to different terminal sizes

### 🔧 Technical Features

- **Multiple Storage Backends**: Environment variables, system keyring, or encrypted files
- **Async Architecture**: Non-blocking UI with async operations
- **Professional Styling**: Material Design-inspired color scheme
- **Comprehensive Validation**: Input validation for all user data
- **Extensible Design**: Modular architecture for easy extension

## Installation

### Prerequisites

- Python 3.11 or higher
- Google API key for Gemini models and video generation
- Optional: Tavily, Exa, or LinkUp API keys for enhanced search

### Install Dependencies

```bash
# Install the package with all dependencies
pip install -e .

# Or install additional dependencies manually
pip install textual cryptography keyring
```

## Quick Start

### 1. Launch the TUI

```bash
# Using the installed script
veo3-tui

# Or run directly
python -m tui.main
```

### 2. Configure API Keys

1. Navigate to the **Settings** tab (F10)
2. Enter your API keys:
   - **Google API Key** (Required): For Gemini models and video generation
   - **Tavily API Key** (Optional): For enhanced web search
   - **Exa API Key** (Optional): For additional search capabilities
   - **LinkUp API Key** (Optional): For more search options
3. Click **Save Settings**

### 3. Start Creating

1. **Generate Tab**: Create prompt ideas using AI agents
2. **Enhance Tab**: Improve prompts with LangGraph workflows
3. **Create Video Tab**: Generate videos using Veo3 models

## Usage Guide

### Dashboard

The main dashboard provides:

- System status overview
- Quick action buttons
- Usage statistics
- Recent activity log

### Prompt Generation

Three types of generation available:

- **Simple Search**: Basic prompt generation with web search
- **Viral Topics**: Generate trending video ideas
- **Topic Variations**: Create variations of a specific topic

### Prompt Enhancement

LangGraph-powered enhancement that provides:

- **JSON Format**: Structured prompt data
- **XML Format**: Hierarchical prompt structure
- **Natural Language**: Rich narrative descriptions
- **Enhancement Notes**: Detailed improvement explanations

### Video Generation

Create videos with customizable parameters:

- **Duration**: 1-300 seconds
- **Quality**: Low, Medium, High, Ultra
- **Aspect Ratio**: 16:9, 9:16, 1:1, 4:3, 3:4
- **Style**: Cinematic, Photorealistic, Animated, Artistic

## Configuration

### API Key Storage

The TUI supports multiple storage methods (in priority order):

1. **Environment Variables**

   ```bash
   export GOOGLE_API_KEY="your-key-here"
   export TAVILY_API_KEY="your-key-here"
   # Or with VEO3_ prefix
   export VEO3_GOOGLE_API_KEY="your-key-here"
   ```

2. **System Keyring** (Recommended)

   - Secure storage using your OS keyring
   - Configured through the Settings screen

3. **Encrypted File Storage**

   - AES-encrypted local file storage
   - Automatic key generation per user

4. **Plain File Storage** (Development only)
   - Unencrypted JSON file
   - Not recommended for production

### Configuration File

Settings are stored in `~/.veo3-tui/` directory:

- `api_keys.json`: Plain text API keys (if used)
- `api_keys.enc`: Encrypted API keys
- `.encryption_key`: Encryption key for encrypted storage

### Environment Variables

All settings can be overridden with environment variables:

```bash
# API Keys
VEO3_GOOGLE_API_KEY="your-google-key"
VEO3_TAVILY_API_KEY="your-tavily-key"

# Model Configuration
VEO3_PYA_MODEL="gemini-2.5-flash"
VEO3_GOOGLE_MODEL="gemini-2.5-flash"
VEO3_VEO3_MODEL="video-generation-001"

# Application Settings
VEO3_TUI_THEME="dark"
VEO3_OUTPUT_DIR="/path/to/output"
VEO3_VIDEO_QUALITY="high"
VEO3_VIDEO_DURATION="30"
```

## Keyboard Shortcuts

| Key             | Action                       |
| --------------- | ---------------------------- |
| `q` or `Ctrl+C` | Quit application             |
| `F1`            | Show help                    |
| `F10`           | Go to settings               |
| `Ctrl+R`        | Refresh application state    |
| `Tab`           | Navigate between UI elements |
| `Enter`         | Activate buttons/inputs      |
| `Esc`           | Close modals/go back         |

## Architecture

### Package Structure

```
tui/
├── __init__.py              # Package initialization
├── main.py                  # Main application entry point
├── config/                  # Configuration management
│   ├── settings.py         # Unified settings class
│   └── api_keys.py         # Secure API key management
├── screens/                 # TUI screens
│   ├── main_screen.py      # Dashboard
│   ├── settings_screen.py  # Configuration
│   ├── prompt_generation_screen.py
│   ├── prompt_enhancement_screen.py
│   └── video_generation_screen.py
├── agents/                  # AI agent integration
│   ├── pydantic_integration.py
│   ├── langraph_integration.py
│   └── video_generator.py
├── utils/                   # Utilities
│   ├── errors.py           # Custom exceptions
│   ├── validators.py       # Input validation
│   └── helpers.py          # Helper functions
├── widgets/                 # Custom widgets
└── styles/
    └── main.tcss           # Textual CSS styles
```

### Key Components

#### Configuration Management

- **Unified Settings**: Single configuration class merging all agent settings
- **Secure Storage**: Multiple storage backends with encryption support
- **Validation**: Input validation with clear error messages

#### Agent Integration

- **Pydantic AI Manager**: Wrapper for existing pydantic_ai_agents
- **LangGraph Manager**: Integration with langraph_agents workflows
- **Video Generator**: Veo3 model integration with mock support

#### Error Handling

- **Custom Exceptions**: Specific error types for different failure modes
- **User Feedback**: Clear error messages with suggested actions
- **Graceful Degradation**: Continue operation when possible

## Development

### Mock Mode

When AI packages are not available, the TUI runs in mock mode:

- Generates sample data for development
- Allows UI testing without API keys
- Maintains full functionality for testing

### Testing

```bash
# Run with mock data (no API keys needed)
python -m tui.main

# Test individual components
python -c "from tui.config import get_settings; print(get_settings())"
```

### Development Setup

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Run with Textual development tools
textual run --dev tui.main:Veo3WorkflowApp
```

## Troubleshooting

### Common Issues

1. **"google-genai package not available"**

   - Install: `pip install google-genai`
   - Check version compatibility

2. **"API key errors"**

   - Verify API key format and validity
   - Check environment variables
   - Use Settings screen to reconfigure

3. **"Permission denied" for config directory**

   - Check `~/.veo3-tui/` permissions
   - Run: `chmod 755 ~/.veo3-tui/`

4. **Import errors for agent packages**
   - Ensure parent packages are installed
   - Check Python path configuration
   - Run in mock mode for testing

### Debug Mode

```bash
# Enable debug logging
export VEO3_LOG_LEVEL="DEBUG"
python -m tui.main

# View logs
tail -f ~/.veo3-tui/debug.log
```

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Document all public functions
- Add comprehensive error handling

### Testing

- Test with and without API keys
- Verify all UI components
- Test error conditions
- Check responsive layout

### Extending

- Add new screens in `screens/` directory
- Create custom widgets in `widgets/`
- Add new agent integrations in `agents/`
- Update CSS in `styles/main.tcss`

## License

This project is part of the veo3-workflow-agents package. See the main project LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs for detailed error information
3. Open an issue in the main project repository

---

Built with ❤️ using [Textual](https://textual.textualize.io/), [Pydantic AI](https://ai.pydantic.dev/), and [LangGraph](https://langchain-ai.github.io/langgraph/).
