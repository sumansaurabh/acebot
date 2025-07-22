#!/usr/bin/env python3
"""
Integrated Web Server for Interview Corvus
Runs alongside the GUI application and shares the same services.
"""

import base64
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    from PyQt6.QtCore import QObject, pyqtSignal, QThread
except ImportError as e:
    print(f"Missing required dependencies: {e}")
    print("Please install with: poetry install")
    sys.exit(1)

# Import from the main application
from interview_corvus.config import settings
from interview_corvus.core.models import CodeSolution, CodeOptimization

if TYPE_CHECKING:
    from interview_corvus.core.llm_service import LLMService
    from interview_corvus.screenshot.screenshot_manager import ScreenshotManager


class GenerateSolutionRequest(BaseModel):
    """Request model for generating solutions."""
    language: str = Field(default="Python", description="Programming language for the solution")
    screenshot_data: Optional[List[str]] = Field(default=None, description="Base64 encoded screenshot images")


class OptimizeSolutionRequest(BaseModel):
    """Request model for optimizing solutions."""
    code: str = Field(..., description="Code to optimize")
    language: str = Field(default="Python", description="Programming language of the code")


class SolutionResponse(BaseModel):
    """Response model for solution generation."""
    success: bool
    message: str
    solution: Optional[Dict[str, Any]] = None


class OptimizationResponse(BaseModel):
    """Response model for solution optimization."""
    success: bool
    message: str
    optimization: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    gui_connected: bool


class ScreenshotListResponse(BaseModel):
    """Response model for screenshot list."""
    success: bool
    message: str
    screenshots: List[Dict[str, Any]]


