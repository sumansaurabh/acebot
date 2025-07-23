#!/usr/bin/env python3
"""
Test script to verify HTTPS server setup with SSL certificates.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from interview_corvus.api.web_server import create_integrated_web_server
from loguru import logger

def test_https_server():
    """Test HTTPS server setup."""
    try:
        print("🔒 Testing HTTPS server setup...")
        
        # Create web server with SSL enabled
        api_instance, server_thread, actual_port = create_integrated_web_server(
            llm_service=None,  # No GUI services for this test
            screenshot_manager=None,
            host="0.0.0.0",
            port=8443,
            use_ssl=True
        )
        
        print(f"✅ HTTPS server created successfully on port {actual_port}")
        print("🔒 SSL certificates found and configured")
        print(f"🌐 Server ready to start at https://localhost:{actual_port}")
        print("\nTo start the server, run:")
        print("  python -m interview_corvus.main")
        print("\nOr test with a simple HTTPS request:")
        print(f"  curl -k https://localhost:{actual_port}/health")
        
    except FileNotFoundError as e:
        print(f"❌ SSL certificate files not found: {e}")
        print("📋 Make sure you have both cert.pem and key.pem in the certs/ directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to setup HTTPS server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_https_server()
