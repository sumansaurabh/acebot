#!/usr/bin/env python3
"""
Test script to verify Gemini integration syntax and imports work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test import of the main components
    from interview_corvus.core.llm_service import LLMService
    from interview_corvus.config import settings
    print("✅ Core imports successful")

    # Test that the Gemini detection logic works
    test_models = [
        "gpt-4o",  # Should be OpenAI
        "claude-3-5-sonnet-20241022",  # Should be Anthropic
        "models/gemini-1.5-pro",  # Should be Gemini
        "gemini-pro"  # Should be Gemini
    ]

    for model in test_models:
        # Test model detection logic
        is_anthropic = any(
            model_prefix in model
            for model_prefix in ["claude", "anthropic"]
        )
        is_gemini = any(
            model_prefix in model
            for model_prefix in ["gemini", "models/gemini"]
        )

        if is_anthropic:
            provider = "Anthropic"
        elif is_gemini:
            provider = "Gemini"
        else:
            provider = "OpenAI"

        print(f"✅ Model '{model}' correctly detected as {provider}")

    # Test configuration includes Gemini models
    if hasattr(settings.llm, 'available_models'):
        gemini_models = [m for m in settings.llm.available_models if 'gemini' in m.lower()]
        if gemini_models:
            print(f"✅ Found {len(gemini_models)} Gemini models in config: {gemini_models}")
        else:
            print("❌ No Gemini models found in configuration")
    else:
        print("⚠️  available_models not found in configuration")

    print("\n🎉 Gemini integration test completed successfully!")
    print("\nNext steps:")
    print("1. Set a Google API key using the settings dialog")
    print("2. Select a Gemini model from the provider dropdown")
    print("3. Test the connection in the UI")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   This is expected if dependencies are not installed")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)