class WebServerAPI(QObject):
    """Web API that integrates with the GUI application."""
    
    # Signals for communication with GUI
    solution_requested = pyqtSignal(object, str)  # screenshot_paths, language
    optimization_requested = pyqtSignal(str, str)  # code, language
    screenshot_capture_requested = pyqtSignal()
    
    def __init__(self, llm_service: 'LLMService' = None, screenshot_manager: 'ScreenshotManager' = None):
        """Initialize the web API with shared services."""
        super().__init__()
        self.llm_service = llm_service
        self.screenshot_manager = screenshot_manager
        self.gui_connected = llm_service is not None and screenshot_manager is not None
        
        print(f"🌐 Web API initialized (GUI connected: {self.gui_connected})")
    
    def set_services(self, llm_service: 'LLMService', screenshot_manager: 'ScreenshotManager'):
        """Set the shared services from the GUI application."""
        self.llm_service = llm_service
        self.screenshot_manager = screenshot_manager
        self.gui_connected = True
        print("🔗 GUI services connected to Web API")
    
    def generate_solution_from_screenshots(self, request: GenerateSolutionRequest) -> SolutionResponse:
        """Generate solution from available screenshots."""
        try:
            if not self.gui_connected:
                return SolutionResponse(
                    success=False,
                    message="GUI services not connected. Please start the GUI application first."
                )
            
            # Get screenshot paths from stored screenshots or uploaded data
            screenshot_paths = []
            
            if request.screenshot_data:
                # Process uploaded base64 screenshot data
                temp_dir = Path(tempfile.gettempdir()) / "interview_corvus_web_uploads"
                temp_dir.mkdir(exist_ok=True)
                
                for i, base64_data in enumerate(request.screenshot_data):
                    try:
                        # Remove data URL prefix if present
                        if "," in base64_data:
                            base64_data = base64_data.split(",", 1)[1]
                        
                        # Decode base64 image
                        image_data = base64.b64decode(base64_data)
                        
                        # Save to temporary file
                        temp_path = temp_dir / f"web_upload_{i}.png"
                        with open(temp_path, 'wb') as f:
                            f.write(image_data)
                        
                        screenshot_paths.append(str(temp_path))
                    except Exception as e:
                        return SolutionResponse(
                            success=False,
                            message=f"Failed to process screenshot {i}: {str(e)}"
                        )
            else:
                # Use stored screenshots from GUI
                all_screenshots = self.screenshot_manager.get_all_screenshots()
                if not all_screenshots:
                    return SolutionResponse(
                        success=False,
                        message="No screenshots available. Upload screenshot data or take screenshots in the GUI."
                    )
                screenshot_paths = [s["file_path"] for s in all_screenshots]
            
            if not screenshot_paths:
                return SolutionResponse(
                    success=False,
                    message="No screenshots provided or available."
                )
            
            print(f"🔍 Web API: Processing {len(screenshot_paths)} screenshots for solution generation")
            
            # Generate solution using shared LLM service
            solution = self.llm_service.get_solution_from_screenshots(
                screenshot_paths, request.language
            )
            
            # Clean up temporary files if any
            if request.screenshot_data:
                for path in screenshot_paths:
                    try:
                        os.unlink(path)
                    except:
                        pass
            
            # Convert to dictionary for JSON response
            solution_dict = {
                "code": solution.code,
                "language": solution.language,
                "explanation": solution.explanation,
                "time_complexity": solution.time_complexity,
                "space_complexity": solution.space_complexity,
                "edge_cases": solution.edge_cases if solution.edge_cases else [],
                "alternative_approaches": solution.alternative_approaches
            }
            
            print("✅ Web API: Solution generated successfully")
            
            return SolutionResponse(
                success=True,
                message="Solution generated successfully",
                solution=solution_dict
            )
            
        except Exception as e:
            print(f"❌ Web API: Failed to generate solution: {str(e)}")
            return SolutionResponse(
                success=False,
                message=f"Failed to generate solution: {str(e)}"
            )
    
    def optimize_solution(self, request: OptimizeSolutionRequest) -> OptimizationResponse:
        """Optimize the provided code."""
        try:
            if not self.gui_connected:
                return OptimizationResponse(
                    success=False,
                    message="GUI services not connected. Please start the GUI application first."
                )
            
            print(f"🔧 Web API: Optimizing {request.language} code")
            
            optimization = self.llm_service.get_code_optimization(
                request.code, request.language
            )
            
            # Convert to dictionary for JSON response
            optimization_dict = {
                "original_code": optimization.original_code,
                "optimized_code": optimization.optimized_code,
                "language": optimization.language,
                "improvements": optimization.improvements,
                "original_time_complexity": optimization.original_time_complexity,
                "optimized_time_complexity": optimization.optimized_time_complexity,
                "original_space_complexity": optimization.original_space_complexity,
                "optimized_space_complexity": optimization.optimized_space_complexity,
                "explanation": optimization.explanation
            }
            
            print("✅ Web API: Code optimized successfully")
            
            return OptimizationResponse(
                success=True,
                message="Code optimized successfully",
                optimization=optimization_dict
            )
            
        except Exception as e:
            print(f"❌ Web API: Failed to optimize code: {str(e)}")
            return OptimizationResponse(
                success=False,
                message=f"Failed to optimize code: {str(e)}"
            )
    
    def get_screenshots(self) -> ScreenshotListResponse:
        """Get list of available screenshots."""
        try:
            if not self.gui_connected:
                return ScreenshotListResponse(
                    success=False,
                    message="GUI services not connected.",
                    screenshots=[]
                )
            
            screenshots = self.screenshot_manager.get_all_screenshots()
            
            # Convert screenshots to API format (without pixmap data)
            screenshot_list = []
            for i, screenshot in enumerate(screenshots):
                screenshot_info = {
                    "index": i,
                    "file_path": screenshot["file_path"],
                    "width": screenshot.get("width", 0),
                    "height": screenshot.get("height", 0),
                    "type": screenshot.get("type", "unknown")
                }
                screenshot_list.append(screenshot_info)
            
            return ScreenshotListResponse(
                success=True,
                message=f"Found {len(screenshots)} screenshots",
                screenshots=screenshot_list
            )
            
        except Exception as e:
            return ScreenshotListResponse(
                success=False,
                message=f"Failed to get screenshots: {str(e)}",
                screenshots=[]
            )
    
    def trigger_screenshot(self) -> JSONResponse:
        """Trigger a screenshot capture in the GUI."""
        try:
            if not self.gui_connected:
                return JSONResponse(
                    content={"success": False, "message": "GUI services not connected."},
                    status_code=503
                )
            
            # Get current screenshot count before triggering
            current_count = len(self.screenshot_manager.get_all_screenshots())
            
            # Emit signal to trigger screenshot in GUI
            self.screenshot_capture_requested.emit()
            
            return JSONResponse(
                content={
                    "success": True, 
                    "message": "Screenshot capture triggered in GUI",
                    "current_screenshot_count": current_count,
                    "note": "Check /screenshots endpoint to see new screenshots"
                }
            )
            
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": f"Failed to trigger screenshot: {str(e)}"},
                status_code=500
            )
    
    def clear_screenshots(self) -> JSONResponse:
        """Clear all stored screenshots."""
        try:
            if not self.gui_connected:
                return JSONResponse(
                    content={"success": False, "message": "GUI services not connected."},
                    status_code=503
                )
            
            self.screenshot_manager.clear_screenshots()
            return JSONResponse(
                content={"success": True, "message": "All screenshots cleared"}
            )
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": f"Failed to clear screenshots: {str(e)}"},
                status_code=500
            )
    
    def reset_chat_history(self) -> JSONResponse:
        """Reset the LLM chat history."""
        try:
            if not self.gui_connected:
                return JSONResponse(
                    content={"success": False, "message": "GUI services not connected."},
                    status_code=503
                )
            
            self.llm_service.reset_chat_history()
            return JSONResponse(
                content={"success": True, "message": "Chat history reset successfully"}
            )
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": f"Failed to reset chat history: {str(e)}"},
                status_code=500
            )


