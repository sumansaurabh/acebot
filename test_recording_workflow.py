#!/usr/bin/env python3
"""
Test the recording service with Deepgram integration.
"""

import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from interview_corvus.core.recording_service import RecordingService

def test_recording_workflow():
    """Test the complete recording workflow."""
    print("🧪 Testing Recording Service Workflow...")
    
    try:
        # Initialize service
        recording_service = RecordingService()
        print("✅ Recording service initialized")
        
        # Start recording
        print("🎤 Starting recording...")
        success = recording_service.start_recording()
        
        if not success:
            print("❌ Failed to start recording")
            return
        
        print("✅ Recording started successfully")
        print("⏳ Recording for 3 seconds...")
        time.sleep(3)
        
        # Stop recording
        print("🛑 Stopping recording...")
        recording_path = recording_service.stop_recording()
        
        if not recording_path:
            print("❌ Failed to stop recording")
            return
        
        print(f"✅ Recording stopped: {recording_path}")
        
        # Check if file exists
        if Path(recording_path).exists():
            file_size = Path(recording_path).stat().st_size
            print(f"📁 Recording file created: {file_size} bytes")
            
            # Test transcription
            print("🎯 Testing transcription...")
            recording_data = recording_service.prepare_recording_data(recording_path)
            
            if recording_data:
                print("✅ Recording data prepared:")
                print(f"  Content: {recording_data['content'][:100]}...")
                print(f"  Metadata: {recording_data['metadata']}")
            else:
                print("❌ Failed to prepare recording data")
        else:
            print("❌ Recording file not created")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_recording_workflow()
