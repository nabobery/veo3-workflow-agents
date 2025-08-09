"""
Test Setup for Video Prompt Enhancer

Simple validation script to test the installation and basic functionality.
Run this after setting up your environment to ensure everything is working.
"""

import os
import sys
import traceback
from pydantic import ValidationError
from pathlib import Path

from langraph_agents.config import get_settings

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test core dependencies
        from langgraph.version import __version__
        print(f"  ✅ langgraph {__version__}")
        
        import langchain_google_genai
        print(f"  ✅ langchain_google_genai")
        
        import langchain_core
        print(f"  ✅ langchain_core")
        
        import pydantic
        print(f"  ✅ pydantic {pydantic.__version__}")
        
        # Test our modules
        from langraph_agents.prompt_enhancer_state import VideoPromptState, ConfigSettings
        print("  ✅ prompt_enhancer_state")
        
        from langraph_agents.prompt_enhancer_nodes import generate_concept, initialize_llm
        print("  ✅ prompt_enhancer_nodes")
        
        from langraph_agents.prompt_enhancer_graph import PromptEnhancerWorkflow
        print("  ✅ prompt_enhancer_graph")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print("\nPlease install missing dependencies:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_environment():
    """Test environment configuration"""
    print("\n🔧 Testing environment...")
    
    try:
        settings = get_settings()
        # Mask the key for security
        api_key = settings.GOOGLE_API_KEY
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"  ✅ GOOGLE_API_KEY set ({masked_key})")
        return True
    except ValidationError:
        print("  ❌ GOOGLE_API_KEY not set")
        print("\nTo set your API key:")
        print("1. Get an API key from https://ai.google.dev/tutorials/setup")
        print("2. Set the environment variable:")
        print("   export GOOGLE_API_KEY='your-api-key-here'")
        return False


def test_state_creation():
    """Test state creation and validation"""
    print("\n📊 Testing state creation...")
    
    try:
        from prompt_enhancer_state import VideoPromptState, ConfigSettings
        
        # Test basic state creation
        state = VideoPromptState(
            original_prompt="Test prompt",
            current_step="initialized"
        )
        print("  ✅ Basic state creation")
        
        # Test state with config
        config = ConfigSettings(
            duration_seconds=10,
            aspect_ratio="16:9"
        )
        state_with_config = VideoPromptState(
            original_prompt="Test prompt with config",
            config=config
        )
        print("  ✅ State with configuration")
        
        # Test state validation
        try:
            invalid_state = VideoPromptState()  # Should fail - missing required field
            print("  ❌ State validation failed - should have required original_prompt")
            return False
        except Exception:
            print("  ✅ State validation working (correctly rejected invalid state)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ State creation error: {e}")
        traceback.print_exc()
        return False


def test_llm_initialization():
    """Test LLM initialization (without API call)"""
    print("\n🤖 Testing LLM initialization...")
    
    try:
        from langraph_agents.prompt_enhancer_nodes import initialize_llm
        
        llm = initialize_llm()
        print("  ✅ LLM initialized successfully")
        print(f"  📝 Model: {llm.model}")
        print(f"  🌡️  Temperature: {llm.temperature}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ LLM initialization error: {e}")
        return False


def test_workflow_creation():
    """Test workflow graph creation (without execution)"""
    print("\n🔄 Testing workflow creation...")
    
    try:
        from langraph_agents.prompt_enhancer_graph import create_prompt_enhancer_graph, PromptEnhancerWorkflow
        
        # Test graph creation
        graph = create_prompt_enhancer_graph()
        print("  ✅ Graph compiled successfully")
        
        # Test workflow class
        try:
            workflow = PromptEnhancerWorkflow()
            print("  ✅ Workflow class initialized")
            
            # Test visualization
            viz = workflow.get_workflow_visualization()
            print("  ✅ Workflow visualization generated")
        except ValidationError:
            print("  ⚠️  Skipping workflow initialization (no API key)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Workflow creation error: {e}")
        traceback.print_exc()
        return False


def test_complete_workflow():
    """Test a complete workflow execution (requires API key)"""
    print("\n🎬 Testing complete workflow...")
    
    try:
        get_settings()
    except ValidationError:
        print("  ⚠️  Skipping workflow test (no GOOGLE_API_KEY)")
        return True
    
    try:
        from langraph_agents.prompt_enhancer_graph import enhance_video_prompt
        
        # Simple test prompt
        test_prompt = "A simple test scene"
        
        print(f"  🔄 Testing with prompt: '{test_prompt}'")
        result = enhance_video_prompt(test_prompt)
        
        # Validate result structure
        required_keys = ['json_prompt', 'xml_prompt', 'natural_language_prompt', 'enhancement_notes', 'quality_score']
        for key in required_keys:
            if key not in result:
                print(f"  ❌ Missing key in result: {key}")
                return False
            print(f"  ✅ Result contains {key}")
        
        print("  ✅ Complete workflow test passed!")
        print(f"  📊 Quality score: {result['quality_score']:.2f}")
        print(f"  📝 Enhancement notes: {len(result['enhancement_notes'])} items")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Workflow test error: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and provide summary"""
    print("🧪 Video Prompt Enhancer - Setup Validation")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Environment Tests", test_environment),
        ("State Creation Tests", test_state_creation),
        ("LLM Initialization Tests", test_llm_initialization),
        ("Workflow Creation Tests", test_workflow_creation),
        ("Complete Workflow Tests", test_complete_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready to use.")
        print("\nNext steps:")
        print("1. Try the examples: python langraph-agents/example_usage.py")
        print("2. Use the CLI: python main.py --help")
        print("3. Start coding with the workflow!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        if get_settings().GOOGLE_API_KEY:
            print("\n💡 Tip: Set GOOGLE_API_KEY to enable full testing")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)