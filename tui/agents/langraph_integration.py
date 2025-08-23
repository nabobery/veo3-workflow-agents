"""
Integration layer for LangGraph agents.

This module provides a unified interface to the langraph_agents package,
handling configuration, initialization, and execution of the prompt enhancement workflow.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

# Add parent directories to path to import from existing packages
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tui.config import get_settings
from tui.utils.errors import APIKeyError, ModelError, ValidationError

# Import the existing langraph_agents
try:
    from langraph_agents.prompt_enhancer_graph import (
        PromptEnhancerWorkflow,
        enhance_video_prompt,
        create_prompt_enhancer_graph,
        validate_environment
    )
    from langraph_agents.prompt_enhancer_state import WorkflowOutputState
    from langraph_agents.config import Settings as LangGraphSettings
    
    LANGRAPH_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Failed to import langraph_agents: {e}")
    LANGRAPH_AVAILABLE = False
    
    # Create mock classes for development
    class WorkflowOutputState:
        def __init__(self):
            self.json_prompt = {}
            self.xml_prompt = ""
            self.natural_language_prompt = ""
            self.enhancement_notes = []
            self.quality_score = 0.0
            self.saved_dir = ""


logger = logging.getLogger(__name__)


class LangGraphManager:
    """
    Manager class for LangGraph prompt enhancement workflow.
    
    This class provides a unified interface to the LangGraph prompt enhancement
    functionality, handling configuration, error management, and result processing.
    """
    
    def __init__(self):
        """Initialize the LangGraph manager."""
        self.settings = get_settings()
        self.workflow = None
        self._validate_setup()
    
    def _validate_setup(self) -> None:
        """Validate that the setup is correct for LangGraph operations."""
        if not LANGRAPH_AVAILABLE:
            raise ImportError("LangGraph agents package is not available")
        
        if not self.settings.get_google_api_key():
            raise APIKeyError("google", "Google API key is required for LangGraph operations")
    
    def _setup_environment(self) -> None:
        """Set up environment variables for the langraph_agents package."""
        # Set environment variables that langraph_agents expects
        if self.settings.get_google_api_key():
            os.environ["GOOGLE_API_KEY"] = self.settings.get_google_api_key()
        
        # Set other configuration
        os.environ["GOOGLE_MODEL"] = self.settings.GOOGLE_MODEL
        os.environ["DEFAULT_TEMPERATURE"] = str(self.settings.DEFAULT_TEMPERATURE)
    
    def _get_workflow(self) -> 'PromptEnhancerWorkflow':
        """
        Get or create the prompt enhancer workflow.
        
        Returns:
            PromptEnhancerWorkflow instance
        """
        if self.workflow is None:
            if not LANGRAPH_AVAILABLE:
                raise ImportError("LangGraph agents package is not available")
            
            self._setup_environment()
            self.workflow = PromptEnhancerWorkflow()
        
        return self.workflow
    
    async def enhance_prompt(self, user_prompt: str) -> WorkflowOutputState:
        """
        Enhance a user prompt using the LangGraph workflow.
        
        Args:
            user_prompt: The original prompt to enhance
        
        Returns:
            WorkflowOutputState containing all enhanced formats
        
        Raises:
            ValidationError: If prompt is invalid
            APIKeyError: If required API keys are missing
            ModelError: If model execution fails
        """
        if not user_prompt or not user_prompt.strip():
            raise ValidationError("user_prompt", user_prompt, "Prompt cannot be empty")
        
        user_prompt = user_prompt.strip()
        
        if not LANGRAPH_AVAILABLE:
            # Return mock data for development
            mock_result = WorkflowOutputState()
            mock_result.json_prompt = {
                "prompt": user_prompt,
                "style": "cinematic",
                "duration": 30,
                "quality": "high"
            }
            mock_result.xml_prompt = f"""<?xml version="1.0"?>
<video_prompt>
    <text>{user_prompt}</text>
    <style>cinematic</style>
    <duration>30</duration>
    <quality>high</quality>
