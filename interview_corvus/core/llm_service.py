import json
from pathlib import Path
from typing import List, Type, TypeVar, Union, Generator, Optional

from llama_index.core.base.llms.types import ChatMessage, ImageBlock, MessageRole
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI
from loguru import logger
from pydantic import BaseModel
from PyQt6.QtCore import QObject, pyqtSignal

from interview_corvus.config import settings
from interview_corvus.core.models import CodeOptimization, CodeSolution, McqSolution, RecordingSolution
from interview_corvus.core.prompt_manager import PromptManager
from interview_corvus.core.file_processor import FileProcessor
from interview_corvus.security.api_key_manager import APIKeyManager

T = TypeVar("T", bound=BaseModel)


class LLMService(QObject):
    """Service for interacting with LLM through LlamaIndex."""

    # Signals for responses
    completion_finished = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    # Streaming signals
    streaming_chunk_received = pyqtSignal(str)  # For streaming text chunks
    streaming_started = pyqtSignal()  # When streaming begins
    streaming_finished = pyqtSignal(str)  # When streaming completes with full text
    
    llm: OpenAI
    def __init__(self):
        """Initialize the LLM service with configured settings."""
        super().__init__()
        api_key = APIKeyManager().get_api_key()
        
        # Debug: Check if API key is properly retrieved
        if not api_key:
            logger.error("❌ No API key found! Please set your OpenAI API key.")
            raise ValueError("API key is required but not found")
        else:
            logger.info(f"✅ API key found (length: {len(api_key)})")

        # Determine if we're using OpenAI or Anthropic based on model name
        is_anthropic = any(
            model_prefix in settings.llm.model
            for model_prefix in ["claude", "anthropic"]
        )

        if is_anthropic:
            self.llm = Anthropic(
                model=settings.llm.model,
                temperature=settings.llm.temperature,
                api_key=api_key,
                max_tokens=12000,  # Set an appropriate max tokens value
            )
            logger.info(f"Initialized Anthropic LLM with model: {settings.llm.model}")
        else:
            # Initialize OpenAI client
            self.llm = OpenAI(
                model=settings.llm.model,
                temperature=settings.llm.temperature,
                api_key=api_key,
                max_retries=settings.llm.max_retries,
                timeout=settings.llm.timeout,
            )
            logger.info(f"Initialized OpenAI LLM with model: {settings.llm.model}")

        # Initialize chat engine that will maintain conversation history
        self.chat_engine = SimpleChatEngine.from_defaults(
            llm=self.llm,
        )
        
        # Session storage for persistence
        self._last_solution = None
        self._last_optimization = None
        
        # Initialize file processor
        self.file_processor = FileProcessor()

    def reset_chat_history(self):
        """Reset the chat history."""
        logger.info("Resetting chat history")
        # Recreate chat engine to clear the history
        self.chat_engine = SimpleChatEngine.from_defaults(
            llm=self.llm,
        )
        # Clear stored solutions
        self._last_solution = None
        self._last_optimization = None

    def get_code_optimization(
        self, code: str, language: str = None
    ) -> CodeOptimization:
        """
        Get an optimized version of provided code.

        Args:
            code: The code to optimize
            language: The programming language of the code (defaults to settings)

        Returns:
            A structured code optimization response
        """
        # Use default language from settings if none provided
        if language is None:
            language = settings.default_language

        prompt_manager = PromptManager()
        prompt = prompt_manager.get_prompt(
            "code_optimization", code=code, language=language
        )

        message = ChatMessage(
            role=MessageRole.USER,
            content=prompt,
        )

        try:
            structured = self.llm.as_structured_llm(output_cls=CodeOptimization)
            response = structured.chat([message])
            
            logger.info(f"🔍 LLM Service: Received response type: {type(response)}")
            logger.info(f"🔍 LLM Service: Response attributes: {dir(response)}")
            
            # Handle different response formats from LlamaIndex structured LLM
            # First, try to get the structured object directly
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                content = response.message.content
                logger.info(f"🔍 LLM Service: Message content type: {type(content)}")
                
                # If content is already a CodeOptimization object, return it
                if isinstance(content, CodeOptimization):
                    logger.info("✅ LLM Service: Content is already CodeOptimization object")
                    return content
        except Exception as structured_error:
            logger.warning(f"⚠️ LLM Service: Structured LLM failed: {structured_error}")
            logger.info("🔄 LLM Service: Falling back to regular chat")
            
            # Fallback to regular chat and manual parsing
            try:
                response = self.llm.chat([message])
                content = response.message.content
                logger.info(f"🔍 LLM Service: Fallback response type: {type(content)}")
                
                # Try to parse as JSON
                if isinstance(content, str):
                    try:
                        content_dict = json.loads(content)
                        return CodeOptimization(**content_dict)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        # If JSON parsing fails, create a basic response
                        logger.warning("⚠️ LLM Service: Failed to parse as JSON, creating basic response")
                        return CodeOptimization(
                            original_code=code,
                            optimized_code=content,
                            language=language,
                            improvements=["LLM provided optimized version"],
                            original_time_complexity="N/A",
                            optimized_time_complexity="N/A",
                            original_space_complexity="N/A",
                            optimized_space_complexity="N/A",
                            explanation="Optimization generated by LLM"
                        )
                
                return content
            except Exception as fallback_error:
                logger.error(f"❌ LLM Service: Fallback also failed: {fallback_error}")
                # Return a basic error response
                return CodeOptimization(
                    original_code=code,
                    optimized_code="Error occurred during optimization",
                    language=language,
                    improvements=["Error occurred"],
                    original_time_complexity="N/A",
                    optimized_time_complexity="N/A",
                    original_space_complexity="N/A",
                    optimized_space_complexity="N/A",
                    explanation=f"Error occurred during optimization: {fallback_error}"
                )
        
        # Continue with the existing structured response handling if structured LLM succeeded
        try:
            # First, try to get the structured object directly
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                content = response.message.content
                logger.info(f"🔍 LLM Service: Message content type: {type(content)}")
                
                # If content is already a CodeOptimization object, return it
                if isinstance(content, CodeOptimization):
                    logger.info("✅ LLM Service: Content is already CodeOptimization object")
                    return content
                
                # If content is a string (JSON), parse it
                if isinstance(content, str):
                    try:
                        logger.info("🔍 LLM Service: Parsing string content as JSON")
                        content_dict = json.loads(content)
                        return CodeOptimization(**content_dict)
                    except (json.JSONDecodeError, TypeError, ValueError) as e:
                        logger.warning(f"Failed to parse JSON response: {e}, falling back to raw")
                
                # If content is a dict, create CodeOptimization object
                if isinstance(content, dict):
                    logger.info("🔍 LLM Service: Content is dict, creating CodeOptimization")
                    return CodeOptimization(**content)
            
            # If none of the above work, try the raw response
            if hasattr(response, 'raw') and response.raw:
                logger.info(f"🔍 LLM Service: Trying raw response, type: {type(response.raw)}")
                if isinstance(response.raw, CodeOptimization):
                    logger.info("✅ LLM Service: Raw is already CodeOptimization object")
                    return response.raw
                if isinstance(response.raw, str):
                    try:
                        logger.info("🔍 LLM Service: Parsing raw string as JSON")
                        raw_dict = json.loads(response.raw)
                        return CodeOptimization(**raw_dict)
                    except (json.JSONDecodeError, TypeError, ValueError) as e:
                        logger.warning(f"Failed to parse raw JSON: {e}")
                        pass
                if isinstance(response.raw, dict):
                    logger.info("🔍 LLM Service: Raw is dict, creating CodeOptimization")
                    return CodeOptimization(**response.raw)
            
            # Last resort: return response.raw as is (might be a string)
            logger.warning("⚠️ LLM Service: Unable to parse structured response, returning raw response")
            return response.raw
            
        except Exception as e:
            logger.error(f"❌ LLM Service: Error processing structured response: {e}")
            return response.raw

    def get_solution_from_screenshots(
        self, screenshot_paths: List[str], language: str = None
    ) -> Union[CodeSolution, McqSolution]:
        """
        Get a solution based on multiple screenshots of a programming problem.

        Args:
            screenshot_paths: List of paths to the screenshot files
            language: The programming language to use for the solution (defaults to settings)

        Returns:
            A structured code solution response (CodeSolution for code problems, McqSolution for MCQ problems)
        """
        # Use default language from settings if none provided
        if language is None:
            language = settings.default_language

        # For multimodal requests, using direct OpenAI API call through LlamaIndex
        prompt_manager = PromptManager()

        # Get the screenshot prompt with language
        if language == "mcq":
            prompt_text = prompt_manager.get_prompt(
                "mcq_solution", language="mcq"
            )
        else:
            prompt_text = prompt_manager.get_prompt(
                "screenshot_solution", language=language
            )

        logger.info(f"Processing {len(screenshot_paths)} screenshots")

        # Create a system message with the prompt text
        system = ChatMessage(
            role=MessageRole.SYSTEM,
            content=prompt_text,
        )

        # Initialize chat messages with the system message
        chat_messages = [system]

        # Add each screenshot as a user message with an image block
        for path in screenshot_paths:
            logger.info(f"Adding screenshot: {path}")
            screenshot = ChatMessage(
                role=MessageRole.USER,
                blocks=[
                    ImageBlock(
                        path=path,
                    )
                ],
            )
            chat_messages.append(screenshot)

        # For processing screenshots with history context
        try:
            if language == "mcq":
                structured = self.llm.as_structured_llm(output_cls=McqSolution)
                response = structured.chat(chat_messages)
                expected_type = McqSolution
            else:
                structured = self.llm.as_structured_llm(output_cls=CodeSolution)
                response = structured.chat(chat_messages)
                expected_type = CodeSolution

            logger.info(f"🔍 LLM Service: Received response type: {type(response)}")
            logger.info(f"🔍 LLM Service: Expected type: {expected_type}")
            
            # Handle different response formats from LlamaIndex structured LLM
            # First, try to get the structured object directly
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                content = response.message.content
                
                # If content is already the expected object type, return it
                if isinstance(content, expected_type):
                    return content
        except Exception as structured_error:
            logger.warning(f"⚠️ LLM Service: Structured LLM failed for screenshots: {structured_error}")
            logger.info("🔄 LLM Service: Falling back to regular chat for screenshots")
            
            # Fallback to regular chat and manual parsing
            try:
                response = self.llm.chat(chat_messages)
                content = response.message.content
                logger.info(f"🔍 LLM Service: Screenshot fallback response type: {type(content)}")
                
                # Try to parse as JSON
                if isinstance(content, str):
                    try:
                        content_dict = json.loads(content)
                        return expected_type(**content_dict)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        # If JSON parsing fails, create a basic response
                        logger.warning("⚠️ LLM Service: Failed to parse screenshot response as JSON, creating basic response")
                        if language == "mcq":
                            return McqSolution(
                                solution=content
                            )
                        else:
                            return CodeSolution(
                                code=content,
                                language=language,
                                explanation=content,
                                time_complexity="N/A",
                                space_complexity="N/A",
                                edge_cases=[],
                                alternative_approaches=None
                            )
                
                return content
            except Exception as fallback_error:
                logger.error(f"❌ LLM Service: Screenshot fallback also failed: {fallback_error}")
                # Return a basic error response based on language type
                if language == "mcq":
                    return McqSolution(
                        solution=f"Error occurred during screenshot analysis: {fallback_error}",
                    )
                else:
                    return CodeSolution(
                        code=f"# Error occurred during screenshot analysis: {fallback_error}",
                        language=language,
                        explanation=f"Error occurred during screenshot analysis: {fallback_error}",
                        time_complexity="N/A",
                        space_complexity="N/A",
                        edge_cases=[],
                        alternative_approaches=None
                    )
        
        # Continue with the existing structured response handling if structured LLM succeeded
        try:
            # First, try to get the structured object directly
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                content = response.message.content
                
                # If content is already the expected object type, return it
                if isinstance(content, expected_type):
                    return content
                
                # If content is a string (JSON), parse it
                if isinstance(content, str):
                    try:
                        content_dict = json.loads(content)
                        return expected_type(**content_dict)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        logger.warning("Failed to parse JSON response, falling back to raw")
                
                # If content is a dict, create the expected object
                if isinstance(content, dict):
                    return expected_type(**content)
            
            # If none of the above work, try the raw response
            if hasattr(response, 'raw') and response.raw:
                if isinstance(response.raw, expected_type):
                    return response.raw
                if isinstance(response.raw, str):
                    try:
                        raw_dict = json.loads(response.raw)
                        return expected_type(**raw_dict)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        pass
                if isinstance(response.raw, dict):
                    return expected_type(**response.raw)
            
            # Last resort: return response.raw as is (might be a string)
            logger.warning("Unable to parse structured response, returning raw response")
            return response.raw
            
        except Exception as e:
            logger.error(f"Error processing structured response: {e}")
            return response.raw

    def get_solution_from_recording(
        self, file_paths: List[str], prompt: str = None, streaming: bool = True
    ) -> Union[RecordingSolution, Generator[str, None, str]]:
        """
        Get a solution based on uploaded files and optional prompt with streaming support.

        Args:
            file_paths: List of paths to the uploaded files (max 2)
            prompt: Optional custom prompt for the analysis
            streaming: Whether to return streaming response or complete response

        Returns:
            If streaming=True: Generator yielding text chunks, final yield is complete text
            If streaming=False: RecordingSolution object
        """
        logger.info(f"Processing recording solution for {len(file_paths)} files, streaming={streaming}")
        
        # Validate and process files
        validation_errors = self.file_processor.validate_files_for_upload(file_paths)
        if validation_errors:
            error_msg = "File validation failed: " + "; ".join(validation_errors)
            logger.error(error_msg)
            if streaming:
                return self._create_error_stream(error_msg)
            else:
                return RecordingSolution(
                    solution=f"**Error:** {error_msg}",
                    file_summary="File processing failed",
                    confidence=0.0
                )

        # Process files to text
        try:
            combined_text, processing_errors = self.file_processor.process_multiple_files(file_paths)
            
            if processing_errors:
                error_warnings = "\n".join([f"⚠️ {error}" for error in processing_errors])
                logger.warning(f"File processing warnings: {processing_errors}")
            else:
                error_warnings = ""
                
            if not combined_text.strip():
                error_msg = "No readable content found in the uploaded files"
                logger.error(error_msg)
                if streaming:
                    return self._create_error_stream(error_msg)
                else:
                    return RecordingSolution(
                        solution=f"**Error:** {error_msg}",
                        file_summary="No content extracted",
                        confidence=0.0
                    )
                    
        except Exception as e:
            error_msg = f"Failed to process files: {str(e)}"
            logger.error(error_msg)
            if streaming:
                return self._create_error_stream(error_msg)
            else:
                return RecordingSolution(
                    solution=f"**Error:** {error_msg}",
                    file_summary="File processing failed",
                    confidence=0.0
                )

        # Get the recording analysis prompt
        prompt_manager = PromptManager()
        
        if prompt is None:
            # Use default recording analysis prompt
            system_prompt = prompt_manager.get_prompt(
                "recording_solution", 
                file_content=combined_text[:2000] + "..." if len(combined_text) > 2000 else combined_text
            )
        else:
            # Use custom prompt with file content
            system_prompt = f"{prompt}\n\nFile Content:\n{combined_text}"

        # Create file summary for metadata
        file_names = [Path(fp).name for fp in file_paths]
        file_summary = f"Processed {len(file_paths)} files: {', '.join(file_names)}"
        if error_warnings:
            file_summary += f"\n\nProcessing warnings:\n{error_warnings}"

        # Create chat messages
        system_message = ChatMessage(
            role=MessageRole.SYSTEM,
            content=system_prompt,
        )

        user_message = ChatMessage(
            role=MessageRole.USER,
            content=f"Please analyze the provided file content and provide a comprehensive solution in markdown format. Files processed: {', '.join(file_names)}",
        )

        chat_messages = [system_message, user_message]

        if streaming:
            return self._stream_recording_response(chat_messages, file_summary)
        else:
            return self._get_complete_recording_response(chat_messages, file_summary)

    def _create_error_stream(self, error_msg: str) -> Generator[str, None, str]:
        """Create an error stream for streaming responses."""
        error_markdown = f"**Error:** {error_msg}"
        yield error_markdown
        return error_markdown

    def _stream_recording_response(self, chat_messages: List[ChatMessage], file_summary: str) -> Generator[str, None, str]:
        """Stream the recording analysis response."""
        try:
            logger.info("Starting streaming recording analysis")
            self.streaming_started.emit()
            
            # Use the LLM's stream method for real-time response
            accumulated_text = ""
            
            # LlamaIndex streaming - this depends on the specific LLM implementation
            try:
                # For OpenAI, we can use stream_chat
                response_stream = self.llm.stream_chat(chat_messages)
                
                for chunk in response_stream:
                    if hasattr(chunk, 'delta') and chunk.delta:
                        chunk_text = str(chunk.delta)
                    elif hasattr(chunk, 'message') and hasattr(chunk.message, 'content'):
                        chunk_text = str(chunk.message.content)
                    else:
                        chunk_text = str(chunk)
                    
                    if chunk_text:
                        accumulated_text += chunk_text
                        self.streaming_chunk_received.emit(chunk_text)
                        yield chunk_text
                        
            except Exception as stream_error:
                logger.warning(f"Streaming failed, falling back to regular chat: {stream_error}")
                # Fallback to regular chat if streaming fails
                response = self.llm.chat(chat_messages)
                content = response.message.content if hasattr(response, 'message') else str(response)
                accumulated_text = content
                self.streaming_chunk_received.emit(content)
                yield content
            
            logger.info(f"Streaming completed, total length: {len(accumulated_text)}")
            self.streaming_finished.emit(accumulated_text)
            return accumulated_text
            
        except Exception as e:
            error_msg = f"Error during streaming recording analysis: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            error_response = f"**Error:** {error_msg}"
            yield error_response
            return error_response

    def _get_complete_recording_response(self, chat_messages: List[ChatMessage], file_summary: str) -> RecordingSolution:
        """Get complete recording analysis response (non-streaming)."""
        try:
            logger.info("Getting complete recording analysis response")
            
            # Try structured response first
            try:
                structured = self.llm.as_structured_llm(output_cls=RecordingSolution)
                response = structured.chat(chat_messages)
                
                # Handle different response formats
                if hasattr(response, 'message') and hasattr(response.message, 'content'):
                    content = response.message.content
                    if isinstance(content, RecordingSolution):
                        return content
                    
                    # If content is a string, try to parse as JSON
                    if isinstance(content, str):
                        try:
                            content_dict = json.loads(content)
                            return RecordingSolution(**content_dict)
                        except (json.JSONDecodeError, TypeError, ValueError):
                            # Create response with the raw content
                            return RecordingSolution(
                                solution=content,
                                file_summary=file_summary,
                                confidence=0.8
                            )
                    
                    # If content is a dict
                    if isinstance(content, dict):
                        content['file_summary'] = file_summary
                        return RecordingSolution(**content)
                        
            except Exception as structured_error:
                logger.warning(f"Structured LLM failed: {structured_error}")
                
            # Fallback to regular chat
            response = self.llm.chat(chat_messages)
            content = response.message.content if hasattr(response, 'message') else str(response)
            
            return RecordingSolution(
                solution=content,
                file_summary=file_summary,
                confidence=0.7
            )
            
        except Exception as e:
            error_msg = f"Error during recording analysis: {str(e)}"
            logger.error(error_msg)
            return RecordingSolution(
                solution=f"**Error:** {error_msg}",
                file_summary=file_summary,
                confidence=0.0
            )

    def process_recording_with_files(self, recording_data: str, custom_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Process recording with uploaded files and return streaming response.
        
        Args:
            recording_data: Recording data or description
            custom_prompt: Optional custom prompt from user
            
        Yields:
            Streaming response chunks from LLM
        """
        try:
            logger.info("Starting recording analysis with files")
            
            # Get file processor instance
            file_processor = FileProcessor()
            
            # Get uploaded files content
            saved_files = file_processor.get_saved_files_content()
            files_content = None
            
            if saved_files:
                # Combine content from all uploaded files
                combined_content = []
                for file_key, file_data in saved_files.items():
                    if isinstance(file_data, dict) and 'content' in file_data:
                        filename = file_data.get('filename', 'unknown')
                        content = file_data.get('content', '')
                        combined_content.append(f"=== File: {filename} ===\n{content}\n")
                
                if combined_content:
                    files_content = "\n".join(combined_content)
                    logger.info(f"Retrieved {len(saved_files)} uploaded files with {len(files_content)} characters")
            
            # Create recording analysis prompt
            prompt_parts = []
            
            # Base recording prompt
            base_prompt = """Analyze the provided recording and any additional file content. Provide a comprehensive analysis in markdown format.

Recording Data:
{recording_data}
""".format(recording_data=recording_data)
            
            prompt_parts.append(base_prompt)
            
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
            
            full_prompt = "\n".join(prompt_parts)
            
            # Create chat messages
            system_message = ChatMessage(
                role=MessageRole.SYSTEM,
                content="You are an expert analyst. Analyze recordings and related files to provide comprehensive insights."
            )
            
            user_message = ChatMessage(
                role=MessageRole.USER,
                content=full_prompt
            )
            
            chat_messages = [system_message, user_message]
            
            # Stream the response
            logger.info("Starting streaming response for recording analysis")
            self.streaming_started.emit()
            
            accumulated_text = ""
            
            try:
                # Use streaming chat
                response_stream = self.llm.stream_chat(chat_messages)
                
                for chunk in response_stream:
                    if hasattr(chunk, 'delta') and chunk.delta:
                        chunk_text = str(chunk.delta)
                    elif hasattr(chunk, 'message') and hasattr(chunk.message, 'content'):
                        chunk_text = str(chunk.message.content)
                    else:
                        chunk_text = str(chunk)
                    
                    if chunk_text:
                        accumulated_text += chunk_text
                        self.streaming_chunk_received.emit(chunk_text)
                        yield chunk_text
                        
            except Exception as stream_error:
                logger.warning(f"Streaming failed, falling back to regular chat: {stream_error}")
                # Fallback to regular chat if streaming fails
                response = self.llm.chat(chat_messages)
                content = response.message.content if hasattr(response, 'message') else str(response)
                accumulated_text = content
                self.streaming_chunk_received.emit(content)
                yield content
            
            logger.info(f"Recording analysis streaming completed, total length: {len(accumulated_text)}")
            self.streaming_finished.emit(accumulated_text)
            
        except Exception as e:
            error_msg = f"Error during recording analysis: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            yield f"**Error:** {error_msg}"

    def get_recording_analysis_stream(self, recording_data: dict) -> Generator[str, None, None]:
        """Get streaming analysis for recording data with Deepgram transcription.
        
        Args:
            recording_data: Dictionary containing recording information with transcribed content
            
        Yields:
            Streaming response chunks from LLM
        """
        try:
            logger.info("Starting recording analysis stream")
            
            # Extract recording content from the data
            recording_content = recording_data.get('content', 'No recording content available')
            recording_metadata = recording_data.get('metadata', {})
            selected_file_keys = recording_data.get('selected_file_keys', [])
            
            # Check if recording content is valid (not a failure message)
            if recording_content.startswith('[') and ('failed' in recording_content.lower() or 'unavailable' in recording_content.lower()):
                error_msg = f"Recording transcription failed: {recording_content}"
                logger.error(error_msg)
                yield f"**Error:** {error_msg}"
                return
            
            # Check if we have meaningful content to analyze
            if not recording_content or recording_content.strip() == 'No recording content available':
                error_msg = "No valid recording content available for analysis"
                logger.error(error_msg)
                yield f"**Error:** {error_msg}"
                return
            
            logger.info(f"Processing recording with content length: {len(recording_content)} characters")
            
            # Process selected files only
            files_content = None
            
            if selected_file_keys:
                logger.info(f"Processing {len(selected_file_keys)} selected file keys")
                
                # Get file processor instance to access uploaded files
                file_processor = FileProcessor()
                saved_files = file_processor.get_saved_files_content()
                
                if saved_files:
                    combined_content = []
                    
                    for file_key in selected_file_keys:
                        if file_key in saved_files:
                            file_data = saved_files[file_key]
                            if isinstance(file_data, dict) and 'content' in file_data:
                                filename = file_data.get('filename', 'unknown')
                                content = file_data.get('content', '')
                                combined_content.append(f"=== File: {filename} (Key: {file_key}) ===\n{content}\n")
                                logger.info(f"Loaded selected file: {filename} ({len(content)} characters)")
                            else:
                                logger.warning(f"Selected file key has invalid data structure: {file_key}")
                                combined_content.append(f"=== File: {file_key} ===\n[INVALID FILE DATA STRUCTURE]\n")
                        else:
                            logger.warning(f"Selected file key not found in uploaded files: {file_key}")
                            combined_content.append(f"=== File: {file_key} ===\n[FILE KEY NOT FOUND]\n")
                    
                    if combined_content:
                        files_content = "\n".join(combined_content)
                        logger.info(f"Successfully processed {len(selected_file_keys)} selected files with {len(files_content)} total characters")
                else:
                    logger.warning("No uploaded files found in user settings")
                    files_content = "=== No uploaded files found ===\nPlease upload files first before selecting them for analysis.\n"
            else:
                logger.info("No selected file keys provided - processing audio without additional files")
                # Don't load any files if none are specifically selected
                files_content = None
            
            # Create the analysis prompt
            prompt_parts = []
            
            # Base recording prompt
            base_prompt = f"""Answer the technical questions from the transcribed recording directly and concisely. Provide the best technical answers as an expert would.

Recording Transcript:
{recording_content}

Recording Metadata:
{json.dumps(recording_metadata, indent=2) if recording_metadata else 'No metadata available'}
"""
            prompt_parts.append(base_prompt)
            
            # Add file content if available
            if files_content:
                prompt_parts.append(f"""
Additional File Content:
{files_content}
""")
            
            # Final instructions
            prompt_parts.append("""
Please provide direct answers to the technical questions asked in the recording. Format your response as follows:

**For each question identified:**
1. **Question:** [Restate the question clearly]
2. **Answer:** [Provide the best technical answer in bullet points]
3. **Key Keywords:** [List 3-5 relevant technical keywords/concepts]
4. **Additional Notes:** [Any important clarifications in bullet points]

**Response Format:**
- Use bullet points, not paragraphs
- Be concise and technical
- Focus on practical, actionable answers
- Suggest relevant keywords for further study
""")
            
            full_prompt = "\n".join(prompt_parts)
            
            # Create chat messages
            system_message = ChatMessage(
                role=MessageRole.SYSTEM,
                content="You are the best technical expert who provides direct, concise answers to technical questions. Answer questions from transcribed recordings with bullet points and suggest relevant keywords for each topic."
            )
            
            user_message = ChatMessage(
                role=MessageRole.USER,
                content=full_prompt
            )
            
            chat_messages = [system_message, user_message]
            
            # Stream the response
            logger.info("Starting streaming response for recording analysis")
            self.streaming_started.emit()
            
            accumulated_text = ""
            
            try:
                # Use streaming chat
                response_stream = self.llm.stream_chat(chat_messages)
                
                for chunk in response_stream:
                    if hasattr(chunk, 'delta') and chunk.delta:
                        chunk_text = str(chunk.delta)
                    elif hasattr(chunk, 'message') and hasattr(chunk.message, 'content'):
                        chunk_text = str(chunk.message.content)
                    else:
                        chunk_text = str(chunk)
                    
                    if chunk_text:
                        accumulated_text += chunk_text
                        self.streaming_chunk_received.emit(chunk_text)
                        yield chunk_text
                        
            except Exception as stream_error:
                logger.warning(f"Streaming failed, falling back to regular chat: {stream_error}")
                # Fallback to regular chat if streaming fails
                response = self.llm.chat(chat_messages)
                content = response.message.content if hasattr(response, 'message') else str(response)
                accumulated_text = content
                self.streaming_chunk_received.emit(content)
                yield content
            
            logger.info(f"Recording analysis streaming completed, total length: {len(accumulated_text)}")
            self.streaming_finished.emit(accumulated_text)
            
        except Exception as e:
            error_msg = f"Error during recording analysis stream: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            yield f"**Error:** {error_msg}"
