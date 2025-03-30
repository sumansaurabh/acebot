from datetime import datetime
from typing import Dict, List, Tuple

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication

from interview_corvus.config import settings


class ScreenCaptureService:
    """Service for capturing screenshots of the screen."""

    def __init__(self):
        """Initialize the screen capture service."""
        self.app = QApplication.instance()
        self.screenshots_dir = settings.app_data_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)

    def get_available_screens(self) -> List[Dict[str, any]]:
        """
        Get a list of all available screens.

        Returns:
            List of dictionaries with screen information
        """
        screens = []
        for i, screen in enumerate(QApplication.screens()):
            geometry = screen.geometry()
            screens.append(
                {
                    "index": i,
                    "name": screen.name(),
                    "width": geometry.width(),
                    "height": geometry.height(),
                    "x": geometry.x(),
                    "y": geometry.y(),
                    "primary": (screen == QApplication.primaryScreen()),
                }
            )
        return screens

    def capture_full_screen(self) -> Tuple[str, QPixmap]:
        """
        Capture a screenshot of the primary screen.

        Returns:
            Tuple of (file_path, pixmap)
        """
        return self.capture_specific_screen(0)

    def capture_specific_screen(self, screen_index: int = 0) -> Tuple[str, QPixmap]:
        """
        Capture a screenshot of a specific screen.

        Args:
            screen_index: Index of the screen to capture

        Returns:
            Tuple of (file_path, pixmap)
        """
        screens = QApplication.screens()
        if screen_index < 0 or screen_index >= len(screens):
            # Fallback to primary screen if invalid index
            screen = QApplication.primaryScreen()
        else:
            screen = screens[screen_index]

        # Capture the specified screen
        pixmap = screen.grabWindow(0)  # В реальном приложении: pixmap = screen.grab()
        return self._save_screenshot(pixmap)

    def capture_active_window(self) -> Tuple[str, QPixmap]:
        """
        Capture a screenshot of the active window.

        Returns:
            Tuple of (file_path, pixmap)
        """
        # This is a simplified implementation
        # In a real app, you would need platform-specific code to get the active window

        # For demonstration, we'll just capture the full screen
        # In a real implementation, you would:
        # 1. Get the active window handle
        # 2. Get the window rect
        # 3. Capture that specific area

        return self.capture_full_screen()

    def capture_area(self, rect: QRect) -> Tuple[str, QPixmap]:
        """
        Capture a screenshot of a specific area.

        Args:
            rect: The rectangle area to capture

        Returns:
            Tuple of (file_path, pixmap)
        """
        screen = QApplication.primaryScreen()
        # В PyQt6 grabWindow с параметрами x, y, width, height заменен на grab() с QRect
        pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
        # В реальном приложении: pixmap = screen.grab(rect)
        return self._save_screenshot(pixmap)

    def _save_screenshot(self, pixmap: QPixmap) -> Tuple[str, QPixmap]:
        """
        Save a screenshot to a file.

        Args:
            pixmap: The screenshot pixmap

        Returns:
            Tuple of (file_path, pixmap)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = str(self.screenshots_dir / f"screenshot_{timestamp}.png")

        pixmap.save(file_path, "PNG")
        return file_path, pixmap
