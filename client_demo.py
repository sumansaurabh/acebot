#!/usr/bin/env python3
"""
Simple client script to demonstrate interaction with Interview Corvus API.
"""

import base64
import json
import requests
from pathlib import Path


class InterviewCorvusClient:
    """Client for interacting with Interview Corvus API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """Initialize the client."""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> dict:
        """Check if the API is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_screenshots(self) -> dict:
        """Get list of available screenshots."""
        try:
            response = self.session.get(f"{self.base_url}/screenshots")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def trigger_screenshot(self) -> dict:
        """Trigger a screenshot capture in the GUI."""
        try:
            response = self.session.post(f"{self.base_url}/screenshot/capture")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def generate_solution_from_images(self, image_paths: list, language: str = "Python") -> dict:
        """Generate solution from image files."""
        try:
            # Encode images to base64
            screenshot_data = []
            for image_path in image_paths:
                with open(image_path, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode()
                    screenshot_data.append(encoded)
            
            payload = {
                "language": language,
                "screenshot_data": screenshot_data
            }
            
            response = self.session.post(
                f"{self.base_url}/solution",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def upload_and_solve(self, image_paths: list, language: str = "Python") -> dict:
        """Upload images and generate solution."""
        try:
            files = []
            for image_path in image_paths:
                files.append(('files', (Path(image_path).name, open(image_path, 'rb'), 'image/png')))
            
            data = {'language': language}
            
            response = self.session.post(
                f"{self.base_url}/upload-solution",
                files=files,
                data=data
            )
            
            # Close file handles
            for _, (_, file_handle, _) in files:
                file_handle.close()
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def optimize_code(self, code: str, language: str = "Python") -> dict:
        """Optimize the provided code."""
        try:
            payload = {
                "code": code,
                "language": language
            }
            
            response = self.session.post(
                f"{self.base_url}/optimize",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def clear_screenshots(self) -> dict:
        """Clear all screenshots."""
        try:
            response = self.session.delete(f"{self.base_url}/screenshots")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def reset_history(self) -> dict:
        """Reset chat history and screenshots."""
        try:
            response = self.session.delete(f"{self.base_url}/history")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def main():
    """Demonstrate API usage."""
    client = InterviewCorvusClient()
    
    print("🎯 Interview Corvus API Client Demo")
    print("=" * 50)
    
    # Health check
    print("\n1. Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    if "error" in health:
        print("❌ API is not available. Make sure the GUI application with web server is running.")
        return
    
    print(f"✅ API is {'healthy' if health.get('status') == 'healthy' else 'unhealthy'}")
    print(f"🔗 GUI Connected: {health.get('gui_connected', False)}")
    
    # Get screenshots
    print("\n2. Available Screenshots:")
    screenshots = client.get_screenshots()
    print(json.dumps(screenshots, indent=2))
    
    # Example code optimization
    print("\n3. Code Optimization Example:")
    sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    optimization = client.optimize_code(sample_code, "Python")
    if "error" not in optimization and optimization.get("success"):
        print("✅ Code optimized successfully!")
        opt_data = optimization.get("optimization", {})
        print(f"Original Time Complexity: {opt_data.get('original_time_complexity', 'N/A')}")
        print(f"Optimized Time Complexity: {opt_data.get('optimized_time_complexity', 'N/A')}")
        print("\nOptimized Code:")
        print(opt_data.get('optimized_code', 'N/A'))
    else:
        print("❌ Code optimization failed:")
        print(json.dumps(optimization, indent=2))
    
    print("\n" + "=" * 50)
    print("Demo completed! Try these endpoints:")
    print("- GET  /health          - Check API health")
    print("- GET  /screenshots     - List screenshots")
    print("- POST /screenshot/capture - Trigger screenshot in GUI")
    print("- POST /solution        - Generate solution from screenshots")
    print("- POST /upload-solution - Upload images and solve")
    print("- POST /optimize        - Optimize code")
    print("- DELETE /screenshots   - Clear screenshots")
    print("- DELETE /history       - Reset history")
    print("\nAPI Documentation: http://127.0.0.1:8000/docs")


if __name__ == "__main__":
    main()
