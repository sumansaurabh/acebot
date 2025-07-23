"""Deepgram speech-to-text service for transcribing audio recordings."""

import asyncio
import threading
import concurrent.futures
from pathlib import Path
from typing import Optional, Dict, Any
import json

from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from loguru import logger

from interview_corvus.security.api_key_manager import APIKeyManager


class DeepgramService:
    """Service for transcribing audio using Deepgram API."""
    
    def __init__(self):
        """Initialize the Deepgram service."""
        self.api_key = self._get_deepgram_api_key()
        if self.api_key:
            self.client = DeepgramClient(self.api_key)
            logger.info("✅ Deepgram client initialized successfully")
        else:
            self.client = None
            logger.warning("⚠️ No Deepgram API key found, transcription will be disabled")
    
    def _get_deepgram_api_key(self) -> Optional[str]:
        """Get Deepgram API key from configuration.
        
        Returns:
            Deepgram API key or None if not found
        """
        # For now, we'll use the same API key manager but you might want to extend it
        # to support multiple API key types
        api_key_manager = APIKeyManager()
        
        # Try to get Deepgram key first, fallback to a hardcoded one for now
        # You should store this securely in your key manager
        deepgram_key = "005d843dfed9aa2752a614c9265443df5f72951d"  # Your provided key with HT prefix
        
        if deepgram_key:
            return deepgram_key
        
        logger.warning("No Deepgram API key configured")
        return None
    
    async def transcribe_audio_async(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio file asynchronously using Deepgram.
        
        Args:
            audio_file_path: Path to the audio file to transcribe
            
        Returns:
            Dictionary containing transcription results and metadata
        """
        if not self.client:
            logger.error("Deepgram client not initialized - no API key")
            return {
                'success': False,
                'error': 'Deepgram client not initialized - no API key',
                'transcript': '[Transcription failed - no API key]',
                'confidence': 0.0
            }
        
        try:
            # Verify file exists
            file_path = Path(audio_file_path)
            if not file_path.exists():
                logger.error(f"Audio file not found: {audio_file_path}")
                return {
                    'success': False,
                    'error': f'Audio file not found: {audio_file_path}',
                    'transcript': '[Transcription failed - file not found]',
                    'confidence': 0.0
                }
            
            logger.info(f"Starting transcription for: {file_path.name}")
            
            # Read the audio file
            with open(file_path, 'rb') as audio_file:
                buffer_data = audio_file.read()
            
            # Configure transcription options
            options = PrerecordedOptions(
                model="nova-2",
                smart_format=True,
                punctuate=True,
                paragraphs=True,
                utterances=True,
                language="en"
            )
            
            # Create file source
            payload = {
                'buffer': buffer_data,
            }
            
            # Perform transcription
            response = await self.client.listen.asyncprerecorded.v("1").transcribe_file(
                payload, options
            )
            
            # Extract transcript and metadata
            if response and hasattr(response, 'results'):
                results = response.results
                
                # Get the main transcript
                transcript = ""
                confidence = 0.0
                
                if results.channels and len(results.channels) > 0:
                    channel = results.channels[0]
                    if channel.alternatives and len(channel.alternatives) > 0:
                        alternative = channel.alternatives[0]
                        transcript = alternative.transcript or ""
                        confidence = alternative.confidence or 0.0
                
                # Get additional metadata
                metadata = {
                    'duration': getattr(results.summary, 'duration', 0) if hasattr(results, 'summary') else 0,
                    'channels': len(results.channels) if results.channels else 0,
                    'language': 'en',
                    'model': 'nova-2'
                }
                
                logger.info(f"✅ Transcription completed: {len(transcript)} characters, confidence: {confidence:.2f}")
                
                return {
                    'success': True,
                    'transcript': transcript,
                    'confidence': confidence,
                    'metadata': metadata,
                    'raw_response': response
                }
            else:
                logger.error("No results in Deepgram response")
                return {
                    'success': False,
                    'error': 'No results in Deepgram response',
                    'transcript': '[Transcription failed - no results]',
                    'confidence': 0.0
                }
                
        except Exception as e:
            error_msg = f"Deepgram transcription failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'transcript': f'[Transcription failed - {str(e)}]',
                'confidence': 0.0
            }
    
    def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio file synchronously using thread-based async execution.
        
        Args:
            audio_file_path: Path to the audio file to transcribe
            
        Returns:
            Dictionary containing transcription results and metadata
        """
        def run_async_in_thread():
            """Run async transcription in a separate thread with its own event loop."""
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.transcribe_audio_async(audio_file_path))
                    return result
                finally:
                    loop.close()
            except Exception as e:
                logger.error(f"Thread-based transcription error: {str(e)}")
                return {
                    'success': False,
                    'error': f'Thread execution failed: {str(e)}',
                    'transcript': f'[Transcription failed - {str(e)}]',
                    'confidence': 0.0
                }
        
        try:
            # Run in a separate thread to avoid event loop conflicts
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_async_in_thread)
                result = future.result(timeout=30)  # 30 second timeout
                return result
                
        except concurrent.futures.TimeoutError:
            error_msg = "Transcription timed out after 30 seconds"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'transcript': '[Transcription failed - timeout]',
                'confidence': 0.0
            }
        except Exception as e:
            error_msg = f"Error in thread-based transcription: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'transcript': f'[Transcription failed - {str(e)}]',
                'confidence': 0.0
            }
    
    def is_available(self) -> bool:
        """Check if Deepgram service is available.
        
        Returns:
            True if Deepgram client is initialized and ready
        """
        return self.client is not None
