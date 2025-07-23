"""
Screenshot Controls Component.
Contains screenshot thumbnails display and monitor selection controls.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, 
    QComboBox, QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
from loguru import logger

from interview_corvus.config import settings


class ScreenshotControls(QWidget):
    """Widget for screenshot management and monitor selection."""
    
    # Signals
    screenshot_selected = pyqtSignal(int)  # screenshot index
    language_changed = pyqtSignal(str)
    
    def __init__(self, screenshot_manager, parent=None):
        super().__init__(parent)
        self.screenshot_manager = screenshot_manager
        self.selected_screenshot_index = -1
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Set up the screenshot controls UI."""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Screenshots preview section (70% width)
        screenshots_group = self.create_screenshots_section()
        layout.addWidget(screenshots_group, 7)  # stretch factor 7 for 70% space
        
        # Controls section (30% width)
        controls_group = self.create_controls_section()
        layout.addWidget(controls_group, 3)  # stretch factor 3 for 30% space
        
        self.setLayout(layout)
        self.setMinimumHeight(100)  # Ensure the screenshot controls section is visible
        
        # Set size policy to prevent collapse
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Add styling to make the controls visible
        self.setStyleSheet("""
            ScreenshotControls {
                background-color: #ffffff;
                border-bottom: 1px solid #e1e4e8;
                padding: 4px;
            }
            /* Ensure child widgets don't inherit restrictive styles */
            ScreenshotControls > QWidget {
                background: transparent;
            }
        """)
        
    def create_screenshots_section(self):
        """Create the screenshots preview section."""
        screenshots_group = QWidget()
        screenshots_layout = QVBoxLayout(screenshots_group)
        screenshots_layout.setContentsMargins(0, 4, 0, 4)
        
        # Header
        screenshots_header = QHBoxLayout()
        screenshots_label = QLabel("📷 Screenshots:")
        screenshots_label.setStyleSheet("font-weight: bold; color: #666; font-size: 12px;")
        screenshots_header.addWidget(screenshots_label)
        screenshots_header.addStretch()
        screenshots_layout.addLayout(screenshots_header)
        
        # Thumbnails container
        self.thumbnails_container = QWidget()
        self.thumbnails_layout = QHBoxLayout(self.thumbnails_container)
        self.thumbnails_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.thumbnails_layout.setContentsMargins(2, 2, 2, 2)
        self.thumbnails_layout.setSpacing(6)
        
        thumbnails_scroll = QScrollArea()
        thumbnails_scroll.setWidgetResizable(True)
        thumbnails_scroll.setWidget(self.thumbnails_container)
        thumbnails_scroll.setFixedHeight(80)
        thumbnails_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        thumbnails_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        screenshots_layout.addWidget(thumbnails_scroll)
        return screenshots_group
        
    def create_controls_section(self):
        """Create the language and monitor controls section."""
        controls_group = QWidget()
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setContentsMargins(8, 4, 0, 4)
        controls_layout.setSpacing(8)
        
        # Language selection
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
        self.language_combo.setMaximumWidth(200)  # Increased max width
        self.language_combo.setMinimumHeight(28)
        self.language_combo.setMaximumHeight(32)  # Use max height instead of fixed
        # Ensure dropdown can expand properly
        self.language_combo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #4A90E2;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ddd;
                background-color: white;
                selection-background-color: #4A90E2;
                selection-color: white;
                outline: none;
            }
        """)
        language_layout.addWidget(self.language_combo)
        controls_layout.addLayout(language_layout)
        
        # Monitor selection
        monitor_layout = QHBoxLayout()
        monitor_layout.setSpacing(6)
        monitor_label = QLabel("📺 Monitor:")
        monitor_label.setStyleSheet("font-weight: bold; color: #666; font-size: 12px;")
        monitor_layout.addWidget(monitor_label)
        
        self.screen_combo = QComboBox()
        self.update_screen_list()
        self.screen_combo.setMinimumWidth(120)
        self.screen_combo.setMaximumWidth(200)  # Increased max width
        self.screen_combo.setMinimumHeight(28)
        self.screen_combo.setMaximumHeight(32)  # Use max height instead of fixed
        # Ensure dropdown can expand properly
        self.screen_combo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.screen_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #4A90E2;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ddd;
                background-color: white;
                selection-background-color: #4A90E2;
                selection-color: white;
                outline: none;
            }
        """)
        monitor_layout.addWidget(self.screen_combo)
        controls_layout.addLayout(monitor_layout)
        
        controls_layout.addStretch()  # Push controls to top
        return controls_group
        
    def connect_signals(self):
        """Connect internal signals."""
        self.language_combo.currentTextChanged.connect(self.language_changed.emit)
        QApplication.instance().screenAdded.connect(self.update_screen_list)
        QApplication.instance().screenRemoved.connect(self.update_screen_list)
        
    def update_screen_list(self):
        """Update the list of available monitors in the dropdown."""
        self.screen_combo.clear()
        screens = self.screenshot_manager.get_available_screens()
        for screen in screens:
            display_name = f"{screen['name']} ({screen['width']}x{screen['height']})"
            if screen["primary"]:
                display_name += " (Primary)"
            self.screen_combo.addItem(display_name, screen["index"])
            
    def get_selected_screen_index(self):
        """Get the currently selected screen index."""
        return self.screen_combo.currentData()
        
    def update_thumbnails(self):
        """Update screenshot thumbnails display."""
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
            thumbnail_layout.setSpacing(2)
            
            # Create thumbnail
            thumbnail = QLabel()
            pixmap = screenshot["pixmap"].scaled(
                QSize(150, 120),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            thumbnail.setPixmap(pixmap)
            thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Style based on selection
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
            
            # Index number
            index_label = QLabel(f"#{i + 1}")
            index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            index_label.setStyleSheet("""
                font-size: 7px; 
                color: #888; 
                font-weight: normal;
                background-color: rgba(74, 144, 226, 0.08);
                border-radius: 1px;
                padding: 0px 2px;
                max-height: 12px;
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
            
            self.thumbnails_layout.addWidget(thumbnail_widget)
            
        # Auto-select most recent if none selected
        if self.selected_screenshot_index == -1 and screenshots:
            self.select_screenshot(len(screenshots) - 1)
            
    def select_screenshot(self, index):
        """Select a screenshot by index."""
        screenshots = self.screenshot_manager.get_all_screenshots()
        if 0 <= index < len(screenshots):
            self.selected_screenshot_index = index
            logger.info(f"Selected screenshot {index}")
            self.screenshot_selected.emit(index)
            self.update_thumbnails()
            
    def get_selected_screenshot_index(self):
        """Get the currently selected screenshot index."""
        return self.selected_screenshot_index
        
    def clear_screenshots(self):
        """Clear all screenshots and update display."""
        self.screenshot_manager.clear_screenshots()
        self.selected_screenshot_index = -1
        self.update_thumbnails()
