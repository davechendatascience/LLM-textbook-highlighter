#!/usr/bin/env python3
"""
Test OCR-based extraction for mathematical PDFs with vertical fractions
"""
import os
import sys
import time
from pathlib import Path

def test_fitz_vs_ocr_extraction():
    """Compare fitz vs OCR extraction on our test PDF with vertical fractions"""
    
    print("OCR vs Traditional Text Extraction Comparison")
    print("=" * 55)
    
    # Use our previously created proper fractions PDF
    pdfs_dir = Path("pdfs")
    if not pdfs_dir.exists():
        print("ERROR: No pdfs directory found. Run test_proper_fractions.py first.")
        return False
    
    # Find the most recent proper fractions PDF
    fraction_pdfs = list(pdfs_dir.glob("proper_fractions_*.pdf"))
    if not fraction_pdfs:
        print("ERROR: No proper fractions PDF found. Run test_proper_fractions.py first.")
        return False
    
    # Use the most recent one
    pdf_path = max(fraction_pdfs, key=os.path.getctime)
    print(f"Testing PDF: {pdf_path}")
    
    # Test 1: Traditional fitz extraction
    print(f"\n--- Test 1: Traditional fitz extraction ---")
    try:
        import fitz
        
        doc = fitz.open(str(pdf_path))
        page = doc[0]
        fitz_text = page.get_text("text").strip()
        
        print(f"fitz extracted {len(fitz_text)} characters")
        print("Sample fitz output (first 200 chars):")
        safe_fitz = ""
        for char in fitz_text[:200]:
            if ord(char) < 127:
                safe_fitz += char
            else:
                safe_fitz += "?"
        print(f"'{safe_fitz}...'")
        
        # Count mathematical components
        math_components = ['1', '2', 'a', 'b', 'x+y', 'z-w', 'mv', 'Sigma', 'Pi', 'Alpha']
        fitz_found = sum(1 for comp in math_components if comp in fitz_text)
        print(f"Mathematical components found by fitz: {fitz_found}/{len(math_components)}")
        
        doc.close()
        
    except Exception as e:
        print(f"fitz extraction failed: {e}")
        fitz_text = ""
        fitz_found = 0
    
    # Test 2: Try OCR extraction if available
    print(f"\n--- Test 2: OCR-based extraction ---")
    try:
        # Try to import pix2text
        from pix2text import Pix2Text
        
        print("Initializing Pix2Text OCR...")
        p2t = Pix2Text.from_config()
        
        print("Running OCR on PDF...")
        # Convert PDF to markdown with OCR
        ocr_result = p2t(str(pdf_path))
        
        print(f"OCR extracted {len(ocr_result)} characters")
        print("Sample OCR output (first 200 chars):")
        safe_ocr = ""
        for char in ocr_result[:200]:
            if ord(char) < 127:
                safe_ocr += char
            else:
                safe_ocr += "?"
        print(f"'{safe_ocr}...'")
        
        # Count mathematical components in OCR result
        ocr_found = sum(1 for comp in math_components if comp in ocr_result)
        print(f"Mathematical components found by OCR: {ocr_found}/{len(math_components)}")
        
        # Check for LaTeX mathematical notation
        latex_indicators = ['\\frac', '\\sum', '\\int', '\\alpha', '\\beta', '\\pi', '\\sigma']
        latex_found = sum(1 for indicator in latex_indicators if indicator in ocr_result)
        print(f"LaTeX mathematical notation found: {latex_found}/{len(latex_indicators)}")
        
        # Save OCR result for inspection
        ocr_output_path = pdfs_dir / f"ocr_result_{int(time.time())}.md"
        with open(ocr_output_path, 'w', encoding='utf-8') as f:
            f.write(ocr_result)
        print(f"OCR result saved to: {ocr_output_path}")
        
        ocr_success = True
        
    except ImportError:
        print("Pix2Text not available - skipping OCR test")
        print("Install with: pip install pix2text[vlm]")
        ocr_result = ""
        ocr_found = 0
        latex_found = 0
        ocr_success = False
        
    except Exception as e:
        print(f"OCR extraction failed: {e}")
        import traceback
        traceback.print_exc()
        ocr_result = ""
        ocr_found = 0
        latex_found = 0
        ocr_success = False
    
    # Test 3: Alternative OCR if pix2text fails
    if not ocr_success:
        print(f"\n--- Test 3: Alternative OCR approach ---")
        try:
            # Try with basic tesseract if available
            import pytesseract
            from PIL import Image
            import fitz
            
            print("Trying pytesseract OCR...")
            
            # Convert PDF page to image
            doc = fitz.open(str(pdf_path))
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img_data = pix.pil_tobytes(format="PNG")
            
            # Save as image temporarily
            img_path = pdfs_dir / "temp_ocr_image.png"
            with open(img_path, 'wb') as f:
                f.write(img_data)
            
            # OCR the image
            image = Image.open(img_path)
            tesseract_text = pytesseract.image_to_string(image)
            
            print(f"Tesseract extracted {len(tesseract_text)} characters")
            tesseract_found = sum(1 for comp in math_components if comp in tesseract_text)
            print(f"Mathematical components found by tesseract: {tesseract_found}/{len(math_components)}")
            
            # Cleanup
            os.unlink(img_path)
            doc.close()
            
            alt_ocr_success = True
            
        except Exception as e:
            print(f"Alternative OCR failed: {e}")
            alt_ocr_success = False
    
    # Summary comparison
    print(f"\n--- EXTRACTION COMPARISON RESULTS ---")
    print(f"Traditional fitz: {fitz_found}/{len(math_components)} components ({fitz_found/len(math_components)*100:.1f}%)")
    
    if ocr_success:
        print(f"Pix2Text OCR: {ocr_found}/{len(math_components)} components ({ocr_found/len(math_components)*100:.1f}%)")
        print(f"LaTeX notation: {latex_found}/{len(latex_indicators)} indicators ({latex_found/len(latex_indicators)*100:.1f}%)")
        
        if ocr_found > fitz_found or latex_found > 0:
            print("RESULT: OCR shows improvement over traditional extraction!")
            print("OCR can potentially handle vertical fractions and mathematical layout better.")
        else:
            print("RESULT: OCR did not show clear improvement over fitz")
            
    else:
        print("OCR: Not tested (installation issues)")
        print("RESULT: Only fitz extraction was tested")
    
    return ocr_success

