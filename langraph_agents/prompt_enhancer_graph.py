"""
Video Prompt Enhancer Graph

This module builds and compiles the LangGraph workflow for video prompt enhancement.
It creates a linear flow from concept generation through to final output generation.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
import logging

from prompt_enhancer_state import VideoPromptState, WorkflowInputState, WorkflowOutputState
from storage import save_generation_outputs
from prompt_enhancer_nodes import (
    generate_concept,
    enhance_with_details,
    generate_json_format,
    generate_xml_format,
    generate_natural_language_format,
    finalize_results
)
from config import get_settings
from pydantic_core import ValidationError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_prompt_enhancer_graph() -> CompiledStateGraph:
    """
    Build and compile the video prompt enhancer graph.
    
    Creates a linear workflow:
    START -> generate_concept -> enhance_details -> 
    [parallel: json_format, xml_format, natural_language_format] -> 
    finalize_results -> END
    
    Returns:
        CompiledStateGraph: Ready-to-use graph for prompt enhancement
    """
    logger.info("Building prompt enhancer graph...")
    
    # Create the StateGraph with VideoPromptState as the schema
    workflow = StateGraph(VideoPromptState)
    
    # Add all processing nodes
    workflow.add_node("generate_concept", generate_concept)
    workflow.add_node("enhance_details", enhance_with_details)
    workflow.add_node("generate_json", generate_json_format)
    workflow.add_node("generate_xml", generate_xml_format)
    workflow.add_node("generate_natural_language", generate_natural_language_format)
    workflow.add_node("finalize", finalize_results)
    
    # Define the execution flow
    # Linear flow through concept and detail enhancement
    workflow.add_edge(START, "generate_concept")
    workflow.add_edge("generate_concept", "enhance_details")
    
    # Parallel generation of all three output formats
    workflow.add_edge("enhance_details", "generate_json")
    workflow.add_edge("enhance_details", "generate_xml")
    workflow.add_edge("enhance_details", "generate_natural_language")
    
    # All format generators flow to finalization
    workflow.add_edge("generate_json", "finalize")
    workflow.add_edge("generate_xml", "finalize")
    workflow.add_edge("generate_natural_language", "finalize")
    
    # Final edge to END
    workflow.add_edge("finalize", END)
    
    # Compile the workflow
    compiled_graph = workflow.compile()
    
    logger.info("Prompt enhancer graph compiled successfully")
    return compiled_graph


def create_input_state(user_prompt: str) -> VideoPromptState:
    """
    Create an initial VideoPromptState from user input.
    
    Args:
        user_prompt: The original user prompt to enhance
        
    Returns:
        VideoPromptState: Initialized state ready for processing
    """
    return VideoPromptState(
        original_prompt=user_prompt,
        current_step="initialized",
        enhancement_notes=["Workflow initialized"]
    )


def extract_output_state(final_state: VideoPromptState | dict) -> WorkflowOutputState:
    """
    Extract the final output from the completed state.
    
    Args:
        final_state: Completed VideoPromptState
        
    Returns:
        WorkflowOutputState: Clean output with all enhanced formats
    """
    # Support both Pydantic model and plain dict state
    if isinstance(final_state, dict):
        return {
            "json_prompt": final_state.get("json_prompt") or {},
            "xml_prompt": final_state.get("xml_prompt") or "",
            "natural_language_prompt": final_state.get("natural_language_prompt") or "",
            "enhancement_notes": final_state.get("enhancement_notes", []),
            "quality_score": final_state.get("enhancement_quality_score") or 0.0,
            "saved_dir": "",
        }
    else:
        return {
            "json_prompt": final_state.json_prompt or {},
            "xml_prompt": final_state.xml_prompt or "",
            "natural_language_prompt": final_state.natural_language_prompt or "",
            "enhancement_notes": final_state.enhancement_notes,
            "quality_score": final_state.enhancement_quality_score or 0.0,
            "saved_dir": "",
        }


def validate_environment() -> bool:
    """
    Validate that required environment variables are set.
    
    Returns:
        bool: True if environment is properly configured
    """
    try:
        get_settings()
        return True
    except ValidationError as e:
        logger.error(f"Missing required configuration: {e}")
        logger.error("Please set GOOGLE_API_KEY environment variable")
        return False


class PromptEnhancerWorkflow:
    """
    High-level workflow manager for video prompt enhancement.
    
    This class provides a clean interface for running the prompt enhancement
    workflow and handles initialization, execution, and output formatting.
    """
    
    def __init__(self):
        """Initialize the workflow manager."""
        if not validate_environment():
            raise ValueError("Environment not properly configured. Please set required environment variables.")
        
        self.graph = create_prompt_enhancer_graph()
        logger.info("PromptEnhancerWorkflow initialized successfully")
    
    def enhance_prompt(self, user_prompt: str) -> WorkflowOutputState:
        """
        Enhance a user prompt into multiple formats.
        
        Args:
            user_prompt: The original prompt to enhance
            
        Returns:
            WorkflowOutputState: Enhanced prompts in JSON, XML, and natural language formats
            
        Raises:
            ValueError: If the prompt is empty or invalid
            RuntimeError: If the workflow execution fails
        """
        if not user_prompt or not user_prompt.strip():
            raise ValueError("User prompt cannot be empty")
        
        logger.info(f"Starting prompt enhancement for: {user_prompt[:100]}...")
        
        try:
            # Create initial state
            initial_state = create_input_state(user_prompt.strip())

            # Execute the workflow with a simple retry
            final_state = None
            last_err = None
            for attempt in range(2):
                try:
                    final_state = self.graph.invoke(initial_state)
                    break
                except Exception as invoke_err:
                    last_err = invoke_err
                    logger.warning(
                        f"Workflow invoke attempt {attempt + 1} failed: {invoke_err}",
                        exc_info=True,
                    )
            if final_state is None:
                raise last_err  # type: ignore[misc]

            # Extract results
            output = extract_output_state(final_state)

            # Persist to disk
            saved_dir = save_generation_outputs(
                original_prompt=user_prompt.strip(),
                full_state=final_state,
                output=output,
                base_dir="prompt_outputs",
            )
            output["saved_dir"] = saved_dir

            logger.info("Prompt enhancement completed successfully")
            return output

        except Exception as e:
            logger.error("Workflow execution failed", exc_info=True)
            # Attempt to save minimal artifacts for debugging
            try:
                minimal_output = {
                    "json_prompt": {},
                    "xml_prompt": "",
                    "natural_language_prompt": "",
                    "enhancement_notes": [f"Workflow failed: {str(e)}"],
                    "quality_score": 0.0,
                    "saved_dir": "",
                }
                # Construct a lightweight state-like object for storage helper
                class _LiteState:
                    enhanced_concept = None
                    negative_prompt = None
                    config = None

                saved_dir = save_generation_outputs(
                    original_prompt=user_prompt.strip(),
                    full_state=_LiteState(),
                    output=minimal_output,
                    base_dir="prompt_outputs",
                )
                minimal_output["saved_dir"] = saved_dir
                logger.info(f"Saved failure artifacts to: {saved_dir}")
            except Exception:
                pass

            raise RuntimeError(f"Failed to enhance prompt: {str(e)}") from e
    
    def enhance_prompt_with_full_state(self, user_prompt: str) -> VideoPromptState:
        """
        Enhance a prompt and return the full internal state.
        
        Useful for debugging or accessing intermediate results.
        
        Args:
            user_prompt: The original prompt to enhance
            
        Returns:
            VideoPromptState: Complete state with all intermediate and final results
        """
        if not user_prompt or not user_prompt.strip():
            raise ValueError("User prompt cannot be empty")
        
        initial_state = create_input_state(user_prompt.strip())
        return self.graph.invoke(initial_state)
    
    def get_workflow_visualization(self) -> str:
        """
        Get a text representation of the workflow structure.
        
        Returns:
            str: Workflow visualization
        """
        return """
Video Prompt Enhancer Workflow:

START
  ↓
generate_concept (Enhance basic prompt with visual details)
  ↓
enhance_details (Add technical and stylistic specifications)
  ↓
┌─────────────────┬─────────────────┬─────────────────┐
│  generate_json  │  generate_xml   │ generate_natural│
│   (JSON format) │  (XML format)   │ language format │
└─────────────────┴─────────────────┴─────────────────┘
  ↓
finalize (Validate and complete results)
  ↓
END

Output Formats:
- JSON: Structured format for APIs and tools
- XML: Hierarchical format for complex configurations  
- Natural Language: Rich narrative description for human readers
"""


# Convenience function for quick usage
def enhance_video_prompt(user_prompt: str) -> WorkflowOutputState:
    """
    Convenience function to quickly enhance a video prompt.
    
    Args:
        user_prompt: The original prompt to enhance
        
    Returns:
        WorkflowOutputState: Enhanced prompts in all formats
    """
    workflow = PromptEnhancerWorkflow()
    return workflow.enhance_prompt(user_prompt)