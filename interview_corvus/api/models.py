"""
Pydantic models for the Web API.
Request and response schemas for the AceBot web server.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


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


class LanguageResponse(BaseModel):
    """Response model for language settings."""
    success: bool
    message: str
    current_language: str
    available_languages: List[str]


class LanguageUpdateRequest(BaseModel):
    """Request model for updating language."""
    language: str = Field(..., description="Programming language to set as default")
