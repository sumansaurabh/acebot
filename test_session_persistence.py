#!/usr/bin/env python3
"""
Test script to verify session persistence functionality.
"""

import sys
import os

# Add the parent directory to sys.path so we can import interview_corvus modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_session_persistence():
    """Test that session persistence works correctly."""
    print("🧪 Testing session persistence functionality...")
    
    try:
        from interview_corvus.ui.main_window import MainWindow
        from interview_corvus.core.hotkey_manager import HotkeyManager
        from interview_corvus.invisibility.invisibility_manager import InvisibilityManager
        from PyQt6.QtWidgets import QApplication
        
        # Create a test application
        app = QApplication([])
        
        # Create managers
        invisibility_manager = InvisibilityManager()
        hotkey_manager = HotkeyManager()
        
        # Create main window
        window = MainWindow(invisibility_manager, hotkey_manager)
        
        # Test session data initialization
        assert hasattr(window, 'current_session'), "❌ current_session not initialized"
        assert window.current_session['code'] == "", "❌ code not initialized as empty"
        assert window.current_session['explanation'] == "", "❌ explanation not initialized as empty"
        print("✅ Session data structure initialized correctly")
        
        # Test session save/restore methods
        assert hasattr(window, 'save_session_data'), "❌ save_session_data method missing"
        assert hasattr(window, 'restore_session_data'), "❌ restore_session_data method missing"
        assert hasattr(window, 'clear_session_data'), "❌ clear_session_data method missing"
        print("✅ Session management methods present")
        
        # Test manual session data persistence
        test_code = "print('Hello, World!')"
        test_explanation = "This is a test explanation"
        test_time_complexity = "O(1)"
        test_space_complexity = "O(1)"
        
        # Set test data in UI
        window.code_editor.setPlainText(test_code)
        window.explanation_text.setMarkdown(test_explanation)
        window.time_complexity.setText(test_time_complexity)
        window.space_complexity.setText(test_space_complexity)
        
        # Save session data
        window.save_session_data()
        
        # Verify session data was saved
        assert window.current_session['code'] == test_code, "❌ Code not saved to session"
        assert window.current_session['explanation'] == test_explanation, "❌ Explanation not saved to session"
        assert window.current_session['time_complexity'] == test_time_complexity, "❌ Time complexity not saved to session"
        assert window.current_session['space_complexity'] == test_space_complexity, "❌ Space complexity not saved to session"
        print("✅ Session data saved correctly")
        
        # Clear UI
        window.clear_session_data()
        
        # Verify UI was cleared
        assert window.code_editor.toPlainText() == "", "❌ Code editor not cleared"
        assert window.explanation_text.toMarkdown() == "", "❌ Explanation not cleared"
        assert window.time_complexity.text() == "N/A", "❌ Time complexity not reset"
        assert window.space_complexity.text() == "N/A", "❌ Space complexity not reset"
        print("✅ Session data and UI cleared correctly")
        
        # Restore from saved session (simulate by manually setting session data)
        window.current_session = {
            'code': test_code,
            'explanation': test_explanation,
            'time_complexity': test_time_complexity,
            'space_complexity': test_space_complexity,
            'is_optimized': False
        }
        
        window.restore_session_data()
        
        # Verify data was restored
        assert window.code_editor.toPlainText() == test_code, "❌ Code not restored from session"
        assert window.explanation_text.toMarkdown() == test_explanation, "❌ Explanation not restored from session"
        assert window.time_complexity.text() == test_time_complexity, "❌ Time complexity not restored from session"
        assert window.space_complexity.text() == test_space_complexity, "❌ Space complexity not restored from session"
        print("✅ Session data restored correctly")
        
        # Test auto-save timer
        assert hasattr(window, 'session_save_timer'), "❌ Auto-save timer not initialized"
        print("✅ Auto-save timer initialized")
        
        # Clean up
        app.quit()
        
        print("🎉 All session persistence tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_session_persistence()
    sys.exit(0 if success else 1)
