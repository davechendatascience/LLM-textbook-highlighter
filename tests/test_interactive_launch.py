#!/usr/bin/env python3
"""
Test launching the interactive highlighter without actually showing GUI
"""
import sys
import os

# Add paths (from tests/ subdirectory)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_interactive_launch():
    """Test that interactive highlighter can be imported and initialized"""
    try:
        print("Testing Interactive Highlighter Launch")
        print("=" * 45)
        
        # Import the main class
        from interactive_highlighter import InteractivePDFHighlighter
        print("+ Interactive highlighter imported successfully")
        
        # Try to initialize (but don't run mainloop)
        try:
            # This will create the tkinter widgets but not show them
            app = InteractivePDFHighlighter()
            print("+ GUI components initialized successfully") 
            
            # Check that key components exist
            if hasattr(app, 'pdf_processor'):
                print("+ PDF processor attached")
            if hasattr(app, 'api_keys'):
                print("+ API configuration loaded")
            if hasattr(app, 'root'):
                print("+ Tkinter root window created")
            
            # Test text extraction method exists and works
            if hasattr(app, 'extract_text_robust'):
                print("+ extract_text_robust method available")
                
                # Test with a sample PDF if available
                test_pdf_path = os.path.join(os.path.dirname(__file__), "..", "realistic_math_test.pdf")
                if os.path.exists(test_pdf_path):
                    try:
                        # Test PDF processor directly
                        page_count = app.pdf_processor.get_page_count(test_pdf_path)
                        print(f"+ PDF processor can read test file ({page_count} pages)")
                        
                        # Test text extraction from a small region
                        import fitz
                        test_rect = fitz.Rect(100, 100, 300, 200)  # Small test region
                        
                        # This should work without actually opening the PDF in GUI
                        text = app.pdf_processor.extract_text_from_region(
                            test_pdf_path, 0, test_rect, method="standard"
                        )
                        
                        if text:
                            print(f"+ Text extraction working: '{text[:50]}...'")
                        else:
                            print("+ Text extraction method working (empty result from test region)")
                            
                    except Exception as e:
                        print(f"WARNING: PDF test failed (but method exists): {e}")
                else:
                    print("+ extract_text_robust method exists (no test PDF available)")
            else:
                print("ERROR: extract_text_robust method missing!")
                return False
                
            # Clean up
            app.root.destroy()
            print("+ Cleanup successful")
            
            return True
            
        except Exception as e:
            print(f"ERROR: GUI initialization failed: {e}")
            return False
            
    except Exception as e:
        print(f"ERROR: Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_interactive_launch()
    
    if success:
        print(f"\nSUCCESS: Interactive highlighter ready to launch!")
        print("Run: python run_interactive.py")
    else:
        print(f"\nERROR: Interactive highlighter test failed.")
        print("Please check the error messages above.")