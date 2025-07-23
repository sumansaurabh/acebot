"""Recording service for capturing audio/screen recordings and processing with LLM."""

import json
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Generator
import base64

from loguru import logger

from interview_corvus.core.file_processor import FileProcessor
from interview_corvus.core.deepgram_service import DeepgramService


class RecordingService:
    """Service for handling recordings and sending to LLM for analysis."""
    
    def __init__(self):
        """Initialize the recording service."""
        self.file_processor = FileProcessor()
        self.deepgram_service = DeepgramService()
        self.current_recording_path: Optional[str] = None
        self.is_recording = False
        
    def start_recording(self) -> bool:
        """Start recording (placeholder for actual recording implementation).
        
        Returns:
            True if recording started successfully, False otherwise
        """
        if self.is_recording:
            logger.warning("Recording already in progress")
            return False
            
        try:
            # Create temporary file for recording
            temp_dir = Path(tempfile.gettempdir()) / "interview_corvus_recordings"
            temp_dir.mkdir(exist_ok=True)
            
            # For now, we'll use a placeholder path
            # In real implementation, this would start actual audio/screen recording
            self.current_recording_path = str(temp_dir / f"recording_{os.getpid()}.wav")
            self.is_recording = True
            
            logger.info(f"Recording started: {self.current_recording_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and return the recording file path.
        
        Returns:
            Path to the recording file or None if failed
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None
            
        try:
            self.is_recording = False
            recording_path = self.current_recording_path
            self.current_recording_path = None
            
            # In real implementation, this would stop the actual recording
            # For now, create a placeholder file
            if recording_path and not os.path.exists(recording_path):
                with open(recording_path, 'w') as f:
                    f.write("placeholder recording data")
            
            logger.info(f"Recording stopped: {recording_path}")
            return recording_path
            
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return None
    
    def get_uploaded_files_content(self) -> Optional[str]:
        """Get uploaded file content from user settings.
        
        Returns:
            Combined text content from uploaded files or None if no files
        """
        try:
            saved_files = self.file_processor.get_saved_files_content()
            if not saved_files:
                logger.info("No uploaded files found in user settings")
                return None
            
            # Combine content from all uploaded files
            combined_content = []
            for file_key, file_data in saved_files.items():
                if isinstance(file_data, dict) and 'content' in file_data:
                    filename = file_data.get('filename', 'unknown')
                    content = file_data.get('content', '')
                    combined_content.append(f"=== File: {filename} ===\n{content}\n")
            
            if combined_content:
                result = "\n".join(combined_content)
                logger.info(f"Retrieved {len(saved_files)} uploaded files with {len(result)} characters")
                return result
            else:
                logger.warning("No content found in uploaded files")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving uploaded files content: {e}")
            return None
    
    def prepare_recording_data(self, recording_path: str) -> Optional[dict]:
        """Prepare recording data for LLM processing.
        
        Args:
            recording_path: Path to the recording file
            
        Returns:
            Dictionary containing recording data and metadata
        """
        try:
            if not os.path.exists(recording_path):
                logger.error(f"Recording file not found: {recording_path}")
                return None
            
            # Get file info
            file_size = os.path.getsize(recording_path)
            file_name = Path(recording_path).name
            
            # Transcribe audio using Deepgram
            transcript_content = ""
            transcript_confidence = 0.0
            transcription_metadata = {}
            
            if self.deepgram_service.is_available():
                logger.info(f"Transcribing audio file: {file_name}")
                transcription_result = self.deepgram_service.transcribe_audio(recording_path)
                
                if transcription_result['success']:
                    transcript_content = transcription_result['transcript']
                    transcript_confidence = transcription_result['confidence']
                    transcription_metadata = transcription_result.get('metadata', {})
                    logger.info(f"✅ Transcription successful: {len(transcript_content)} characters")
                else:
                    transcript_content = f"[Transcription failed: {transcription_result.get('error', 'Unknown error')}]"
                    logger.error(f"Transcription failed: {transcription_result.get('error')}")
            else:
                transcript_content = f"[Recording: {file_name}, Size: {file_size} bytes - Deepgram service unavailable]"
                logger.warning("Deepgram service not available, using placeholder content")
            
            # Create recording data with actual transcript or fallback message
            recording_data = {
                'content': transcript_content,
                'metadata': {
                    'filename': file_name,
                    'size': file_size,
                    'path': recording_path,
                    'format': 'wav',
                    'transcription': {
                        'confidence': transcript_confidence,
                        'service': 'deepgram' if self.deepgram_service.is_available() else 'none',
                        **transcription_metadata
                    }
                }
            }
            
            logger.info(f"Prepared recording data for: {file_name}")
            return recording_data
            
        except Exception as e:
            logger.error(f"Error preparing recording data: {e}")
            return None
    
    def create_recording_prompt(self, recording_data: str, files_content: Optional[str] = None, custom_prompt: Optional[str] = None) -> str:
        """Create the prompt for LLM analysis.
        
        Args:
            recording_data: Recording data or description
            files_content: Content from uploaded files
            custom_prompt: Optional custom prompt from user
            
        Returns:
            Complete prompt for LLM
        """
        prompt_parts = []
        
        # Base recording prompt
        base_prompt = """Analyze the provided recording and any additional file content and answer the question in the recording

Recording Data:
{recording_data}
"""
        
        prompt_parts.append(base_prompt.format(recording_data=recording_data))
        
        # Add file content if available
        if files_content:
            prompt_parts.append(f"""
Additional File Content:
{files_content}
""")
        
        # Add custom prompt if provided
        if custom_prompt:
            prompt_parts.append(f"""
Specific Instructions:
{custom_prompt}
""")
        
        # Final instructions
        prompt_parts.append("""
Please provide your analysis in clear markdown format with appropriate headers and sections.""")
        
        return "\n".join(prompt_parts)
    
    def process_recording_with_llm(self, recording_path: str, custom_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Process recording with LLM and return streaming response.
        
        Args:
            recording_path: Path to the recording file
            custom_prompt: Optional custom prompt from user
            
        Yields:
            Streaming response chunks from LLM
        """
        try:
            # Prepare recording data
            recording_data = self.prepare_recording_data(recording_path)
            if not recording_data:
                yield "Error: Could not prepare recording data"
                return
            
            # Get uploaded files content
            files_content = self.get_uploaded_files_content()
            
            # Create prompt
            prompt = self.create_recording_prompt(recording_data, files_content, custom_prompt)
            
            logger.info("Starting LLM processing for recording analysis")
            
            # For now, yield a mock streaming response
            # In real implementation, this would call the actual LLM service
            mock_response = f"""# Recording Analysis

## Summary
Analyzing the provided recording data with {len(files_content) if files_content else 0} characters from uploaded files.

## Recording Details
{recording_data}

## File Content Analysis
{files_content[:200] + "..." if files_content and len(files_content) > 200 else files_content or "No additional files provided"}

## Analysis Results
The recording has been processed successfully. This is a streaming response that would normally come from the LLM service.

## Recommendations
Based on the analysis, here are the key findings and recommendations...
"""
            
            # Simulate streaming by yielding chunks
            words = mock_response.split()
            chunk_size = 5
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size]) + " "
                yield chunk
                
        except Exception as e:
            error_msg = f"Error processing recording with LLM: {e}"
            logger.error(error_msg)
            yield f"Error: {error_msg}"
    
    def cleanup_recording(self, recording_path: str) -> bool:
        """Clean up recording file.
        
        Args:
            recording_path: Path to the recording file to delete
            
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            if recording_path and os.path.exists(recording_path):
                os.remove(recording_path)
                logger.info(f"Cleaned up recording file: {recording_path}")
                return True
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up recording: {e}")
            return False
