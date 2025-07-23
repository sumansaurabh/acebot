#!/usr/bin/env python3
"""
Integrated Web Server for AceBot
Main entry point that creates and configures the web server components.
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple
from loguru import logger

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .api_handler import WebServerAPI
from .server import WebServerThread
from .network_utils import find_available_port, get_local_ip_addresses, print_server_info

if TYPE_CHECKING:
    from interview_corvus.core.llm_service import LLMService
    from interview_corvus.screenshot.screenshot_manager import ScreenshotManager


def create_integrated_web_server(
    llm_service: 'LLMService' = None, 
    screenshot_manager: 'ScreenshotManager' = None,
    host: str = "0.0.0.0",
    port: int = 26262,
    auto_find_port: bool = True,
    use_ssl: bool = False
) -> Tuple[WebServerAPI, WebServerThread, int]:
    """
    Create an integrated web server that works with the GUI application.
    Automatically finds available port and discovers local network addresses.
    
    Args:
        llm_service: The LLM service from the GUI
        screenshot_manager: The screenshot manager from the GUI
        host: Host to bind to (default: "0.0.0.0" for all interfaces)
        port: Preferred port to bind to (default: 26262, or 8443 for SSL)
        auto_find_port: Whether to automatically find an available port if preferred is taken
        use_ssl: Whether to enable HTTPS with SSL certificates
    
    Returns:
        Tuple of (API instance, Server thread, actual port used)
    
    Raises:
        RuntimeError: If no available port could be found
    """
    # Use different default port for HTTPS
    if use_ssl and port == 26262:
        port = 8443  # Common alternative HTTPS port
    
    actual_port = port
    
    if auto_find_port:
        # Try to find an available port starting from the preferred port
        found_port = find_available_port(host, port)
        if found_port is None:
            raise RuntimeError(f"Could not find available port starting from {port}")
        actual_port = found_port
        
        if actual_port != port:
            logger.info(f"Port {port} was not available, using port {actual_port} instead")
    
    # Get and log local IP addresses for user reference
    local_ips = get_local_ip_addresses()
    logger.info(f"Local IP addresses discovered: {local_ips}")
    
    # Create API and server instances
    api_instance = WebServerAPI(llm_service, screenshot_manager)
    server_thread = WebServerThread(api_instance, host, actual_port, use_ssl=use_ssl)
    
    # Log server setup information
    protocol = "https" if use_ssl else "http"
    logger.info(f"Web server configured on {protocol}://{host}:{actual_port}")
    if use_ssl:
        logger.info("🔒 SSL/HTTPS enabled with certificates from certs/ directory")
    
    return api_instance, server_thread, actual_port
