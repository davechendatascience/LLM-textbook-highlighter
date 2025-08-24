#!/usr/bin/env python3
"""
Test lightweight OCR alternatives for mathematical PDFs
"""
import os
import sys
from pathlib import Path

def test_lightweight_solutions():
    """Test various lightweight OCR approaches"""
    
    print("Testing Lightweight Mathematical OCR Solutions")
    print("=" * 55)
    
    # Find our test PDF
    pdfs_dir = Path("pdfs")
    fraction_pdfs = list(pdfs_dir.glob("proper_fractions_*.pdf"))
    if not fraction_pdfs:
        print("ERROR: Run test_proper_fractions.py first to create test PDF")
        return False
    
    pdf_path = max(fraction_pdfs, key=os.path.getctime)
    print(f"Testing with: {pdf_path}")
    
    results = {}
    
    # Test 1: EasyOCR (lightweight alternative)
    print(f"\n--- Test 1: EasyOCR ---")
    try:
        # Try to use EasyOCR if available
        import easyocr
        import fitz
        from PIL import Image
        
        print("EasyOCR found - testing...")
        
        # Convert PDF page to image
        doc = fitz.open(str(pdf_path))
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
        
        # Save as temporary image
        img_path = pdfs_dir / "temp_easyocr.png"
        pix.save(str(img_path))
        
        # Initialize EasyOCR (English)
        reader = easyocr.Reader(['en'])
        
        # Extract text
        result = reader.readtext(str(img_path))
        
        # Process results
        extracted_text = " ".join([text for (bbox, text, conf) in result if conf > 0.5])
        
        print(f"EasyOCR extracted {len(extracted_text)} characters")
        print(f"Sample: '{extracted_text[:100]}...'")
        
        # Check mathematical components
        math_components = ['1', '2', 'a', 'b', 'x+y', 'z-w', 'Sigma', 'Pi', 'Alpha']
        found = sum(1 for comp in math_components if comp.lower() in extracted_text.lower())
        print(f"Mathematical components: {found}/{len(math_components)}")
        
        results['easyocr'] = {'found': found, 'total': len(math_components), 'text_length': len(extracted_text)}
        
        # Cleanup
        os.unlink(img_path)
        doc.close()
        
    except ImportError:
        print("EasyOCR not installed - skipping")
        print("Install with: pip install easyocr")
        results['easyocr'] = None
    except Exception as e:
        print(f"EasyOCR failed: {e}")
        results['easyocr'] = None
    
    # Test 2: Tesseract (if available)
    print(f"\n--- Test 2: Tesseract OCR ---")
    try:
        import pytesseract
        from PIL import Image
        import fitz
        
        print("Tesseract found - testing...")
        
        # Convert PDF to image
        doc = fitz.open(str(pdf_path))
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        # Save as image
        img_path = pdfs_dir / "temp_tesseract.png"
        pix.save(str(img_path))
        
        # OCR with tesseract
        image = Image.open(str(img_path))
        tesseract_text = pytesseract.image_to_string(image)
        
        print(f"Tesseract extracted {len(tesseract_text)} characters")
        print(f"Sample: '{tesseract_text[:100].replace(chr(10), ' ')}...'")
        
        # Check components
        found = sum(1 for comp in math_components if comp.lower() in tesseract_text.lower())
        print(f"Mathematical components: {found}/{len(math_components)}")
        
        results['tesseract'] = {'found': found, 'total': len(math_components), 'text_length': len(tesseract_text)}
        
        # Cleanup
        os.unlink(img_path)
        doc.close()
        
    except ImportError:
        print("Tesseract not installed - skipping")
        print("Install with: pip install pytesseract")
        print("Also need tesseract binary: https://github.com/tesseract-ocr/tesseract")
        results['tesseract'] = None
    except Exception as e:
        print(f"Tesseract failed: {e}")
        results['tesseract'] = None
    
    # Test 3: Simple PyMuPDF image extraction + analysis
    print(f"\n--- Test 3: PyMuPDF Image Analysis ---")
    try:
        import fitz
        
        print("Analyzing PDF structure with PyMuPDF...")
        
        doc = fitz.open(str(pdf_path))
        page = doc[0]
        
        # Get text with position information
        text_dict = page.get_text("dict")
        
        print("Analyzing text positioning for mathematical layouts...")
        
        # Look for potential fractions (text above and below each other)
        text_positions = []
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            bbox = span["bbox"]
                            text_positions.append({
                                'text': text,
                                'x': bbox[0],
                                'y': bbox[1],
                                'width': bbox[2] - bbox[0],
                                'height': bbox[3] - bbox[1]
                            })
        
        # Find potential vertical fractions
        potential_fractions = []
        for i, item1 in enumerate(text_positions):
            for j, item2 in enumerate(text_positions):
                if i != j:
                    # Check if item1 is above item2 (similar x, different y)
                    x_overlap = abs(item1['x'] - item2['x']) < 20  # Similar x position
                    y_separation = item2['y'] - (item1['y'] + item1['height'])  # item2 below item1
                    
                    if x_overlap and 5 < y_separation < 50:  # Reasonable separation
                        potential_fractions.append(f"{item1['text']}/{item2['text']}")
        
        print(f"Potential fractions detected: {len(potential_fractions)}")
        for frac in potential_fractions[:5]:  # Show first 5
            print(f"  - {frac}")
        
        results['pymupdf_analysis'] = {
            'text_elements': len(text_positions),
            'potential_fractions': len(potential_fractions),
            'fractions': potential_fractions[:5]
        }
        
        doc.close()
        
    except Exception as e:
        print(f"PyMuPDF analysis failed: {e}")
        results['pymupdf_analysis'] = None
    
    # Test 4: Baseline fitz comparison
    print(f"\n--- Test 4: Baseline fitz ---")
    try:
        import fitz
        
        math_components = ['1', '2', 'a', 'b', 'x+y', 'z-w', 'Sigma', 'Pi', 'Alpha']
        
        doc = fitz.open(str(pdf_path))
        page = doc[0]
        fitz_text = page.get_text("text")
        
        found = sum(1 for comp in math_components if comp.lower() in fitz_text.lower())
        print(f"fitz baseline: {found}/{len(math_components)} components")
        
        results['fitz'] = {'found': found, 'total': len(math_components), 'text_length': len(fitz_text)}
        
        doc.close()
        
    except Exception as e:
        print(f"fitz baseline failed: {e}")
        results['fitz'] = None
    
    # Summary
    print(f"\n--- LIGHTWEIGHT OCR COMPARISON ---")
    for method, result in results.items():
        if result:
            if 'found' in result:
                accuracy = result['found'] / result['total'] * 100
                print(f"{method:20}: {result['found']}/{result['total']} components ({accuracy:.1f}%)")
            else:
                print(f"{method:20}: Analysis completed")
        else:
            print(f"{method:20}: Not available")
    
    return results

