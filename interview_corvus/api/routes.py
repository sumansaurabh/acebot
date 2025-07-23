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
    OptimizationResponse, HealthResponse, ScreenshotListResponse,
    LanguageResponse, LanguageUpdateRequest, StateResponse
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
    
    @app.get("/solution/current")
    async def get_current_solutions():
        return api_instance.get_current_solutions()
    
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
    
    # Language endpoints
    @app.get("/language", response_model=LanguageResponse)
    async def get_language():
        return api_instance.get_language()
    
    @app.put("/language")
    async def set_language(request: LanguageUpdateRequest):
        return api_instance.set_language(request)
    
    # State synchronization endpoint
    @app.get("/state", response_model=StateResponse)
    async def get_current_state():
        """Get current application state for synchronization."""
        return api_instance.get_current_state()
