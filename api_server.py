#!/usr/bin/env python3
"""
FastAPI Web Server for Interview Corvus
Provides HTTP API endpoints for screenshot analysis, solution generation, and optimization.
"""

import base64
import io
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    from PIL import Image
except ImportError as e:
    print(f"Missing required dependencies: {e}")
    print("Please install with: poetry install")
    sys.exit(1)

# Import from the main application - only core components
try:
    from interview_corvus.config import settings
    from interview_corvus.core.llm_service import LLMService
    from interview_corvus.core.models import CodeSolution, CodeOptimization
    # Skip GUI-dependent screenshot manager for now, create our own minimal version
except ImportError as e:
    print(f"Could not import application modules: {e}")
    print("Make sure you're running from the project root and dependencies are installed")
    sys.exit(1)


class SimpleScreenshotManager:
    """Simplified screenshot manager for API use without GUI dependencies."""
    
    def __init__(self):
        self.screenshots: List[Dict[str, Any]] = []
        self.max_screenshots = 10
        self.screenshots_dir = Path(tempfile.gettempdir()) / "interview_corvus_api_screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def save_uploaded_image(self, image_data: bytes, filename: str = None) -> str:
        """Save uploaded image data to a temporary file."""
        if filename is None:
            import time
            filename = f"screenshot_{int(time.time())}.png"
        
        file_path = self.screenshots_dir / filename
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # Store screenshot info
        screenshot_info = {
            "file_path": str(file_path),
            "filename": filename,
        }
        
        if len(self.screenshots) >= self.max_screenshots:
            # Remove oldest screenshot
            old_screenshot = self.screenshots.pop(0)
            try:
                os.unlink(old_screenshot["file_path"])
            except:
                pass
        
        self.screenshots.append(screenshot_info)
        return str(file_path)
    
    def get_all_screenshots(self) -> List[Dict[str, Any]]:
        """Get all stored screenshots."""
        return self.screenshots
    
    def clear_screenshots(self):
        """Clear all screenshots."""
        for screenshot in self.screenshots:
            try:
                os.unlink(screenshot["file_path"])
            except:
                pass
        self.screenshots.clear()


class TakeScreenshotRequest(BaseModel):
    """Request model for taking screenshots."""
    screen_index: int = Field(default=0, description="Index of the screen to capture")


class GenerateSolutionRequest(BaseModel):
    """Request model for generating solutions."""
    language: str = Field(default="Python", description="Programming language for the solution")
    screenshot_data: Optional[List[str]] = Field(default=None, description="Base64 encoded screenshot images")


class OptimizeSolutionRequest(BaseModel):
    """Request model for optimizing solutions."""
    code: str = Field(..., description="Code to optimize")
    language: str = Field(default="Python", description="Programming language of the code")


class ScreenshotResponse(BaseModel):
    """Response model for screenshot operations."""
    success: bool
    message: str
    screenshot_id: Optional[str] = None
    screenshot_data: Optional[str] = None  # Base64 encoded image


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


