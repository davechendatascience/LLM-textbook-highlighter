#!/usr/bin/env python3
"""
Launch the interactive PDF highlighter GUI
"""
import sys
import os

# Add src and utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from config import load_secrets, get_available_apis
from interactive_highlighter import InteractivePDFHighlighter

def main():
    """Launch the interactive highlighter"""
    print("LLM Textbook Highlighter - Interactive Mode with OCR")
    print("=" * 55)
    
    # Check API availability
    secrets = load_secrets()
    available_apis = get_available_apis()
    
    if not available_apis:
        print("Warning: No API keys found in secrets.json")
        print("Interactive features will be limited to text extraction only")
        print()
    else:
        print(f"Available APIs: {', '.join(available_apis)}")
        print()
    
    # Check OCR availability
    from ocr_processor import get_ocr_processor
    ocr = get_ocr_processor()
    if ocr.is_available():
        print("[OCR] EasyOCR available for enhanced mathematical text extraction")
        print("      Toggle OCR in the toolbar to enable for complex mathematical content")
    else:
        print("[OCR] EasyOCR not available - install with: pip install easyocr")
        print("      Will use traditional PyMuPDF text extraction")
    print()
    
    # Launch the GUI
    try:
        app = InteractivePDFHighlighter()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Error launching application: {e}")
        print("Please check your Python environment and dependencies")

if __name__ == "__main__":
    main()