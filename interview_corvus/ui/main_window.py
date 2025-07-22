import platform
import re

from loguru import logger
from PyQt6.QtCore import QEvent, QSize, Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QFont, QIcon, QKeySequence, QSyntaxHighlighter, QTextCharFormat, QTextDocument, QColor, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QStatusBar,
    QSystemTrayIcon,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QDialog,
)

from interview_corvus.config import settings
from interview_corvus.core.hotkey_manager import HotkeyManager
from interview_corvus.core.llm_service import LLMService
from interview_corvus.invisibility.invisibility_manager import InvisibilityManager
from interview_corvus.screenshot.screenshot_manager import ScreenshotManager
from interview_corvus.ui.settings_dialog import SettingsDialog
from interview_corvus.ui.styles import Styles, Theme

# Try to import web server (optional dependency)
try:
    from interview_corvus.api.web_server import create_integrated_web_server
    WEB_SERVER_AVAILABLE = True
except ImportError:
    WEB_SERVER_AVAILABLE = False
    logger.warning("Web server dependencies not available. Web API will be disabled.")


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
        self.highlighting_rules.append((re.compile(r'\b\d+\b'), number_format))
        
        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(220, 220, 170))  # Yellow
        self.highlighting_rules.append((re.compile(r'\bdef\s+(\w+)'), function_format))
        
        # Class format
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(78, 201, 176))  # Cyan
        class_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((re.compile(r'\bclass\s+(\w+)'), class_format))
        
    def highlightBlock(self, text: str):
        """Apply syntax highlighting to a block of text."""
        for pattern, format_obj in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format_obj)


