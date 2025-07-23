"""
AceBot Web API components.
"""

from .web_server import create_integrated_web_server
from .api_handler import WebServerAPI
from .server import WebServerThread
from .models import (
    GenerateSolutionRequest, OptimizeSolutionRequest, SolutionResponse,
    OptimizationResponse, HealthResponse, ScreenshotListResponse
)

__all__ = [
    'create_integrated_web_server',
    'WebServerAPI',
    'WebServerThread',
    'GenerateSolutionRequest',
    'OptimizeSolutionRequest', 
    'SolutionResponse',
    'OptimizationResponse',
    'HealthResponse',
    'ScreenshotListResponse'
]
