#!/usr/bin/env python3
"""
Integrated Web Server for AceBot
Main entry point that creates and configures the web server components.
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .api_handler import WebServerAPI
from .server import WebServerThread

if TYPE_CHECKING:
    from interview_corvus.core.llm_service import LLMService
    from interview_corvus.screenshot.screenshot_manager import ScreenshotManager


def create_integrated_web_server(
    llm_service: 'LLMService' = None, 
    screenshot_manager: 'ScreenshotManager' = None,
    host: str = "0.0.0.0",
    port: int = 8000
) -> tuple[WebServerAPI, WebServerThread]:
    """
    Create an integrated web server that works with the GUI application.
    
    Args:
        llm_service: The LLM service from the GUI
        screenshot_manager: The screenshot manager from the GUI
        host: Host to bind to
        port: Port to bind to
    
    Returns:
        Tuple of (API instance, Server thread)
    """
    api_instance = WebServerAPI(llm_service, screenshot_manager)
    server_thread = WebServerThread(api_instance, host, port)
    
    return api_instance, server_thread
