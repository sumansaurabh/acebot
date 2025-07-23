"""
Action Bar Component for the main window.
Contains all action buttons like screenshot, solve, optimize, etc.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QSizePolicy

from interview_corvus.config import settings


class ActionBar(QWidget):
    """Action bar with main function buttons."""
    
    # Signals
    screenshot_requested = pyqtSignal()
    generate_requested = pyqtSignal()
    optimize_requested = pyqtSignal()
    copy_requested = pyqtSignal()
    reset_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    visibility_toggle_requested = pyqtSignal()
    web_server_toggle_requested = pyqtSignal()
    file_upload_requested = pyqtSignal()
    recording_start_requested = pyqtSignal()
    recording_stop_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Set up the action bar UI."""
        layout = QHBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main action buttons
        self.screenshot_button = QPushButton("📸 Capture")
        self.screenshot_button.setToolTip(f"Take Screenshot ({settings.hotkeys.screenshot_key})")
        self.screenshot_button.setFixedSize(90, 35)
        layout.addWidget(self.screenshot_button)
        
        self.generate_button = QPushButton("🚀 Solve")
        self.generate_button.setToolTip(f"Generate Solution ({settings.hotkeys.generate_solution_key})")
        self.generate_button.setFixedSize(90, 35)
        self.generate_button.setEnabled(False)
        layout.addWidget(self.generate_button)
        
        self.optimize_button = QPushButton("⚡ Optimize")
        self.optimize_button.setToolTip(f"Optimize Solution ({settings.hotkeys.optimize_solution_key})")
        self.optimize_button.setFixedSize(90, 35)
        self.optimize_button.setEnabled(False)
        layout.addWidget(self.optimize_button)
        
        self.copy_button = QPushButton("📋 Copy")
        self.copy_button.setFixedSize(90, 35)
        self.copy_button.setToolTip("Copy Solution")
        self.copy_button.setEnabled(False)
        layout.addWidget(self.copy_button)
        
        # Upload button
        self.upload_button = QPushButton("📁 Upload")
        self.upload_button.setFixedSize(90, 35)
        self.upload_button.setToolTip("Upload Files and Save to Settings")
        layout.addWidget(self.upload_button)
        
        # Recording buttons
        self.record_button = QPushButton("🎙️ Record")
        self.record_button.setFixedSize(90, 35)
        self.record_button.setToolTip("Start Recording")
        layout.addWidget(self.record_button)
        
        self.stop_record_button = QPushButton("⏹️ Stop")
        self.stop_record_button.setFixedSize(90, 35)
        self.stop_record_button.setToolTip("Stop Recording & Analyze")
        self.stop_record_button.setEnabled(False)
        layout.addWidget(self.stop_record_button)
        
        # Reset button
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setFixedSize(85, 35)
        self.reset_button.setToolTip(f"Reset All ({settings.hotkeys.reset_history_key})")
        layout.addWidget(self.reset_button)
        
        # Add stretch to separate action buttons from header buttons
        layout.addStretch()
        
        # Header buttons (right side)
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.setFixedSize(80, 32)
        self.settings_button.setToolTip("Settings")
        layout.addWidget(self.settings_button)
        
        self.visibility_button = QPushButton("👁️ Hide")
        self.visibility_button.setFixedSize(70, 32)
        self.visibility_button.setToolTip(f"Toggle Visibility ({settings.hotkeys.toggle_visibility_key})")
        layout.addWidget(self.visibility_button)
        
        # Web server button (optional)
        try:
            from interview_corvus.api.web_server import create_integrated_web_server
            self.web_server_button = QPushButton("🌐 API")
            self.web_server_button.setFixedSize(70, 32)
            self.web_server_button.setToolTip("Toggle Web API Server")
            layout.addWidget(self.web_server_button)
        except ImportError:
            self.web_server_button = None
        
        # Set the layout and styling
        self.setLayout(layout)
        self.setMinimumHeight(40)
        self.setMaximumHeight(45)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.setStyleSheet("""
            ActionBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #e1e4e8;
                padding: 4px;
            }
        """)
        
    def connect_signals(self):
        """Connect button signals to class signals."""
        self.screenshot_button.clicked.connect(self.screenshot_requested.emit)
        self.generate_button.clicked.connect(self.generate_requested.emit)
        self.optimize_button.clicked.connect(self.optimize_requested.emit)
        self.copy_button.clicked.connect(self.copy_requested.emit)
        self.upload_button.clicked.connect(self.file_upload_requested.emit)
        self.record_button.clicked.connect(self.start_recording)
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.reset_button.clicked.connect(self.reset_requested.emit)
        self.settings_button.clicked.connect(self.settings_requested.emit)
        self.visibility_button.clicked.connect(self.visibility_toggle_requested.emit)
        
        if self.web_server_button:
            self.web_server_button.clicked.connect(self.web_server_toggle_requested.emit)
    
    def start_recording(self):
        """Handle start recording button click."""
        self.is_recording = True
        self.record_button.setEnabled(False)
        self.stop_record_button.setEnabled(True)
        self.record_button.setText("🔴 Recording")
        self.recording_start_requested.emit()
    
    def stop_recording(self):
        """Handle stop recording button click."""
        self.is_recording = False
        self.record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)
        self.record_button.setText("🎙️ Record")
        self.recording_stop_requested.emit()
    
    def set_recording_state(self, is_recording: bool):
        """Set the recording state from external source."""
        self.is_recording = is_recording
        self.record_button.setEnabled(not is_recording)
        self.stop_record_button.setEnabled(is_recording)
        if is_recording:
            self.record_button.setText("🔴 Recording")
        else:
            self.record_button.setText("🎙️ Record")
    
    def set_processing_state(self, processing: bool):
        """Enable/disable buttons based on processing state."""
        self.generate_button.setEnabled(not processing)
        self.optimize_button.setEnabled(not processing)
        # Don't disable recording buttons during processing
        
    def update_button_states(self, has_screenshots: bool = False, has_solution: bool = False):
        """Update button enabled states based on available content."""
        self.generate_button.setEnabled(has_screenshots)
        self.optimize_button.setEnabled(has_solution)
        self.copy_button.setEnabled(has_solution)
        
    def update_button_texts(self):
        """Update button tooltips to reflect current hotkey settings."""
        self.screenshot_button.setToolTip(f"Take Screenshot ({settings.hotkeys.screenshot_key})")
        self.generate_button.setToolTip(f"Generate Solution ({settings.hotkeys.generate_solution_key})")
        self.optimize_button.setToolTip(f"Optimize Solution ({settings.hotkeys.optimize_solution_key})")
        self.visibility_button.setToolTip(f"Toggle Visibility ({settings.hotkeys.toggle_visibility_key})")
