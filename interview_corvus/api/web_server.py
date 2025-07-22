#!/usr/bin/env python3
"""
Integrated Web Server for AceBot
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
    from fastapi.responses import JSONResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles
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
    screenshots_cleared = pyqtSignal()
    chat_history_reset = pyqtSignal()
    window_show_requested = pyqtSignal()
    window_hide_requested = pyqtSignal()
    window_toggle_requested = pyqtSignal()
    
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
            
            # Debug: Check the type of solution object
            print(f"🔍 Web API: Solution object type: {type(solution)}")
            
            # Safely convert to dictionary for JSON response
            try:
                solution_dict = {
                    "code": getattr(solution, 'code', ''),
                    "language": getattr(solution, 'language', request.language),
                    "explanation": getattr(solution, 'explanation', 'No explanation provided.'),
                    "time_complexity": getattr(solution, 'time_complexity', 'N/A'),
                    "space_complexity": getattr(solution, 'space_complexity', 'N/A'),
                    "edge_cases": getattr(solution, 'edge_cases', []) or [],
                    "alternative_approaches": getattr(solution, 'alternative_approaches', None)
                }
            except Exception as attr_error:
                print(f"❌ Web API: Error accessing solution attributes: {attr_error}")
                # Fallback: try to convert directly if it's already a dict
                if isinstance(solution, dict):
                    solution_dict = solution
                else:
                    # If it's a Pydantic model, use model_dump
                    if hasattr(solution, 'model_dump'):
                        solution_dict = solution.model_dump()
                    else:
                        raise ValueError(f"Unexpected solution object type: {type(solution)}")
            
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
            
            # Debug: Check the type of optimization object
            print(f"🔍 Web API: Optimization object type: {type(optimization)}")
            print(f"🔍 Web API: Optimization object: {optimization}")
            
            # Handle different types of optimization responses
            optimization_dict = {}
            
            # If it's already a Pydantic model with attributes
            if hasattr(optimization, 'model_dump'):
                optimization_dict = optimization.model_dump()
            # If it's a dictionary
            elif isinstance(optimization, dict):
                optimization_dict = optimization
            # If it's a string (fallback case)
            elif isinstance(optimization, str):
                try:
                    import json
                    optimization_dict = json.loads(optimization)
                except (json.JSONDecodeError, TypeError, ValueError):
                    # If we can't parse the string, create a basic response
                    optimization_dict = {
                        "original_code": request.code,
                        "optimized_code": optimization,  # Use the string as optimized code
                        "language": request.language,
                        "improvements": ["LLM provided optimized version"],
                        "original_time_complexity": "N/A",
                        "optimized_time_complexity": "N/A", 
                        "original_space_complexity": "N/A",
                        "optimized_space_complexity": "N/A",
                        "explanation": "Optimization generated by LLM"
                    }
            # Fallback: try to extract attributes manually
            else:
                optimization_dict = {
                    "original_code": getattr(optimization, 'original_code', request.code),
                    "optimized_code": getattr(optimization, 'optimized_code', ''),
                    "language": getattr(optimization, 'language', request.language),
                    "improvements": getattr(optimization, 'improvements', []),
                    "original_time_complexity": getattr(optimization, 'original_time_complexity', 'N/A'),
                    "optimized_time_complexity": getattr(optimization, 'optimized_time_complexity', 'N/A'),
                    "original_space_complexity": getattr(optimization, 'original_space_complexity', 'N/A'),
                    "optimized_space_complexity": getattr(optimization, 'optimized_space_complexity', 'N/A'),
                    "explanation": getattr(optimization, 'explanation', 'No explanation provided.')
                }
            
            print("✅ Web API: Code optimized successfully")
            
            return OptimizationResponse(
                success=True,
                message="Code optimized successfully",
                optimization=optimization_dict
            )
            
        except Exception as e:
            print(f"❌ Web API: Failed to optimize code: {str(e)}")
            print(f"❌ Web API: Error type: {type(e)}")
            import traceback
            print(f"❌ Web API: Traceback: {traceback.format_exc()}")
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
            # Emit signal to update GUI
            self.screenshots_cleared.emit()
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
            # Emit signal to update GUI
            self.chat_history_reset.emit()
            return JSONResponse(
                content={"success": True, "message": "Chat history reset successfully"}
            )
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": f"Failed to reset chat history: {str(e)}"},
                status_code=500
            )
    
    def show_window(self) -> JSONResponse:
        """Show the main application window."""
        try:
            if not self.gui_connected:
                return JSONResponse(
                    content={"success": False, "message": "GUI services not connected."},
                    status_code=503
                )
            
            # Emit signal to show window in GUI
            self.window_show_requested.emit()
            
            return JSONResponse(
                content={"success": True, "message": "Window show requested"}
            )
            
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": f"Failed to show window: {str(e)}"},
                status_code=500
            )
    
    def hide_window(self) -> JSONResponse:
        """Hide the main application window."""
        try:
            if not self.gui_connected:
                return JSONResponse(
                    content={"success": False, "message": "GUI services not connected."},
                    status_code=503
                )
            
            # Emit signal to hide window in GUI
            self.window_hide_requested.emit()
            
            return JSONResponse(
                content={"success": True, "message": "Window hide requested"}
            )
            
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": f"Failed to hide window: {str(e)}"},
                status_code=500
            )
    
    def toggle_window(self) -> JSONResponse:
        """Toggle the visibility of the main application window."""
        try:
            if not self.gui_connected:
                return JSONResponse(
                    content={"success": False, "message": "GUI services not connected."},
                    status_code=503
                )
            
            # Emit signal to toggle window visibility in GUI
            self.window_toggle_requested.emit()
            
            return JSONResponse(
                content={"success": True, "message": "Window visibility toggle requested"}
            )
            
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": f"Failed to toggle window: {str(e)}"},
                status_code=500
            )
    
    def get_main_ui(self) -> HTMLResponse:
        """Serve a compact web UI with larger, colored buttons, a Toggle button, and screenshot count."""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes, minimum-scale=1.0, maximum-scale=5.0">
    <title>🤖 AceBot</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/4.3.0/marked.min.js"></script>
    <style>
        html, body { background: #fff; margin: 0; padding: 0; }
        body { font-family: system-ui, sans-serif; font-size: 15px; color: #222; }
        .main-content { max-width: 800px; margin: 0 auto; padding: 12px 0 0 0; }
        .action-buttons {
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
            gap: 4px;
            margin-bottom: 14px;
            justify-content: flex-start;
        }
        .action-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            min-width: 70px;
            min-height: 32px;
            transition: background 0.15s, box-shadow 0.15s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .capture-btn { background: #4caf50; color: #fff; }
        .capture-btn:hover { background: #388e3c; }
        .solve-btn { background: #2196f3; color: #fff; }
        .solve-btn:hover { background: #1565c0; }
        .optimize-btn { background: #ff9800; color: #fff; }
        .optimize-btn:hover { background: #ef6c00; }
        .toggle-btn { background: #9c27b0; color: #fff; }
        .toggle-btn:hover { background: #6d1b7b; }
        .clear-btn { background: #e53935; color: #fff; }
        .clear-btn:hover { background: #b71c1c; }
        .reset-btn { background: #607d8b; color: #fff; }
        .reset-btn:hover { background: #37474f; }
        .action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .status-bar {
            font-size: 13px;
            margin-bottom: 10px;
            color: #666;
            min-height: 18px;
        }
        .screenshot-count {
            font-size: 14px;
            font-weight: 600;
            color: #2196f3;
            margin-bottom: 10px;
        }
        .loading-spinner {
            display: none;
            width: 22px;
            height: 22px;
            border: 3px solid #eee;
            border-top: 3px solid #888;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results-container { margin-top: 12px; }
        .result-section { 
            background: #fafbfc; 
            border-radius: 8px; 
            padding: 16px; 
            border: 1px solid #e1e4e8; 
            margin-bottom: 16px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .section-header {
            font-size: 16px;
            font-weight: 600;
            color: #24292e;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e1e4e8;
        }
        .brute-header { border-bottom-color: #2196f3; }
        .optimized-header { border-bottom-color: #ff9800; }
        
        .explanation { 
            font-size: 14px; 
            line-height: 1.6;
            margin: 12px 0; 
            color: #24292e;
        }
        .explanation h1, .explanation h2, .explanation h3 {
            color: #24292e;
            margin-top: 16px;
            margin-bottom: 8px;
        }
        .explanation h1 { font-size: 18px; }
        .explanation h2 { font-size: 16px; }
        .explanation h3 { font-size: 14px; }
        .explanation p { margin: 8px 0; }
        .explanation ul, .explanation ol { margin: 8px 0 8px 20px; }
        .explanation li { margin: 4px 0; }
        .explanation code {
            background: #f6f8fa;
            border: 1px solid #e1e4e8;
            border-radius: 3px;
            padding: 2px 4px;
            font-size: 13px;
            font-family: Monaco, "Cascadia Code", "Fira Code", monospace;
        }
        .explanation blockquote {
            border-left: 4px solid #dfe2e5;
            padding-left: 16px;
            margin-left: 0;
            color: #6a737d;
        }
        
        .code-block { 
            background: #1e1e1e !important; 
            color: #d4d4d4 !important; 
            border-radius: 8px !important; 
            font-size: 13px; 
            padding: 16px !important; 
            overflow-x: auto; 
            margin: 12px 0 !important;
            border: 1px solid #3c3c3c !important;
            font-family: Monaco, "Cascadia Code", "Fira Code", "JetBrains Mono", Consolas, monospace !important;
        }
        .code-block code {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            color: inherit !important;
        }
        
        /* Prism.js syntax highlighting colors for dark background */
        .code-block .token.comment,
        .code-block .token.prolog,
        .code-block .token.doctype,
        .code-block .token.cdata {
            color: #6A9955;
            font-style: italic;
        }
        .code-block .token.namespace {
            opacity: 0.7;
        }
        .code-block .token.string,
        .code-block .token.attr-value {
            color: #CE9178;
        }
        .code-block .token.punctuation,
        .code-block .token.operator {
            color: #D4D4D4;
        }
        .code-block .token.entity,
        .code-block .token.url,
        .code-block .token.symbol,
        .code-block .token.number,
        .code-block .token.boolean,
        .code-block .token.variable,
        .code-block .token.constant,
        .code-block .token.property,
        .code-block .token.regex,
        .code-block .token.inserted {
            color: #B5CEA8;
        }
        .code-block .token.atrule,
        .code-block .token.keyword,
        .code-block .token.attr-name {
            color: #569CD6;
        }
        .code-block .token.function {
            color: #DCDCAA;
        }
        .code-block .token.deleted {
            color: #F44747;
        }
        .code-block .token.tag,
        .code-block .token.selector {
            color: #F44747;
        }
        .code-block .token.class-name {
            color: #4EC9B0;
        }
        .code-block .token.important,
        .code-block .token.bold {
            font-weight: bold;
        }
        .code-block .token.italic {
            font-style: italic;
        }
        
        .complexity-info { display: flex; gap: 10px; font-size: 12px; margin: 5px 0; }
        .complexity-item { background: #fff; border: 1px solid #eee; border-radius: 4px; padding: 3px 8px; }
        @media (max-width: 600px) {
            .main-content { padding: 6px 0 0 0; }
            .action-btn { font-size: 14px; min-width: 70px; min-height: 32px; padding: 7px 10px; }
            .explanation { font-size: 11px; }
            .explanation h1 { font-size: 14px; }
            .explanation h2 { font-size: 13px; }
            .explanation h3 { font-size: 12px; }
            .explanation code { font-size: 10px; }
            .code-block { font-size: 10px; padding: 12px !important; }
        }
    </style>
</head>
<body>
    <div class="main-content">
        <div class="screenshot-count">Screenshots: <span id="screenshotCount">0</span></div>
        <div class="action-buttons">
            <button class="action-btn capture-btn" onclick="captureScreen()" id="captureBtn">Capture</button>
            <button class="action-btn solve-btn" onclick="solveBrute()" id="solveBtn">Solve</button>
            <button class="action-btn optimize-btn" onclick="optimizeBest()" id="optimizeBtn">Optimize</button>
            <button class="action-btn toggle-btn" onclick="toggleWindow()" id="toggleBtn">Toggle</button>
            <button class="action-btn clear-btn" onclick="clearScreenshots()" id="clearBtn">Clear</button>
            <button class="action-btn reset-btn" onclick="resetAll()" id="resetBtn">Reset</button>
        </div>
        <div class="status-bar" id="statusBar">Ready</div>
        <div class="loading-spinner" id="loadingSpinner"></div>
        <div class="results-container" id="resultsContainer" style="display: none;">
            <div class="result-section" id="bruteSection" style="display: none;">
                <div class="section-header brute-header">💡 Initial Solution</div>
                <div class="explanation" id="bruteExplanation"></div>
                <pre class="code-block language-python"><code id="bruteCode"></code></pre>
                <div class="complexity-info">
                    <div class="complexity-item">⏱️ Time: <span id="bruteTimeComplexity">-</span></div>
                    <div class="complexity-item">💾 Space: <span id="bruteSpaceComplexity">-</span></div>
                </div>
            </div>
            <div class="result-section" id="optimizedSection" style="display: none;">
                <div class="section-header optimized-header">🚀 Optimized Solution</div>
                <div class="explanation" id="optimizedExplanation"></div>
                <pre class="code-block language-python"><code id="optimizedCode"></code></pre>
                <div class="complexity-info">
                    <div class="complexity-item">⏱️ Time: <span id="optimizedTimeComplexity">-</span></div>
                    <div class="complexity-item">💾 Space: <span id="optimizedSpaceComplexity">-</span></div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
    <script>
        const API_BASE = '';
        let bruteSolution = null;
        function updateStatus(message, type = 'info') {
            const statusBar = document.getElementById('statusBar');
            statusBar.textContent = message;
        }
        function showLoading(show = true) {
            const spinner = document.getElementById('loadingSpinner');
            spinner.style.display = show ? 'block' : 'none';
        }
        function updateScreenshotCount() {
            fetch(`${API_BASE}/screenshots`)
                .then(response => response.json())
                .then(data => {
                    const count = data.screenshots ? data.screenshots.length : 0;
                    document.getElementById('screenshotCount').textContent = count;
                    // Enable/disable solve button based on screenshot availability
                    document.getElementById('solveBtn').disabled = count === 0;
                })
                .catch(() => { document.getElementById('screenshotCount').textContent = '0'; });
        }
        async function captureScreen() {
            updateStatus('Capturing...'); showLoading(true);
            try {
                // Get current count before capture
                const currentCount = parseInt(document.getElementById('screenshotCount').textContent);
                
                const response = await fetch(`${API_BASE}/screenshot/capture`, { method: 'POST' });
                const result = await response.json();
                if (response.ok) {
                    updateStatus('Captured');
                    // Immediately update count without waiting for API call
                    const newCount = Math.min(currentCount + 1, 10); // Max 10 screenshots
                    document.getElementById('screenshotCount').textContent = newCount;
                    // Enable solve button if we have screenshots
                    document.getElementById('solveBtn').disabled = newCount === 0;
                } else updateStatus('Error: ' + result.message);
            } catch (error) { updateStatus('Connection error'); }
            finally { showLoading(false); }
        }
        async function solveBrute() {
            updateStatus('Solving...'); showLoading(true);
            try {
                const response = await fetch(`${API_BASE}/solution`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ language: 'Python' })
                });
                const result = await response.json();
                if (response.ok && result.solution) {
                    bruteSolution = result.solution;
                    displayBruteSolution(result.solution);
                    updateStatus('Solved');
                    document.getElementById('optimizeBtn').disabled = false;
                } else updateStatus('Error: ' + result.message);
            } catch (error) { updateStatus('Connection error'); }
            finally { showLoading(false); }
        }
        async function optimizeBest() {
            if (!bruteSolution) { updateStatus('Solve first'); return; }
            updateStatus('Optimizing...'); showLoading(true);
            try {
                const response = await fetch(`${API_BASE}/optimize`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: bruteSolution.code, language: bruteSolution.language })
                });
                const result = await response.json();
                if (response.ok && result.optimization) {
                    displayOptimizedSolution(result.optimization);
                    updateStatus('Optimized');
                } else updateStatus('Error: ' + result.message);
            } catch (error) { updateStatus('Connection error'); }
            finally { showLoading(false); }
        }
        async function clearScreenshots() {
            updateStatus('Clearing...'); showLoading(true);
            try {
                const response = await fetch(`${API_BASE}/screenshots`, { method: 'DELETE' });
                const result = await response.json();
                if (response.ok && result.success) {
                    updateStatus('Cleared');
                    // Immediately update count
                    document.getElementById('screenshotCount').textContent = '0';
                    document.getElementById('solveBtn').disabled = true;
                    document.getElementById('resultsContainer').style.display = 'none';
                    document.getElementById('bruteSection').style.display = 'none';
                    document.getElementById('optimizedSection').style.display = 'none';
                    bruteSolution = null;
                    document.getElementById('optimizeBtn').disabled = true;
                } else updateStatus('Error: ' + result.message);
            } catch (error) { updateStatus('Connection error'); }
            finally { showLoading(false); }
        }
        async function resetAll() {
            updateStatus('Resetting...'); showLoading(true);
            try {
                const response1 = await fetch(`${API_BASE}/screenshots`, { method: 'DELETE' });
                const response2 = await fetch(`${API_BASE}/history`, { method: 'DELETE' });
                const result1 = await response1.json();
                const result2 = await response2.json();
                if ((response1.ok && result1.success) && (response2.ok && result2.success)) {
                    updateStatus('Reset');
                    // Immediately update count
                    document.getElementById('screenshotCount').textContent = '0';
                    document.getElementById('solveBtn').disabled = true;
                    document.getElementById('resultsContainer').style.display = 'none';
                    document.getElementById('bruteSection').style.display = 'none';
                    document.getElementById('optimizedSection').style.display = 'none';
                    bruteSolution = null;
                    document.getElementById('optimizeBtn').disabled = true;
                } else updateStatus('Error: ' + (result1.message || result2.message));
            } catch (error) { updateStatus('Connection error'); }
            finally { showLoading(false); }
        }
        function displayBruteSolution(solution) {
            document.getElementById('resultsContainer').style.display = 'block';
            document.getElementById('bruteSection').style.display = 'block';
            
            // Render markdown explanation
            const explanationHtml = marked.parse(solution.explanation || 'No explanation provided.');
            document.getElementById('bruteExplanation').innerHTML = explanationHtml;
            
            // Render syntax-highlighted code
            document.getElementById('bruteCode').textContent = solution.code || '';
            Prism.highlightElement(document.getElementById('bruteCode'));
            
            document.getElementById('bruteTimeComplexity').textContent = solution.time_complexity || '-';
            document.getElementById('bruteSpaceComplexity').textContent = solution.space_complexity || '-';
        }
        function displayOptimizedSolution(optimization) {
            document.getElementById('optimizedSection').style.display = 'block';
            
            // Render markdown explanation
            const explanationHtml = marked.parse(optimization.explanation || 'No optimization explanation provided.');
            document.getElementById('optimizedExplanation').innerHTML = explanationHtml;
            
            // Render syntax-highlighted optimized code
            document.getElementById('optimizedCode').textContent = optimization.optimized_code || '';
            Prism.highlightElement(document.getElementById('optimizedCode'));
            
            document.getElementById('optimizedTimeComplexity').textContent = optimization.optimized_time_complexity || '-';
            document.getElementById('optimizedSpaceComplexity').textContent = optimization.optimized_space_complexity || '-';
        }
        function toggleWindow() {
            fetch(`${API_BASE}/window/toggle`, { method: 'POST' })
                .then(() => updateStatus('Toggled'))
                .catch(() => updateStatus('Toggle failed'));
        }
        window.addEventListener('load', () => {
            document.getElementById('solveBtn').disabled = true;
            document.getElementById('optimizeBtn').disabled = true;
            updateScreenshotCount();
            updateStatus('Ready');
        });
        setInterval(updateScreenshotCount, 5000);
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html_content)


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
            return self.api_instance.get_main_ui()
        
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
        
        # Window control endpoints
        @app.post("/window/show")
        async def show_window():
            return self.api_instance.show_window()
        
        @app.post("/window/hide")
        async def hide_window():
            return self.api_instance.hide_window()
        
        @app.post("/window/toggle")
        async def toggle_window():
            return self.api_instance.toggle_window()
        
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
