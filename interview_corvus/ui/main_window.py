"""
Refactored Main Window using separate components.
This version breaks down the original large MainWindow class into manageable components.
"""

import platform
from loguru import logger
from PyQt6.QtCore import QEvent, Qt, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox, QDialog
)

from interview_corvus.config import settings
from interview_corvus.core.hotkey_manager import HotkeyManager
from interview_corvus.core.llm_service import LLMService
from interview_corvus.invisibility.invisibility_manager import InvisibilityManager
from interview_corvus.screenshot.screenshot_manager import ScreenshotManager
from interview_corvus.ui.settings_dialog import SettingsDialog
from interview_corvus.ui.styles import Styles, Theme

# Import our new components
from interview_corvus.ui.components.action_bar import ActionBar
from interview_corvus.ui.components.screenshot_controls import ScreenshotControls
from interview_corvus.ui.components.content_display import ContentDisplay
from interview_corvus.ui.components.menu_manager import MenuManager
from interview_corvus.ui.components.status_bar import StatusBarManager

# Try to import web server (optional dependency)
try:
    from interview_corvus.api.web_server import create_integrated_web_server
    WEB_SERVER_AVAILABLE = True
except ImportError:
    WEB_SERVER_AVAILABLE = False
    logger.warning("Web server dependencies not available. Web API will be disabled.")


