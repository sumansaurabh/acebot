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
        """Serve the main web UI."""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview Corvus - AI Coding Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .main-content {
            padding: 40px;
        }
        
        .action-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .action-btn {
            padding: 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }
        
        .action-btn:before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .action-btn:hover:before {
            left: 100%;
        }
        
        .capture-btn {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
        }
        
        .solve-btn {
            background: linear-gradient(135deg, #2196F3, #1976D2);
            color: white;
        }
        
        .optimize-btn {
            background: linear-gradient(135deg, #FF9800, #F57C00);
            color: white;
        }
        
        .action-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .action-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .status-bar {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 4px solid #4CAF50;
        }
        
        .status-bar.error {
            border-left-color: #f44336;
            background: #ffebee;
        }
        
        .status-bar.loading {
            border-left-color: #2196F3;
            background: #e3f2fd;
        }
        
        .results-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 30px;
        }
        
        .result-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            border: 1px solid #e0e0e0;
        }
        
        .result-section h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .code-block {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            line-height: 1.5;
            overflow-x: auto;
            margin: 15px 0;
            white-space: pre-wrap;
        }
        
        .explanation {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            line-height: 1.6;
            margin: 15px 0;
        }
        
        .complexity-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }
        
        .complexity-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            text-align: center;
        }
        
        .complexity-item strong {
            color: #667eea;
            font-size: 1.1em;
        }
        
        .screenshots-info {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .loading-spinner {
            display: none;
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .hidden {
            display: none;
        }
        
        @media (max-width: 768px) {
            .results-container {
                grid-template-columns: 1fr;
            }
            
            .action-buttons {
                grid-template-columns: 1fr;
            }
            
            .main-content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        
        <div class="main-content">
            <div class="screenshots-info" id="screenshotInfo">
                📸 Screenshots: <span id="screenshotCount">0</span> captured
            </div>
            
            <div class="action-buttons">
                <button class="action-btn capture-btn" onclick="captureScreen()">
                    📸 Capture
                    <div style="font-size: 12px; margin-top: 5px;">Take Screenshot</div>
                </button>
                
                <button class="action-btn solve-btn" onclick="solveBrute()" id="solveBtn">
                    🧠 Solve [Brute]
                    <div style="font-size: 12px; margin-top: 5px;">Generate Solution</div>
                </button>
                
                <button class="action-btn optimize-btn" onclick="optimizeBest()" id="optimizeBtn">
                    ⚡ Optimize [Best]
                    <div style="font-size: 12px; margin-top: 5px;">Optimize Solution</div>
                </button>
            </div>
            
            <div class="status-bar" id="statusBar">
                Ready to assist with your coding interview
            </div>
            
            <div class="loading-spinner" id="loadingSpinner"></div>
            
            <div class="results-container" id="resultsContainer" style="display: none;">
                <div class="result-section" id="bruteSection" style="display: none;">
                    <h3>🧠 Brute Force Solution</h3>
                    <div class="explanation" id="bruteExplanation"></div>
                    <div class="code-block" id="bruteCode"></div>
                    <div class="complexity-info">
                        <div class="complexity-item">
                            <strong>Time:</strong><br>
                            <span id="bruteTimeComplexity">-</span>
                        </div>
                        <div class="complexity-item">
                            <strong>Space:</strong><br>
                            <span id="bruteSpaceComplexity">-</span>
                        </div>
                    </div>
                </div>
                
                <div class="result-section" id="optimizedSection" style="display: none;">
                    <h3>⚡ Optimized Solution</h3>
                    <div class="explanation" id="optimizedExplanation"></div>
                    <div class="code-block" id="optimizedCode"></div>
                    <div class="complexity-info">
                        <div class="complexity-item">
                            <strong>Time:</strong><br>
                            <span id="optimizedTimeComplexity">-</span>
                        </div>
                        <div class="complexity-item">
                            <strong>Space:</strong><br>
                            <span id="optimizedSpaceComplexity">-</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = '';
        let bruteSolution = null;
        
        function updateStatus(message, type = 'info') {
            const statusBar = document.getElementById('statusBar');
            statusBar.textContent = message;
            statusBar.className = `status-bar ${type}`;
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
                    const solveBtn = document.getElementById('solveBtn');
                    solveBtn.disabled = count === 0;
                })
                .catch(error => console.error('Error updating screenshot count:', error));
        }
        
        async function captureScreen() {
            updateStatus('Taking screenshot...', 'loading');
            showLoading(true);
            
            try {
                const response = await fetch(`${API_BASE}/screenshot/capture`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    updateStatus('✅ Screenshot captured successfully');
                    updateScreenshotCount();
                } else {
                    updateStatus(`❌ Failed to capture screenshot: ${result.message}`, 'error');
                }
            } catch (error) {
                updateStatus('❌ Connection failed - Make sure Interview Corvus is running!', 'error');
            } finally {
                showLoading(false);
            }
        }
        
        async function solveBrute() {
            updateStatus('Generating brute force solution...', 'loading');
            showLoading(true);
            
            try {
                const response = await fetch(`${API_BASE}/solution`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        language: 'Python'
                    })
                });
                
                const result = await response.json();
                
                if (response.ok && result.solution) {
                    bruteSolution = result.solution;
                    displayBruteSolution(result.solution);
                    updateStatus('✅ Brute force solution generated successfully');
                    
                    // Enable optimize button
                    document.getElementById('optimizeBtn').disabled = false;
                } else {
                    updateStatus(`❌ Failed to generate solution: ${result.message}`, 'error');
                }
            } catch (error) {
                updateStatus('❌ Connection failed - Make sure Interview Corvus is running!', 'error');
            } finally {
                showLoading(false);
            }
        }
        
        async function optimizeBest() {
            if (!bruteSolution) {
                updateStatus('❌ Please generate a brute force solution first', 'error');
                return;
            }
            
            updateStatus('Optimizing solution...', 'loading');
            showLoading(true);
            
            try {
                const response = await fetch(`${API_BASE}/optimize`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        code: bruteSolution.code,
                        language: bruteSolution.language
                    })
                });
                
                const result = await response.json();
                
                if (response.ok && result.optimization) {
                    displayOptimizedSolution(result.optimization);
                    updateStatus('✅ Solution optimized successfully');
                } else {
                    updateStatus(`❌ Failed to optimize solution: ${result.message}`, 'error');
                }
            } catch (error) {
                updateStatus('❌ Connection failed - Make sure Interview Corvus is running!', 'error');
            } finally {
                showLoading(false);
            }
        }
        
        function displayBruteSolution(solution) {
            document.getElementById('resultsContainer').style.display = 'grid';
            document.getElementById('bruteSection').style.display = 'block';
            
            document.getElementById('bruteExplanation').textContent = solution.explanation || 'No explanation provided';
            document.getElementById('bruteCode').textContent = solution.code || 'No code provided';
            document.getElementById('bruteTimeComplexity').textContent = solution.time_complexity || 'Not specified';
            document.getElementById('bruteSpaceComplexity').textContent = solution.space_complexity || 'Not specified';
        }
        
        function displayOptimizedSolution(optimization) {
            document.getElementById('optimizedSection').style.display = 'block';
            
            document.getElementById('optimizedExplanation').textContent = optimization.explanation || 'No explanation provided';
            document.getElementById('optimizedCode').textContent = optimization.optimized_code || 'No optimized code provided';
            document.getElementById('optimizedTimeComplexity').textContent = optimization.optimized_time_complexity || 'Not specified';
            document.getElementById('optimizedSpaceComplexity').textContent = optimization.optimized_space_complexity || 'Not specified';
        }
        
        // Initialize
        window.addEventListener('load', () => {
            updateScreenshotCount();
            updateStatus('Ready to assist with your coding interview');
            
            // Initially disable solve and optimize buttons
            document.getElementById('solveBtn').disabled = true;
            document.getElementById('optimizeBtn').disabled = true;
        });
        
        // Auto-refresh screenshot count every 5 seconds
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
            print("🌐 Interview Corvus Integrated Web Server")
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
