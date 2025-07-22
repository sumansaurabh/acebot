"""
Web server thread and application setup for AceBot.
Handles FastAPI server creation and execution.
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import uvicorn
    from fastapi import FastAPI
    from PyQt6.QtCore import QThread
except ImportError as e:
    print(f"Missing required dependencies: {e}")
    print("Please install with: poetry install")
    sys.exit(1)

from .api_handler import WebServerAPI
from .routes import create_routes

if TYPE_CHECKING:
    pass


class WebServerThread(QThread):
    """Thread to run the FastAPI server."""
    
    def __init__(self, api_instance: WebServerAPI, host: str = "0.0.0.0", port: int = 8000):
        super().__init__()
        self.api_instance = api_instance
        self.host = host
        self.port = port
        self.app = self._create_app()
    
    def _create_app(self) -> FastAPI:
        """Create the FastAPI application."""
        app = FastAPI(
            title="🤖 AceBot Integrated API",
            description="AI-powered coding interview assistant API integrated with GUI",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Configure routes
        create_routes(app, self.api_instance)
        
        return app
    
    def run(self):
        """Run the FastAPI server."""
        try:
            print("=" * 60)
            print("🌐 AceBot Integrated Web Server")
            print("=" * 60)
            print(f"🚀 Server: http://{self.host}:{self.port}")
            print(f"📚 API Documentation: http://{self.host}:{self.port}/docs")
            print(f"📖 ReDoc Documentation: http://{self.host}:{self.port}/redoc")
            print(f"🔗 GUI Connected: {self.api_instance.gui_connected}")
            print("=" * 60)
            print("Available endpoints:")
            print("  GET  /health                 - Health check")
            print("  GET  /screenshots            - List screenshots")
            print("  POST /screenshot/capture     - Trigger screenshot")
            print("  POST /solution               - Generate solution")
            print("  POST /upload-solution        - Upload & solve")
            print("  POST /optimize               - Optimize code")
            print("  POST /window/show            - Show window")
            print("  POST /window/hide            - Hide window")
            print("  POST /window/toggle          - Toggle window")
            print("  DELETE /screenshots          - Clear screenshots")
            print("  DELETE /history              - Reset history")
            print("=" * 60)
            
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
