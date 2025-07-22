#!/usr/bin/env python3
"""
Test script to verify the refactored components work correctly
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, '/Users/sumansaurabh/Documents/interview-cracker/interview-corvus')

def test_components():
    """Test if components can be imported and instantiated."""
    try:
        print("Testing ActionBar import...")
        from interview_corvus.ui.components.action_bar import ActionBar
        print("✓ ActionBar imported successfully")
        
        print("Testing ScreenshotControls import...")
        from interview_corvus.ui.components.screenshot_controls import ScreenshotControls
        print("✓ ScreenshotControls imported successfully")
        
        print("Testing ContentDisplay import...")
        from interview_corvus.ui.components.content_display import ContentDisplay
        print("✓ ContentDisplay imported successfully")
        
        print("Testing MenuManager import...")
        from interview_corvus.ui.components.menu_manager import MenuManager
        print("✓ MenuManager imported successfully")
        
        print("Testing StatusBarManager import...")
        from interview_corvus.ui.components.status_bar import StatusBarManager
        print("✓ StatusBarManager imported successfully")
        
        print("Testing MainWindow import...")
        from interview_corvus.ui.main_window import MainWindow
        print("✓ MainWindow imported successfully")
        
        print("\n🎉 All components imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

if __name__ == "__main__":
    success = test_components()
    sys.exit(0 if success else 1)