class MainWindow(QMainWindow):
    """
    Refactored main application window using separate components.
    Handles coordination between components and core application logic.
    """

    def __init__(self, invisibility_manager: InvisibilityManager, hotkey_manager: HotkeyManager):
        """Initialize the main window with component-based architecture."""
        super().__init__()

        # Core managers
        self.invisibility_manager = invisibility_manager
        self.hotkey_manager = hotkey_manager
        # hotkey disabled, so no permissions for now
        # self.check_and_request_permissions()

        # Initialize services
        self.screenshot_manager = ScreenshotManager()
        self.llm_service = LLMService()
        self.styles = Styles()

        # Initialize web server (optional)
        self.web_api = None
        self.web_server_thread = None
        self.web_server_port = None
        if WEB_SERVER_AVAILABLE:
            self._initialize_web_server()

        # Connect LLM service signals
        self.llm_service.completion_finished.connect(self.on_solution_ready)
        self.llm_service.error_occurred.connect(self.on_processing_error)

        # Processing state
        self.processing_screenshot = False
        self.solution_text = ""

        # Auto-save timer for session persistence
        self.session_save_timer = QTimer()
        self.session_save_timer.setSingleShot(True)
        self.session_save_timer.timeout.connect(self._save_session_data)

        # Set up UI with components
        self.init_ui()

        # Connect all signals
        self.connect_signals()

        # Set window properties
        self.setWindowTitle(settings.app_name)
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        # Initialize opacity and always on top
        self.set_opacity(1.0)
        self.set_always_on_top(settings.ui.always_on_top)

        # Set window handle for invisibility manager
        self.invisibility_manager.set_window_handle(self)
        logger.info(f"Window visibility at startup: {self.invisibility_manager.is_visible}")

        # Register hotkeys
        self.hotkey_manager.register_hotkeys(self)
        self.installEventFilter(self.hotkey_manager)

    def _initialize_web_server(self):
        """Initialize the optional web server."""
        try:
            self.web_api, self.web_server_thread, actual_port = create_integrated_web_server(
                llm_service=self.llm_service,
                screenshot_manager=self.screenshot_manager,
                host="0.0.0.0",
                port=26262  # Changed from 8000 to 26262 as requested
            )
            self.web_server_port = actual_port  # Store the actual port used
            logger.info(f"✅ Web server initialized successfully on port {actual_port}")

            # Connect web server signals
            self.web_api.screenshot_capture_requested.connect(self.take_screenshot)
            self.web_api.screenshots_cleared.connect(self.clear_screenshots)
            self.web_api.chat_history_reset.connect(self.reset_chat_history)
            self.web_api.window_show_requested.connect(self.show)
            self.web_api.window_hide_requested.connect(self.hide)
            self.web_api.window_toggle_requested.connect(self.toggle_visibility)
            self.web_api.language_changed.connect(self.on_language_changed_from_web)
            
            # Connect bidirectional solution synchronization signals
            self.web_api.solution_generated_from_web.connect(self.on_solution_ready)
            self.web_api.optimization_generated_from_web.connect(self.on_optimization_ready)

            # Auto-start the web server
            if self.web_server_thread:
                self.web_server_thread.start()
                logger.info(f"🚀 Web server auto-started on port {actual_port}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize web server: {e}")
            self.web_api = None
            self.web_server_thread = None
            self.web_server_port = None

    def init_ui(self):
        """Set up the user interface with components."""
        # Set stylesheet
        self.setStyleSheet(self._get_minimal_stylesheet())
        logger.info("Stylesheet applied")

        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(12, 4, 12, 12)
        logger.info("Central widget and main layout created")

        # Create and add action bar
        self.action_bar = ActionBar(self)
        main_layout.addWidget(self.action_bar, 0)  # No stretch
        logger.info("Action bar created and added to layout")

        # Create and add screenshot controls
        self.screenshot_controls = ScreenshotControls(self.screenshot_manager, self)
        main_layout.addWidget(self.screenshot_controls, 0)  # No stretch
        logger.info("Screenshot controls created and added to layout")

        # Create and add content display
        self.content_display = ContentDisplay(self)
        main_layout.addWidget(self.content_display, 1)  # stretch factor of 1
        logger.info("Content display created and added to layout")

        # Set up main widget
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        logger.info("Central widget set up and assigned to main window")

        # Create menu manager and set up menus
        self.menu_manager = MenuManager(self)
        self.menu_manager.create_menu_bar()
        self.menu_manager.create_system_tray()
        logger.info("Menu manager created")

        # Create status bar manager
        self.status_bar_manager = StatusBarManager(self)
        self.status_bar_manager.create_status_bar()
        logger.info("Status bar manager created")

        # Update initial state
        self.screenshot_controls.update_thumbnails()
        self.action_bar.update_button_texts()
        logger.info("Initial state updated")

        # Update web server status if auto-started
        if WEB_SERVER_AVAILABLE and self.web_server_thread and self.web_server_thread.isRunning():
            self.status_bar_manager.update_web_server_status(True, self.web_server_port)
            logger.info("Web server status updated")

    def connect_signals(self):
        """Connect all component signals to handlers."""
        # Action bar signals
        self.action_bar.screenshot_requested.connect(self.take_screenshot)
        self.action_bar.generate_requested.connect(self.generate_solution)
        self.action_bar.optimize_requested.connect(self.optimize_solution)
        self.action_bar.copy_requested.connect(self.copy_solution)
        self.action_bar.reset_requested.connect(self.reset_chat_history)
        self.action_bar.settings_requested.connect(self.show_settings)
        self.action_bar.visibility_toggle_requested.connect(self.toggle_visibility)
        if self.action_bar.web_server_button:
            self.action_bar.web_server_toggle_requested.connect(self.toggle_web_server)

        # Screenshot controls signals
        self.screenshot_controls.screenshot_selected.connect(self._on_screenshot_selected)
        self.screenshot_controls.language_changed.connect(self.on_language_changed)

        # Content display signals
        self.content_display.code_changed.connect(self.on_code_changed)

        # Menu manager signals
        self.menu_manager.take_screenshot_triggered.connect(self.take_screenshot)
        self.menu_manager.generate_solution_triggered.connect(self.generate_solution)
        self.menu_manager.optimize_solution_triggered.connect(self.optimize_solution)
        self.menu_manager.reset_history_triggered.connect(self.reset_chat_history)
        self.menu_manager.toggle_visibility_triggered.connect(self.toggle_visibility)
        self.menu_manager.show_settings_triggered.connect(self.show_settings)
        self.menu_manager.show_about_triggered.connect(self._show_about)
        self.menu_manager.show_shortcuts_triggered.connect(self._show_shortcuts)
        self.menu_manager.set_theme_triggered.connect(self.set_theme)
        self.menu_manager.toggle_always_on_top_triggered.connect(self.set_always_on_top)
        self.menu_manager.close_app_triggered.connect(self.close)

        # Hotkey manager signals
        self.hotkey_manager.screenshot_triggered.connect(self.take_screenshot)
        self.hotkey_manager.solution_triggered.connect(self.generate_solution)
        self.hotkey_manager.visibility_triggered.connect(self.toggle_visibility)
        self.hotkey_manager.move_window_triggered.connect(self.move_window)
        self.hotkey_manager.panic_triggered.connect(self.activate_panic_mode)
        self.hotkey_manager.optimize_solution_triggered.connect(self.optimize_solution)
        self.hotkey_manager.reset_history_triggered.connect(self.reset_chat_history)

        # Invisibility manager signals
        self.invisibility_manager.visibility_changed.connect(self.on_visibility_changed)
        self.invisibility_manager.screen_sharing_detected.connect(self.on_screen_sharing_detected)

        # Screen change signals
        QApplication.instance().screenAdded.connect(self.screenshot_controls.update_screen_list)
        QApplication.instance().screenRemoved.connect(self.screenshot_controls.update_screen_list)

        logger.info("Connected all component signals")

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

    # Core action methods
    @pyqtSlot()
    def take_screenshot(self):
        """Take a screenshot without generating a solution."""
        self.status_bar_manager.show_message("Taking screenshot...")
        logger.info("Taking screenshot...")

        # Get the index of the selected monitor
        selected_index = self.screenshot_controls.get_selected_screen_index()

        # Temporarily hide the window if visible using invisibility manager
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
        self.status_bar_manager.show_message(
            f"Screenshot captured: {screenshot['width']}x{screenshot['height']}"
        )
        self.screenshot_controls.update_thumbnails()
        # Select the newly captured screenshot (last one in the list)
        screenshot_count = len(self.screenshot_manager.get_all_screenshots())
        if screenshot_count > 0:
            self.screenshot_controls.select_screenshot(screenshot_count - 1)
            
        # Update action bar button states - enable generate button when screenshots are available
        has_screenshots = len(self.screenshot_manager.get_all_screenshots()) > 0
        has_solution = bool(self.solution_text.strip())
        self.action_bar.update_button_states(has_screenshots=has_screenshots, has_solution=has_solution)

    @pyqtSlot()
    def generate_solution(self):
        """Generate a solution based on all available screenshots."""
        if self.processing_screenshot:
            self.status_bar_manager.show_message("Already processing screenshot, please wait...")
            return

        screenshots = self.screenshot_manager.get_all_screenshots()
        if not screenshots:
            self.status_bar_manager.show_message("No screenshots available. Take a screenshot first.")
            return

        self.status_bar_manager.show_message(f"Generating solution from {len(screenshots)} screenshots...")
        logger.info(f"Generating solution from {len(screenshots)} screenshots...")

        # Set processing state
        self.processing_screenshot = True
        self.action_bar.set_processing_state(True)
        self.status_bar_manager.set_progress_text("Generating solution...")

        # Clear previous solution
        self.solution_text = ""

        # Get selected language and screenshot paths
        selected_language = self.screenshot_controls.language_combo.currentText()
        screenshot_paths = [screenshot["file_path"] for screenshot in screenshots]

        # Create and start processing thread
        self.processing_thread = self._create_solution_thread(screenshot_paths, selected_language)
        self.processing_thread.solution_ready.connect(self.on_solution_ready)
        self.processing_thread.error_occurred.connect(self.on_processing_error)
        self.processing_thread.start()

    @pyqtSlot()
    def optimize_solution(self):
        """Optimize the current solution."""
        current_code = self.content_display.get_current_code()
        if not current_code.strip():
            self.status_bar_manager.show_message("No solution to optimize. Generate a solution first.")
            return

        if self.processing_screenshot:
            self.status_bar_manager.show_message("Already processing request, please wait...")
            return

        self.status_bar_manager.show_message("Optimizing solution...")
        logger.info("Optimizing solution...")

        # Set processing state
        self.processing_screenshot = True
        self.action_bar.set_processing_state(True)
        self.status_bar_manager.set_progress_text("Optimizing solution...")

        # Get selected language
        selected_language = self.screenshot_controls.language_combo.currentText()

        # Create and start optimization thread
        self.optimization_thread = self._create_optimization_thread(current_code, selected_language)
        self.optimization_thread.solution_ready.connect(self.on_optimization_ready)
        self.optimization_thread.error_occurred.connect(self.on_processing_error)
        self.optimization_thread.start()

    def _create_solution_thread(self, screenshot_paths, language):
        """Create a thread for solution generation."""
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
                    logger.info(f"Processing {len(self.screenshot_paths)} screenshots in thread")
                    solution = self.llm_service.get_solution_from_screenshots(
                        self.screenshot_paths, self.language
                    )
                    self.solution_ready.emit(solution)
                except Exception as e:
                    logger.error(f"Error in processing thread: {e}")
                    self.error_occurred.emit(str(e))

        return ScreenshotProcessingThread(self.llm_service, screenshot_paths, language)

    def _create_optimization_thread(self, code, language):
        """Create a thread for optimization."""
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
                    optimization = self.llm_service.get_code_optimization(self.code, self.language)
                    self.solution_ready.emit(optimization)
                except Exception as e:
                    logger.error(f"Error in optimization thread: {e}")
                    self.error_occurred.emit(str(e))

        return OptimizationThread(self.llm_service, code, language)

    @pyqtSlot()
    def reset_chat_history(self):
        """Reset the chat history and clear screenshots."""
        if hasattr(self.llm_service, "reset_chat_history"):
            self.llm_service.reset_chat_history()
            self.screenshot_controls.clear_screenshots()
            self.content_display.clear_content()
            self.status_bar_manager.show_message("Chat history and screenshots reset.")
            logger.info("Chat history and screenshots have been reset")
        else:
            self.status_bar_manager.show_message("Chat history reset not implemented.")

    def copy_solution(self):
        """Copy the solution code to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.content_display.get_current_code())
        self.status_bar_manager.show_message("Solution copied to clipboard")
        logger.info("Solution copied to clipboard")

    def clear_screenshots(self):
        """Clear all screenshots."""
        self.screenshot_controls.clear_screenshots()
        self.content_display.clear_content()
        self.status_bar_manager.show_message("All screenshots cleared")

    # Signal handlers
    @pyqtSlot(object)
    def on_solution_ready(self, solution):
        """Handle completed solution from LLM."""
        self.processing_screenshot = False
        self.action_bar.set_processing_state(False)
        self.status_bar_manager.set_progress_text("Idle")

        self.content_display.display_solution(solution)
        
        # Extract solution text for button state management
        if hasattr(solution, 'code'):
            self.solution_text = solution.code
        elif hasattr(solution, 'solution'):
            self.solution_text = solution.solution
        else:
            self.solution_text = str(solution)
        
        # Update button states to enable optimize and copy buttons
        has_screenshots = len(self.screenshot_manager.get_all_screenshots()) > 0
        has_solution = bool(self.solution_text.strip())
        self.action_bar.update_button_states(has_screenshots=has_screenshots, has_solution=has_solution)
        
        # Update web API state if connected
        if self.web_api:
            self.web_api.update_solution_from_gui(solution)
        
        self.status_bar_manager.show_message("Solution generated")
        logger.info("Solution generated successfully")

    @pyqtSlot(object)
    def on_optimization_ready(self, optimization):
        """Handle completed optimization from LLM."""
        self.processing_screenshot = False
        self.action_bar.set_processing_state(False)
        self.status_bar_manager.set_progress_text("Idle")

        self.content_display.display_optimization(optimization)
        self.solution_text = optimization.optimized_code if hasattr(optimization, 'optimized_code') else str(optimization)
        
        # Update button states
        has_screenshots = len(self.screenshot_manager.get_all_screenshots()) > 0
        has_solution = bool(self.solution_text.strip())
        self.action_bar.update_button_states(has_screenshots=has_screenshots, has_solution=has_solution)
        
        # Update web API state if connected
        if self.web_api:
            self.web_api.update_optimization_from_gui(optimization)
        
        self.status_bar_manager.show_message("Solution optimized")
        logger.info("Solution optimized successfully")

    @pyqtSlot(str)
    def on_processing_error(self, error_message):
        """Handle errors during processing."""
        self.processing_screenshot = False
        self.action_bar.set_processing_state(False)
        self.status_bar_manager.set_progress_text("Error")

        self.status_bar_manager.show_message(f"Error processing request: {error_message}")
        logger.error(f"Error processing request: {error_message}")
        QMessageBox.critical(self, "Error", f"Failed to process request: {error_message}")

    @pyqtSlot(str)
    def on_language_changed(self, language: str):
        """Handle language change from screenshot controls."""
        logger.info(f"Language changed to: {language}")
        # Update web API state if connected
        if self.web_api:
            self.web_api.update_language_from_gui(language)    @pyqtSlot(str)
    def on_language_changed_from_web(self, language: str):
        """Handle language changes from web API."""
        # Update the GUI language dropdown to match web selection
        index = self.screenshot_controls.language_combo.findText(language)
        if index >= 0:
            # Block signals temporarily to prevent recursive calls
            self.screenshot_controls.language_combo.blockSignals(True)
            self.screenshot_controls.language_combo.setCurrentIndex(index)
            self.screenshot_controls.language_combo.blockSignals(False)
        
        # Update settings and show message
        settings.default_language = language
        self.status_bar_manager.show_message(f"Language updated from web to {language}")
        settings.save_user_settings()

    def on_code_changed(self):
        """Handle code editor changes."""
        self.session_save_timer.start(500)

    def _on_screenshot_selected(self, index):
        """Handle screenshot selection."""
        self.status_bar_manager.show_message(f"Selected screenshot {index + 1}")

    def _save_session_data(self):
        """Save session data."""
        self.content_display.save_session_data()

    # Window management methods
    def set_always_on_top(self, enabled: bool):
        """Set whether the window should always be on top."""
        flags = self.windowFlags()
        has_flag = bool(flags & Qt.WindowType.WindowStaysOnTopHint)
        
        if has_flag == enabled:
            return

        if enabled:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint

        pos = self.pos()
        visible = self.isVisible()

        self.setWindowFlags(flags)
        self.move(pos)

        if visible:
            self.show()

        settings.ui.always_on_top = enabled
        settings.save_user_settings()

        self.menu_manager.update_always_on_top_state(enabled)
        logger.info(f"Always on top set to: {enabled}")
        self.status_bar_manager.show_message(f"Always on top: {'enabled' if enabled else 'disabled'}")

    def set_opacity(self, opacity: float):
        """Set window opacity."""
        self.setWindowOpacity(opacity)

    def set_theme(self, theme_name: str):
        """Set the application theme."""
        self.styles.set_theme(Theme(theme_name))
        self.status_bar_manager.show_message(f"Theme set to {theme_name}")

    @pyqtSlot()
    def toggle_visibility(self):
        """Toggle the visibility of the application window."""
        logger.info(f"Toggle visibility called, current state: {self.invisibility_manager.is_visible}")
        new_state = self.invisibility_manager.toggle_visibility()
        logger.info(f"Toggled visibility, new state: {new_state}")
        self.on_visibility_changed(new_state)

    @pyqtSlot(bool)
    def on_visibility_changed(self, is_visible: bool):
        """Handle visibility state changes."""
        if is_visible:
            self.action_bar.visibility_button.setText("👁️ Hide")
        else:
            self.action_bar.visibility_button.setText("👁️ Show")
        logger.info(f"Visibility changed to: {is_visible}")

    @pyqtSlot(bool)
    def on_screen_sharing_detected(self, is_sharing: bool):
        """Handle screen sharing detection."""
        if is_sharing:
            logger.info("Screen sharing detected - hiding window")
            self.invisibility_manager.set_visibility(False)

    @pyqtSlot(str)
    def move_window(self, direction: str):
        """Move window in the specified direction."""
        geometry = self.geometry()
        x, y = geometry.x(), geometry.y()
        
        move_distance = 50
        
        if direction == "up":
            y = max(0, y - move_distance)
        elif direction == "down":
            y += move_distance
        elif direction == "left":
            x = max(0, x - move_distance)
        elif direction == "right":
            x += move_distance
            
        self.move(x, y)
        logger.info(f"Moved window {direction} to ({x}, {y})")

    @pyqtSlot()
    def activate_panic_mode(self):
        """Activate panic mode to quickly hide the application."""
        self.invisibility_manager.set_visibility(False)
        logger.info("Panic mode activated - window hidden")

    def toggle_web_server(self):
        """Toggle the web server on/off."""
        if not WEB_SERVER_AVAILABLE:
            return

        if self.web_server_thread and self.web_server_thread.isRunning():
            self.web_server_thread.terminate()
            self.web_server_thread.wait(3000)
            self.status_bar_manager.update_web_server_status(False)
            self.status_bar_manager.show_message("Web server stopped")
        else:
            if self.web_server_thread:
                self.web_server_thread.start()
                self.status_bar_manager.update_web_server_status(True, self.web_server_port)
                self.status_bar_manager.show_message("Web server started")

    # Dialog methods
    def show_settings(self):
        """Show the settings dialog."""
        self.content_display.save_session_data()
        
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update services
            self.llm_service = LLMService()
            self.llm_service.completion_finished.connect(self.on_solution_ready)
            self.llm_service.error_occurred.connect(self.on_processing_error)

            # Update UI
            index = self.screenshot_controls.language_combo.findText(settings.default_language)
            if index >= 0:
                self.screenshot_controls.language_combo.setCurrentIndex(index)

            self.set_always_on_top(settings.ui.always_on_top)
            self.action_bar.update_button_texts()
            self.hotkey_manager.register_hotkeys(self)
            self.content_display.restore_session_data()

            self.status_bar_manager.show_message("Settings updated")
            logger.info("Settings updated")

    def _show_about(self):
        """Show the about dialog."""
        self.menu_manager.show_about_dialog()

    def _show_shortcuts(self):
        """Show the keyboard shortcuts dialog."""
        self.menu_manager.show_shortcuts_dialog()

    # Permissions and system integration
    def check_and_request_permissions(self):
        """Check for and request required permissions."""
        if platform.system() == "Darwin":
            self._check_macos_permissions()
        elif platform.system() == "Windows":
            self._check_windows_permissions()

    def _check_macos_permissions(self):
        """Check macOS accessibility permissions."""
        try:
            import Cocoa
            import HIServices
            
            trusted = HIServices.AXIsProcessTrusted()
            logger.info(f"Application accessibility permissions status: {trusted}")

            if not trusted:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Permissions Required")
                msg.setText("AceBot needs Accessibility permissions to use global hotkeys.")
                msg.setInformativeText(
                    "You'll need to enable AceBot in System Preferences → Security & Privacy → Privacy → Accessibility."
                )
                msg.exec()

        except Exception as e:
            logger.error(f"Error checking accessibility permissions: {e}")

    def _check_windows_permissions(self):
        """Check Windows administrator permissions."""
        try:
            import ctypes
            
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Administrator Permission Required")
                msg.setText("AceBot needs to be run as administrator for the first time.")
                msg.setInformativeText("Right-click on the AceBot icon and select 'Run as administrator'.")
                msg.exec()

        except Exception as e:
            logger.error(f"Error checking Windows permissions: {e}")

    # Event handlers
    def closeEvent(self, event):
        """Handle window close event."""
        if hasattr(self, 'web_server_thread') and self.web_server_thread and self.web_server_thread.isRunning():
            logger.info("Stopping web server...")
            self.web_server_thread.terminate()
            self.web_server_thread.wait(3000)

        if hasattr(self, "hotkey_manager"):
            self.hotkey_manager.stop_global_listener()

        event.accept()
        logger.info("Application closed")
        QApplication.quit()

    def changeEvent(self, event):
        """Handle window state changes."""
        if event.type() == QEvent.Type.WindowStateChange:
            self.hotkey_manager.register_hotkeys(self)
            logger.info("Re-registered hotkeys after window state change")
        super().changeEvent(event)

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        self.content_display.save_session_data()

    def showEvent(self, event):
        """Handle show events."""
        super().showEvent(event)
        # self.content_display.restore_session_data()
