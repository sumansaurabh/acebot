"""
Menu and System Tray Component.
Handles menu bar and system tray functionality.
"""

from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QSystemTrayIcon, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QPixmap, QColor
from loguru import logger

from interview_corvus.config import settings
from interview_corvus.ui.styles import Theme


class MenuManager(QObject):
    """Manages menu bar and system tray functionality."""
    
    # Signals
    take_screenshot_triggered = pyqtSignal()
    generate_solution_triggered = pyqtSignal()
    optimize_solution_triggered = pyqtSignal()
    reset_history_triggered = pyqtSignal()
    toggle_visibility_triggered = pyqtSignal()
    show_settings_triggered = pyqtSignal()
    show_about_triggered = pyqtSignal()
    show_shortcuts_triggered = pyqtSignal()
    set_theme_triggered = pyqtSignal(str)
    toggle_always_on_top_triggered = pyqtSignal(bool)
    close_app_triggered = pyqtSignal()
    
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.menu_bar = None
        self.tray_icon = None
        self.always_on_top_action = None
        self.tray_always_on_top_action = None
        
    def create_menu_bar(self):
        """Create the application menu bar."""
        self.menu_bar = self.parent_window.menuBar()
        
        # File menu
        self._create_file_menu()
        
        # View menu
        self._create_view_menu()
        
        # Help menu
        self._create_help_menu()
        
        return self.menu_bar
        
    def _create_file_menu(self):
        """Create the File menu."""
        file_menu = self.menu_bar.addMenu("&File")
        
        # Take screenshot
        take_screenshot_action = QAction(
            f"Take Screenshot ({settings.hotkeys.screenshot_key})", self.parent_window
        )
        take_screenshot_action.setShortcut(settings.hotkeys.screenshot_key)
        take_screenshot_action.triggered.connect(self.take_screenshot_triggered.emit)
        file_menu.addAction(take_screenshot_action)
        
        # Settings
        settings_action = QAction("Settings", self.parent_window)
        settings_action.triggered.connect(self.show_settings_triggered.emit)
        file_menu.addAction(settings_action)
        
        # Generate solution
        generate_solution_action = QAction(
            f"Generate Solution ({settings.hotkeys.generate_solution_key})", self.parent_window
        )
        generate_solution_action.setShortcut(settings.hotkeys.generate_solution_key)
        generate_solution_action.triggered.connect(self.generate_solution_triggered.emit)
        file_menu.addAction(generate_solution_action)
        
        # Optimize solution
        optimize_solution_action = QAction(
            f"Optimize Solution ({settings.hotkeys.optimize_solution_key})", self.parent_window
        )
        optimize_solution_action.setShortcut(settings.hotkeys.optimize_solution_key)
        optimize_solution_action.triggered.connect(self.optimize_solution_triggered.emit)
        file_menu.addAction(optimize_solution_action)
        
        # Reset history
        reset_history_action = QAction(
            f"Reset All ({settings.hotkeys.reset_history_key})", self.parent_window
        )
        reset_history_action.setShortcut(settings.hotkeys.reset_history_key)
        reset_history_action.triggered.connect(self.reset_history_triggered.emit)
        file_menu.addAction(reset_history_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self.parent_window)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close_app_triggered.emit)
        file_menu.addAction(exit_action)
        
    def _create_view_menu(self):
        """Create the View menu."""
        view_menu = self.menu_bar.addMenu("&View")
        
        # Toggle visibility
        toggle_visibility_action = QAction(
            f"Toggle Visibility ({settings.hotkeys.toggle_visibility_key})", self.parent_window
        )
        toggle_visibility_action.setShortcut(settings.hotkeys.toggle_visibility_key)
        toggle_visibility_action.triggered.connect(self.toggle_visibility_triggered.emit)
        view_menu.addAction(toggle_visibility_action)
        
        # Always on top
        self.always_on_top_action = QAction("Always on Top", self.parent_window)
        self.always_on_top_action.setCheckable(True)
        self.always_on_top_action.setChecked(settings.ui.always_on_top)
        self.always_on_top_action.triggered.connect(
            lambda: self.toggle_always_on_top_triggered.emit(self.always_on_top_action.isChecked())
        )
        view_menu.addAction(self.always_on_top_action)
        
        # Theme submenu
        theme_menu = QMenu("Theme", self.parent_window)
        
        light_theme_action = QAction("Light", self.parent_window)
        light_theme_action.triggered.connect(lambda: self.set_theme_triggered.emit(Theme.LIGHT.value))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("Dark", self.parent_window)
        dark_theme_action.triggered.connect(lambda: self.set_theme_triggered.emit(Theme.DARK.value))
        theme_menu.addAction(dark_theme_action)
        
        view_menu.addMenu(theme_menu)
        
    def _create_help_menu(self):
        """Create the Help menu."""
        help_menu = self.menu_bar.addMenu("&Help")
        
        # About
        about_action = QAction("&About", self.parent_window)
        about_action.triggered.connect(self.show_about_triggered.emit)
        help_menu.addAction(about_action)
        
        # Shortcuts
        shortcuts_action = QAction("&Keyboard Shortcuts", self.parent_window)
        shortcuts_action.triggered.connect(self.show_shortcuts_triggered.emit)
        help_menu.addAction(shortcuts_action)
        
    def create_system_tray(self):
        """Create the system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self.parent_window)
        
        # Create a simple colored icon as fallback
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(74, 144, 226))  # Blue color matching theme
        icon = QIcon(pixmap)
        
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip(settings.app_name)
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # Create context menu
        tray_menu = QMenu()
        
        # Show/Hide
        show_action = tray_menu.addAction("Show/Hide")
        show_action.triggered.connect(self.toggle_visibility_triggered.emit)
        
        # Optimize solution
        optimize_action = tray_menu.addAction("Optimize Solution")
        optimize_action.triggered.connect(self.optimize_solution_triggered.emit)
        
        # Always on top
        self.tray_always_on_top_action = QAction("Always on Top", self.parent_window)
        self.tray_always_on_top_action.setCheckable(True)
        self.tray_always_on_top_action.setChecked(settings.ui.always_on_top)
        self.tray_always_on_top_action.triggered.connect(
            lambda: self.toggle_always_on_top_triggered.emit(self.tray_always_on_top_action.isChecked())
        )
        tray_menu.addAction(self.tray_always_on_top_action)
        
        # Reset history
        reset_history_action = tray_menu.addAction("Reset All")
        reset_history_action.triggered.connect(self.reset_history_triggered.emit)
        
        tray_menu.addSeparator()
        
        # Quit
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.close_app_triggered.emit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        return self.tray_icon
        
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            logger.info("Tray icon clicked - toggling visibility")
            self.toggle_visibility_triggered.emit()
            
    def update_always_on_top_state(self, enabled: bool):
        """Update the always on top menu state."""
        if self.always_on_top_action:
            self.always_on_top_action.setChecked(enabled)
        if self.tray_always_on_top_action:
            self.tray_always_on_top_action.setChecked(enabled)
            
    def show_about_dialog(self):
        """Show the about dialog."""
        about_text = f"""
        <h2>{settings.app_name}</h2>
        <p>An intelligent coding assistant for interview preparation.</p>
        <p>Version: 1.0.0</p>
        <p>Built with PyQt6 and modern AI technologies.</p>
        """
        QMessageBox.about(self.parent_window, "About", about_text)
        
    def show_shortcuts_dialog(self):
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
        QMessageBox.information(self.parent_window, "Keyboard Shortcuts", shortcuts)
