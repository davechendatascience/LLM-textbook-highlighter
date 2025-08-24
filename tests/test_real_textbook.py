#!/usr/bin/env python3
"""
Test text extraction with real textbook (classical mechanics)
"""
import sys
import os
import fitz

# Add paths (from tests/ subdirectory)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_textbook_extraction():
    """Test extraction with the actual classical mechanics textbook"""
    
    textbook_path = os.path.join(os.path.dirname(__file__), "..", "classical mechanics john taylor.pdf")
    
    if not os.path.exists(textbook_path):
        print(f"ERROR: Textbook not found at {textbook_path}")
        return False
    
    print("Testing Real Textbook Extraction")
    print("=" * 45)
    print(f"Using: {textbook_path}")
    
    try:
        # Import the PDF processor
        from pdf_processor import PDFProcessor
        processor = PDFProcessor(use_advanced_extraction=True)
        
        # Test basic page access
        doc = fitz.open(textbook_path)
        page_count = len(doc)
        print(f"+ Textbook has {page_count} pages")
        
        # Test on first few pages to find content
        for page_num in range(min(5, page_count)):
            page = doc[page_num]
            
            # Get some text from the page to see what we're working with
            full_page_text = page.get_text("text")
            
            if len(full_page_text) > 100:  # Page has substantial content
                print(f"\n--- Testing Page {page_num + 1} ---")
                print(f"Full page text length: {len(full_page_text)} chars")
                print(f"Sample: '{full_page_text[:100]}...'")
                
                # Test different sized rectangles
                page_rect = page.rect
                test_regions = [
                    # Small region (top-left corner)
                    fitz.Rect(50, 50, 250, 150),
                    # Medium region (center)
                    fitz.Rect(100, 200, 400, 400),
                    # Large region (most of page)
                    fitz.Rect(50, 100, page_rect.width-50, page_rect.height-100)
                ]
                
                for i, test_rect in enumerate(test_regions):
                    print(f"\nRegion {i+1}: {test_rect}")
                    
                    # Test standard extraction
                    standard_text = page.get_text("text", clip=test_rect).strip()
                    print(f"Standard: '{standard_text[:80]}...' ({len(standard_text)} chars)")
                    
                    # Test our processor
                    try:
                        processor_text = processor.extract_text_from_region(
                            textbook_path, page_num, test_rect, method="standard"
                        )
                        print(f"Processor: '{processor_text[:80]}...' ({len(processor_text)} chars)")
                        
                        # Compare results
                        if standard_text == processor_text:
                            print("✓ Results match")
                        else:
                            print("! Results differ")
                            
                    except Exception as e:
                        print(f"✗ Processor failed: {e}")
                
                break  # Only test first content page
        
        doc.close()
        
        # Test the interactive highlighter method
        print(f"\n--- Testing Interactive Highlighter ---")
        from interactive_highlighter import InteractivePDFHighlighter
        
        # Create a test instance (but don't show GUI)
        app = InteractivePDFHighlighter()
        
        # Simulate loading the PDF
        app.pdf_doc = fitz.open(textbook_path)
        app.pdf_path = textbook_path
        app.current_page = 1  # Use page 2 (index 1) which has content
        
        # Test the extract_text_robust method
        page = app.pdf_doc[1]  # Page 2
        test_rect = fitz.Rect(100, 200, 400, 400)
        
        print(f"Testing extract_text_robust on page 1, rect {test_rect}")
        extracted = app.extract_text_robust(page, test_rect)
        print(f"Result: '{extracted[:100]}...' ({len(extracted)} chars)")
        
        # Cleanup
        app.pdf_doc.close()
        app.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_textbook_extraction()
    
    if success:
        print(f"\nSUCCESS: Real textbook extraction test completed")
    else:
        print(f"\nERROR: Real textbook extraction test failed")