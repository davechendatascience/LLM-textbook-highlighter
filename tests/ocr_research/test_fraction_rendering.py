#!/usr/bin/env python3
"""
Test mathematical fractions in PDF creation and extraction
"""
import os
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import fitz

def test_fraction_rendering():
    """Test different ways to represent mathematical fractions"""
    
    print("Testing Mathematical Fraction Rendering")
    print("=" * 45)
    
    os.makedirs("pdfs", exist_ok=True)
    timestamp = int(time.time())
    pdf_path = os.path.join("pdfs", f"fraction_test_{timestamp}.pdf")
    
    try:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        print("Creating PDF with various fraction representations...")
        
        y_pos = 750
        c.drawString(100, y_pos, "MATHEMATICAL FRACTIONS TEST")
        y_pos -= 40
        
        # Test different fraction representations
        fraction_tests = [
            # Simple inline fractions
            ("Simple inline", "1/2, 3/4, 5/8"),
            
            # Algebraic fractions
            ("Algebraic", "a/b, x/y, (a+b)/c"),
            
            # Complex numerators/denominators
            ("Complex", "(x+y)/(z-w), (a²+b²)/(2c)"),
            
            # Fractions with symbols
            ("With symbols", "π/2, α/β, ∑/n"),
            
            # Physics fractions
            ("Physics", "E/mc², ℏ/2π, kT/eV"),
            
            # Nested fractions
            ("Nested", "a/(b/c), (x/y)/(z/w)"),
            
            # Fractions in equations
            ("In equations", "y = (mx + b)/2, F = ma/t"),
            
            # Complex physics equations with fractions
            ("Complex physics", "v = √(2KE/m), E = mc²/√(1-v²/c²)"),
            
            # Mathematical constants as fractions
            ("Constants", "e^(iπ)/1 = -1, sin(π/6) = 1/2"),
            
            # Unicode fraction symbols (if supported)
            ("Unicode fractions", "½, ¼, ¾, ⅓, ⅔, ⅛")
        ]
        
        print(f"Testing {len(fraction_tests)} different fraction types...")
        
        for category, examples in fraction_tests:
            c.drawString(100, y_pos, f"{category}:")
            y_pos -= 20
            
            try:
                c.drawString(120, y_pos, examples)
                print(f"  SUCCESS: {category}")
                y_pos -= 25
            except Exception as e:
                c.drawString(120, y_pos, f"[ENCODING ERROR: {category}]")
                print(f"  ENCODING ERROR: {category} - {str(e)[:50]}...")
                y_pos -= 25
        
        c.save()
        
        print(f"\nPDF created: {pdf_path}")
        print(f"File size: {os.path.getsize(pdf_path)} bytes")
        
        # Test extraction
        print(f"\n--- Testing fraction extraction ---")
        doc = fitz.open(pdf_path)
        page = doc[0]
        extracted_text = page.get_text("text")
        
        print(f"Extracted text length: {len(extracted_text)} chars")
        
        # Check for specific fraction patterns
        fraction_patterns = [
            "1/2", "3/4", "a/b", "π/2", "E/mc", "x/y", 
            "½", "¼", "¾", "+b²", "√", "²"
        ]
        
        found_patterns = []
        for pattern in fraction_patterns:
            if pattern in extracted_text:
                found_patterns.append(pattern)
        
        print(f"Fraction patterns found in extraction: {len(found_patterns)}/{len(fraction_patterns)}")
        print(f"Found patterns: {found_patterns}")
        
        # Display extracted text safely
        print(f"\nSample extracted text:")
        safe_text = extracted_text.replace('\n', ' ').strip()
        # Replace problematic Unicode with ASCII equivalents for display
        display_text = ""
        for char in safe_text[:300]:
            if ord(char) < 128:
                display_text += char
            else:
                display_text += f"[U{ord(char):04X}]"
        
        print(f"'{display_text}...'")
        
        doc.close()
        
        # Analysis
        print(f"\n--- ANALYSIS ---")
        print(f"PDF Creation: SUCCESS ({os.path.getsize(pdf_path)} bytes)")
        print(f"Text Extraction: SUCCESS ({len(extracted_text)} chars)")
        print(f"Fraction Pattern Preservation: {len(found_patterns)/len(fraction_patterns)*100:.1f}%")
        
        if len(found_patterns) >= len(fraction_patterns) * 0.7:
            print("RESULT: Fraction handling works well!")
            success = True
        elif len(found_patterns) >= len(fraction_patterns) * 0.4:
            print("RESULT: Fraction handling partially works")
            success = True
        else:
            print("RESULT: Fraction handling has issues")
            success = False
            
        return pdf_path, success
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None, False

if __name__ == "__main__":
    pdf_file, success = test_fraction_rendering()
    
    if pdf_file:
        print(f"\nTest PDF created: {pdf_file}")
        print("Open it to check fraction rendering quality!")
        
        if success:
            print("Mathematical fractions appear to work in PDF creation/extraction")
        else:
            print("There may be issues with complex fraction rendering")
    else:
        print("Could not create fraction test PDF")