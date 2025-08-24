#!/usr/bin/env python3
"""
Test proper mathematical fractions with numerator above denominator
"""
import os
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import fitz

def test_proper_fraction_rendering():
    """Test vertical fractions (numerator above denominator) and font rendering"""
    
    print("Testing Proper Mathematical Fractions (Vertical Layout)")
    print("=" * 60)
    
    os.makedirs("pdfs", exist_ok=True)
    timestamp = int(time.time())
    pdf_path = os.path.join("pdfs", f"proper_fractions_{timestamp}.pdf")
    
    try:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        print("Creating PDF with vertical fractions and testing font rendering...")
        
        y_pos = 750
        c.drawString(100, y_pos, "PROPER MATHEMATICAL FRACTIONS TEST")
        y_pos -= 40
        
        # Test 1: Check which characters actually render (not black boxes)
        c.drawString(100, y_pos, "Character Rendering Test:")
        y_pos -= 25
        
        # Test basic symbols that should work
        safe_symbols = [
            ("Plus", "+"),
            ("Minus", "-"), 
            ("Times", "*"),
            ("Equals", "="),
            ("Parentheses", "()"),
            ("Letters", "abcxyz"),
            ("Numbers", "123456")
        ]
        
        for name, symbol in safe_symbols:
            c.drawString(120, y_pos, f"{name}: {symbol}")
            y_pos -= 18
        
        y_pos -= 10
        c.drawString(100, y_pos, "Potentially problematic Unicode:")
        y_pos -= 25
        
        # Test Unicode symbols that might render as black boxes
        unicode_tests = [
            ("Sigma", "Σ", "S"),           # Fallback to S
            ("Pi", "π", "pi"),             # Fallback to pi
            ("Alpha", "α", "alpha"),       # Fallback to alpha  
            ("Integral", "∫", "integral"), # Fallback to integral
            ("Sqrt", "√", "sqrt"),         # Fallback to sqrt
            ("Half", "½", "1/2"),          # Fallback to 1/2
            ("Quarter", "¼", "1/4"),       # Fallback to 1/4
        ]
        
        for name, unicode_char, fallback in unicode_tests:
            try:
                # Try Unicode first
                c.drawString(120, y_pos, f"{name}: {unicode_char} (or {fallback})")
                print(f"  Attempted: {name} with Unicode and fallback")
            except:
                # Use fallback only
                c.drawString(120, y_pos, f"{name}: {fallback}")
                print(f"  Used fallback for: {name}")
            y_pos -= 18
        
        y_pos -= 20
        
        # Test 2: Vertical fractions using positioning
        c.drawString(100, y_pos, "Vertical Fractions (numerator above denominator):")
        y_pos -= 30
        
        fraction_tests = [
            ("Simple", "1", "2"),
            ("Variables", "a", "b"), 
            ("Complex num", "x+y", "z-w"),
            ("With powers", "a²+b²", "2c"),
            ("Physics", "mv²", "2"),
            ("Constants", "πr²", "4")
        ]
        
        x_start = 120
        for i, (name, numerator, denominator) in enumerate(fraction_tests):
            x_pos = x_start + (i * 80)  # Space them horizontally
            
            # Draw the fraction name below
            c.drawString(x_pos, y_pos - 50, name)
            
            # Draw numerator above
            c.drawString(x_pos + 5, y_pos - 10, numerator)
            
            # Draw horizontal line (fraction bar)
            line_width = max(len(numerator), len(denominator)) * 6 + 10
            c.line(x_pos, y_pos - 18, x_pos + line_width, y_pos - 18)
            
            # Draw denominator below
            c.drawString(x_pos + 5, y_pos - 30, denominator)
            
            print(f"  Created vertical fraction: fraction_{i+1}")
        
        y_pos -= 80
        
        # Test 3: Mixed expressions with vertical fractions
        c.drawString(100, y_pos, "Complex expressions with vertical fractions:")
        y_pos -= 40
        
        # Quadratic formula parts
        c.drawString(120, y_pos, "Quadratic formula: x = ")
        
        # First fraction: -b / 2a
        c.drawString(220, y_pos - 5, "-b")
        c.line(220, y_pos - 13, 245, y_pos - 13)
        c.drawString(220, y_pos - 25, "2a")
        
        c.drawString(250, y_pos - 10, " ± ")
        
        # Second fraction: sqrt(discriminant) / 2a
        c.drawString(270, y_pos - 5, "√(b²-4ac)")
        c.line(270, y_pos - 13, 340, y_pos - 13)
        c.drawString(290, y_pos - 25, "2a")
        
        print("  Created quadratic formula with proper fractions")
        
        y_pos -= 60
        
        # Test 4: Physics equations with proper fractions
        c.drawString(100, y_pos, "Physics equations:")
        y_pos -= 30
        
        # Kinetic energy: KE = (1/2)mv²
        c.drawString(120, y_pos, "Kinetic Energy: KE = ")
        c.drawString(230, y_pos + 5, "1")
        c.line(230, y_pos - 3, 240, y_pos - 3)
        c.drawString(230, y_pos - 15, "2")
        c.drawString(245, y_pos, "mv²")
        
        print("  Created kinetic energy formula")
        
        c.save()
        
        print(f"\nPDF created: {pdf_path}")
        print(f"File size: {os.path.getsize(pdf_path)} bytes")
        
        # Test extraction
        print(f"\n--- Testing extraction of vertical fractions ---")
        doc = fitz.open(pdf_path)
        page = doc[0]
        extracted_text = page.get_text("text")
        
        print(f"Extracted text length: {len(extracted_text)} chars")
        
        # Check if we can find components of our fractions
        fraction_components = [
            "1", "2", "a", "b", "x+y", "z-w", "mv", "πr", 
            "Simple", "Variables", "Complex", "Physics"
        ]
        
        found_components = []
        for component in fraction_components:
            if component in extracted_text:
                found_components.append(component)
        
        print(f"Fraction components found: {len(found_components)}/{len(fraction_components)}")
        print(f"Found: {found_components}")
        
        # Show sample extracted text
        print(f"\nSample extracted text (first 200 chars):")
        clean_text = ""
        for char in extracted_text[:200]:
            if ord(char) < 127:
                clean_text += char
            else:
                clean_text += "?"
        print(f"'{clean_text}...'")
        
        doc.close()
        
        success = len(found_components) >= len(fraction_components) * 0.6
        return pdf_path, success
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None, False

if __name__ == "__main__":
    pdf_file, success = test_proper_fraction_rendering()
    
    if pdf_file:
        print(f"\nProper fractions test PDF: {pdf_file}")
        print("Open this PDF to check:")
        print("1. Are there black boxes where symbols should be?")
        print("2. Do the vertical fractions (numerator above denominator) look correct?")
        print("3. Are complex expressions like quadratic formula readable?")
        
        if success:
            print("\nRESULT: Vertical fraction rendering appears to work")
        else:
            print("\nRESULT: May have issues with vertical fraction rendering")
    else:
        print("Could not create proper fractions test")