"""
Core API handler for the AceBot web server.
Contains the main API logic and service integration.
"""

import base64
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, pyqtSignal
from fastapi.responses import JSONResponse, HTMLResponse

from .models import (
    GenerateSolutionRequest, OptimizeSolutionRequest, SolutionResponse, 
    OptimizationResponse, ScreenshotListResponse, LanguageResponse, LanguageUpdateRequest
)
from .ui_template import get_main_ui_template

if TYPE_CHECKING:
    from interview_corvus.core.llm_service import LLMService
    from interview_corvus.screenshot.screenshot_manager import ScreenshotManager


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
    language_changed = pyqtSignal(str)  # new language
    
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
                if request.language != "mcq":
                    # Handle regular code solutions
                    solution_dict = {
                        "code": getattr(solution, 'code', ''),
                        "language": getattr(solution, 'language', request.language),
                        "explanation": getattr(solution, 'explanation', 'No explanation provided.'),
                        "time_complexity": getattr(solution, 'time_complexity', 'N/A'),
                        "space_complexity": getattr(solution, 'space_complexity', 'N/A'),
                        "edge_cases": getattr(solution, 'edge_cases', []) or [],
                        "alternative_approaches": getattr(solution, 'alternative_approaches', None)
                    }
                else:
                    # Handle MCQ solutions - transpose MCQ data into explanation format
                    result = getattr(solution, 'solution', 'No question provided.')
                    
                    solution_dict = {
                        "code": "",  # Put the full MCQ in the code field
                        "language": "mcq",
                        "explanation": result,  # Also put it in explanation for consistency
                        "time_complexity": "N/A",
                        "space_complexity": "N/A",
                        "edge_cases": [],
                        "alternative_approaches": None
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
            
            # Store the solution for persistence
            self.llm_service._last_solution = solution_dict
            
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
            
            # Store the optimization for persistence
            self.llm_service._last_optimization = optimization_dict
            
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
            # Clear stored solutions
            self.llm_service._last_solution = None
            self.llm_service._last_optimization = None
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
    
    def get_current_solutions(self) -> JSONResponse:
        """Get the current session solutions if available."""
        try:
            if not self.gui_connected:
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "brute_solution": None,
                        "optimized_solution": None,
                        "message": "No GUI connected - no solutions available"
                    }
                )
            
            # Get current session data from the content display component
            # Note: This is a simplified implementation - in a real scenario,
            # you might want to store solutions in a more persistent way
            current_session = getattr(self.llm_service, '_last_solution', None)
            optimized_session = getattr(self.llm_service, '_last_optimization', None)
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "brute_solution": current_session,
                    "optimized_solution": optimized_session,
                    "message": "Current solutions retrieved"
                }
            )
            
        except Exception as e:
            print(f"❌ Web API: Failed to get current solutions: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Failed to get current solutions: {str(e)}"
                }
            )
    
    def get_language(self) -> LanguageResponse:
        """Get current language settings."""
        try:
            from interview_corvus.config import settings
            
            return LanguageResponse(
                success=True,
                message="Language settings retrieved successfully",
                current_language=settings.default_language,
                available_languages=settings.available_languages
            )
            
        except Exception as e:
            return LanguageResponse(
                success=False,
                message=f"Failed to get language settings: {str(e)}",
                current_language="python",
                available_languages=["python"]
            )
    
    def set_language(self, request: LanguageUpdateRequest) -> JSONResponse:
        """Set the current programming language."""
        try:
            from interview_corvus.config import settings
            
            # Validate language is in available languages
            if request.language not in settings.available_languages:
                return JSONResponse(
                    content={
                        "success": False, 
                        "message": f"Invalid language '{request.language}'. Available languages: {settings.available_languages}"
                    },
                    status_code=400
                )
            
            # Update language in settings
            settings.default_language = request.language
            settings.save_user_settings()
            
            # Emit signal to update GUI if connected
            if self.gui_connected:
                self.language_changed.emit(request.language)
            
            return JSONResponse(
                content={
                    "success": True, 
                    "message": f"Language set to {request.language}",
                    "current_language": request.language
                }
            )
            
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": f"Failed to set language: {str(e)}"},
                status_code=500
            )
    
    def get_main_ui(self) -> HTMLResponse:
        """Get the main UI HTML page."""
        return HTMLResponse(content=get_main_ui_template())
