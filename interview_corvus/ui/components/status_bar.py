"""
Status Bar Component.
Handles status bar display and web server status.
"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QApplication, QPushButton, QHBoxLayout, QWidget
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QCursor
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
        self.network_ips_widget = None
        self.network_ips = []
        
    def get_network_ips(self):
        """Get network IP addresses excluding localhost."""
        try:
            from interview_corvus.api.network_utils import get_local_ip_addresses
            all_ips = get_local_ip_addresses()
            # Filter out localhost
            network_ips = [ip for ip in all_ips if ip != '127.0.0.1']
            self.network_ips = network_ips
            logger.info(f"Network IPs for status bar: {network_ips}")
            return network_ips
        except ImportError:
            logger.debug("Network utils not available")
            return []
        except Exception as e:
            logger.error(f"Error getting network IPs: {e}")
            return []
    
    def create_network_ips_widget(self):
        """Create widget showing network IP addresses with port and copy functionality."""
        network_ips = self.get_network_ips()
        if not network_ips:
            return None
            
        # Get the current web server port
        server_port = getattr(self.parent_window, 'web_server_port', 26262)
            
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Add label
        ip_label = QLabel("📡")
        ip_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(ip_label)
        
        # Add IP addresses with port as clickable labels
        for i, ip in enumerate(network_ips):
            ip_with_port = f"{ip}:{server_port}"
            ip_button = QPushButton(ip_with_port)
            ip_button.setFlat(True)
            ip_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            ip_button.setStyleSheet("""
                QPushButton {
                    color: #2c5aa0; 
                    background-color: #f8f9fa;
                    font-weight: 500; 
                    font-size: 10px; 
                    border: 1px solid #e1e4e8;
                    border-radius: 3px;
                    padding: 1px 4px;
                    margin: 0px;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                    border-color: #4A90E2;
                    color: #1976d2;
                }
                QPushButton:pressed {
                    background-color: #bbdefb;
                }
            """)
            ip_button.setToolTip(f"Click to copy {ip_with_port} to clipboard")
            ip_button.clicked.connect(lambda checked, addr=ip_with_port: self.copy_ip_to_clipboard(addr))
            layout.addWidget(ip_button)
            
            # Add separator if not the last item
            if i < len(network_ips) - 1:
                separator = QLabel("|")
                separator.setStyleSheet("color: #ccc; font-size: 10px; margin: 0px 2px;")
                layout.addWidget(separator)
        
        return container
    
    def copy_ip_to_clipboard(self, ip_address_with_port):
        """Copy IP address with port to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(ip_address_with_port)
        self.show_message(f"Copied {ip_address_with_port} to clipboard", 2000)
        logger.info(f"Copied IP address with port {ip_address_with_port} to clipboard")
        
    def create_status_bar(self):
        """Create and set up the status bar."""
        self.status_bar = QStatusBar()
        self.parent_window.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Progress indicator
        self.progress_label = QLabel("Idle")
        self.progress_label.setStyleSheet("color: #4A90E2; font-weight: bold; font-size: 11px;")
        self.status_bar.addPermanentWidget(self.progress_label)
        
        # Network IP addresses
        self.network_ips_widget = self.create_network_ips_widget()
        if self.network_ips_widget:
            self.status_bar.addPermanentWidget(self.network_ips_widget)
        
        
        
        # Web server status (if available)
        try:
            from interview_corvus.api.web_server import create_integrated_web_server
            self.web_server_status = QLabel("🌐 API: Off")
            self.web_server_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
            self.status_bar.addPermanentWidget(self.web_server_status)
        except ImportError:
            logger.debug("Web server not available, skipping status widget")

        # App title in the middle
        self.app_title_label = QLabel("🤖 AceBot")
        self.app_title_label.setStyleSheet("color: #4A90E2; font-weight: bold; font-size: 12px; padding: 0 16px;")
        self.status_bar.addPermanentWidget(self.app_title_label)
            
        return self.status_bar
        
    def show_message(self, message: str, timeout: int = 0):
        """Show a message in the status bar."""
        if self.status_bar:
            self.status_bar.showMessage(message, timeout)
            
    def set_progress_text(self, text: str):
        """Set the progress indicator text."""
        if self.progress_label:
            self.progress_label.setText(text)
            
    def update_web_server_status(self, is_running: bool, port: int = None):
        """Update the web server status display."""
        # Check if we need to refresh network IPs due to port change
        old_port = getattr(self.parent_window, 'web_server_port', None)
        needs_refresh = (port != old_port and port is not None)
        
        if self.web_server_status:
            if is_running:
                port_text = f":{port}" if port else ""
                self.web_server_status.setText(f"🌐 API: On")
                self.web_server_status.setStyleSheet("color: #51cf66; font-weight: bold; font-size: 12px;")
            else:
                self.web_server_status.setText("🌐 API: Off")
                self.web_server_status.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
        
        # Refresh network IPs if port changed and status bar is ready
        if needs_refresh and self.status_bar and hasattr(self.status_bar, 'parent') and self.status_bar.parent():
            self.refresh_network_ips()
    
    def refresh_network_ips(self):
        """Refresh the network IP addresses display."""
        if self.network_ips_widget and self.status_bar:
            # Remove old widget
            self.status_bar.removeWidget(self.network_ips_widget)
            self.network_ips_widget.deleteLater()
            self.network_ips_widget = None
            
        # Create new widget with updated IPs
        new_widget = self.create_network_ips_widget()
        if new_widget:
            self.network_ips_widget = new_widget
            # Insert after progress label - use index 1 (fixed position)
            self.status_bar.insertPermanentWidget(1, self.network_ips_widget)
