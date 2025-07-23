#!/usr/bin/env python3
"""
Test script to verify PDF processing functionality.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from interview_corvus.core.file_processor import FileProcessor

def test_pdf_support():
    """Test PDF processing capabilities."""
    processor = FileProcessor()
    
    # Test if PDF files are recognized as supported
    test_pdf_path = "test.pdf"
    is_supported = processor.is_supported_file(test_pdf_path)
    
    print(f"PDF support available: {is_supported}")
    print(f"Supported extensions: {sorted(processor.SUPPORTED_EXTENSIONS)}")
    
    # Check PDF processing libraries
    try:
        import PyPDF2
        print("✅ PyPDF2 is available")
    except ImportError:
        print("❌ PyPDF2 is not available")
    
    try:
        import pdfplumber
        print("✅ pdfplumber is available")
    except ImportError:
        print("❌ pdfplumber is not available")

if __name__ == "__main__":
    test_pdf_support()
