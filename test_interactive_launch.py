#!/usr/bin/env python3
"""
Test launching the interactive system to verify hybrid OCR integration
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_hybrid_ocr_import():
    """Test importing and initializing the hybrid OCR system"""
    try:
        print("Testing hybrid OCR import...")
        from hybrid_ocr_processor import HybridOCRProcessor
        
        processor = HybridOCRProcessor()
        
        print(f"General OCR: {processor.general_ocr}")
        print(f"Math processor available: {processor.math_processor is not None}")
        print(f"Math model available: {processor.math_model is not None}")
        
        return True
    except Exception as e:
        print(f"Error importing hybrid OCR: {e}")
        return False

def test_interactive_system_import():
    """Test importing the updated interactive system"""
    try:
        print("\nTesting interactive system import...")
        from interactive_highlighter import InteractivePDFHighlighter
        
        print("Interactive highlighter imported successfully")
        
        # Test creating instance (without actually launching GUI)
        # This will test the hybrid OCR initialization
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        highlighter = InteractivePDFHighlighter(root)
        
        print(f"Hybrid OCR processor initialized: {highlighter.hybrid_ocr_processor is not None}")
        print(f"General OCR available: {highlighter.hybrid_ocr_processor.general_ocr is not None}")
        print(f"Math OCR available: {highlighter.hybrid_ocr_processor.math_processor is not None}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"Error with interactive system: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run integration tests"""
    print("Testing Hybrid OCR Integration")
    print("=" * 40)
    
    success1 = test_hybrid_ocr_import()
    success2 = test_interactive_system_import()
    
    print("\n" + "=" * 40)
    if success1 and success2:
        print("✓ All integration tests passed!")
        print("The interactive system is ready with hybrid OCR support.")
    else:
        print("✗ Some tests failed - check the errors above")
    
    return success1 and success2

if __name__ == "__main__":
    main()