class MainWindow(QMainWindow):
    """
    Main application window with unified interface.
    Handles user interactions and coordinates between components.
    """

    def __init__(
        self, invisibility_manager: InvisibilityManager, hotkey_manager: HotkeyManager
    ):
        """
        Initialize the main window.

        Args:
            invisibility_manager: Manager for invisibility features
            hotkey_manager: Manager for hotkey handling
        """
        super().__init__()

        self.invisibility_manager = invisibility_manager
        self.hotkey_manager = hotkey_manager
        self.check_and_request_permissions()

        # Initialize other components
        self.screenshot_manager = ScreenshotManager()
        self.llm_service = LLMService()
        self.styles = Styles()

        # Initialize web server (optional)
        self.web_api = None
        self.web_server_thread = None
        if WEB_SERVER_AVAILABLE:
            try:
                self.web_api, self.web_server_thread = create_integrated_web_server(
                    llm_service=self.llm_service,
                    screenshot_manager=self.screenshot_manager,
                    host="0.0.0.0",
                    port=8000
                )
                logger.info("✅ Web server initialized successfully")
                
                # Connect web server signals immediately
                self.web_api.screenshot_capture_requested.connect(self.take_screenshot)
                self.web_api.screenshots_cleared.connect(self.clear_screenshots)
                self.web_api.chat_history_reset.connect(self.reset_chat_history)
                self.web_api.window_show_requested.connect(self.show)
                self.web_api.window_hide_requested.connect(self.hide)
                self.web_api.window_toggle_requested.connect(self.toggle_visibility)
                
                # Auto-start the web server
                if self.web_server_thread:
                    self.web_server_thread.start()
                    logger.info("🚀 Web server auto-started on http://0.0.0.0:8000 (accessible from all interfaces)")
                    # Will update button text in init_ui after button is created
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize web server: {e}")
                self.web_api = None
                self.web_server_thread = None

        # Connect LLM service signals
        self.llm_service.completion_finished.connect(self.on_solution_ready)
        self.llm_service.error_occurred.connect(self.on_processing_error)

        # Processing state
        self.processing_screenshot = False
        self.solution_text = ""
        
        # Session state to persist generated code and explanations
        self.current_session = {
            "code": "",
            "explanation": "",
            "time_complexity": "N/A",
            "space_complexity": "N/A",
            "is_optimized": False
        }
        
        # Auto-save timer for session persistence
        self.session_save_timer = QTimer()
        self.session_save_timer.setSingleShot(True)
        self.session_save_timer.timeout.connect(self.save_session_data)
        self._is_optimized = False

        # Set up UI
        self.init_ui()

        # Connect signals to slots
        self.connect_signals()

        # Set window properties
        self.setWindowTitle(settings.app_name)
        self.resize(1000, 700)  # Better default size for unified interface
        self.setMinimumSize(800, 600)  # Set minimum size

        # Initialize opacity to 100%
        self.set_opacity(1.0)

        # Set always on top flag
        self.set_always_on_top(settings.ui.always_on_top)

        # Set this window handle for the invisibility manager
        self.invisibility_manager.set_window_handle(self)
        logger.info(
            f"Window visibility at startup: {self.invisibility_manager.is_visible}"
        )

        # Register hotkeys now that the window is created
        self.hotkey_manager.register_hotkeys(self)
        self.installEventFilter(self.hotkey_manager)

    def init_ui(self):
        """Set up the minimalistic user interface."""
        # Set modern dark stylesheet
        self.setStyleSheet(self._get_minimal_stylesheet())

        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)  # Remove all spacing between layouts
        main_layout.setContentsMargins(12, 4, 12, 12)  # Minimal top margin

        # Main action buttons with header buttons on the same row
        action_layout = QHBoxLayout()
        action_layout.setSpacing(3)  # Reduced spacing from 6 to 3
        action_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to eliminate space above

        # Screenshot button
        self.screenshot_button = QPushButton("📸 Capture")
        self.screenshot_button.clicked.connect(self.take_screenshot)
        self.screenshot_button.setToolTip(f"Take Screenshot ({settings.hotkeys.screenshot_key})")
        self.screenshot_button.setFixedSize(90, 35)
        action_layout.addWidget(self.screenshot_button)

        # Generate solution button
        self.generate_button = QPushButton("🚀 Solve")
        self.generate_button.clicked.connect(self.generate_solution)
        self.generate_button.setToolTip(f"Generate Solution ({settings.hotkeys.generate_solution_key})")
        self.generate_button.setFixedSize(90, 35)
        action_layout.addWidget(self.generate_button)

        # Optimize button
        self.optimize_button = QPushButton("⚡ Optimize")
        self.optimize_button.clicked.connect(self.optimize_solution)
        self.optimize_button.setToolTip(f"Optimize Solution ({settings.hotkeys.optimize_solution_key})")
        self.optimize_button.setFixedSize(90, 35)
        action_layout.addWidget(self.optimize_button)

        # Copy button
        self.copy_button = QPushButton("📋 Copy")
        self.copy_button.setFixedSize(50, 35)
        self.copy_button.clicked.connect(self.copy_solution)
        self.copy_button.setToolTip("Copy Solution")
        action_layout.addWidget(self.copy_button)

        # Reset All button
        reset_button = QPushButton("🔄 Reset")
        reset_button.setFixedSize(85, 35)
        reset_button.clicked.connect(self.reset_chat_history)
        reset_button.setToolTip(f"Reset All ({settings.hotkeys.reset_history_key})")
        action_layout.addWidget(reset_button)
        
        # Add stretch to separate action buttons from header buttons
        action_layout.addStretch()

        # Header buttons on the same row as action buttons (right side)
        # Settings button
        settings_button = QPushButton("⚙️ Settings")
        settings_button.setFixedSize(80, 32)
        settings_button.clicked.connect(self.show_settings)
        settings_button.setToolTip("Settings")
        action_layout.addWidget(settings_button)

        # Visibility toggle
        self.visibility_button = QPushButton("👁️ Hide")
        self.visibility_button.setFixedSize(70, 32)
        self.visibility_button.clicked.connect(self.toggle_visibility)
        self.visibility_button.setToolTip(f"Toggle Visibility ({settings.hotkeys.toggle_visibility_key})")
        action_layout.addWidget(self.visibility_button)

        # Web server toggle (if available)
        if WEB_SERVER_AVAILABLE:
            self.web_server_button = QPushButton("🌐 API")
            self.web_server_button.setFixedSize(70, 32)
            self.web_server_button.clicked.connect(self.toggle_web_server)
            self.web_server_button.setToolTip("Toggle Web API Server")
            action_layout.addWidget(self.web_server_button)

        main_layout.addLayout(action_layout)

        # Screenshots and controls section - horizontal layout
        screenshots_controls_layout = QHBoxLayout()
        screenshots_controls_layout.setSpacing(12)
        screenshots_controls_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Screenshots preview - expanded to fill remaining space
        screenshots_group = QWidget()
        screenshots_layout = QVBoxLayout(screenshots_group)
        screenshots_layout.setContentsMargins(0, 4, 0, 4)

        screenshots_header = QHBoxLayout()
        screenshots_label = QLabel("📷 Screenshots:")
        screenshots_label.setStyleSheet("font-weight: bold; color: #666; font-size: 12px;")
        screenshots_header.addWidget(screenshots_label)
        screenshots_header.addStretch()

        screenshots_layout.addLayout(screenshots_header)

        # Compact thumbnails container - will expand to fill available space
        self.thumbnails_container = QWidget()
        self.thumbnails_layout = QHBoxLayout(self.thumbnails_container)
        self.thumbnails_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.thumbnails_layout.setContentsMargins(2, 2, 2, 2)
        self.thumbnails_layout.setSpacing(6)

        thumbnails_scroll = QScrollArea()
        thumbnails_scroll.setWidgetResizable(True)
        thumbnails_scroll.setWidget(self.thumbnails_container)
        thumbnails_scroll.setFixedHeight(80)  # Increased height from 50 to 80
        thumbnails_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        thumbnails_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        screenshots_layout.addWidget(thumbnails_scroll)
        # Remove width limitation to let it expand
        screenshots_controls_layout.addWidget(screenshots_group, 1)  # stretch factor 1 to fill space
        
        # Language and Monitor controls - compact horizontal layout, right-aligned
        controls_group = QWidget()
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setContentsMargins(8, 4, 0, 4)
        controls_layout.setSpacing(8)  # Reduced spacing
        
        # Language selection - horizontal layout (label + dropdown side by side)
        language_layout = QHBoxLayout()
        language_layout.setSpacing(6)
        lang_label = QLabel("🌐 Language:")
        lang_label.setStyleSheet("font-weight: bold; color: #666; font-size: 12px;")
        language_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(settings.available_languages)
        index = self.language_combo.findText(settings.default_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        self.language_combo.setMinimumWidth(120)
        self.language_combo.setMaximumWidth(150)
        self.language_combo.setFixedHeight(28)
        language_layout.addWidget(self.language_combo)
        
        controls_layout.addLayout(language_layout)
        
        # Monitor selection - horizontal layout (label + dropdown side by side)
        monitor_layout = QHBoxLayout()
        monitor_layout.setSpacing(6)
        monitor_label = QLabel("📺 Monitor:")
        monitor_label.setStyleSheet("font-weight: bold; color: #666; font-size: 12px;")
        monitor_layout.addWidget(monitor_label)
        
        self.screen_combo = QComboBox()
        self.update_screen_list()
        self.screen_combo.setMinimumWidth(120)
        self.screen_combo.setMaximumWidth(150)
        self.screen_combo.setFixedHeight(28)
        monitor_layout.addWidget(self.screen_combo)
        
        controls_layout.addLayout(monitor_layout)
        controls_layout.addStretch()  # Push controls to top
        
        # Set fixed width for controls to keep them compact
        controls_group.setFixedWidth(200)
        screenshots_controls_layout.addWidget(controls_group)
        
        main_layout.addLayout(screenshots_controls_layout)

        # Content area - side by side layout instead of tabs
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        
        # Set minimum size for content area to expand properly
        content_splitter.setMinimumHeight(400)

        # Code section
        code_widget = QWidget()
        code_layout = QVBoxLayout(code_widget)
        code_layout.setContentsMargins(4, 4, 4, 4)
        
        code_header = QLabel("💻 Code")
        code_header.setStyleSheet("font-weight: bold; color: #4A90E2; font-size: 14px; padding: 4px;")
        code_layout.addWidget(code_header)

        self.code_editor = QPlainTextEdit()
        self.code_editor.setReadOnly(True)
        font = QFont("Fira Code", 11)
        if not font.exactMatch():
            font = QFont("Consolas", 11)
        if not font.exactMatch():
            font = QFont("Monaco", 11)
        self.code_editor.setFont(font)
        
        self.setup_syntax_highlighting()
        self.code_editor.setPlaceholderText("Generated code will appear here...")
        
        code_layout.addWidget(self.code_editor)
        content_splitter.addWidget(code_widget)

        # Info section
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(4, 4, 4, 4)
        
        info_header = QLabel("📝 Explanation")
        info_header.setStyleSheet("font-weight: bold; color: #4A90E2; font-size: 14px; padding: 4px;")
        info_layout.addWidget(info_header)

        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        self.explanation_text.setAcceptRichText(True)
        self.explanation_text.setMarkdown("")
        
        self.explanation_text.setPlaceholderText("Solution explanation will appear here...")
        info_layout.addWidget(self.explanation_text)

        # Complexity info - compact horizontal layout
        complexity_container = QWidget()
        complexity_layout = QHBoxLayout(complexity_container)
        complexity_layout.setContentsMargins(0, 8, 0, 0)
        complexity_layout.setSpacing(16)

        time_label = QLabel("⏱️ Time:")
        time_label.setStyleSheet("font-weight: bold; color: #666; font-size: 12px;")
        self.time_complexity = QLabel("N/A")
        self.time_complexity.setStyleSheet("color: #4A90E2; font-weight: bold; font-size: 12px;")
        
        space_label = QLabel("💾 Space:")
        space_label.setStyleSheet("font-weight: bold; color: #666; font-size: 12px;")
        self.space_complexity = QLabel("N/A")
        self.space_complexity.setStyleSheet("color: #4A90E2; font-weight: bold; font-size: 12px;")

        complexity_layout.addWidget(time_label)
        complexity_layout.addWidget(self.time_complexity)
        complexity_layout.addStretch()
        complexity_layout.addWidget(space_label)
        complexity_layout.addWidget(self.space_complexity)

        info_layout.addWidget(complexity_container)
        content_splitter.addWidget(info_widget)
        
        # Set ratio: 70% code, 30% info
        content_splitter.setSizes([70, 30])
        
        # Add with stretch factor so it expands to fill available space
        main_layout.addWidget(content_splitter, 1)  # stretch factor of 1

        # Minimal status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Progress indicator
        self.progress_label = QLabel("Idle")
        self.progress_label.setStyleSheet("color: #4A90E2; font-weight: bold; font-size: 11px;")
        self.status_bar.addPermanentWidget(self.progress_label)
        
        # AceBot title in the middle
        self.app_title_label = QLabel("🤖 AceBot")
        self.app_title_label.setStyleSheet("color: #4A90E2; font-weight: bold; font-size: 12px; padding: 0 16px;")
        self.status_bar.addPermanentWidget(self.app_title_label)

        # Web server status (if available)
        if WEB_SERVER_AVAILABLE:
            self.web_server_status = QLabel("🌐 API: Off")
            self.web_server_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
            self.status_bar.addPermanentWidget(self.web_server_status)

        # Set up main widget
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Create menu bar
        self._create_menu_bar()

        # Create system tray
        self._create_system_tray()

        # Initialize selected screenshot index
        self.selected_screenshot_index = -1

        # Update thumbnails
        self.update_thumbnails()
        self.update_button_texts()
        
        # Restore session data if available
        self.restore_session_data()
        
        # Update web server button state if auto-started
        if WEB_SERVER_AVAILABLE and self.web_server_thread and self.web_server_thread.isRunning():
            if hasattr(self, 'web_server_status'):
                self.web_server_status.setText("🌐 API: On")
                self.web_server_status.setStyleSheet("color: #51cf66;")

    def _get_minimal_stylesheet(self):
        """Get the minimal modern stylesheet."""
        return """
        QMainWindow {
            background-color: #ffffff;
            color: #333333;
        }
        
        QWidget {
            background-color: #ffffff;
            color: #333333;
        }
        
        QPushButton {
            background-color: #4A90E2;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 8px;
            font-weight: 600;
            font-size: 11px;
            min-height: 18px;
        }
        
        QPushButton:hover {
            background-color: #357ABD;
            transform: translateY(-1px);
        }
        
        QPushButton:pressed {
            background-color: #2868A0;
            transform: translateY(0px);
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        
        QComboBox {
            background-color: #f8f9fa;
            border: 1px solid #e1e4e8;
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 12px;
            min-height: 16px;
        }
        
        QComboBox:hover {
            border-color: #4A90E2;
        }
        
        QComboBox:focus {
            border-color: #4A90E2;
            outline: none;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            width: 12px;
            height: 12px;
        }
        
        QSplitter::handle {
            background-color: #e1e4e8;
            width: 2px;
        }
        
        QSplitter::handle:hover {
            background-color: #4A90E2;
        }
        
        QScrollArea {
            background-color: #f8f9fa;
            border: 1px solid #e1e4e8;
            border-radius: 4px;
        }
        
        QScrollBar:horizontal {
            background-color: #f8f9fa;
            height: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #ced4da;
            border-radius: 5px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #adb5bd;
        }
        
        QScrollBar:vertical {
            background-color: #f8f9fa;
            width: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #ced4da;
            border-radius: 5px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #adb5bd;
        }
        
        QLabel {
            color: #333333;
        }
        
        QPlainTextEdit {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 12px;
            font-family: "Fira Code", "Consolas", "Monaco", monospace;
            font-size: 12px;
            line-height: 1.5;
            selection-background-color: #b3d7ff;
        }
        
        QTextEdit {
            background-color: #f8f9fa;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 12px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: 13px;
            line-height: 1.5;
        }
        
        QStatusBar {
            background-color: #f8f9fa;
            border-top: 1px solid #e1e4e8;
            font-size: 11px;
            color: #666;
            padding: 3px 6px;
        }
        """

    def setup_syntax_highlighting(self):
        """Set up Python syntax highlighting for the code editor."""
        self.syntax_highlighter = PythonSyntaxHighlighter(self.code_editor.document())

    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        take_screenshot_action = QAction(
            f"Take Screenshot ({settings.hotkeys.screenshot_key})", self
        )
        take_screenshot_action.setShortcut(settings.hotkeys.screenshot_key)
        take_screenshot_action.triggered.connect(self.take_screenshot)
        file_menu.addAction(take_screenshot_action)

        # Add action for settings
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        generate_solution_action = QAction(
            f"Generate Solution ({settings.hotkeys.generate_solution_key})", self
        )
        generate_solution_action.setShortcut(settings.hotkeys.generate_solution_key)
        generate_solution_action.triggered.connect(self.generate_solution)
        file_menu.addAction(generate_solution_action)

        # Add action for optimizing solution
        optimize_solution_action = QAction(
            f"Optimize Solution ({settings.hotkeys.optimize_solution_key})", self
        )
        optimize_solution_action.setShortcut(settings.hotkeys.optimize_solution_key)
        optimize_solution_action.triggered.connect(self.optimize_solution)
        file_menu.addAction(optimize_solution_action)

        # Add action for resetting chat history
        reset_history_action = QAction(
            f"Reset All ({settings.hotkeys.reset_history_key})", self
        )
        reset_history_action.setShortcut(settings.hotkeys.reset_history_key)
        reset_history_action.triggered.connect(self.reset_chat_history)
        file_menu.addAction(reset_history_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        toggle_visibility_action = QAction(
            f"Toggle Visibility ({settings.hotkeys.toggle_visibility_key})", self
        )
        toggle_visibility_action.setShortcut(settings.hotkeys.toggle_visibility_key)
        toggle_visibility_action.triggered.connect(self.toggle_visibility)
        view_menu.addAction(toggle_visibility_action)

        # Add always on top action
        self.always_on_top_action = QAction("Always on Top", self)
        self.always_on_top_action.setCheckable(True)
        self.always_on_top_action.setChecked(settings.ui.always_on_top)
        self.always_on_top_action.triggered.connect(self.toggle_always_on_top_menu)
        view_menu.addAction(self.always_on_top_action)

        # Theme submenu
        theme_menu = QMenu("Theme", self)

        light_theme_action = QAction("Light", self)
        light_theme_action.triggered.connect(lambda: self.set_theme(Theme.LIGHT.value))
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("Dark", self)
        dark_theme_action.triggered.connect(lambda: self.set_theme(Theme.DARK.value))
        theme_menu.addAction(dark_theme_action)

        view_menu.addMenu(theme_menu)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)

    def _create_system_tray(self):
        """Create the system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple colored icon as fallback
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(74, 144, 226))  # Blue color matching our theme
        icon = QIcon(pixmap)
        
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip(settings.app_name)
        self.tray_icon.activated.connect(self.on_tray_activated)

        # Создаем контекстное меню для системного трея
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show/Hide")
        show_action.triggered.connect(self.toggle_visibility)
        optimize_action = tray_menu.addAction("Optimize Solution")
        optimize_action.triggered.connect(self.optimize_solution)

        # Add always on top action to tray menu
        self.tray_always_on_top_action = QAction("Always on Top", self)
        self.tray_always_on_top_action.setCheckable(True)
        self.tray_always_on_top_action.setChecked(settings.ui.always_on_top)
        self.tray_always_on_top_action.triggered.connect(self.toggle_always_on_top_menu)
        tray_menu.addAction(self.tray_always_on_top_action)

        reset_history_action = tray_menu.addAction("Reset All")
        reset_history_action.triggered.connect(self.reset_chat_history)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        """
        Handle tray icon activation.

        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            logger.info("Tray icon clicked - toggling visibility")
            self.toggle_visibility()

    def connect_signals(self):
        """Connect signals to slots."""
        # Hotkey manager signals
        self.hotkey_manager.screenshot_triggered.connect(self.take_screenshot)
        self.hotkey_manager.solution_triggered.connect(self.generate_solution)
        self.hotkey_manager.visibility_triggered.connect(self.toggle_visibility)
        self.hotkey_manager.move_window_triggered.connect(self.move_window)
        self.hotkey_manager.panic_triggered.connect(self.activate_panic_mode)
        self.hotkey_manager.optimize_solution_triggered.connect(self.optimize_solution)
        self.hotkey_manager.reset_history_triggered.connect(self.reset_chat_history)

        logger.info("Connected all hotkey signals including optimize and reset history")

        # Invisibility manager signals
        self.invisibility_manager.visibility_changed.connect(self.on_visibility_changed)
        self.invisibility_manager.screen_sharing_detected.connect(
            self.on_screen_sharing_detected
        )

        # Language combo box
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        QApplication.instance().screenAdded.connect(self.update_screen_list)
        QApplication.instance().screenRemoved.connect(self.update_screen_list)
        
        # Session persistence - connect code editor changes
        self.code_editor.textChanged.connect(self.on_code_changed)

    def set_always_on_top(self, enabled: bool):
        """
        Set whether the window should always be on top.

        Args:
            enabled: True to enable always on top, False to disable
        """
        # Store current flags
        flags = self.windowFlags()

        # Check if we need to make changes
        has_flag = bool(flags & Qt.WindowType.WindowStaysOnTopHint)
        if has_flag == enabled:
            return

        # Clear or set the flag
        if enabled:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint

        # Remember current position and visibility
        pos = self.pos()
        visible = self.isVisible()

        # Apply new flags - this will hide the window
        self.setWindowFlags(flags)

        # Restore position
        self.move(pos)

        # Restore visibility if it was visible
        if visible:
            self.show()

        # Update settings
        settings.ui.always_on_top = enabled
        settings.save_user_settings()

        # Update UI - only menu items since we removed the checkbox in minimal design
        self.always_on_top_action.setChecked(enabled)
        self.tray_always_on_top_action.setChecked(enabled)

        logger.info(f"Always on top set to: {enabled}")
        self.status_bar.showMessage(
            f"Always on top: {'enabled' if enabled else 'disabled'}"
        )

    def toggle_always_on_top(self, state):
        """
        Toggle always on top from checkbox.

        Args:
            state: Checkbox state
        """
        self.set_always_on_top(state == Qt.CheckState.Checked)

    def toggle_always_on_top_menu(self):
        """Toggle always on top from menu action."""
        # Use the current state of the action
        self.set_always_on_top(self.always_on_top_action.isChecked())

    def update_thumbnails(self):
        """Update screenshot thumbnails display - minimal version."""
        # Save session data before updating thumbnails (which can cause UI refresh)
        if hasattr(self, 'current_session'):
            self.save_session_data()
            
        # Clear existing thumbnails
        while self.thumbnails_layout.count():
            item = self.thumbnails_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get all screenshots
        screenshots = self.screenshot_manager.get_all_screenshots()

        if not screenshots:
            # Add placeholder
            placeholder = QLabel("No screenshots")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("""
                color: #999; 
                font-style: italic; 
                padding: 12px;
                font-size: 11px;
                background-color: #f5f5f5;
                border: 1px dashed #ddd;
                border-radius: 4px;
            """)
            self.thumbnails_layout.addWidget(placeholder)
            self.selected_screenshot_index = -1
            return

        # Add thumbnails for each screenshot
        for i, screenshot in enumerate(screenshots):
            thumbnail_widget = QWidget()
            thumbnail_layout = QVBoxLayout(thumbnail_widget)
            thumbnail_layout.setContentsMargins(2, 2, 2, 2)
            thumbnail_layout.setSpacing(1)

            # Create thumbnail - larger size for increased height
            thumbnail = QLabel()
            pixmap = screenshot["pixmap"].scaled(
                QSize(60, 45),  # Increased size to match the increased height
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            thumbnail.setPixmap(pixmap)
            thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Better styling with selection state
            if i == self.selected_screenshot_index:
                thumbnail.setStyleSheet("""
                    border: 2px solid #4A90E2; 
                    border-radius: 4px;
                    background-color: #f0f7ff;
                    padding: 2px;
                """)
            else:
                thumbnail.setStyleSheet("""
                    border: 1px solid #ddd; 
                    border-radius: 4px;
                    background-color: white;
                    padding: 2px;
                """)

            thumbnail_layout.addWidget(thumbnail)

            # Index number with better styling
            index_label = QLabel(f"#{i + 1}")
            index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            index_label.setStyleSheet("""
                font-size: 10px; 
                color: #666; 
                font-weight: bold;
                background-color: rgba(74, 144, 226, 0.1);
                border-radius: 2px;
                padding: 1px 4px;
            """)
            thumbnail_layout.addWidget(index_label)

            # Make widget clickable
            thumbnail_widget.mouseReleaseEvent = (
                lambda event, idx=i: self.select_screenshot(idx)
            )
            thumbnail_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Hover effect
            thumbnail_widget.setStyleSheet("""
                QWidget:hover {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                }
            """)

            # Add to container
            self.thumbnails_layout.addWidget(thumbnail_widget)

        # If no screenshot is selected, select the most recent one
        if self.selected_screenshot_index == -1 and screenshots:
            self.select_screenshot(len(screenshots) - 1)
        
        # Restore session data after thumbnail update
        if hasattr(self, 'current_session'):
            self.restore_session_data()

    def select_screenshot(self, index):
        """
        Select a screenshot by index.

        Args:
            index: Index of the screenshot to select
        """
        if index < 0 or index >= len(self.screenshot_manager.get_all_screenshots()):
            return

        self.selected_screenshot_index = index
        logger.info(f"Selected screenshot {index}")
        self.status_bar.showMessage(f"Selected screenshot {index + 1}")

        # Update thumbnails to show selection
        self.update_thumbnails()

    def clear_screenshots(self):
        """Clear all screenshots."""
        self.screenshot_manager.clear_screenshots()
        self.selected_screenshot_index = -1
        self.update_thumbnails()
        
        # Clear solution display as well
        self.code_editor.clear()
        self.explanation_text.setMarkdown("")  # Clear markdown content
        self.time_complexity.setText("N/A")
        self.space_complexity.setText("N/A")
        
        self.status_bar.showMessage("All screenshots cleared")

    @pyqtSlot(str)
    def on_language_changed(self, language: str):
        """
        Handle language selection changes.

        Args:
            language: The newly selected programming language
        """
        # Update default language in settings
        settings.default_language = language
        self.status_bar.showMessage(f"Solution language set to {language}")

        # Save settings
        settings.save_user_settings()
    
    def on_code_changed(self):
        """Handle code editor changes to preserve session data."""
        # Only save if we have actual content to avoid overwriting with empty text during initialization
        if hasattr(self, 'current_session') and self.code_editor.toPlainText().strip():
            # Use timer to avoid too frequent saves while typing
            self.session_save_timer.start(500)  # Save after 500ms of inactivity

    @pyqtSlot()
    def take_screenshot(self):
        """Take a screenshot without generating a solution."""
        self.status_bar.showMessage("Taking screenshot...")
        logger.info("Taking screenshot...")

        # Get the index of the selected monitor
        selected_index = self.screen_combo.currentData()

        # Save the currently active window handle before taking 
        # This can be done with platform-specific code

        # Temporarily hide the window if visible
        was_visible = self.invisibility_manager.is_visible
        self.invisibility_manager.set_visibility(False)
        QApplication.processEvents()

        # Take the screenshot
        screenshot = self.screenshot_manager.take_screenshot(selected_index)

        # Restore visibility if needed, but don't activate the window
        if was_visible:
            QTimer.singleShot(
                200,
                lambda: self.invisibility_manager.restore_visibility_without_focus(),
            )

        # Update UI elements
        self.status_bar.showMessage(
            f"Screenshot captured: {screenshot['width']}x{screenshot['height']}"
        )
        self.update_thumbnails()
        self.select_screenshot(len(self.screenshot_manager.get_all_screenshots()) - 1)

    @pyqtSlot()
    def reset_chat_history(self):
        """Reset the chat history and clear screenshots."""
        if hasattr(self.llm_service, "reset_chat_history"):
            self.llm_service.reset_chat_history()

            # Clear all screenshots
            self.screenshot_manager.clear_screenshots()
            self.selected_screenshot_index = -1
            self.update_thumbnails()

            # Clear UI components and session data
            self.clear_session_data()

            self.status_bar.showMessage("Chat history and screenshots reset.")
            logger.info("Chat history and screenshots have been reset")
        else:
            self.status_bar.showMessage("Chat history reset not implemented.")
            logger.info("Chat history reset not implemented")

    @pyqtSlot()
    def generate_solution(self):
        """Generate a solution based on all available screenshots."""
        # Check if processing is already in progress
        if self.processing_screenshot:
            self.status_bar.showMessage("Already processing screenshot, please wait...")
            return

        # Get all screenshots
        screenshots = self.screenshot_manager.get_all_screenshots()
        if not screenshots:
            self.status_bar.showMessage(
                "No screenshots available. Take a screenshot first."
            )
            logger.info("No screenshots available")
            return

        self.status_bar.showMessage(
            f"Generating solution from {len(screenshots)} screenshots..."
        )
        logger.info(f"Generating solution from {len(screenshots)} screenshots...")

        # Set processing flag
        self.processing_screenshot = True
        self.generate_button.setEnabled(False)
        self.optimize_button.setEnabled(False)
        self.progress_label.setText("Generating solution...")

        # Clear previous solution
        self.solution_text = ""
        self.code_editor.clear()

        # Get the selected language
        selected_language = self.language_combo.currentText()
        logger.info(f"Using language: {selected_language}")

        # Get all screenshot paths
        screenshot_paths = [screenshot["file_path"] for screenshot in screenshots]

        class ScreenshotProcessingThread(QThread):
            solution_ready = pyqtSignal(object)
            error_occurred = pyqtSignal(str)

            def __init__(self, llm_service, screenshot_paths, language):
                super().__init__()
                self.llm_service = llm_service
                self.screenshot_paths = screenshot_paths
                self.language = language

            def run(self):
                try:
                    logger.info(
                        f"Processing {len(self.screenshot_paths)} screenshots in thread"
                    )
                    solution = self.llm_service.get_solution_from_screenshots(
                        self.screenshot_paths, self.language
                    )
                    self.solution_ready.emit(solution)
                except Exception as e:
                    logger.info(f"Error in processing thread: {e}")
                    self.error_occurred.emit(str(e))

        # Create and start the thread
        self.processing_thread = ScreenshotProcessingThread(
            self.llm_service, screenshot_paths, selected_language
        )

        self.processing_thread.solution_ready.connect(self.on_solution_ready)
        self.processing_thread.error_occurred.connect(self.on_processing_error)
        self.processing_thread.start()

    @pyqtSlot()
    def optimize_solution(self):
        """Optimize the current solution."""
        # Check if there's a solution to optimize
        current_code = self.code_editor.toPlainText()
        if not current_code.strip():
            self.status_bar.showMessage(
                "No solution to optimize. Generate a solution first."
            )
            logger.info("No code to optimize")
            return

        # Check if processing is already in progress
        if self.processing_screenshot:
            self.status_bar.showMessage("Already processing request, please wait...")
            return

        self.status_bar.showMessage("Optimizing solution...")
        logger.info("Optimizing solution...")

        # Set processing flag
        self.processing_screenshot = True
        self.generate_button.setEnabled(False)
        self.optimize_button.setEnabled(False)
        self.progress_label.setText("Optimizing solution...")

        # Save original code and explanation for comparison
        self.original_code = current_code
        self.original_explanation = self.explanation_text.toPlainText()
        self.original_time_complexity = self.time_complexity.text()
        self.original_space_complexity = self.space_complexity.text()

        # Reset solution text
        self.solution_text = ""

        # Get the selected language
        selected_language = self.language_combo.currentText()
        logger.info(f"Using language: {selected_language} for optimization")

        class OptimizationThread(QThread):
            solution_ready = pyqtSignal(object)
            error_occurred = pyqtSignal(str)

            def __init__(self, llm_service, code, language):
                super().__init__()
                self.llm_service = llm_service
                self.code = code
                self.language = language

            def run(self):
                try:
                    logger.info("Processing code optimization in thread")
                    optimization = self.llm_service.get_code_optimization(
                        self.code, self.language
                    )
                    self.solution_ready.emit(optimization)
                except Exception as e:
                    logger.info(f"Error in optimization thread: {e}")
                    self.error_occurred.emit(str(e))

        # Create and start the thread
        self.optimization_thread = OptimizationThread(
            self.llm_service, current_code, selected_language
        )

        self.optimization_thread.solution_ready.connect(self.on_optimization_ready)
        self.optimization_thread.error_occurred.connect(self.on_processing_error)
        self.optimization_thread.start()

    def update_screen_list(self):
        """Update the list of available monitors in the dropdown."""
        self.screen_combo.clear()

        screens = self.screenshot_manager.get_available_screens()
        for screen in screens:
            display_name = f"{screen['name']} ({screen['width']}x{screen['height']})"
            if screen["primary"]:
                display_name += " (Primary)"
            self.screen_combo.addItem(display_name, screen["index"])

    @pyqtSlot(object)
    def on_solution_ready(self, solution):
        """
        Handle completed solution from LLM.

        Args:
            solution: The completed solution object
        """
        # Reset processing flag
        self.processing_screenshot = False
        self.generate_button.setEnabled(True)
        self.optimize_button.setEnabled(True)
        self.progress_label.setText("Idle")

        # Update UI with solution
        self.code_editor.setPlainText(solution.code)
        
        # Render explanation as markdown
        self.explanation_text.setMarkdown(solution.explanation)
        
        self.time_complexity.setText(solution.time_complexity)
        self.space_complexity.setText(solution.space_complexity)
        
        # Mark as not optimized and save session
        self._is_optimized = False
        self.save_session_data()

        self.status_bar.showMessage("Solution generated")
        logger.info("Solution generated successfully")

    @pyqtSlot(object)
    def on_optimization_ready(self, optimization):
        """
        Handle completed optimization from LLM.

        Args:
            optimization: The completed optimization object
        """
        # Reset processing flag
        self.processing_screenshot = False
        self.generate_button.setEnabled(True)
        self.optimize_button.setEnabled(True)
        self.progress_label.setText("Idle")

        # Update UI with optimized solution
        self.code_editor.setPlainText(optimization.optimized_code)

        # Create a detailed explanation that includes the improvements
        detailed_explanation = "## Optimization Details\n\n"
        detailed_explanation += optimization.explanation + "\n\n"
        detailed_explanation += "## Improvements\n\n"
        for improvement in optimization.improvements:
            detailed_explanation += f"- {improvement}\n"
        detailed_explanation += "\n\n## Time Complexity\n\n"
        detailed_explanation += f"**Original:** {optimization.original_time_complexity}\n\n"
        detailed_explanation += (
            f"**Optimized:** {optimization.optimized_time_complexity}\n\n"
        )
        detailed_explanation += "## Space Complexity\n\n"
        detailed_explanation += f"**Original:** {optimization.original_space_complexity}\n\n"
        detailed_explanation += (
            f"**Optimized:** {optimization.optimized_space_complexity}\n"
        )

        # Render explanation as markdown
        self.explanation_text.setMarkdown(detailed_explanation)
        self.time_complexity.setText(optimization.optimized_time_complexity)
        self.space_complexity.setText(optimization.optimized_space_complexity)
        
        # Mark as optimized and save session
        self._is_optimized = True
        self.save_session_data()

        self.status_bar.showMessage("Solution optimized")
        logger.info("Solution optimized successfully")

    @pyqtSlot(str)
    def on_processing_error(self, error_message):
        """
        Handle errors during screenshot processing.

        Args:
            error_message: The error message
        """
        # Reset processing flag
        self.processing_screenshot = False
        self.generate_button.setEnabled(True)
        self.optimize_button.setEnabled(True)
        self.progress_label.setText("Error")

        # Display error message
        self.status_bar.showMessage(f"Error processing request: {error_message}")
        logger.info(f"Error processing request: {error_message}")
        QMessageBox.critical(
            self, "Error", f"Failed to process request: {error_message}"
        )

    def copy_solution(self):
        """Copy the solution code to clipboard."""
        from PyQt6.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_editor.toPlainText())
        self.status_bar.showMessage("Solution copied to clipboard")
        logger.info("Solution copied to clipboard")
    
    def save_session_data(self):
        """Save current session data to preserve across UI refreshes."""
        self.current_session = {
            "code": self.code_editor.toPlainText(),
            "explanation": self.explanation_text.toMarkdown(),
            "time_complexity": self.time_complexity.text(),
            "space_complexity": self.space_complexity.text(),
            "is_optimized": getattr(self, '_is_optimized', False)
        }
        logger.debug("Session data saved")
    
    def restore_session_data(self):
        """Restore session data to UI components."""
        if self.current_session["code"]:
            self.code_editor.setPlainText(self.current_session["code"])
            self.explanation_text.setMarkdown(self.current_session["explanation"])
            self.time_complexity.setText(self.current_session["time_complexity"])
            self.space_complexity.setText(self.current_session["space_complexity"])
            logger.debug("Session data restored")
    
    def clear_session_data(self):
        """Clear session data and UI components."""
        self.current_session = {
            "code": "",
            "explanation": "",
            "time_complexity": "N/A",
            "space_complexity": "N/A",
            "is_optimized": False
        }
        self.code_editor.clear()
        self.explanation_text.setMarkdown("")
        self.time_complexity.setText("N/A")
        self.space_complexity.setText("N/A")
        self._is_optimized = False
        logger.debug("Session data cleared")

    def toggle_web_server(self):
        """Toggle the web server on/off."""
        if not WEB_SERVER_AVAILABLE:
            self.status_bar.showMessage("Web server not available - missing dependencies")
            return
        
        if self.web_server_thread and self.web_server_thread.isRunning():
            # Stop the web server
            try:
                self.web_server_thread.terminate()
                self.web_server_thread.wait(3000)  # Wait up to 3 seconds
                self.web_server_button.setText("Start Web Server")
                self.status_bar.showMessage("Web server stopped")
                if hasattr(self, 'web_server_status'):
                    self.web_server_status.setText("Web API: Stopped")
                    self.web_server_status.setStyleSheet("color: red;")
                logger.info("🛑 Web server stopped")
            except Exception as e:
                logger.error(f"Error stopping web server: {e}")
                self.status_bar.showMessage(f"Error stopping web server: {e}")
        else:
            # Start the web server
            try:
                if self.web_server_thread:
                    self.web_server_thread.start()
                    self.web_server_button.setText("Stop Web Server")
                    self.status_bar.showMessage("Web server started on all interfaces (port 8000)")
                    if hasattr(self, 'web_server_status'):
                        self.web_server_status.setText("Web API: Running")
                        self.web_server_status.setStyleSheet("color: green;")
                    logger.info("🚀 Web server started on http://0.0.0.0:8000 (accessible from all interfaces)")
                    
                    # Show notification with API info
                    if hasattr(self, 'tray_icon') and self.tray_icon:
                        self.tray_icon.showMessage(
                            "Web Server Started",
                            "API available on port 8000 (all interfaces)\nDocs: http://localhost:8000/docs",
                            QSystemTrayIcon.MessageIcon.Information,
                            5000
                        )
                else:
                    self.status_bar.showMessage("Web server not initialized")
            except Exception as e:
                logger.error(f"Error starting web server: {e}")
                self.status_bar.showMessage(f"Error starting web server: {e}")

    @pyqtSlot()
    def toggle_visibility(self):
        """Toggle the visibility of the application window."""
        logger.info(
            f"Toggle visibility called, current state: {self.invisibility_manager.is_visible}"
        )
        new_state = self.invisibility_manager.toggle_visibility()
        logger.info(f"Toggled visibility, new state: {new_state}")
        self.on_visibility_changed(new_state)

    @pyqtSlot(bool)
    def on_visibility_changed(self, is_visible: bool):
        """
        Handle visibility state changes.

        Args:
            is_visible: The new visibility state
        """
        if is_visible:
            self.visibility_button.setText("👁️")
            self.visibility_button.setToolTip("Hide Window")
            # Restore session data when becoming visible again
            if hasattr(self, 'current_session'):
                self.restore_session_data()
        else:
            self.visibility_button.setText("👁️‍🗨️")
            self.visibility_button.setToolTip("Show Window")
            # Save session data before hiding
            if hasattr(self, 'current_session'):
                self.save_session_data()

        self.status_bar.showMessage(
            f"Visibility set to {'visible' if is_visible else 'hidden'}"
        )
        logger.info(f"Visibility changed to: {is_visible}")

    @pyqtSlot(bool)
    def on_screen_sharing_detected(self, is_sharing: bool):
        """
        Handle screen sharing detection.

        Args:
            is_sharing: True if screen sharing was detected, False otherwise
        """
        if is_sharing:
            self.status_bar.showMessage(
                "Screen sharing detected! Window hidden automatically."
            )
            logger.info("Screen sharing detected, hiding window")
            # The invisibility manager should automatically hide the window
        else:
            self.status_bar.showMessage("Screen sharing ended.")
            logger.info("Screen sharing ended")

    @pyqtSlot(str)
    def move_window(self, direction: str):
        """
        Move the window in the specified direction.

        Args:
            direction: Direction to move ("up", "down", "left", "right")
        """
        # Fixed direct implementation to ensure window movement works
        distance = 60  # pixels to move
        current_pos = self.pos()
        new_x, new_y = current_pos.x(), current_pos.y()

        if direction == "up":
            new_y -= distance
        elif direction == "down":
            new_y += distance
        elif direction == "left":
            new_x -= distance
        elif direction == "right":
            new_x += distance

        # Direct window movement
        self.move(new_x, new_y)
        logger.info(f"Window moved {direction} to position ({new_x}, {new_y})")
        self.status_bar.showMessage(
            f"Window moved {direction} to position ({new_x}, {new_y})"
        )

    @pyqtSlot()
    def activate_panic_mode(self):
        """Activate panic mode to quickly hide the application."""
        logger.info("Panic mode activated!")
        self.invisibility_manager.set_visibility(False)
        self.status_bar.showMessage("Panic mode activated!")

    @pyqtSlot(int)
    def opacity_changed(self, value: int):
        """
        Handle opacity slider changes.

        Args:
            value: Opacity value from 10-100
        """
        opacity = value / 100.0
        self.set_opacity(opacity)

    def set_opacity(self, opacity: float):
        """
        Set the window opacity.

        Args:
            opacity: Opacity value from 0.0 to 1.0
        """
        # Set window opacity
        self.setWindowOpacity(opacity)
        logger.info(f"Window opacity set to {opacity}")

    def set_theme(self, theme_name: str):
        """
        Set the application theme.

        Args:
            theme_name: Name of the theme ("light" or "dark")
        """
        self.styles.set_theme(theme_name)

        # Update the application stylesheet
        self.setStyleSheet(self.styles.get_stylesheet())

        self.status_bar.showMessage(f"Theme changed to {theme_name}")
        logger.info(f"Theme changed to {theme_name}")

    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About AceBot",
            f"""
            <h1>🤖 AceBot</h1>
            <p>Version: {__import__("interview_corvus").__version__}</p>
            <p>Your intelligent coding assistant for technical interviews.</p>
            <p>AceBot helps you solve programming problems during technical interviews 
            by providing real-time solutions while remaining invisible during screen sharing.</p>
            <p>Built with ❤️ for developers</p>
            """,
        )

    def show_shortcuts(self):
        """Show the keyboard shortcuts dialog."""
        shortcuts = f"""
        <h2>Keyboard Shortcuts</h2>
        <ul>
            <li><b>{settings.hotkeys.screenshot_key}</b>: Take Screenshot</li>
            <li><b>{settings.hotkeys.generate_solution_key}</b>: Generate Solution</li>
            <li><b>{settings.hotkeys.optimize_solution_key}</b>: Optimize Solution</li>
            <li><b>{settings.hotkeys.toggle_visibility_key}</b>: Toggle Visibility</li>
            <li><b>{settings.hotkeys.reset_history_key}</b>: Reset Chat History and Screenshots</li>
            <li><b>{settings.hotkeys.move_window_keys["up"]}</b>: Move Window Up</li>
            <li><b>{settings.hotkeys.move_window_keys["down"]}</b>: Move Window Down</li>
            <li><b>{settings.hotkeys.move_window_keys["left"]}</b>: Move Window Left</li>
            <li><b>{settings.hotkeys.move_window_keys["right"]}</b>: Move Window Right</li>
            <li><b>{settings.hotkeys.panic_key}</b>: Panic Mode (Instant Hide)</li>
        </ul>
        """

        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts)

    def show_settings(self):
        """Show the settings dialog."""
        # Save current session before opening settings
        if hasattr(self, 'current_session'):
            self.save_session_data()
            
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update services that depend on settings
            self.llm_service = LLMService()

            # Reconnect signals
            self.llm_service.completion_finished.connect(self.on_solution_ready)
            self.llm_service.error_occurred.connect(self.on_processing_error)

            # Update UI to reflect new settings
            index = self.language_combo.findText(settings.default_language)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)

            # Update always on top setting
            self.set_always_on_top(settings.ui.always_on_top)

            # Update button texts with new hotkey settings
            self.update_button_texts()

            # Re-register hotkeys with the hotkey manager
            self.hotkey_manager.register_hotkeys(self)
            
            # Restore session data after settings update
            if hasattr(self, 'current_session'):
                self.restore_session_data()

            self.status_bar.showMessage("Settings updated")
            logger.info("Settings updated")

    def closeEvent(self, event):
        """
        Handle window close event.

        Args:
            event: Close event
        """
        # Stop web server if running
        if hasattr(self, 'web_server_thread') and self.web_server_thread and self.web_server_thread.isRunning():
            logger.info("Stopping web server...")
            self.web_server_thread.terminate()
            self.web_server_thread.wait(3000)
            logger.info("Web server stopped")

        if hasattr(self, "hotkey_manager"):
            self.hotkey_manager.stop_global_listener()

        event.accept()

        logger.info("Application closed")

        QApplication.quit()

    def changeEvent(self, event):
        """
        Handle window state changes for proper hotkey operation.
        """
        if event.type() == QEvent.Type.WindowStateChange:
            # Re-register hotkeys when minimizing/restoring
            self.hotkey_manager.register_hotkeys(self)
            logger.info("Re-registered hotkeys after window state change")

        super().changeEvent(event)

    def keyPressEvent(self, event):
        """
        Additional key press event handling.
        """
        # Debug information about pressed keys
        logger.info(f"Key pressed: {event.key()}, modifiers: {event.modifiers()}")

        # Standard key press handling
        super().keyPressEvent(event)

    def update_button_texts(self):
        """Update button texts to reflect current hotkey settings."""
        # Update tooltips since we're using minimal icon-based buttons
        self.screenshot_button.setToolTip(f"Take Screenshot ({settings.hotkeys.screenshot_key})")
        self.generate_button.setToolTip(f"Generate Solution ({settings.hotkeys.generate_solution_key})")
        self.optimize_button.setToolTip(f"Optimize Solution ({settings.hotkeys.optimize_solution_key})")
        self.visibility_button.setToolTip(f"Toggle Visibility ({settings.hotkeys.toggle_visibility_key})")

        # Also update menu actions if they exist
        if hasattr(self, "take_screenshot_action"):
            self.take_screenshot_action.setText(
                f"Take Screenshot ({settings.hotkeys.screenshot_key})"
            )
            self.take_screenshot_action.setShortcut(
                QKeySequence(settings.hotkeys.screenshot_key)
            )

        if hasattr(self, "generate_solution_action"):
            self.generate_solution_action.setText(
                f"Generate Solution ({settings.hotkeys.generate_solution_key})"
            )
            self.generate_solution_action.setShortcut(
                QKeySequence(settings.hotkeys.generate_solution_key)
            )

        if hasattr(self, "toggle_visibility_action"):
            self.toggle_visibility_action.setText(
                f"Toggle Visibility ({settings.hotkeys.toggle_visibility_key})"
            )
            self.toggle_visibility_action.setShortcut(
                QKeySequence(settings.hotkeys.toggle_visibility_key)
            )

        if hasattr(self, "optimize_solution_action"):
            self.optimize_solution_action.setText(
                f"Optimize Solution ({settings.hotkeys.optimize_solution_key})"
            )
            self.optimize_solution_action.setShortcut(
                QKeySequence(settings.hotkeys.optimize_solution_key)
            )

        if hasattr(self, "reset_history_action"):
            self.reset_history_action.setText(
                f"Reset All ({settings.hotkeys.reset_history_key})"
            )
            self.reset_history_action.setShortcut(
                QKeySequence(settings.hotkeys.reset_history_key)
            )
    
    def resizeEvent(self, event):
        """Handle resize events to preserve session data."""
        super().resizeEvent(event)
        # Save session data when window is resized (which can trigger UI refresh)
        if hasattr(self, 'current_session'):
            self.save_session_data()
    
    def showEvent(self, event):
        """Handle show events to restore session data."""
        super().showEvent(event)
        # Restore session data when window is shown (in case of UI refresh)
        if hasattr(self, 'current_session'):
            self.restore_session_data()

    def check_and_request_permissions(self):
        """Check for and request required permissions for global hotkey monitoring."""
        if platform.system() == "Darwin":
            import Cocoa
            import HIServices
            try:
                # Check if we have accessibility permissions
                trusted = HIServices.AXIsProcessTrusted()
                logger.info(f"Application accessibility permissions status: {trusted}")

                if not trusted:
                    # Show dialog explaining why we need permissions
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("Permissions Required")
                    msg.setText(
                        "AceBot needs Accessibility permissions to use global hotkeys."
                    )
                    msg.setInformativeText(
                        "You'll need to enable AceBot in System Preferences → Security & Privacy → Privacy → Accessibility."
                    )
                    msg.setDetailedText(
                        "Without these permissions, global hotkeys (like taking screenshots or toggling visibility) won't work outside the application window."
                    )

                    # Add button to open System Preferences
                    open_prefs_btn = msg.addButton(
                        "Open System Preferences", QMessageBox.ButtonRole.ActionRole
                    )
                    msg.addButton("Later", QMessageBox.ButtonRole.RejectRole)

                    msg.exec()

                    # If user clicked the button to open System Preferences
                    if msg.clickedButton() == open_prefs_btn:
                        # Open System Preferences at the Accessibility pane
                        Cocoa.NSWorkspace.sharedWorkspace().openURL_(
                            Cocoa.NSURL.URLWithString_(
                                "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
                            )
                        )
            except Exception as e:
                logger.error(f"Error checking accessibility permissions: {e}")
        
        # For Windows, request foreground window permission
        if platform.system() == "Windows":
            import ctypes
            from ctypes import wintypes

            # Define the user32 functions we need
            user32 = ctypes.WinDLL("user32", use_last_error=True)

            # Check if the process is running as administrator
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()

            if not is_admin:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Administrator Permission Required")
                msg.setText("AceBot needs to be run as administrator for the first time.")
                msg.setInformativeText("Right-click on the AceBot icon and select 'Run as administrator'.")
                msg.setDetailedText("This is required to enable global hotkeys and other features.")
                msg.addButton("OK", QMessageBox.ButtonRole.AcceptRole)

                msg.exec()

                # Attempt to relaunch the application as administrator
                import sys
                import os

                if not hasattr(sys, "_MEIPASS"):
                    # Not frozen with PyInstaller, normal launch
                    exe_path = sys.executable
                else:
                    # Frozen with PyInstaller, locate the exe
                    exe_path = os.path.join(sys._MEIPASS, "interview_corvus.exe")

                # Relaunch the application as administrator
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",  # This is the key part that requests admin
                    exe_path,
                    " ".join(sys.argv),  # Pass along any arguments
                    None,
                    1,  # Show normal window
                )

                # Exit the current instance
                QApplication.quit()
                sys.exit()

            # If we are admin, just continue
            logger.info("Running with administrator privileges")
