"""
Video Prompt State Management

This module defines the state schema for the video prompt enhancer agent.
It uses Pydantic BaseModel for structured data validation and type safety.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class CameraConfig(BaseModel):
    """Camera configuration for video prompts"""
    movement: str = Field(default="static", description="Camera movement type")
    angle: str = Field(default="medium_shot", description="Camera angle")
    lens: str = Field(default="50mm_equivalent", description="Lens type")


class StyleConfig(BaseModel):
    """Style configuration for video prompts"""
    aesthetic: str = Field(default="photorealistic", description="Visual aesthetic")
    rendering: str = Field(default="high_quality", description="Rendering quality")
    color_palette: Optional[str] = Field(default=None, description="Color palette description")


class ConfigSettings(BaseModel):
    """Configuration settings for video generation"""
    duration_seconds: int = Field(default=8, description="Video duration in seconds")
    aspect_ratio: str = Field(default="16:9", description="Video aspect ratio")
    generate_audio: bool = Field(default=True, description="Whether to generate audio")
    camera: CameraConfig = Field(default_factory=CameraConfig, description="Camera settings")
    style: StyleConfig = Field(default_factory=StyleConfig, description="Style settings")


class VideoPromptState(BaseModel):
    """
    Central state for the video prompt enhancer workflow.
    
    This class represents the final JSON/XML structure and serves as the 
    central state of the graph. It tracks the progression from basic user
    input to enhanced prompts in multiple formats.
    
    Attributes:
        original_prompt: The initial user prompt input
        enhanced_concept: Conceptually enhanced version of the prompt
        json_prompt: JSON-formatted enhanced prompt
        xml_prompt: XML-formatted enhanced prompt  
        natural_language_prompt: Natural language enhanced prompt
        negative_prompt: Negative prompt for avoiding unwanted elements
        config: Technical configuration settings
        enhancement_notes: Notes from the enhancement process
        current_step: Current processing step for workflow tracking
    """
    
    # Core prompt fields
    original_prompt: str = Field(description="The original user input prompt")
    enhanced_concept: Optional[str] = Field(default=None, description="Conceptually enhanced prompt")
    
    # Output format fields
    json_prompt: Optional[Dict[str, Any]] = Field(default=None, description="JSON-formatted prompt")
    xml_prompt: Optional[str] = Field(default=None, description="XML-formatted prompt")
    natural_language_prompt: Optional[str] = Field(default=None, description="Enhanced natural language prompt")
    
    # Supporting fields
    negative_prompt: Optional[str] = Field(default=None, description="Negative prompt for quality control")
    config: Optional[ConfigSettings] = Field(default_factory=ConfigSettings, description="Configuration settings")
    
    # Workflow tracking
    enhancement_notes: List[str] = Field(default_factory=list, description="Enhancement process notes")
    current_step: str = Field(default="initialized", description="Current processing step")
    
    # Quality metrics
    enhancement_quality_score: Optional[float] = Field(default=None, description="Quality score (0-1)")
    
    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        extra = "forbid"  # Prevent additional fields
        json_encoders = {
            # Custom encoders if needed
        }


class WorkflowInputState(TypedDict):
    """Input state for the workflow - simplified for user input"""
    prompt: str


class WorkflowOutputState(TypedDict):
    """Output state containing all enhanced formats"""
    json_prompt: Dict[str, Any]
    xml_prompt: str
    natural_language_prompt: str
    enhancement_notes: List[str]
    quality_score: float
    saved_dir: str