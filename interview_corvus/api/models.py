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


class StateResponse(BaseModel):
    """Response model for current application state."""
    success: bool
    message: str
    current_solution: Optional[Dict[str, Any]] = None
    current_optimization: Optional[Dict[str, Any]] = None
    current_language: str
    has_screenshots: bool
    selected_files: List[str] = Field(default_factory=list, description="List of selected file keys")


class FileSelectionRequest(BaseModel):
    """Request model for managing file selection."""
    file_key: str = Field(..., description="Key of the file to add/remove from selection")
    action: str = Field(..., description="Action to perform: add, remove, or clear")


class FileSelectionResponse(BaseModel):
    """Response model for file selection operations."""
    success: bool
    message: str
    available_files: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Available files with selection status")


class RecordingStartRequest(BaseModel):
    """Request model for starting recording."""
    audio_data: Optional[str] = Field(default=None, description="Base64 encoded audio data (for mobile)")
    recording_type: str = Field(default="audio", description="Type of recording: audio, screen, or mobile")
    selected_file_keys: List[str] = Field(default_factory=list, description="List of selected file keys to analyze")


class RecordingResponse(BaseModel):
    """Response model for recording operations."""
    success: bool
    message: str
    recording_id: Optional[str] = None


class RecordingAnalysisRequest(BaseModel):
    """Request model for recording analysis."""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    recording_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Recording metadata")
    custom_prompt: Optional[str] = Field(default=None, description="Custom analysis prompt")
