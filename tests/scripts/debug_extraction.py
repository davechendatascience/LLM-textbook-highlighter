#!/usr/bin/env python3
"""
Debug text extraction to compare methods and identify the issue
"""
import fitz
import sys
import os

def debug_text_extraction(pdf_path):
    """Debug different text extraction methods"""
    print(f"=== Debugging text extraction for: {pdf_path} ===")
    
    doc = fitz.open(pdf_path)
    
    for page_num in range(min(3, len(doc))):  # Test first 3 pages
        print(f"\n--- Page {page_num + 1} ---")
        page = doc[page_num]
        
        print(f"Page rect: {page.rect}")
        
        # Method 1: Full page text (like main.py uses)
        full_text = page.get_text("text")
        print(f"Full page text length: {len(full_text)}")
        print(f"Full page text sample: '{full_text[:300]}...'")
        
        # Method 2: Test a selection rectangle in the middle of the page
        rect = page.rect
        # Select middle 50% of the page
        margin_x = rect.width * 0.25
        margin_y = rect.height * 0.25
        test_rect = fitz.Rect(
            rect.x0 + margin_x, 
            rect.y0 + margin_y,
            rect.x1 - margin_x,
            rect.y1 - margin_y
        )
        
        print(f"Test selection rect: {test_rect}")
        clipped_text = page.get_text("text", clip=test_rect)
        print(f"Clipped text length: {len(clipped_text)}")
        print(f"Clipped text: '{clipped_text}'")
        
        # Method 3: Dictionary method
        text_dict = page.get_text("dict")
        dict_parts = []
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span.get("text", "").strip()
                        if text:
                            dict_parts.append(text)
        
        dict_text = " ".join(dict_parts)
        print(f"Dictionary text length: {len(dict_text)}")
        print(f"Dictionary text sample: '{dict_text[:300]}...'")
        
        # Check for mathematical symbols
        math_symbols = ["∑", "∫", "∂", "∇", "π", "α", "β", "σ", "λ", "μ", "δ", "θ", "ω", "Δ", "Γ", "Π", "Σ"]
        found_symbols = [s for s in math_symbols if s in full_text]
        if found_symbols:
            print(f"Mathematical symbols found: {found_symbols}")
        else:
            print("No mathematical symbols found in full text")
        
        print("-" * 50)

if __name__ == "__main__":
    # Test with different PDF files
    test_files = [
        "test_document.pdf",
        "realistic_math_test.pdf", 
        "latex_math_test.pdf"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            debug_text_extraction(test_file)
            print("\n" + "=" * 80 + "\n")
        else:
            print(f"File not found: {test_file}")