</video_prompt>"""
            mock_result.natural_language_prompt = f"Create a cinematic-style video lasting 30 seconds with high quality, depicting: {user_prompt}"
            mock_result.enhancement_notes = ["Mock enhancement applied", "Added cinematic style", "Set duration to 30 seconds"]
            mock_result.quality_score = 0.85
            mock_result.saved_dir = "/mock/output/dir"
            
            return mock_result
        
        try:
            workflow = self._get_workflow()
            result = workflow.enhance_prompt(user_prompt)
            return result
        
        except Exception as e:
            logger.error(f"Failed to enhance prompt: {e}", exc_info=True)
            self._handle_error(e)
    
    async def enhance_prompt_with_full_state(self, user_prompt: str) -> Dict[str, Any]:
        """
        Enhance a prompt and return the full internal state.
        
        Args:
            user_prompt: The original prompt to enhance
        
        Returns:
            Dictionary containing the full workflow state
        
        Raises:
            ValidationError: If prompt is invalid
            APIKeyError: If required API keys are missing
            ModelError: If model execution fails
        """
        if not user_prompt or not user_prompt.strip():
            raise ValidationError("user_prompt", user_prompt, "Prompt cannot be empty")
        
        user_prompt = user_prompt.strip()
        
        if not LANGRAPH_AVAILABLE:
            # Return mock data for development
            return {
                "original_prompt": user_prompt,
                "enhanced_concept": f"Enhanced version of: {user_prompt}",
                "json_prompt": {"prompt": user_prompt, "style": "mock"},
                "xml_prompt": f"<prompt>{user_prompt}</prompt>",
                "natural_language_prompt": f"Enhanced: {user_prompt}",
                "enhancement_notes": ["Mock enhancement"],
                "quality_score": 0.8
            }
        
        try:
            workflow = self._get_workflow()
            result = workflow.enhance_prompt_with_full_state(user_prompt)
            
            # Convert to dictionary if it's a Pydantic model
            if hasattr(result, 'model_dump'):
                return result.model_dump()
            elif hasattr(result, '__dict__'):
                return result.__dict__
            else:
                return {"state": str(result)}
        
        except Exception as e:
            logger.error(f"Failed to enhance prompt with full state: {e}", exc_info=True)
            self._handle_error(e)
    
    def get_workflow_visualization(self) -> str:
        """
        Get a text representation of the workflow structure.
        
        Returns:
            String containing workflow visualization
        """
        if not LANGRAPH_AVAILABLE:
            return """
Mock LangGraph Workflow:

START
  ↓
generate_concept (Mock concept generation)
  ↓
enhance_details (Mock detail enhancement)
  ↓
┌─────────────────┬─────────────────┬─────────────────┐
│  generate_json  │  generate_xml   │ generate_natural│
│   (JSON format) │  (XML format)   │ language format │
└─────────────────┴─────────────────┴─────────────────┘
  ↓
finalize (Mock validation and completion)
  ↓
END

Note: This is a mock visualization. LangGraph agents package is not available.
"""
        
        try:
            workflow = self._get_workflow()
            return workflow.get_workflow_visualization()
        except Exception as e:
            logger.error(f"Failed to get workflow visualization: {e}")
            return f"Error getting workflow visualization: {str(e)}"
    
    def _handle_error(self, error: Exception) -> None:
        """
        Handle and re-raise errors with appropriate TUI error types.
        
        Args:
            error: The original error to handle
        
        Raises:
            Appropriate TUI error type based on the original error
        """
        error_msg = str(error).lower()
        
        # Check for API key errors
        if "api key" in error_msg or "authentication" in error_msg:
            raise APIKeyError("google", str(error))
        
        # Check for environment errors
        if "environment" in error_msg or "configuration" in error_msg:
            raise APIKeyError("google", str(error))
        
        # Check for model errors
        if "model" in error_msg or "gemini" in error_msg:
            raise ModelError(self.settings.GOOGLE_MODEL, str(error))
        
        # Re-raise as generic model error for other cases
        raise ModelError(self.settings.GOOGLE_MODEL, str(error))
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models for LangGraph.
        
        Returns:
            List of available model names
        """
        return [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of LangGraph integration.
        
        Returns:
            Dictionary containing status information
        """
        status = {
            "available": LANGRAPH_AVAILABLE,
            "google_api_key": bool(self.settings.get_google_api_key()),
            "current_model": self.settings.GOOGLE_MODEL,
            "default_temperature": self.settings.DEFAULT_TEMPERATURE,
            "workflow_initialized": self.workflow is not None,
        }
        
        # Check if minimum requirements are met
        status["ready"] = (
            status["available"] and 
            status["google_api_key"]
        )
        
        # Validate environment if LangGraph is available
        if LANGRAPH_AVAILABLE:
            try:
                self._setup_environment()
                status["environment_valid"] = validate_environment()
            except Exception as e:
                status["environment_valid"] = False
                status["environment_error"] = str(e)
        else:
            status["environment_valid"] = False
        
        return status
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the current configuration and return any issues.
        
        Returns:
            List of validation error messages (empty if no issues)
        """
        issues = []
        
        if not LANGRAPH_AVAILABLE:
            issues.append("LangGraph agents package is not available")
        
        if not self.settings.get_google_api_key():
            issues.append("Google API key is not configured")
        
        if self.settings.GOOGLE_MODEL not in self.get_available_models():
            issues.append(f"Model '{self.settings.GOOGLE_MODEL}' is not in the list of available models")
        
        if self.settings.DEFAULT_TEMPERATURE < 0 or self.settings.DEFAULT_TEMPERATURE > 2:
            issues.append("Default temperature should be between 0 and 2")
        
        # Try to validate environment if LangGraph is available
        if LANGRAPH_AVAILABLE:
            try:
                self._setup_environment()
                if not validate_environment():
                    issues.append("LangGraph environment validation failed")
            except Exception as e:
                issues.append(f"LangGraph environment validation error: {str(e)}")
        
        return issues
    
    def reset_workflow(self) -> None:
        """Reset the workflow instance to force re-initialization."""
        self.workflow = None
