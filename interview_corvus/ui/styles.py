"""UI styles and themes for the application."""

from enum import Enum
from typing import Dict

from interview_corvus.config import settings


class Theme(Enum):
    """Available UI themes."""

    LIGHT = "light"
    DARK = "dark"


class Styles:
    """
    Manages styles and themes for the application UI.
    """

    def __init__(self, theme: str = None):
        """
        Initialize styles with specified theme.

        Args:
            theme: Theme name ("light" or "dark"), defaults to settings value
        """
        self.theme = theme or settings.ui.default_theme
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """Initialize style dictionaries for themes."""
        # Base styles (shared between themes)
        self.base_styles = {
            "font_family": "Consolas, 'Courier New', monospace",
            "font_size": f"{settings.ui.default_font_size}pt",
            "font_code": "Consolas, 'Source Code Pro', monospace",
            "border_radius": "4px",
            "padding": "8px",
        }

        # Light theme
        self.light_theme = {
            "window_bg": "#F8F8F8",
            "panel_bg": "#FFFFFF",
            "text_color": "#333333",
            "code_bg": "#F5F5F5",
            "accent_color": "#007AFF",
            "button_bg": "#E0E0E0",
            "button_text": "#333333",
            "highlight_color": "#FFD700",
            "border_color": "#DDDDDD",
        }

        # Dark theme
        self.dark_theme = {
            "window_bg": "#1E1E1E",
            "panel_bg": "#252526",
            "text_color": "#CCCCCC",
            "code_bg": "#2D2D2D",
            "accent_color": "#0A84FF",
            "button_bg": "#3A3A3A",
            "button_text": "#FFFFFF",
            "highlight_color": "#FFD700",
            "border_color": "#555555",
        }

        # Syntax highlighting for code
        self.syntax_light = {
            "keyword": "#0000FF",  # blue
            "string": "#008000",  # green
            "comment": "#808080",  # gray
            "function": "#800000",  # maroon
            "number": "#FF8000",  # orange
            "class": "#800080",  # purple
            "background": "#FFFFFF",  # white
        }

        self.syntax_dark = {
            "keyword": "#569CD6",  # blue
            "string": "#CE9178",  # brownish
            "comment": "#6A9955",  # green
            "function": "#DCDCAA",  # yellow
            "number": "#B5CEA8",  # light green
            "class": "#4EC9B0",  # teal
            "background": "#1E1E1E",  # dark gray
        }

    def get_theme_colors(self) -> Dict[str, str]:
        """
        Get the colors for the current theme.

        Returns:
            Dictionary of color properties
        """
        if self.theme == Theme.LIGHT.value:
            return self.light_theme
        else:
            return self.dark_theme

    def get_syntax_colors(self) -> Dict[str, str]:
        """
        Get the syntax highlighting colors for the current theme.

        Returns:
            Dictionary of syntax highlighting colors
        """
        if self.theme == Theme.LIGHT.value:
            return self.syntax_light
        else:
            return self.syntax_dark

    def get_stylesheet(self) -> str:
        """
        Get the Qt stylesheet for the current theme.

        Returns:
            CSS-like stylesheet string for Qt
        """
        theme = self.get_theme_colors()
        base = self.base_styles

        return f"""
        QWidget {{
            background-color: {theme["window_bg"]};
            color: {theme["text_color"]};
            font-family: {base["font_family"]};
            font-size: {base["font_size"]};
        }}

        QMainWindow {{
            background-color: {theme["window_bg"]};
        }}

        QLabel {{
            color: {theme["text_color"]};
        }}

        QPushButton {{
            background-color: {theme["button_bg"]};
            color: {theme["button_text"]};
            border: 1px solid {theme["border_color"]};
            border-radius: {base["border_radius"]};
            padding: {base["padding"]};
        }}

        QPushButton:hover {{
            background-color: {theme["accent_color"]};
            color: white;
        }}

        QTextEdit, QPlainTextEdit {{
            background-color: {theme["code_bg"]};
            color: {theme["text_color"]};
            font-family: {base["font_code"]};
            border: 1px solid {theme["border_color"]};
            border-radius: {base["border_radius"]};
        }}

        QScrollBar:vertical {{
            border: none;
            background: {theme["panel_bg"]};
            width: 10px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background: {theme["button_bg"]};
            min-height: 20px;
            border-radius: 5px;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """

    def set_theme(self, theme_name: str) -> None:
        """
        Set the current theme.

        Args:
            theme_name: Name of the theme ("light" or "dark")
        """
        if theme_name in [t.value for t in Theme]:
            self.theme = theme_name
        else:
            raise ValueError(f"Unknown theme: {theme_name}")
