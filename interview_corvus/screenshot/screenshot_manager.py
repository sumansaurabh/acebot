from typing import Dict, List, Optional

from interview_corvus.screenshot.screen_capture_service import ScreenCaptureService


class ScreenshotManager:
    """
    Manager for capturing and storing screenshots.
    Maintains up to 2 screenshots at a time.
    """

    def __init__(self):
        """Initialize the screenshot manager."""
        self.capture_service = ScreenCaptureService()
        self.screenshots: List[Dict[str, any]] = []
        self.max_screenshots = 2

    def get_available_screens(self) -> List[Dict[str, any]]:
        """
        Get a list of all available screens.

        Returns:
            List of dictionaries with screen information
        """
        return self.capture_service.get_available_screens()

    def take_screenshot(self, screen_index: int = 0) -> Dict[str, any]:
        """
        Take a new screenshot of the specified screen.

        Args:
            screen_index: Index of the screen to capture (0 for primary by default)

        Returns:
            Dictionary with screenshot information
        """
        file_path, pixmap = self.capture_service.capture_specific_screen(screen_index)

        screenshot_info = {
            "file_path": file_path,
            "pixmap": pixmap,
            "width": pixmap.width(),
            "height": pixmap.height(),
            "type": "full_screen",
            "screen_index": screen_index,
        }

        self._add_screenshot(screenshot_info)
        return screenshot_info

    def take_active_window_screenshot(self) -> Dict[str, any]:
        """
        Take a new screenshot of the active window.

        Returns:
            Dictionary with screenshot information
        """
        file_path, pixmap = self.capture_service.capture_active_window()

        screenshot_info = {
            "file_path": file_path,
            "pixmap": pixmap,
            "width": pixmap.width(),
            "height": pixmap.height(),
            "type": "active_window",
        }

        self._add_screenshot(screenshot_info)
        return screenshot_info

    def _add_screenshot(self, screenshot_info: Dict[str, any]) -> None:
        """
        Add a screenshot to the managed list, removing oldest if necessary.

        Args:
            screenshot_info: Dictionary with screenshot information
        """
        # If we're at the limit, remove the oldest screenshot
        if len(self.screenshots) >= self.max_screenshots:
            oldest = self.screenshots.pop(0)
            # In a production app, you might want to delete the file here
            # import os
            # os.remove(oldest["file_path"])

        self.screenshots.append(screenshot_info)

    def get_screenshot(self, index: int = -1) -> Optional[Dict[str, any]]:
        """
        Get a screenshot by index.

        Args:
            index: Index of the screenshot (-1 for most recent)

        Returns:
            Dictionary with screenshot information or None if not found
        """
        if (
            not self.screenshots
            or index >= len(self.screenshots)
            or abs(index) > len(self.screenshots)
        ):
            return None

        return self.screenshots[index]

    def get_all_screenshots(self) -> List[Dict[str, any]]:
        """
        Get all current screenshots.

        Returns:
            List of dictionaries with screenshot information
        """
        return self.screenshots

    def clear_screenshots(self) -> None:
        """Clear all screenshots."""
        self.screenshots = []
