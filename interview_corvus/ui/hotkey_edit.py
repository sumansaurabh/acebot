"""Custom widget for capturing hotkey combinations."""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QLineEdit


class HotkeyEdit(QLineEdit):
    """
    Custom widget for capturing and displaying hotkey combinations.
    User can click on the widget and press a key combination to set a hotkey.
    """

    def __init__(self, initial_value=None, parent=None):
        """Initialize the hotkey edit field."""
        super().__init__(parent)
        self.setReadOnly(True)
        if initial_value:
            self.setText(initial_value)
        self.setClearButtonEnabled(True)
        self.setPlaceholderText("Click and press key combination")

    def keyPressEvent(self, event):
        """Handle key press event to capture the hotkey combination."""
        # Convert the key event to a readable hotkey string
        modifiers = event.modifiers()
        key = event.key()

        # Don't trigger on just modifier keys
        if key in (
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
        ):
            return

        # Build the key combination string
        combo = []
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            combo.append("Ctrl")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            combo.append("Shift")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            combo.append("Alt")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            if sys.platform == "darwin":
                combo.append("Cmd")
            else:
                combo.append("Win")

        # Add the actual key
        key_text = QKeySequence(key).toString()
        if key_text and key_text != "":
            combo.append(key_text)

        # Set the text if we have a valid combination
        if combo and len(combo) > 1:  # Require at least one modifier
            self.setText("+".join(combo))

        # Prevent default behavior
        event.accept()

    def clear(self):
        """Clear the current hotkey and set focus to allow new entry."""
        super().clear()
        self.setFocus()
