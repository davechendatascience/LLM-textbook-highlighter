#!/usr/bin/env python3
"""
Create a test PDF that simulates LaTeX-rendered mathematical content
This will help test text extraction challenges commonly found in academic textbooks
"""
import fitz  # PyMuPDF
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_latex_style_pdf(filename="latex_math_test.pdf"):
    """Create a PDF that simulates LaTeX mathematical typesetting challenges"""
    
    doc = fitz.open()  # Create new PDF
    
    # Page 1 - Simulate LaTeX mathematical expressions
    page1 = doc.new_page()
    
    # Use different insertion methods to simulate LaTeX rendering challenges
    
    # Title with regular text
    page1.insert_text((50, 50), "Advanced Calculus - LaTeX Style Math", fontsize=16, fontname="helv")
    
    # Simulate how LaTeX might render a complex equation by inserting parts separately
    y_pos = 100
    
    # Example 1: Summation that might be rendered as separate components
    page1.insert_text((50, y_pos), "1. Series Convergence:", fontsize=12, fontname="helv")
    y_pos += 25
    
    # Simulate LaTeX rendering: summation symbol, limits, and expression as separate elements
    page1.insert_text((70, y_pos), "∑", fontsize=20, fontname="symb")  # Summation symbol
    page1.insert_text((65, y_pos + 15), "n=1", fontsize=8, fontname="helv")  # Lower limit
    page1.insert_text((75, y_pos - 8), "∞", fontsize=8, fontname="symb")   # Upper limit  
    page1.insert_text((100, y_pos), "1/n", fontsize=12, fontname="helv")   # Expression
    page1.insert_text((125, y_pos - 5), "2", fontsize=8, fontname="helv")  # Superscript
    page1.insert_text((140, y_pos), "= π", fontsize=12, fontname="helv")    # Result part 1
    page1.insert_text((170, y_pos - 5), "2", fontsize=8, fontname="helv")  # Superscript
    page1.insert_text((180, y_pos), "/6", fontsize=12, fontname="helv")     # Result part 2
    
    y_pos += 50
    
    # Example 2: Integral with complex bounds
    page1.insert_text((50, y_pos), "2. Definite Integration:", fontsize=12, fontname="helv")
    y_pos += 25
    
    # Simulate integral rendering
    page1.insert_text((70, y_pos), "∫", fontsize=20, fontname="symb")      # Integral symbol
    page1.insert_text((65, y_pos + 15), "0", fontsize=8, fontname="helv")  # Lower limit
    page1.insert_text((75, y_pos - 8), "π", fontsize=8, fontname="symb")   # Upper limit
    page1.insert_text((95, y_pos), "sin(x) dx = 2", fontsize=12, fontname="helv")
    
    y_pos += 50
    
    # Example 3: Fraction with complex numerator/denominator
    page1.insert_text((50, y_pos), "3. Complex Fraction:", fontsize=12, fontname="helv")
    y_pos += 25
    
    # Simulate fraction rendering (often problematic in extraction)
    page1.insert_text((70, y_pos - 10), "x² + 2x + 1", fontsize=12, fontname="helv")  # Numerator
    page1.insert_text((70, y_pos), "_________________", fontsize=12, fontname="helv")    # Fraction line
    page1.insert_text((80, y_pos + 15), "x + 1", fontsize=12, fontname="helv")         # Denominator
    page1.insert_text((140, y_pos), "= x + 1", fontsize=12, fontname="helv")
    
    y_pos += 60
    
    # Example 4: Matrix representation
    page1.insert_text((50, y_pos), "4. Matrix Operations:", fontsize=12, fontname="helv")
    y_pos += 25
    
    # Simulate matrix brackets and elements (often extracted poorly)
    page1.insert_text((70, y_pos - 10), "⎡", fontsize=20, fontname="symb")     # Left bracket top
    page1.insert_text((70, y_pos + 10), "⎣", fontsize=20, fontname="symb")     # Left bracket bottom
    page1.insert_text((85, y_pos - 5), "a₁₁  a₁₂", fontsize=10, fontname="helv")  # Row 1
    page1.insert_text((85, y_pos + 10), "a₂₁  a₂₂", fontsize=10, fontname="helv") # Row 2
    page1.insert_text((140, y_pos - 10), "⎤", fontsize=20, fontname="symb")    # Right bracket top
    page1.insert_text((140, y_pos + 10), "⎦", fontsize=20, fontname="symb")    # Right bracket bottom
    
    # Page 2 - More challenging LaTeX-style content
    page2 = doc.new_page()
    
    page2.insert_text((50, 50), "Advanced Mathematical Expressions", fontsize=16, fontname="helv")
    
    y_pos = 100
    
    # Example 5: Multi-line equation with alignment (common LaTeX pattern)
    page2.insert_text((50, y_pos), "5. System of Equations:", fontsize=12, fontname="helv")
    y_pos += 25
    
    # Equations often appear as separate text blocks in different positions
    page2.insert_text((70, y_pos), "2x + 3y = 7", fontsize=12, fontname="helv")
    y_pos += 20
    page2.insert_text((70, y_pos), "4x - y = 1", fontsize=12, fontname="helv")
    y_pos += 30
    page2.insert_text((70, y_pos), "Solution: x = 1, y = ", fontsize=12, fontname="helv")
    page2.insert_text((210, y_pos), "5", fontsize=12, fontname="helv")
    page2.insert_text((220, y_pos), "/", fontsize=12, fontname="helv")
    page2.insert_text((225, y_pos), "3", fontsize=12, fontname="helv")
    
    y_pos += 50
    
    # Example 6: Physics equation with vectors and subscripts
    page2.insert_text((50, y_pos), "6. Maxwell's Equation:", fontsize=12, fontname="helv")
    y_pos += 25
    
    # Vector notation often gets separated
    page2.insert_text((70, y_pos), "∇", fontsize=14, fontname="symb")       # Del operator
    page2.insert_text((85, y_pos), "×", fontsize=12, fontname="helv")       # Cross product
    page2.insert_text((100, y_pos), "B", fontsize=12, fontname="helv")      # Field B
    page2.insert_text((115, y_pos), "= μ", fontsize=12, fontname="helv")    # Equals mu
    page2.insert_text((135, y_pos + 5), "0", fontsize=8, fontname="helv")   # Subscript 0
    page2.insert_text((145, y_pos), "J", fontsize=12, fontname="helv")      # Current J
    
    y_pos += 50
    
    # Example 7: Chemical equation (another common LaTeX use case)
    page2.insert_text((50, y_pos), "7. Chemical Reaction:", fontsize=12, fontname="helv")
    y_pos += 25
    
    # Chemical formulas with subscripts
    page2.insert_text((70, y_pos), "2H", fontsize=12, fontname="helv")
    page2.insert_text((90, y_pos + 5), "2", fontsize=8, fontname="helv")     # Subscript
    page2.insert_text((100, y_pos), "+ O", fontsize=12, fontname="helv")
    page2.insert_text((125, y_pos + 5), "2", fontsize=8, fontname="helv")    # Subscript
    page2.insert_text((140, y_pos), "→ 2H", fontsize=12, fontname="helv")
    page2.insert_text((175, y_pos + 5), "2", fontsize=8, fontname="helv")    # Subscript
    page2.insert_text((185, y_pos), "O", fontsize=12, fontname="helv")
    
    # Page 3 - Test extraction challenges
    page3 = doc.new_page()
    
    page3.insert_text((50, 50), "Text Extraction Challenge Cases", fontsize=16, fontname="helv")
    
    text_block = """
    Regular paragraph text that should extract normally. This represents the kind of 
    explanatory text found in textbooks between mathematical expressions.
    
    The challenge comes when mathematical notation is embedded within sentences, such as:
    "The limit of f(x) as x approaches infinity is often denoted as lim f(x) = L."
    
    Another challenge occurs with inline mathematical expressions like x² + y² = r² 
    or when variables are defined such as "let α be the angle of rotation."
    
    Multi-variable calculus expressions such as ∂f/∂x represent partial derivatives,
    and these symbols often get lost or corrupted during text extraction from PDFs
    generated by LaTeX or other mathematical typesetting systems.
    """
    
    page3.insert_text((50, 100), text_block, fontsize=11, fontname="helv")
    
    # Add some intentionally problematic elements
    y_pos = 400
    page3.insert_text((50, y_pos), "Problematic Cases:", fontsize=12, fontname="helv")
    y_pos += 25
    
    # Overlapping text (sometimes happens in LaTeX)
    page3.insert_text((70, y_pos), "Overlapping", fontsize=12, fontname="helv")
    page3.insert_text((75, y_pos), "Text", fontsize=12, fontname="helv")
    
    y_pos += 25
    # Widely spaced text
    page3.insert_text((70, y_pos), "W", fontsize=12, fontname="helv")
    page3.insert_text((85, y_pos), "i", fontsize=12, fontname="helv")
    page3.insert_text((95, y_pos), "d", fontsize=12, fontname="helv")
    page3.insert_text((110, y_pos), "e", fontsize=12, fontname="helv")
    page3.insert_text((125, y_pos), "l", fontsize=12, fontname="helv")
    page3.insert_text((135, y_pos), "y", fontsize=12, fontname="helv")
    page3.insert_text((155, y_pos), "S", fontsize=12, fontname="helv")
    page3.insert_text((170, y_pos), "p", fontsize=12, fontname="helv")
    page3.insert_text((185, y_pos), "a", fontsize=12, fontname="helv")
    page3.insert_text((200, y_pos), "c", fontsize=12, fontname="helv")
    page3.insert_text((215, y_pos), "e", fontsize=12, fontname="helv")
    page3.insert_text((230, y_pos), "d", fontsize=12, fontname="helv")
    
    # Save the PDF
    doc.save(filename)
    doc.close()
    
    print(f"LaTeX-style mathematical test PDF created: {filename}")
    print("This PDF simulates common LaTeX rendering patterns that cause text extraction issues:")
    print("- Composite mathematical symbols")
    print("- Separate positioning of equation components") 
    print("- Complex fractions and matrices")
    print("- Subscripts and superscripts")
    print("- Vector and chemical notation")
    print("- Overlapping and widely-spaced text")
    
    return filename

if __name__ == "__main__":
    create_latex_style_pdf()