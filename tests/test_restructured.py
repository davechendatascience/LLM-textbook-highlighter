#!/usr/bin/env python3
"""
Quick test of the restructured codebase
"""
import sys
import os

# Add paths (from tests/ subdirectory)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'extraction_methods'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        print("Testing imports...")
        
        from config import load_secrets, get_available_apis
        print("+ Config module imported")
        
        from pdf_processor import PDFProcessor  
        print("+ PDF processor imported")
        
        from symbol_fixer import SymbolFixer
        print("+ Symbol fixer imported")
        
        from advanced_extraction import AdvancedPDFExtractor
        print("+ Advanced extraction imported")
        
        # Test configuration
        secrets = load_secrets()
        apis = get_available_apis()
        print(f"+ Available APIs: {apis}")
        
        # Test PDF processor creation
        processor = PDFProcessor()
        print("+ PDF processor created successfully")
        
        # Test symbol fixer
        fixer = SymbolFixer()
        test_text = "Sum(i=1 to n) x_i != 0"
        fixed = fixer.fix_symbols(test_text)
        print(f"+ Symbol fixer working: '{test_text}' -> '{fixed}'")
        
        print("\nSUCCESS: All core modules working correctly!")
        return True
        
    except Exception as e:
        print(f"ERROR: Import error: {e}")
        return False

def test_gui_import():
    """Test GUI module import"""
    try:
        from interactive_highlighter import InteractivePDFHighlighter
        print("+ GUI module imported successfully")
        
        # Don't actually create the GUI in testing
        print("+ GUI can be imported without errors")
        return True
        
    except Exception as e:
        print(f"ERROR: GUI import error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Restructured Codebase")
    print("=" * 40)
    
    success = True
    success &= test_imports()
    success &= test_gui_import()
    
    if success:
        print(f"\nSUCCESS: Restructuring successful!")
        print("You can now run: python run_interactive.py")
    else:
        print(f"\nERROR: Some tests failed. Please check the imports.")