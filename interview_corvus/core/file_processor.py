"""Simple file processor for extracting content and saving to user settings."""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from loguru import logger

# PDF processing imports
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not available. PDF files will not be supported.")


class FileProcessor:
    """Simple service for processing files and saving content to user settings."""

    def __init__(self, settings_file_path: str = "user_settings.json"):
        """Initialize the file processor.
        
        Args:
            settings_file_path: Path to the user settings JSON file
        """
        self.app_data_dir = Path.home() / ".interview_corvus"
        self.app_data_dir.mkdir(exist_ok=True)  # Create directory if it doesn't exist
        
        # If a full path is provided, use it; otherwise use the default location
        if os.path.isabs(settings_file_path):
            self.settings_file_path = settings_file_path
        else:
            self.settings_file_path = self.app_data_dir / settings_file_path
            
        self.max_files = 2
        
    def extract_text_from_file(self, file_path: str) -> Optional[str]:
        """Extract text content from a single file.
        
        Args:
            file_path: Path to the file to extract text from
            
        Returns:
            Extracted text content or None if extraction failed
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml']:
                return self._extract_plain_text(file_path)
            else:
                logger.warning(f"Unsupported file extension: {file_extension}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None
    
    def _extract_pdf_text(self, file_path: str) -> Optional[str]:
        """Extract text from PDF file."""
        if not PDF_AVAILABLE:
            logger.error("PyPDF2 not available for PDF processing")
            return None
            
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                for page in pdf_reader.pages:
                    text_content.append(page.extract_text())
                
                return '\n'.join(text_content)
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {e}")
            return None
    
    def _extract_plain_text(self, file_path: str) -> Optional[str]:
        """Extract text from plain text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error reading text file {file_path}: {e}")
                return None
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return None
    
    def process_files_and_save(self, file_paths: List[str]) -> bool:
        """Process uploaded files and save content to user settings.
        
        Args:
            file_paths: List of file paths to process (max 2 files)
            
        Returns:
            True if processing and saving was successful, False otherwise
        """
        if len(file_paths) > self.max_files:
            logger.error(f"Too many files provided. Maximum allowed: {self.max_files}")
            return False
        
        if not file_paths:
            logger.error("No files provided for processing")
            return False
        
        # Extract content from all files
        extracted_content = {}
        
        for i, file_path in enumerate(file_paths):
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                continue
                
            content = self.extract_text_from_file(file_path)
            if content:
                file_name = Path(file_path).name
                extracted_content[f"file_{i+1}"] = {
                    "filename": file_name,
                    "content": content,
                    "file_path": file_path
                }
            else:
                logger.warning(f"Failed to extract content from: {file_path}")
        
        if not extracted_content:
            logger.error("No content could be extracted from any files")
            return False
        
        # Save to user settings
        return self._save_to_user_settings(extracted_content)
    
    def _save_to_user_settings(self, extracted_content: Dict[str, Any]) -> bool:
        """Save extracted content to user settings JSON file.
        
        Args:
            extracted_content: Dictionary containing extracted file content
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            # Load existing settings or create new ones
            settings = {}
            if os.path.exists(self.settings_file_path):
                try:
                    with open(self.settings_file_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON in settings file, creating new one")
                    settings = {}
            
            # Add uploaded files content
            settings["uploaded_files"] = extracted_content
            
            # Save back to file
            with open(self.settings_file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved {len(extracted_content)} files to {self.settings_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to user settings: {e}")
            return False
    
    def get_saved_files_content(self) -> Optional[Dict[str, Any]]:
        """Get previously saved files content from user settings.
        
        Returns:
            Dictionary containing saved file content or None if not found
        """
        try:
            if not os.path.exists(self.settings_file_path):
                return None
                
            with open(self.settings_file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            return settings.get("uploaded_files")
            
        except Exception as e:
            logger.error(f"Error reading saved files content: {e}")
            return None
    
    def clear_saved_files(self) -> bool:
        """Clear saved files content from user settings.
        
        Returns:
            True if clearing was successful, False otherwise
        """
        try:
            if not os.path.exists(self.settings_file_path):
                return True
                
            with open(self.settings_file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            if "uploaded_files" in settings:
                del settings["uploaded_files"]
                
                with open(self.settings_file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
            
            logger.info("Successfully cleared saved files content")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing saved files content: {e}")
            return False