def test_ocr_with_controlled_pdf():
    """Create a PDF specifically designed to test OCR capabilities"""
    
    print(f"\n--- Creating OCR-optimized test PDF ---")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        timestamp = int(time.time())
        pdf_path = Path("pdfs") / f"ocr_test_{timestamp}.pdf"
        
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        
        # Create content specifically challenging for traditional extraction
        # but good for OCR
        y_pos = 750
        
        c.drawString(100, y_pos, "OCR MATHEMATICAL EXTRACTION TEST")
        y_pos -= 40
        
        # Test 1: Large, clear vertical fractions
        c.drawString(100, y_pos, "Large Vertical Fractions:")
        y_pos -= 30
        
        # Create bigger, clearer fractions for OCR
        fractions = [
            ("a", "b", 150),
            ("x+1", "y-2", 220),
            ("sin(x)", "cos(x)", 300)
        ]
        
        for numerator, denominator, x_pos in fractions:
            # Numerator
            c.setFont("Helvetica", 14)
            c.drawString(x_pos, y_pos, numerator)
            # Fraction line
            line_width = max(len(numerator), len(denominator)) * 8
            c.line(x_pos - 5, y_pos - 8, x_pos + line_width, y_pos - 8)
            # Denominator  
            c.drawString(x_pos, y_pos - 20, denominator)
        
        y_pos -= 60
        
        # Test 2: Mathematical equations with symbols
        c.setFont("Helvetica", 12)
        c.drawString(100, y_pos, "Mathematical Expressions:")
        y_pos -= 25
        c.drawString(120, y_pos, "Quadratic: ax² + bx + c = 0")
        y_pos -= 20
        c.drawString(120, y_pos, "Integration: ∫f(x)dx")
        y_pos -= 20
        c.drawString(120, y_pos, "Summation: Σ(i=1 to n) xi")
        y_pos -= 20
        c.drawString(120, y_pos, "Greek: α β γ δ π σ ω")
        
        c.save()
        
        print(f"OCR-optimized PDF created: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"Failed to create OCR test PDF: {e}")
        return None

if __name__ == "__main__":
    print("Starting OCR vs Traditional Extraction Test...")
    
    # First test with existing fraction PDF
    success = test_fitz_vs_ocr_extraction()
    
    # Create and test with OCR-optimized PDF
    ocr_pdf = test_ocr_with_controlled_pdf()
    
    if ocr_pdf and success:
        print(f"\nCreated OCR-optimized test PDF: {ocr_pdf}")
        print("Rerun this script to test OCR on the optimized PDF too!")
    
    print(f"\nOCR extraction testing completed!")