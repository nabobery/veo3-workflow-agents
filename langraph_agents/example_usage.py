"""
Example Usage of Video Prompt Enhancer

This module demonstrates how to use the video prompt enhancer agent
with various types of input prompts and shows the different output formats.
"""

import json
from typing import Dict, Any
from .prompt_enhancer_graph import PromptEnhancerWorkflow, enhance_video_prompt
from .config import get_settings
from pydantic import ValidationError


def setup_environment():
    """Set up environment variables for testing"""
    # In a real application, these would be set in your environment
    # For testing, you can uncomment and set your actual API key
    
    # os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"
    
    try:
        get_settings()
        return True
    except ValidationError:
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY='your-api-key-here'")
        return False


def print_separator(title: str):
    """Print a formatted separator"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("="*60)


def print_results(output: Dict[str, Any], prompt: str):
    """Print the enhancement results in a formatted way"""
    print(f"\n📝 Original Prompt:")
    print(f"   {prompt}")
    
    print(f"\n📊 Quality Score: {output['quality_score']:.2f}")
    
    print(f"\n📋 Enhancement Notes:")
    for note in output['enhancement_notes']:
        print(f"   • {note}")
    
    print_separator("JSON FORMAT")
    print(json.dumps(output["json_prompt"], indent=2))
    
    print_separator("XML FORMAT")
    print(output["xml_prompt"])
    
    print_separator("NATURAL LANGUAGE FORMAT")
    print(output["natural_language_prompt"])


def example_basic_usage():
    """Demonstrate basic usage of the prompt enhancer"""
    print_separator("BASIC USAGE EXAMPLE")
    
    # Simple prompt enhancement
    prompt = "A cat sitting on a windowsill"
    
    try:
        output = enhance_video_prompt(prompt)
        print_results(output, prompt)
    except Exception as e:
        print(f"❌ Error: {e}")


def example_workflow_class():
    """Demonstrate using the workflow class directly"""
    print_separator("WORKFLOW CLASS EXAMPLE")
    
    try:
        # Create workflow instance
        workflow = PromptEnhancerWorkflow()
        
        print("📊 Workflow Structure:")
        print(workflow.get_workflow_visualization())
        
        # Enhanced prompt example
        prompt = "A magical transformation scene where furniture appears in an empty room"
        
        print(f"\n🎬 Enhancing prompt: {prompt}")
        output = workflow.enhance_prompt(prompt)
        print_results(output, prompt)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_complex_prompt():
    """Demonstrate with a more complex input prompt"""
    print_separator("COMPLEX PROMPT EXAMPLE")
    
    prompt = """A time-lapse video showing the transformation of a small seed growing into a magnificent oak tree. 
    The scene should capture the changing seasons, with snow, rain, and sunshine. 
    Include birds building nests and wildlife interacting with the tree over the years."""
    
    try:
        output = enhance_video_prompt(prompt)
        print_results(output, prompt)
    except Exception as e:
        print(f"❌ Error: {e}")


def example_technical_prompt():
    """Demonstrate with a technical/cinematic prompt"""
    print_separator("TECHNICAL PROMPT EXAMPLE")
    
    prompt = """Cinematic slow-motion shot of water droplets creating ripples in a still pond, 
    with dramatic lighting and macro lens detail"""
    
    try:
        workflow = PromptEnhancerWorkflow()
        
        # Get full state for inspection
        full_state = workflow.enhance_prompt_with_full_state(prompt)
        
        print(f"📝 Original: {prompt}")
        print(f"\n🎯 Enhanced Concept:")
        print(full_state.enhanced_concept)
        
        print(f"\n🚫 Negative Prompt:")
        print(full_state.negative_prompt)
        
        print(f"\n⚙️ Config Settings:")
        if full_state.config:
            print(f"   Duration: {full_state.config.duration_seconds}s")
            print(f"   Aspect Ratio: {full_state.config.aspect_ratio}")
            print(f"   Camera Movement: {full_state.config.camera.movement}")
            print(f"   Style: {full_state.config.style.aesthetic}")
        
        # Show final outputs
        output = {
            'json_prompt': full_state.json_prompt,
            'xml_prompt': full_state.xml_prompt,
            'natural_language_prompt': full_state.natural_language_prompt,
            'enhancement_notes': full_state.enhancement_notes,
            'quality_score': full_state.enhancement_quality_score or 0.0
        }
        print_results(output, prompt)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def interactive_example():
    """Interactive example where user can input their own prompt"""
    print_separator("INTERACTIVE EXAMPLE")
    
    print("🎬 Enter your video prompt to enhance:")
    print("(or press Enter for a default example)")
    
    user_input = input("> ").strip()
    
    if not user_input:
        user_input = "A sunrise over a mountain lake with mist rising from the water"
        print(f"Using default prompt: {user_input}")
    
    try:
        output = enhance_video_prompt(user_input)
        print_results(output, user_input)
    except Exception as e:
        print(f"❌ Error: {e}")


def run_all_examples():
    """Run all example demonstrations"""
    print("🚀 Video Prompt Enhancer - Example Usage")
    print("=" * 60)
    
    if not setup_environment():
        return
    
    try:
        # Run all examples
        example_basic_usage()
        example_workflow_class()
        example_complex_prompt()
        example_technical_prompt()
        
        # Optional interactive example
        print("\n" + "="*60)
        response = input("Would you like to try the interactive example? (y/n): ")
        if response.lower().startswith('y'):
            interactive_example()
        
        print_separator("ALL EXAMPLES COMPLETED")
        print("✅ All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    import sys
    try:
        run_all_examples()
    except ImportError as e:
        print("Error: This module must be run as part of the langraph_agents package.")
        print("Use: python -m langraph_agents.example_usage")
        print(f"Details: {e}")
        sys.exit(1)