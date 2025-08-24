#!/usr/bin/env python3
"""
Test OCR integration in the interactive highlighter
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ocr_processor import get_ocr_processor
import fitz

def test_ocr_integration():
    """Test OCR processor integration"""
    
    print("Testing OCR Integration")
    print("=" * 30)
    
    # Test OCR processor availability
    ocr = get_ocr_processor()
    print(f"OCR Available: {ocr.is_available()}")
    
    if not ocr.is_available():
        print("EasyOCR not available - install with: pip install easyocr")
        return False
    
    # Find a test PDF
    pdfs_dir = "pdfs"
    if os.path.exists(pdfs_dir):
        pdf_files = [f for f in os.listdir(pdfs_dir) if f.endswith('.pdf')]
        if pdf_files:
            pdf_path = os.path.join(pdfs_dir, pdf_files[0])
            print(f"Testing with: {pdf_path}")
            
            try:
                # Open PDF and test extraction
                doc = fitz.open(pdf_path)
                page = doc[0]
                
                # Test on a portion of the page
                page_rect = page.rect
                test_rect = fitz.Rect(
                    page_rect.x0 + 100,
                    page_rect.y0 + 100, 
                    page_rect.x0 + 500,
                    page_rect.y0 + 300
                )
                
                print(f"\nTesting extraction from rect: {test_rect}")
                
                # Test with fallback method
                result = ocr.extract_with_fallback(page, test_rect)
                
                print(f"\nResults:")
                print(f"Method used: {result['method_used']}")
                print(f"Fitz text length: {result['fitz_length']}")
                print(f"OCR available: {result['ocr_available']}")
                
                if 'ocr_confidence' in result:
                    print(f"OCR confidence: {result['ocr_confidence']:.2f}")
                    print(f"OCR parts: {result['ocr_parts']}")
                
                recommended = result['recommended_text']
                print(f"\nRecommended text ({len(recommended)} chars):")
                # Safe display for Windows cp950
                safe_text = ""
                for char in recommended[:200]:
                    if ord(char) < 128:
                        safe_text += char
                    else:
                        safe_text += "?"
                print(f"'{safe_text}...'")
                
                # Test mathematical analysis
                math_analysis = ocr.analyze_mathematical_content(recommended)
                print(f"\nMathematical content analysis:")
                print(f"Has mathematical symbols: {math_analysis['has_math_symbols']}")
                print(f"Has fractions: {math_analysis['has_fractions']}")
                print(f"Complexity score: {math_analysis['complexity_score']}")
                
                doc.close()
                
                print(f"\nOCR integration test: PASSED")
                return True
                
            except Exception as e:
                print(f"Error testing OCR: {e}")
                return False
    
    print("No test PDF found in pdfs/ directory")
    return False

def test_interactive_highlighter_import():
    """Test that interactive highlighter can import OCR processor"""
    
    print(f"\nTesting Interactive Highlighter Integration")
    print("=" * 45)
    
    try:
        from interactive_highlighter import InteractivePDFHighlighter
        
        # Create instance (without starting GUI)
        highlighter = InteractivePDFHighlighter(root=None)
        
        print(f"OCR processor available: {highlighter.ocr_processor.is_available()}")
        print(f"Use OCR setting: {highlighter.use_ocr}")
        
        print(f"Interactive highlighter integration: PASSED")
        return True
        
    except Exception as e:
        print(f"Error testing interactive highlighter: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("OCR Integration Test Suite")
    print("=" * 40)
    
    success1 = test_ocr_integration()
    success2 = test_interactive_highlighter_import()
    
    print(f"\n" + "=" * 40)
    if success1 and success2:
        print("ALL TESTS PASSED! [SUCCESS]")
        print("OCR integration is working correctly")
    else:
        print("SOME TESTS FAILED! [ERROR]")
        print("Check the errors above")