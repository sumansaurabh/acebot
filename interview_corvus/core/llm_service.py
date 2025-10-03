import json
from typing import List, Type, TypeVar, Union, Generator, Iterator
import re

from llama_index.core.base.llms.types import ChatMessage, ImageBlock, MessageRole
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI
from loguru import logger
from pydantic import BaseModel
from PyQt6.QtCore import QObject, pyqtSignal

from interview_corvus.config import settings
from interview_corvus.core.models import CodeOptimization, CodeSolution, McqSolution
from interview_corvus.core.prompt_manager import PromptManager
from interview_corvus.security.api_key_manager import APIKeyManager

T = TypeVar("T", bound=BaseModel)


class LLMService(QObject):
    """Service for interacting with LLM through LlamaIndex."""

    # Signals for responses
    completion_finished = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    # New signals for streaming
    optimization_progress = pyqtSignal(object)  # Emits partial CodeOptimization objects
    optimization_completed = pyqtSignal(object)  # Emits final CodeOptimization object
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

    def get_code_optimization_stream(
        self, code: str, language: str = None
    ) -> Generator[CodeOptimization, None, None]:
        """
        Get an optimized version of provided code using streaming.
        
        Args:
            code: The code to optimize
            language: The programming language of the code (defaults to settings)
            
        Yields:
            Partial and final CodeOptimization objects as the stream progresses
        """
        # Use default language from settings if none provided
        if language is None:
            language = settings.default_language

        logger.info(f"🌊 Starting streaming optimization for {language} code")
        
        # Check if streaming is enabled in settings
        if not settings.llm.streaming:
            logger.info("🌊 Streaming disabled in settings, falling back to regular optimization")
            yield self.get_code_optimization(code, language)
            return

        prompt_manager = PromptManager()
        prompt = prompt_manager.get_prompt(
            "code_optimization", code=code, language=language
        )

        message = ChatMessage(
            role=MessageRole.USER,
            content=prompt,
        )

        # Initialize partial optimization object
        partial_optimization = CodeOptimization(
            original_code=code,
            optimized_code="",
            language=language,
            improvements=[],
            original_time_complexity="Analyzing...",
            optimized_time_complexity="Analyzing...",
            original_space_complexity="Analyzing...",
            optimized_space_complexity="Analyzing...",
            explanation="Starting optimization analysis...",
            is_complete=False,
            progress=0.0
        )

        try:
            # Emit initial progress
            partial_optimization.progress = 0.1
            self.optimization_progress.emit(partial_optimization)
            yield partial_optimization
            
            # Try streaming with regular LLM first
            logger.info("🌊 Attempting to stream optimization response")
            
            if hasattr(self.llm, 'stream_chat'):
                stream_response = self.llm.stream_chat([message])
                accumulated_text = ""
                current_section = ""
                
                # Track which sections we're currently in
                sections_found = {
                    'optimized_code': False,
                    'improvements': False,
                    'explanation': False,
                    'complexities': False
                }
                
                for chunk in stream_response:
                    if hasattr(chunk, 'delta') and chunk.delta:
                        chunk_text = chunk.delta
                    elif hasattr(chunk, 'message') and hasattr(chunk.message, 'content'):
                        chunk_text = chunk.message.content
                    else:
                        chunk_text = str(chunk)
                    
                    accumulated_text += chunk_text
                    
                    # Try to parse and extract information progressively
                    updated_optimization = self._parse_streaming_optimization(
                        accumulated_text, partial_optimization, sections_found
                    )
                    
                    # Update progress based on content
                    progress = min(0.9, 0.1 + (len(accumulated_text) / 2000) * 0.8)
                    updated_optimization.progress = progress
                    
                    # Emit progress update
                    self.optimization_progress.emit(updated_optimization)
                    yield updated_optimization
                
                # Final parsing attempt
                final_optimization = self._finalize_streaming_optimization(
                    accumulated_text, code, language
                )
                final_optimization.is_complete = True
                final_optimization.progress = 1.0
                
                logger.info("✅ Streaming optimization completed successfully")
                self.optimization_completed.emit(final_optimization)
                yield final_optimization
                return
                
            else:
                logger.warning("⚠️ LLM doesn't support stream_chat, falling back to regular optimization")
                
        except Exception as streaming_error:
            logger.error(f"❌ Streaming optimization failed: {streaming_error}")
            logger.info("🔄 Falling back to regular optimization")
            
        # Fallback to regular optimization
        try:
            result = self.get_code_optimization(code, language)
            result.is_complete = True
            result.progress = 1.0
            self.optimization_completed.emit(result)
            yield result
        except Exception as fallback_error:
            error_optimization = CodeOptimization(
                original_code=code,
                optimized_code=f"Error occurred during optimization: {fallback_error}",
                language=language,
                improvements=["Error occurred"],
                original_time_complexity="N/A",
                optimized_time_complexity="N/A",
                original_space_complexity="N/A",
                optimized_space_complexity="N/A",
                explanation=f"Error occurred during optimization: {fallback_error}",
                is_complete=True,
                progress=1.0
            )
            self.error_occurred.emit(str(fallback_error))
            yield error_optimization

    def _parse_streaming_optimization(
        self, text: str, base_optimization: CodeOptimization, sections_found: dict
    ) -> CodeOptimization:
        """
        Parse streaming text and update optimization object progressively.
        """
        # Create a copy of the base optimization to modify
        updated = CodeOptimization(
            original_code=base_optimization.original_code,
            optimized_code=base_optimization.optimized_code,
            language=base_optimization.language,
            improvements=base_optimization.improvements.copy(),
            original_time_complexity=base_optimization.original_time_complexity,
            optimized_time_complexity=base_optimization.optimized_time_complexity,
            original_space_complexity=base_optimization.original_space_complexity,
            optimized_space_complexity=base_optimization.optimized_space_complexity,
            explanation=base_optimization.explanation,
            is_complete=False,
            progress=base_optimization.progress
        )
        
        # Try to parse as JSON first
        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, dict):
                    for key, value in parsed.items():
                        if hasattr(updated, key) and value:
                            setattr(updated, key, value)
                    return updated
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Fallback to pattern matching for partial content
        patterns = {
            'optimized_code': r'(?:```\w*\n)?(.*?)(?:\n```)?',
            'explanation': r'(?:explanation|analysis|description)[:]\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            'improvements': r'(?:improvements|optimizations)[:]\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            'original_time_complexity': r'original.*time.*complexity[:]\s*(O\([^)]+\)|\w+)',
            'optimized_time_complexity': r'optimized.*time.*complexity[:]\s*(O\([^)]+\)|\w+)',
            'original_space_complexity': r'original.*space.*complexity[:]\s*(O\([^)]+\)|\w+)',
            'optimized_space_complexity': r'optimized.*space.*complexity[:]\s*(O\([^)]+\)|\w+)',
        }
        
        for field, pattern in patterns.items():
            if not sections_found.get(field, False):
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    value = match.group(1).strip()
                    if value:
                        if field == 'improvements' and isinstance(value, str):
                            # Try to split improvements into a list
                            improvements = [imp.strip('- ').strip() for imp in value.split('\n') if imp.strip()]
                            updated.improvements = improvements[:5]  # Limit to 5 improvements
                        else:
                            setattr(updated, field, value)
                        sections_found[field] = True
        
        # Update explanation with streaming indicator
        if not updated.explanation or updated.explanation == base_optimization.explanation:
            updated.explanation = f"Analyzing optimization... ({len(text)} chars received)"
        
        return updated

    def _finalize_streaming_optimization(
        self, full_text: str, original_code: str, language: str
    ) -> CodeOptimization:
        """
        Parse the complete streamed text into a final CodeOptimization object.
        """
        try:
            # Try to parse as JSON first
            json_match = re.search(r'\{.*\}', full_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, dict):
                    # Ensure required fields are present
                    parsed.setdefault('original_code', original_code)
                    parsed.setdefault('language', language)
                    parsed.setdefault('optimized_code', original_code)
                    parsed.setdefault('improvements', ['Optimized version provided'])
                    parsed.setdefault('original_time_complexity', 'N/A')
                    parsed.setdefault('optimized_time_complexity', 'N/A')
                    parsed.setdefault('original_space_complexity', 'N/A')
                    parsed.setdefault('optimized_space_complexity', 'N/A')
                    parsed.setdefault('explanation', 'Optimization completed.')
                    
                    return CodeOptimization(**parsed)
                    
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse final JSON: {e}")
        
        # Fallback: create optimization from raw text
        return CodeOptimization(
            original_code=original_code,
            optimized_code=full_text if full_text.strip() else original_code,
            language=language,
            improvements=["Streaming optimization completed"],
            original_time_complexity="N/A",
            optimized_time_complexity="N/A", 
            original_space_complexity="N/A",
            optimized_space_complexity="N/A",
            explanation=full_text if full_text.strip() else "Optimization completed via streaming.",
            is_complete=True,
            progress=1.0
        )

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