class InterviewCorvusAPI:
    """Main API class containing all the endpoints logic."""
    
    def __init__(self):
        """Initialize the API with required services."""
        try:
            self.llm_service = LLMService()
            self.screenshot_manager = SimpleScreenshotManager()
            print("✅ LLM Service and Screenshot Manager initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize services: {e}")
            raise
    
    def generate_solution_from_screenshots(self, request: GenerateSolutionRequest) -> SolutionResponse:
        """Generate solution from available screenshots."""
        try:
            # Get screenshot paths from stored screenshots or uploaded data
            screenshot_paths = []
            
            if request.screenshot_data:
                # Process uploaded base64 screenshot data
                for i, base64_data in enumerate(request.screenshot_data):
                    try:
                        # Remove data URL prefix if present
                        if "," in base64_data:
                            base64_data = base64_data.split(",", 1)[1]
                        
                        # Decode base64 image
                        image_data = base64.b64decode(base64_data)
                        
                        # Save to file
                        temp_path = self.screenshot_manager.save_uploaded_image(
                            image_data, f"uploaded_{i}.png"
                        )
                        screenshot_paths.append(temp_path)
                    except Exception as e:
                        return SolutionResponse(
                            success=False,
                            message=f"Failed to process screenshot {i}: {str(e)}"
                        )
            else:
                # Use stored screenshots
                all_screenshots = self.screenshot_manager.get_all_screenshots()
                if not all_screenshots:
                    return SolutionResponse(
                        success=False,
                        message="No screenshots available. Upload screenshot data or use the upload endpoint."
                    )
                screenshot_paths = [s["file_path"] for s in all_screenshots]
            
            if not screenshot_paths:
                return SolutionResponse(
                    success=False,
                    message="No screenshots provided or available."
                )
            
            print(f"🔍 Processing {len(screenshot_paths)} screenshots for solution generation")
            
            # Generate solution using LLM service
            solution = self.llm_service.get_solution_from_screenshots(
                screenshot_paths, request.language
            )
            
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
            
            print("✅ Solution generated successfully")
            
            return SolutionResponse(
                success=True,
                message="Solution generated successfully",
                solution=solution_dict
            )
            
        except Exception as e:
            print(f"❌ Failed to generate solution: {str(e)}")
            return SolutionResponse(
                success=False,
                message=f"Failed to generate solution: {str(e)}"
            )
    
    def optimize_solution(self, request: OptimizeSolutionRequest) -> OptimizationResponse:
        """Optimize the provided code."""
        try:
            print(f"🔧 Optimizing {request.language} code")
            
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
            
            print("✅ Code optimized successfully")
            
            return OptimizationResponse(
                success=True,
                message="Code optimized successfully",
                optimization=optimization_dict
            )
            
        except Exception as e:
            print(f"❌ Failed to optimize code: {str(e)}")
            return OptimizationResponse(
                success=False,
                message=f"Failed to optimize code: {str(e)}"
            )
    
    def clear_screenshots(self) -> JSONResponse:
        """Clear all stored screenshots."""
        try:
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
            self.llm_service.reset_chat_history()
            return JSONResponse(
                content={"success": True, "message": "Chat history reset successfully"}
            )
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": f"Failed to reset chat history: {str(e)}"},
                status_code=500
            )


# Initialize FastAPI app
app = FastAPI(
    title="Interview Corvus API",
    description="AI-powered coding interview assistant API",
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

# Initialize API instance
try:
    api = InterviewCorvusAPI()
    print("🚀 Interview Corvus API initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize API: {e}")
    sys.exit(1)


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/solution", response_model=SolutionResponse)
async def generate_solution(request: GenerateSolutionRequest):
    """Generate a solution from screenshots."""
    return api.generate_solution_from_screenshots(request)


@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_solution(request: OptimizeSolutionRequest):
    """Optimize the provided code."""
    return api.optimize_solution(request)


@app.post("/upload-solution", response_model=SolutionResponse)
async def upload_and_solve(
    files: List[UploadFile] = File(...),
    language: str = Form(default="Python")
):
    """Upload images and generate solution."""
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
        
        return api.generate_solution_from_screenshots(request)
        
    except Exception as e:
        return SolutionResponse(
            success=False,
            message=f"Failed to process uploaded files: {str(e)}"
        )


@app.delete("/screenshots")
async def clear_screenshots():
    """Clear all stored screenshots."""
    return api.clear_screenshots()


@app.delete("/history") 
async def reset_history():
    """Reset chat history and clear screenshots."""
    try:
        api.clear_screenshots()
        api.reset_chat_history()
        return JSONResponse(
            content={"success": True, "message": "History and screenshots cleared"}
        )
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"Failed to reset: {str(e)}"},
            status_code=500
        )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Interview Corvus API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎯 Interview Corvus API Server")
    print("=" * 60)
    print(f"🌐 Server: http://{args.host}:{args.port}")
    print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"📖 ReDoc Documentation: http://{args.host}:{args.port}/redoc")
    print("=" * 60)
    print("Available endpoints:")
    print("  GET  /               - Health check")
    print("  GET  /health         - Health check") 
    print("  POST /solution       - Generate solution from base64 screenshots")
    print("  POST /optimize       - Optimize code")
    print("  POST /upload-solution - Upload images and generate solution")
    print("  DELETE /screenshots  - Clear all screenshots")
    print("  DELETE /history      - Reset chat history and screenshots")
    print("=" * 60)
    print("Usage examples:")
    print("  curl -X POST http://localhost:8000/solution -H 'Content-Type: application/json' \\")
    print("       -d '{\"language\": \"Python\", \"screenshot_data\": [\"base64_image_data\"]}'")
    print("")
    print("  curl -X POST http://localhost:8000/optimize -H 'Content-Type: application/json' \\")
    print("       -d '{\"code\": \"def hello(): pass\", \"language\": \"Python\"}'")
    print("=" * 60)
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
