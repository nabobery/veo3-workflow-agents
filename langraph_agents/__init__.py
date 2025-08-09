"""
Video Prompt Enhancer Agent

A LangGraph-based agent that transforms basic video prompts into three enhanced formats:
- JSON: Structured format for API usage
- XML: Hierarchical format for complex configurations
- Natural Language: Rich narrative description

The agent uses Google Gemini models for intelligent prompt enhancement.
"""

from .prompt_enhancer_graph import (
    PromptEnhancerWorkflow,
    enhance_video_prompt,
    create_prompt_enhancer_graph
)
from .prompt_enhancer_state import (
    VideoPromptState,
    WorkflowInputState,
    WorkflowOutputState,
    ConfigSettings,
    CameraConfig,
    StyleConfig
)

__all__ = [
    "PromptEnhancerWorkflow",
    "enhance_video_prompt", 
    "create_prompt_enhancer_graph",
    "VideoPromptState",
    "WorkflowInputState",
    "WorkflowOutputState",
    "ConfigSettings",
    "CameraConfig",
    "StyleConfig"
]

__version__ = "0.1.0"