"""
Content Display Component.
Contains the code editor and explanation display areas.
"""

import re
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSplitter,
    QPlainTextEdit, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import (
    QFont, QSyntaxHighlighter, QTextCharFormat, 
    QTextDocument, QColor
)
from loguru import logger


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python code."""
    
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        
        # Define highlighting rules
        self.highlighting_rules = []
        
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(86, 156, 214))  # Blue
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'exec', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'not', 'or', 'pass', 'print', 'raise', 'return', 'try',
            'while', 'with', 'yield', 'None', 'True', 'False'
        ]
        for keyword in keywords:
            pattern = f'\\b{keyword}\\b'
            self.highlighting_rules.append((re.compile(pattern), keyword_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(206, 145, 120))  # Orange
        self.highlighting_rules.append((re.compile(r'".*?"'), string_format))
        self.highlighting_rules.append((re.compile(r"'.*?'"), string_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(106, 153, 85))  # Green
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'#.*'), comment_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168))  # Light green
        self.highlighting_rules.append((re.compile(r'\\b\\d+\\b'), number_format))
        
        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(220, 220, 170))  # Yellow
        self.highlighting_rules.append((re.compile(r'\\bdef\\s+(\\w+)'), function_format))
        
        # Class format
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(78, 201, 176))  # Cyan
        class_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((re.compile(r'\\bclass\\s+(\\w+)'), class_format))
        
    def highlightBlock(self, text: str):
        """Apply syntax highlighting to a block of text."""
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)


class ContentDisplay(QWidget):
    """Widget for displaying code and explanation content."""
    
    # Signals
    code_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_session = {
            "code": "",
            "explanation": "",
            "time_complexity": "N/A",
            "space_complexity": "N/A",
            "is_optimized": False
        }
        self._is_optimized = False
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Set up the content display UI."""
        # Create horizontal splitter for side-by-side layout
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        content_splitter.setMinimumHeight(400)
        
        # Code section
        code_widget = self.create_code_section()
        content_splitter.addWidget(code_widget)
        
        # Info section
        info_widget = self.create_info_section()
        content_splitter.addWidget(info_widget)
        
        # Set ratio: 70% code, 30% info
        content_splitter.setSizes([700, 300])
        
        layout = QHBoxLayout()
        layout.addWidget(content_splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
    def create_code_section(self):
        """Create the code editor section."""
        code_widget = QWidget()
        code_layout = QVBoxLayout(code_widget)
        code_layout.setContentsMargins(4, 4, 4, 4)
        
        # Header
        code_header = QLabel("💻 Code")
        code_header.setStyleSheet("font-weight: bold; color: #4A90E2; font-size: 14px; padding: 4px;")
        code_layout.addWidget(code_header)
        
        # Code editor
        self.code_editor = QPlainTextEdit()
        self.code_editor.setReadOnly(True)
        
        # Set font
        font = QFont("Fira Code", 11)
        if not font.exactMatch():
            font = QFont("Consolas", 11)
        if not font.exactMatch():
            font = QFont("Monaco", 11)
        self.code_editor.setFont(font)
        
        # Set up syntax highlighting
        self.syntax_highlighter = PythonSyntaxHighlighter(self.code_editor.document())
        self.code_editor.setPlaceholderText("Generated code will appear here...")
        
        code_layout.addWidget(self.code_editor)
        return code_widget
        
    def create_info_section(self):
        """Create the explanation and complexity info section."""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(4, 4, 4, 4)
        
        # Header
        info_header = QLabel("📝 Explanation")
        info_header.setStyleSheet("font-weight: bold; color: #4A90E2; font-size: 14px; padding: 4px;")
        info_layout.addWidget(info_header)
        
        # Explanation text
        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        self.explanation_text.setAcceptRichText(True)
        self.explanation_text.setMarkdown("")
        self.explanation_text.setPlaceholderText("Solution explanation will appear here...")
        info_layout.addWidget(self.explanation_text)
        
        # Complexity info
        complexity_container = self.create_complexity_section()
        info_layout.addWidget(complexity_container)
        
        return info_widget
        
    def create_complexity_section(self):
        """Create the complexity information section."""
        complexity_container = QWidget()
        complexity_layout = QHBoxLayout(complexity_container)
        complexity_layout.setContentsMargins(0, 8, 0, 0)
        complexity_layout.setSpacing(16)
        
        # Time complexity
        time_label = QLabel("⏱️ Time:")
        time_label.setStyleSheet("font-weight: bold; color: #666; font-size: 12px;")
        self.time_complexity = QLabel("N/A")
        self.time_complexity.setStyleSheet("color: #4A90E2; font-weight: bold; font-size: 12px;")
        
        # Space complexity
        space_label = QLabel("💾 Space:")
        space_label.setStyleSheet("font-weight: bold; color: #666; font-size: 12px;")
        self.space_complexity = QLabel("N/A")
        self.space_complexity.setStyleSheet("color: #4A90E2; font-weight: bold; font-size: 12px;")
        
        complexity_layout.addWidget(time_label)
        complexity_layout.addWidget(self.time_complexity)
        complexity_layout.addStretch()
        complexity_layout.addWidget(space_label)
        complexity_layout.addWidget(self.space_complexity)
        
        return complexity_container
        
    def connect_signals(self):
        """Connect internal signals."""
        self.code_editor.textChanged.connect(self.code_changed.emit)
        
    def display_solution(self, solution):
        """Display a new solution."""
        self.code_editor.setPlainText(solution.code)
        self.explanation_text.setMarkdown(solution.explanation)
        self.time_complexity.setText(solution.time_complexity)
        self.space_complexity.setText(solution.space_complexity)
        self._is_optimized = False
        self.save_session_data()
        
    def display_optimization(self, optimization):
        """Display an optimization result."""
        self.code_editor.setPlainText(optimization.optimized_code)
        
        # Create detailed explanation including improvements
        detailed_explanation = "## Optimization Details\\n\\n"
        detailed_explanation += optimization.explanation + "\\n\\n"
        detailed_explanation += "## Improvements\\n\\n"
        for improvement in optimization.improvements:
            detailed_explanation += f"- {improvement}\\n"
        detailed_explanation += "\\n\\n## Time Complexity\\n\\n"
        detailed_explanation += f"**Original:** {optimization.original_time_complexity}\\n\\n"
        detailed_explanation += f"**Optimized:** {optimization.optimized_time_complexity}\\n\\n"
        detailed_explanation += "## Space Complexity\\n\\n"
        detailed_explanation += f"**Original:** {optimization.original_space_complexity}\\n\\n"
        detailed_explanation += f"**Optimized:** {optimization.optimized_space_complexity}\\n"
        
        self.explanation_text.setMarkdown(detailed_explanation)
        self.time_complexity.setText(optimization.optimized_time_complexity)
        self.space_complexity.setText(optimization.optimized_space_complexity)
        self._is_optimized = True
        self.save_session_data()
        
    def get_current_code(self):
        """Get the current code from the editor."""
        return self.code_editor.toPlainText()
        
    def clear_content(self):
        """Clear all displayed content."""
        self.code_editor.clear()
        self.explanation_text.setMarkdown("")
        self.time_complexity.setText("N/A")
        self.space_complexity.setText("N/A")
        self._is_optimized = False
        self.clear_session_data()
        
    def save_session_data(self):
        """Save current session data."""
        self.current_session = {
            "code": self.code_editor.toPlainText(),
            "explanation": self.explanation_text.toMarkdown(),
            "time_complexity": self.time_complexity.text(),
            "space_complexity": self.space_complexity.text(),
            "is_optimized": self._is_optimized
        }
        logger.debug("Session data saved")
        
    def restore_session_data(self):
        """Restore session data to UI components."""
        if self.current_session["code"]:
            self.code_editor.setPlainText(self.current_session["code"])
            self.explanation_text.setMarkdown(self.current_session["explanation"])
            self.time_complexity.setText(self.current_session["time_complexity"])
            self.space_complexity.setText(self.current_session["space_complexity"])
            self._is_optimized = self.current_session.get("is_optimized", False)
            logger.debug("Session data restored")
            
    def clear_session_data(self):
        """Clear session data."""
        self.current_session = {
            "code": "",
            "explanation": "",
            "time_complexity": "N/A",
            "space_complexity": "N/A",
            "is_optimized": False
        }
        self._is_optimized = False
        logger.debug("Session data cleared")