class WebServerThread(QThread):
    """Thread to run the FastAPI server."""
    
    def __init__(self, api_instance: WebServerAPI, host: str = "127.0.0.1", port: int = 8000):
        super().__init__()
        self.api_instance = api_instance
        self.host = host
        self.port = port
        self.app = self._create_app()
    
    def _create_app(self) -> FastAPI:
        """Create the FastAPI application."""
        app = FastAPI(
            title="Interview Corvus Integrated API",
            description="AI-powered coding interview assistant API integrated with GUI",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Health check endpoints
        @app.get("/", response_model=HealthResponse)
        async def root():
            return HealthResponse(
                status="healthy", 
                version="1.0.0",
                gui_connected=self.api_instance.gui_connected
            )
        
        @app.get("/health", response_model=HealthResponse)
        async def health_check():
            return HealthResponse(
                status="healthy", 
                version="1.0.0",
                gui_connected=self.api_instance.gui_connected
            )
        
        # Screenshot endpoints
        @app.get("/screenshots", response_model=ScreenshotListResponse)
        async def get_screenshots():
            return self.api_instance.get_screenshots()
        
        @app.post("/screenshot/capture")
        async def trigger_screenshot():
            return self.api_instance.trigger_screenshot()
        
        @app.delete("/screenshots")
        async def clear_screenshots():
            return self.api_instance.clear_screenshots()
        
        # Solution generation endpoints
        @app.post("/solution", response_model=SolutionResponse)
        async def generate_solution(request: GenerateSolutionRequest):
            return self.api_instance.generate_solution_from_screenshots(request)
        
        @app.post("/upload-solution", response_model=SolutionResponse)
        async def upload_and_solve(
            files: List[UploadFile] = File(...),
            language: str = Form(default="Python")
        ):
            try:
                screenshot_data = []
                
                for file in files:
                    # Validate file type
                    if not file.content_type.startswith('image/'):
                        return SolutionResponse(
                            success=False,
                            message=f"File {file.filename} is not a valid image"
                        )
                    
                    # Read and encode file to base64
                    contents = await file.read()
                    encoded = base64.b64encode(contents).decode()
                    screenshot_data.append(encoded)
                
                request = GenerateSolutionRequest(
                    language=language,
                    screenshot_data=screenshot_data
                )
                
                return self.api_instance.generate_solution_from_screenshots(request)
                
            except Exception as e:
                return SolutionResponse(
                    success=False,
                    message=f"Failed to process uploaded files: {str(e)}"
                )
        
        # Code optimization endpoint
        @app.post("/optimize", response_model=OptimizationResponse)
        async def optimize_solution(request: OptimizeSolutionRequest):
            return self.api_instance.optimize_solution(request)
        
        # Management endpoints
        @app.delete("/history")
        async def reset_history():
            return self.api_instance.reset_chat_history()
        
        return app
    
    def run(self):
        """Run the FastAPI server."""
        try:
            print("=" * 60)
            print("🌐 Interview Corvus Integrated Web Server")
            print("=" * 60)
            print(f"🚀 Server: http://{self.host}:{self.port}")
            print(f"📚 API Documentation: http://{self.host}:{self.port}/docs")
            print(f"📖 ReDoc Documentation: http://{self.host}:{self.port}/redoc")
            print(f"🔗 GUI Connected: {self.api_instance.gui_connected}")
            print("=" * 60)
            
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")


def create_integrated_web_server(
    llm_service: 'LLMService' = None, 
    screenshot_manager: 'ScreenshotManager' = None,
    host: str = "127.0.0.1",
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
