import json
from typing import List, Type, TypeVar

from llama_index.core.base.llms.types import ChatMessage, ImageBlock, MessageRole
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI
from loguru import logger
from pydantic import BaseModel
from PyQt6.QtCore import QObject, pyqtSignal

from interview_corvus.config import settings
from interview_corvus.core.models import CodeOptimization, CodeSolution
from interview_corvus.core.prompt_manager import PromptManager
from interview_corvus.security.api_key_manager import APIKeyManager

T = TypeVar("T", bound=BaseModel)


class LLMService(QObject):
    """Service for interacting with LLM through LlamaIndex."""

    # Signals for responses
    completion_finished = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
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

    def reset_chat_history(self):
        """Reset the chat history."""
        logger.info("Resetting chat history")
        # Recreate chat engine to clear the history
        self.chat_engine = SimpleChatEngine.from_defaults(
            llm=self.llm,
        )

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
    ) -> CodeSolution:
        """
        Get a solution based on multiple screenshots of a programming problem.

        Args:
            screenshot_paths: List of paths to the screenshot files
            language: The programming language to use for the solution (defaults to settings)

        Returns:
            A structured code solution response
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
            structured = self.llm.as_structured_llm(output_cls=CodeSolution)
            response = structured.chat(chat_messages)
            
            # Handle different response formats from LlamaIndex structured LLM
            # First, try to get the structured object directly
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                content = response.message.content
                
                # If content is already a CodeSolution object, return it
                if isinstance(content, CodeSolution):
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
                        return CodeSolution(**content_dict)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        # If JSON parsing fails, create a basic response
                        logger.warning("⚠️ LLM Service: Failed to parse screenshot response as JSON, creating basic response")
                        return CodeSolution(
                            code=content,
                            language=language,
                            explanation="Solution generated from screenshot analysis",
                            time_complexity="N/A",
                            space_complexity="N/A",
                            edge_cases=[],
                            alternative_approaches=None
                        )
                
                return content
            except Exception as fallback_error:
                logger.error(f"❌ LLM Service: Screenshot fallback also failed: {fallback_error}")
                # Return a basic error response
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
                
                # If content is already a CodeSolution object, return it
                if isinstance(content, CodeSolution):
                    return content
                
                # If content is a string (JSON), parse it
                if isinstance(content, str):
                    try:
                        content_dict = json.loads(content)
                        return CodeSolution(**content_dict)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        logger.warning("Failed to parse JSON response, falling back to raw")
                
                # If content is a dict, create CodeSolution object
                if isinstance(content, dict):
                    return CodeSolution(**content)
            
            # If none of the above work, try the raw response
            if hasattr(response, 'raw') and response.raw:
                if isinstance(response.raw, CodeSolution):
                    return response.raw
                if isinstance(response.raw, str):
                    try:
                        raw_dict = json.loads(response.raw)
                        return CodeSolution(**raw_dict)
                    except (json.JSONDecodeError, TypeError, ValueError):
                        pass
                if isinstance(response.raw, dict):
                    return CodeSolution(**response.raw)
            
            # Last resort: return response.raw as is (might be a string)
            logger.warning("Unable to parse structured response, returning raw response")
            return response.raw
            
        except Exception as e:
            logger.error(f"Error processing structured response: {e}")
            return response.raw
