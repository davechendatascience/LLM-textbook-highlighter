#!/usr/bin/env python3
"""
Test different ways to include actual Unicode mathematical symbols in PDF
"""
import os
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def test_unicode_symbol_methods():
    """Test different methods to include actual Unicode symbols like Σ, ∫, ∇"""
    
    print("Testing Unicode Mathematical Symbol Encoding Methods")
    print("=" * 60)
    
    os.makedirs("pdfs", exist_ok=True)
    timestamp = int(time.time())
    pdf_path = os.path.join("pdfs", f"unicode_symbols_test_{timestamp}.pdf")
    
    try:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        print("Testing different encoding methods for mathematical symbols...")
        
        # Page 1: Test basic Unicode
        y_pos = 750
        c.drawString(100, y_pos, "UNICODE MATHEMATICAL SYMBOLS TEST")
        y_pos -= 40
        
        # Method 1: Direct Unicode strings
        print("Method 1: Direct Unicode strings...")
        c.drawString(100, y_pos, "Method 1: Direct Unicode")
        y_pos -= 25
        
        try:
            # These are the actual Unicode symbols
            symbols_to_test = [
                ("Sigma", "Σ"),
                ("Integral", "∫"), 
                ("Nabla", "∇"),
                ("Partial", "∂"),
                ("Alpha", "α"),
                ("Beta", "β"),
                ("Pi", "π"),
                ("Plus-minus", "±"),
                ("Not equal", "≠"),
                ("Less equal", "≤"),
                ("Infinity", "∞")
            ]
            
            for name, symbol in symbols_to_test:
                try:
                    c.drawString(120, y_pos, f"{name}: {symbol}")
                    print(f"  SUCCESS: {name} ({symbol})")
                    y_pos -= 20
                except Exception as e:
                    c.drawString(120, y_pos, f"{name}: [FAILED]")
                    print(f"  FAILED: {name} - {e}")
                    y_pos -= 20
        except Exception as e:
            print(f"Method 1 completely failed: {e}")
        
        # Method 2: Unicode escape sequences
        y_pos -= 10
        c.drawString(100, y_pos, "Method 2: Unicode escapes")
        y_pos -= 25
        
        try:
            # Using Unicode code points
            unicode_tests = [
                ("Sigma", "\u03A3"),
                ("Integral", "\u222B"),
                ("Nabla", "\u2207"),
                ("Alpha", "\u03B1"),
                ("Pi", "\u03C0")
            ]
            
            for name, code in unicode_tests:
                try:
                    c.drawString(120, y_pos, f"{name}: {code}")
                    print(f"  SUCCESS: {name} (\\u{ord(code):04X})")
                    y_pos -= 20
                except Exception as e:
                    c.drawString(120, y_pos, f"{name}: [FAILED]")
                    print(f"  FAILED: {name} - {e}")
                    y_pos -= 20
        except Exception as e:
            print(f"Method 2 failed: {e}")
        
        # Method 3: Try with font specification
        y_pos -= 10
        c.drawString(100, y_pos, "Method 3: With font settings")
        y_pos -= 25
        
        try:
            # Try to use a font that supports Unicode
            # Most systems have Arial which supports many Unicode chars
            c.setFont("Helvetica", 12)
            c.drawString(120, y_pos, "Testing with Helvetica font:")
            y_pos -= 20
            
            test_string = "Math symbols: Σ ∫ ∇ ∂ α β π ± ≠ ∞"
            c.drawString(140, y_pos, test_string)
            print(f"  Attempted full symbol string with Helvetica")
            y_pos -= 25
            
        except Exception as e:
            print(f"Method 3 failed: {e}")
        
        # Method 4: Fallback - just test if we can make the PDF
        c.drawString(100, y_pos, "Method 4: ASCII fallback test")
        y_pos -= 20
        c.drawString(120, y_pos, "Sigma-like: S, Integral-like: f, Pi-like: n")
        
        c.save()
        
        print(f"\nPDF created: {pdf_path}")
        print(f"File size: {os.path.getsize(pdf_path)} bytes")
        
        # Now test extraction to see what we get
        print(f"\n--- Testing extraction from our Unicode PDF ---")
        import fitz
        
        doc = fitz.open(pdf_path)
        page = doc[0]
        extracted_text = page.get_text("text")
        
        print(f"Extracted text length: {len(extracted_text)} chars")
        
        # Look for our test symbols
        test_symbols = ['Σ', '∫', '∇', '∂', 'α', 'β', 'π', '±', '≠', '∞']
        found_symbols = []
        
        for symbol in test_symbols:
            if symbol in extracted_text:
                found_symbols.append(symbol)
        
        print(f"Symbols successfully round-tripped: {found_symbols}")
        print(f"Success rate: {len(found_symbols)}/{len(test_symbols)} = {len(found_symbols)/len(test_symbols)*100:.1f}%")
        
        # Show extracted text safely
        safe_extracted = extracted_text.encode('ascii', 'replace').decode('ascii')
        print(f"\nExtracted text (ASCII safe): '{safe_extracted[:300]}...'")
        
        doc.close()
        
        return pdf_path, len(found_symbols) > 0
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None, False

if __name__ == "__main__":
    pdf_file, symbols_worked = test_unicode_symbol_methods()
    
    if pdf_file:
        print(f"\nTest PDF created: {pdf_file}")
        if symbols_worked:
            print("SUCCESS: Some Unicode symbols worked in the round-trip!")
        else:
            print("PARTIAL: PDF created but Unicode symbols may not work")
        print("Open the PDF to see which encoding methods worked")
    else:
        print("FAILED: Could not create test PDF")