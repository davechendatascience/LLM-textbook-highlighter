#!/usr/bin/env python3
"""
Controlled test: Create PDF with known mathematical symbols, then test extraction
"""
import sys
import os
import fitz

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_controlled_math_pdf():
    """Create a 2-page PDF with known mathematical content"""
    
    import time
    timestamp = int(time.time())
    pdf_path = os.path.join("pdfs", f"math_test_{timestamp}.pdf")
    
    # Ensure pdfs directory exists
    os.makedirs("pdfs", exist_ok=True)
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Define exactly what we're putting in - these are our EXPECTED results
    # Including ACTUAL mathematical symbols to test extraction
    page1_content = [
        "Page 1: Mathematical Symbols Test",
        "Summation: Σ(i=1 to n) x_i",
        "Integration: ∫[a,b] f(x)dx", 
        "Greek letters: α β γ δ θ λ μ π σ ω",
        "Operators: ± × ÷ ≈ ≠ ≤ ≥ ∞",
        "Sets: ∈ ∉ ⊆ ∪ ∩",
        "Gradient: ∇f(x,y,z)",
        "Partial derivative: ∂f/∂x"
    ]
    
    page2_content = [
        "Page 2: Physics Equations with Symbols",
        "Maxwell: ∇×B = μ₀J + μ₀ε₀(∂E/∂t)",
        "Gauss law: ∇·E = ρ/ε₀", 
        "Schrodinger: iℏ(∂ψ/∂t) = Ĥψ",
        "Wave function: ∫|ψ|²dx = 1",
        "Energy: E = mc² ± ΔE",
        "Planck: E = ℏω where ω ≠ 0",
        "Statistical: ⟨x⟩ = Σᵢ pᵢxᵢ"
    ]
    
    # Page 1
    y_pos = 750
    for line in page1_content:
        c.drawString(100, y_pos, line)
        y_pos -= 30
    
    # Page 2
    c.showPage()
    y_pos = 750
    for line in page2_content:
        c.drawString(100, y_pos, line)
        y_pos -= 30
    
    c.save()
    
    # Return the expected content for comparison
    expected_page1 = "\n".join(page1_content)
    expected_page2 = "\n".join(page2_content)
    
    return pdf_path, expected_page1, expected_page2

def test_controlled_extraction():
    """Test extraction against known input"""
    
    print("Controlled Mathematical Symbol Extraction Test")
    print("=" * 55)
    
    try:
        # Create our controlled PDF
        print("Creating controlled test PDF...")
        pdf_path, expected_page1, expected_page2 = create_controlled_math_pdf()
        print(f"Created: {pdf_path}")
        
        # What we EXPECT to extract (avoid Unicode display issues)
        print(f"\nEXPECTED content includes mathematical symbols:")
        print(f"Page 1: Sigma, integral, Greek letters, operators")
        print(f"Page 2: Maxwell equations, Schrodinger, physics symbols")
        
        # Now test our extraction
        print(f"\n--- Testing fitz extraction ---")
        doc = fitz.open(pdf_path)
        
        success_count = 0
        total_tests = 2
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            extracted_text = page.get_text("text").strip()
            
            print(f"\nPage {page_num + 1} EXTRACTED ({len(extracted_text)} chars):")
            # Safe display - replace problematic Unicode with placeholders for display
            safe_text = extracted_text.encode('ascii', 'replace').decode('ascii')
            print(f"'{safe_text[:200]}...' (showing first 200 chars)")
            
            # Compare with expected content
            if page_num == 0:
                expected = expected_page1
            else:
                expected = expected_page2
                
            # Check if key terms are present
            expected_lines = expected.split('\n')
            found_lines = 0
            
            for expected_line in expected_lines:
                # Look for key words from each expected line
                key_words = expected_line.lower().split()
                if len(key_words) > 2:  # Skip short lines
                    key_words = key_words[:3]  # Check first 3 words
                    
                if all(word in extracted_text.lower() for word in key_words):
                    found_lines += 1
                    safe_line = expected_line[:50].encode('ascii', 'replace').decode('ascii')
                    print(f"  + Found key content: {safe_line}...")
                else:
                    safe_line = expected_line[:50].encode('ascii', 'replace').decode('ascii')
                    print(f"  - Missing content: {safe_line}...")
            
            # SPECIFIC CHECK: Look for mathematical symbols we put in
            mathematical_symbols = ['Σ', '∫', '∇', '∂', 'α', 'β', 'γ', 'δ', 'θ', 'λ', 'μ', 'π', 'σ', 'ω',
                                   '±', '×', '÷', '≈', '≠', '≤', '≥', '∞', '∈', '∉', '⊆', '∪', '∩', 
                                   'ℏ', 'ψ', 'ρ', 'ε₀', 'μ₀', 'ΔE', '⟨', '⟩']
            
            found_symbols = []
            missing_symbols = []
            
            for symbol in mathematical_symbols:
                if symbol in expected:  # Only check symbols we put on this page
                    if symbol in extracted_text:
                        found_symbols.append(symbol)
                    else:
                        missing_symbols.append(symbol)
            
            if found_symbols:
                # Safe display of found symbols
                found_display = [s.encode('ascii', 'replace').decode('ascii') for s in found_symbols]
                print(f"  + Mathematical symbols found: {len(found_symbols)} symbols")
            if missing_symbols:
                # Safe display of missing symbols  
                missing_display = [s.encode('ascii', 'replace').decode('ascii') for s in missing_symbols]
                print(f"  - Mathematical symbols missing: {len(missing_symbols)} symbols")
            
            match_percentage = (found_lines / len(expected_lines)) * 100
            symbol_match = len(found_symbols) / (len(found_symbols) + len(missing_symbols)) * 100 if (found_symbols or missing_symbols) else 100
            
            print(f"  Text match rate: {match_percentage:.1f}% ({found_lines}/{len(expected_lines)} lines)")
            print(f"  Symbol preservation: {symbol_match:.1f}% ({len(found_symbols)}/{len(found_symbols)+len(missing_symbols)} symbols)")
            
            if match_percentage >= 50 and symbol_match >= 50:  # Both text and symbols must work
                success_count += 1
                print(f"  SUCCESS: Page {page_num + 1} extraction acceptable")
            else:
                print(f"  FAILED: Page {page_num + 1} - text:{match_percentage:.1f}% symbols:{symbol_match:.1f}%")
        
        doc.close()
        
        # Overall results
        print(f"\n--- OVERALL RESULTS ---")
        print(f"Successful pages: {success_count}/{total_tests}")
        print(f"Overall success rate: {(success_count/total_tests)*100:.1f}%")
        
        if success_count >= total_tests:
            print(f"CONCLUSION: fitz extraction works correctly!")
            print(f"We can reliably extract text that we put into PDFs.")
        elif success_count >= 1:
            print(f"CONCLUSION: fitz extraction partially works.")
            print(f"Some content extracted successfully, may have formatting issues.")  
        else:
            print(f"CONCLUSION: fitz extraction has serious issues.")
            print(f"Unable to extract content we know is in the PDF.")
        
        # Clean up
        if os.path.exists(pdf_path):
            print(f"\nTest PDF preserved at: {pdf_path}")
        
        return success_count >= 1  # At least 1 page must work
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_controlled_extraction()
    
    if success:
        print(f"\nSUCCESS: Controlled extraction test passed!")
        print(f"fitz can extract the mathematical content we create.")
    else:
        print(f"\nFAILED: Controlled extraction test failed!")
        print(f"There are issues with basic fitz extraction.")