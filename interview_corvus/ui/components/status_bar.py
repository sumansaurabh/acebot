"""
Status Bar Component.
Handles status bar display and web server status.
"""

from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import QObject, pyqtSignal
from loguru import logger

from interview_corvus.config import settings


class StatusBarManager(QObject):
    """Manages the status bar and its components."""
    
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.status_bar = None
        self.progress_label = None
        self.app_title_label = None
        self.web_server_status = None
        
    def create_status_bar(self):
        """Create and set up the status bar."""
        self.status_bar = QStatusBar()
        self.parent_window.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Progress indicator
        self.progress_label = QLabel("Idle")
        self.progress_label.setStyleSheet("color: #4A90E2; font-weight: bold; font-size: 11px;")
        self.status_bar.addPermanentWidget(self.progress_label)
        
        # App title in the middle
        self.app_title_label = QLabel("🤖 AceBot")
        self.app_title_label.setStyleSheet("color: #4A90E2; font-weight: bold; font-size: 12px; padding: 0 16px;")
        self.status_bar.addPermanentWidget(self.app_title_label)
        
        # Web server status (if available)
        try:
            from interview_corvus.api.web_server import create_integrated_web_server
            self.web_server_status = QLabel("🌐 API: Off")
            self.web_server_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
            self.status_bar.addPermanentWidget(self.web_server_status)
        except ImportError:
            logger.debug("Web server not available, skipping status widget")
            
        return self.status_bar
        
    def show_message(self, message: str, timeout: int = 0):
        """Show a message in the status bar."""
        if self.status_bar:
            self.status_bar.showMessage(message, timeout)
            
    def set_progress_text(self, text: str):
        """Set the progress indicator text."""
        if self.progress_label:
            self.progress_label.setText(text)
            
    def update_web_server_status(self, is_running: bool):
        """Update the web server status display."""
        if self.web_server_status:
            if is_running:
                self.web_server_status.setText("🌐 API: On")
                self.web_server_status.setStyleSheet("color: #51cf66; font-weight: bold; font-size: 12px;")
            else:
                self.web_server_status.setText("🌐 API: Off")
                self.web_server_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