def recommend_lightweight_solution(results):
    """Recommend the best lightweight solution based on results"""
    
    print(f"\n--- RECOMMENDATIONS ---")
    
    # Check if any OCR method beat fitz baseline
    fitz_result = results.get('fitz')
    fitz_score = fitz_result.get('found', 0) if fitz_result else 0
    
    best_ocr = None
    best_score = 0
    
    for method in ['easyocr', 'tesseract']:
        result = results.get(method)
        if result and 'found' in result:
            score = result['found']
            if score > best_score:
                best_score = score
                best_ocr = method
    
    print(f"Baseline fitz performance: {fitz_score} components")
    
    if best_ocr and best_score >= fitz_score:
        print(f"RECOMMENDATION: {best_ocr} matches/beats fitz performance")
        print(f"  - Lightweight alternative available")
        print(f"  - Consider for mathematical layout understanding")
    else:
        print("RECOMMENDATION: Stick with fitz for now")
        print("  - Already excellent performance")
        print("  - OCR alternatives don't provide clear benefit")
        print("  - PyMuPDF analysis can detect potential fractions")
    
    pymupdf_result = results.get('pymupdf_analysis')
    if pymupdf_result:
        fractions = pymupdf_result.get('potential_fractions', 0)
        print(f"  - PyMuPDF detected {fractions} potential fraction layouts")
        print("  - This could be enhanced for spatial understanding")

if __name__ == "__main__":
    results = test_lightweight_solutions()
    recommend_lightweight_solution(results)