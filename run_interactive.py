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
    print("LLM Textbook Highlighter - Interactive Mode with Hybrid OCR")
    print("=" * 60)
    
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
    
    # Check Hybrid OCR availability
    from hybrid_ocr_processor import HybridOCRProcessor
    hybrid_ocr = HybridOCRProcessor()
    
    print("[Hybrid OCR] Checking availability...")
    if hybrid_ocr.general_ocr:
        ocr_type = hybrid_ocr.general_ocr if isinstance(hybrid_ocr.general_ocr, str) else "EasyOCR"
        print(f"[Hybrid OCR] General OCR ({ocr_type}) available")
        
        if hybrid_ocr.math_processor and hybrid_ocr.math_model:
            print("[Hybrid OCR] Math OCR (Pix2Text) available")
            print("             Two-stage OCR: General OCR + specialized math enhancement")
        else:
            print("[Hybrid OCR] Math OCR not available - general OCR only")
            print("             Install with: pip install transformers>=4.37.0 optimum[onnxruntime]")
    else:
        print("[Hybrid OCR] No OCR engines available")
        print("             Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
        print("             Or install EasyOCR: pip install easyocr")
        print("             Will use traditional PyMuPDF text extraction")
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