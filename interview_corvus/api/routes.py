"""
FastAPI route definitions for the AceBot web server.
Defines all HTTP endpoints and their handlers.
"""

import base64
from typing import List

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

from .models import (
    GenerateSolutionRequest, OptimizeSolutionRequest, SolutionResponse,
    OptimizationResponse, HealthResponse, ScreenshotListResponse
)
from .api_handler import WebServerAPI


def create_routes(app: FastAPI, api_instance: WebServerAPI) -> None:
    """Create and configure all routes for the FastAPI application."""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoints
    @app.get("/", response_class=HTMLResponse)
    async def root():
        return api_instance.get_main_ui()
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        return HealthResponse(
            status="healthy", 
            version="1.0.0",
            gui_connected=api_instance.gui_connected
        )
    
    # Screenshot endpoints
    @app.get("/screenshots", response_model=ScreenshotListResponse)
    async def get_screenshots():
        return api_instance.get_screenshots()
    
    @app.post("/screenshot/capture")
    async def trigger_screenshot():
        return api_instance.trigger_screenshot()
    
    @app.delete("/screenshots")
    async def clear_screenshots():
        return api_instance.clear_screenshots()
    
    # Solution generation endpoints
    @app.post("/solution", response_model=SolutionResponse)
    async def generate_solution(request: GenerateSolutionRequest):
        return api_instance.generate_solution_from_screenshots(request)
    
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
            
            return api_instance.generate_solution_from_screenshots(request)
            
        except Exception as e:
            return SolutionResponse(
                success=False,
                message=f"Failed to process uploaded files: {str(e)}"
            )
    
    # Code optimization endpoint
    @app.post("/optimize", response_model=OptimizationResponse)
    async def optimize_solution(request: OptimizeSolutionRequest):
        return api_instance.optimize_solution(request)
    
    # Management endpoints
    @app.delete("/history")
    async def reset_history():
        return api_instance.reset_chat_history()
    
    # Window control endpoints
    @app.post("/window/show")
    async def show_window():
        return api_instance.show_window()
    
    @app.post("/window/hide")
    async def hide_window():
        return api_instance.hide_window()
    
    @app.post("/window/toggle")
    async def toggle_window():
        return api_instance.toggle_window()
