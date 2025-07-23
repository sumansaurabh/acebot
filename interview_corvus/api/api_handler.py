"""
Core API handler for the AceBot web server.
Contains the main API logic and service integration.
"""

import base64
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger
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

# Import Deepgram service
from interview_corvus.core.deepgram_service import DeepgramService


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
    
    # Recording signals
    recording_start_requested = pyqtSignal()
    recording_stop_requested = pyqtSignal()
    mobile_recording_received = pyqtSignal(object)  # recording data
    
    # New signals for solution synchronization
    solution_generated_from_web = pyqtSignal(object)  # solution object
    optimization_generated_from_web = pyqtSignal(object)  # optimization object
    
    def __init__(self, llm_service: 'LLMService' = None, screenshot_manager: 'ScreenshotManager' = None):
        """Initialize the web API with shared services."""
        super().__init__()
        self.llm_service = llm_service
        self.screenshot_manager = screenshot_manager
        self.deepgram_service = DeepgramService()
        self.gui_connected = llm_service is not None and screenshot_manager is not None
        
        print(f"🌐 Web API initialized (GUI connected: {self.gui_connected})")
        print(f"🎤 Deepgram service available: {self.deepgram_service.is_available()}")
    
    def set_services(self, llm_service: 'LLMService', screenshot_manager: 'ScreenshotManager'):
        """Set the shared services from the GUI application."""
        self.llm_service = llm_service
        self.screenshot_manager = screenshot_manager
        self.gui_connected = True
        print("🔗 GUI services connected to Web API")
    
    # State synchronization methods
    def update_solution_from_gui(self, solution):
        """Update the current solution from GUI - stored in LLM service."""
        # Convert solution object to dictionary for JSON serialization
        try:
            if hasattr(solution, 'model_dump'):
                solution_dict = solution.model_dump()
            elif hasattr(solution, '__dict__'):
                solution_dict = solution.__dict__
            else:
                solution_dict = {"raw": str(solution)}
            self.llm_service._last_solution = solution_dict
        except Exception as e:
            print(f"❌ Web API: Failed to serialize solution from GUI: {e}")
            self.llm_service._last_solution = {"raw": str(solution)}
        print("🔄 Web API: Solution updated from GUI")
    
    def update_optimization_from_gui(self, optimization):
        """Update the current optimization from GUI - stored in LLM service."""
        # Convert optimization object to dictionary for JSON serialization
        try:
            if hasattr(optimization, 'model_dump'):
                optimization_dict = optimization.model_dump()
            elif hasattr(optimization, '__dict__'):
                optimization_dict = optimization.__dict__
            else:
                optimization_dict = {"raw": str(optimization)}
            self.llm_service._last_optimization = optimization_dict
        except Exception as e:
            print(f"❌ Web API: Failed to serialize optimization from GUI: {e}")
            self.llm_service._last_optimization = {"raw": str(optimization)}
        print("🔄 Web API: Optimization updated from GUI")
    
    def update_language_from_gui(self, language: str):
        """Update the current language from GUI."""
        from interview_corvus.config import settings
        settings.default_language = language
        print(f"🔄 Web API: Language updated from GUI to {language}")
    
    def get_current_solution(self):
        """Get the current solution for web interface."""
        return getattr(self.llm_service, '_last_solution', None)
    
    def get_current_optimization(self):
        """Get the current optimization for web interface."""
        return getattr(self.llm_service, '_last_optimization', None)
    
    def get_current_language(self):
        """Get the current language for web interface."""
        from interview_corvus.config import settings
        return settings.default_language
    
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
            
            # Store the solution in LLM service as dictionary and emit signal for GUI sync
            self.llm_service._last_solution = solution_dict
            self.solution_generated_from_web.emit(solution)
            
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
            
            # Store the optimization in LLM service as dictionary and emit signal for GUI sync
            self.llm_service._last_optimization = optimization_dict
            self.optimization_generated_from_web.emit(optimization)
            
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
            
            # Get current session data from LLM service (should be dictionaries)
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
    
    def get_current_state(self):
        """Get the current application state for synchronization."""
        from .models import StateResponse
        
        try:
            # Get current solution and optimization from LLM service (already dictionaries)
            current_solution = getattr(self.llm_service, '_last_solution', None)
            current_optimization = getattr(self.llm_service, '_last_optimization', None)
            
            # Convert solution to dict if it exists and isn't already a dict
            solution_dict = None
            if current_solution:
                if isinstance(current_solution, dict):
                    solution_dict = current_solution
                elif hasattr(current_solution, 'model_dump'):
                    solution_dict = current_solution.model_dump()
                elif hasattr(current_solution, '__dict__'):
                    solution_dict = current_solution.__dict__
                else:
                    solution_dict = {"raw": str(current_solution)}
            
            # Convert optimization to dict if it exists and isn't already a dict
            optimization_dict = None
            if current_optimization:
                if isinstance(current_optimization, dict):
                    optimization_dict = current_optimization
                elif hasattr(current_optimization, 'model_dump'):
                    optimization_dict = current_optimization.model_dump()
                elif hasattr(current_optimization, '__dict__'):
                    optimization_dict = current_optimization.__dict__
                else:
                    optimization_dict = {"raw": str(current_optimization)}
            
            # Check if there are screenshots available
            has_screenshots = False
            if self.gui_connected and self.screenshot_manager:
                screenshots = self.screenshot_manager.get_all_screenshots()
                has_screenshots = len(screenshots) > 0
            
            # Get current language
            from interview_corvus.config import settings
            current_language = settings.default_language
            
            return StateResponse(
                success=True,
                message="Current state retrieved successfully",
                current_solution=solution_dict,
                current_optimization=optimization_dict,
                current_language=current_language,
                has_screenshots=has_screenshots,
                selected_files=settings.get_selected_file_keys()
            )
        except Exception as e:
            return StateResponse(
                success=False,
                message=f"Failed to get current state: {str(e)}",
                current_solution=None,
                current_optimization=None,
                current_language="python",
                has_screenshots=False,
                selected_files=[]
            )

    # Recording methods
    def start_mobile_recording(self, request) -> JSONResponse:
        """Start mobile recording analysis."""
        try:
            if not self.gui_connected or not self.llm_service:
                return JSONResponse(
                    status_code=503,
                    content={"success": False, "message": "GUI services not connected"}
                )

            # For mobile recording, we process the audio data immediately
            if request.audio_data:
                # Decode base64 audio data
                try:
                    audio_bytes = base64.b64decode(request.audio_data)
                    
                    # Create temporary file
                    temp_dir = Path(tempfile.gettempdir()) / "interview_corvus_recordings"
                    temp_dir.mkdir(exist_ok=True)
                    
                    temp_file = temp_dir / f"mobile_recording_{os.getpid()}.wav"
                    with open(temp_file, "wb") as f:
                        f.write(audio_bytes)
                    
                    # Transcribe audio using Deepgram
                    transcript_content = ""
                    transcript_confidence = 0.0
                    transcription_metadata = {}
                    transcription_success = False
                    
                    if self.deepgram_service.is_available():
                        logger.info(f"Transcribing mobile recording: {temp_file.name}")
                        transcription_result = self.deepgram_service.transcribe_audio(str(temp_file))
                        
                        if transcription_result['success']:
                            transcript_content = transcription_result['transcript']
                            transcript_confidence = transcription_result['confidence']
                            transcription_metadata = transcription_result.get('metadata', {})
                            transcription_success = True
                            logger.info(f"✅ Mobile transcription successful: {len(transcript_content)} characters")
                        else:
                            transcript_content = f"[Mobile transcription failed: {transcription_result.get('error', 'Unknown error')}]"
                            logger.error(f"Mobile transcription failed: {transcription_result.get('error')}")
                    else:
                        transcript_content = f"[Mobile Recording: {temp_file.name}, Size: {len(audio_bytes)} bytes - Deepgram service unavailable]"
                        logger.warning("Deepgram service not available for mobile recording")
                    
                    # Only proceed if transcription was successful or if we have selected files
                    if not transcription_success and not request.selected_file_keys:
                        return JSONResponse(
                            status_code=400,
                            content={
                                "success": False, 
                                "message": "Transcription failed and no files selected for analysis",
                                "error": transcript_content
                            }
                        )
                    
                    # Process the recording with selected files
                    recording_data = {
                        'content': transcript_content,
                        'metadata': {
                            'filename': temp_file.name,
                            'size': len(audio_bytes),
                            'type': 'mobile_audio',
                            'format': 'wav',
                            'transcription': {
                                'confidence': transcript_confidence,
                                'service': 'deepgram' if self.deepgram_service.is_available() else 'none',
                                **transcription_metadata
                            }
                        },
                        'selected_file_keys': request.selected_file_keys or []
                    }
                    
                    # Store for streaming
                    self._current_recording_data = recording_data
                    
                    # Clean up temp file
                    try:
                        temp_file.unlink()
                    except:
                        pass
                    
                    return JSONResponse(content={
                        "success": True,
                        "message": "Mobile recording received and ready for analysis",
                        "recording_id": f"mobile_{os.getpid()}"
                    })
                    
                except Exception as e:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "message": f"Failed to process audio data: {str(e)}"}
                    )
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": "No audio data provided"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": f"Failed to start mobile recording: {str(e)}"}
            )

    def get_recording_analysis_stream(self):
        """Get streaming analysis for the current recording."""
        try:
            if not hasattr(self, '_current_recording_data') or not self._current_recording_data:
                yield f"data: {{'error': 'No recording data available'}}\n\n"
                return

            if not self.gui_connected or not self.llm_service:
                yield f"data: {{'error': 'GUI services not connected'}}\n\n"
                return

            # Start streaming analysis
            yield f"data: {{'status': 'starting_analysis'}}\n\n"
            
            accumulated_text = ""
            chunk_count = 0
            
            try:
                # Get streaming response from LLM service
                for chunk in self.llm_service.get_recording_analysis_stream(self._current_recording_data):
                    if chunk:
                        accumulated_text += chunk
                        chunk_count += 1
                        
                        # Send chunk as SSE event
                        import json
                        chunk_data = {
                            'chunk': chunk,
                            'chunk_count': chunk_count,
                            'total_length': len(accumulated_text)
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Send completion event
                completion_data = {
                    'status': 'completed',
                    'complete_text': accumulated_text,
                    'total_chunks': chunk_count,
                    'final_length': len(accumulated_text)
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
            except Exception as e:
                error_data = {
                    'status': 'error',
                    'error': str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"
            
            # Clean up
            self._current_recording_data = None
            
        except Exception as e:
            yield f"data: {{'error': 'Streaming failed: {str(e)}'}}\n\n"

    # File selection methods
    def get_selected_files(self):
        """Get the list of currently selected files."""
        from .models import FileSelectionResponse
        from interview_corvus.config import settings
        
        try:
            return FileSelectionResponse(
                success=True,
                message="Available files retrieved successfully",
                available_files=settings.get_available_files()
            )
        except Exception as e:
            return FileSelectionResponse(
                success=False,
                message=f"Failed to get available files: {str(e)}",
                available_files={}
            )

    def manage_file_selection(self, request):
        """Add, remove, or clear selected files."""
        from .models import FileSelectionResponse
        from interview_corvus.config import settings
        
        try:
            if request.action == "add":
                # Validate file key exists
                available_files = settings.get_available_files()
                if request.file_key not in available_files:
                    return FileSelectionResponse(
                        success=False,
                        message="File key does not exist",
                        available_files=settings.get_available_files()
                    )
                settings.add_selected_file(request.file_key)
                message = f"File selected: {available_files[request.file_key]['filename']}"
                
            elif request.action == "remove":
                settings.remove_selected_file(request.file_key)
                message = f"File unselected"
                
            elif request.action == "clear":
                settings.clear_selected_files()
                message = "All files unselected"
                
            else:
                return FileSelectionResponse(
                    success=False,
                    message="Invalid action. Use 'add', 'remove', or 'clear'",
                    available_files=settings.get_available_files()
                )
            
            return FileSelectionResponse(
                success=True,
                message=message,
                available_files=settings.get_available_files()
            )
            
        except Exception as e:
            return FileSelectionResponse(
                success=False,
                message=f"Failed to manage file selection: {str(e)}",
                available_files=settings.get_available_files()
            )
