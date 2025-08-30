#!/usr/bin/env python3
"""
Debug test script to see the HTML output from math rendering.
"""

import sys
import os
from PySide6.QtWidgets import QApplication

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.markdown_widget import EnhancedMarkdownTextWidget
import markdown

def test_math_debug():
    """Test math rendering and show the HTML output."""
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Test content with various math expressions
    test_content = """
# Math Rendering Test

## Inline Math Tests

This is inline math with dollar signs: $x^2 + y^2 = z^2$

This is inline math with parentheses: \\(\\frac{a}{b} + c\\)

This is inline math without delimiters: α + β = γ

This is inline math with subscripts: x₁ + x₂ = x₃

This is inline math with Greek letters: θ = π/2

This is LaTeX command without delimiters: \\sqrt{16} = 4

This is fraction without delimiters: \\frac{1}{2}

## Display Math Tests

This is display math with dollar signs:
$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$

This is display math with brackets:
\\[\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}\\]

## Mixed Content

Here's a paragraph with inline math $E = mc^2$ and some regular text, followed by more math \\(\\sqrt{16} = 4\\) and even more text.

## Complex Expressions

Inline: $\\frac{\\partial f}{\\partial x} = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}$

Display:
$$\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix} \\begin{pmatrix} x \\\\ y \\end{pmatrix} = \\begin{pmatrix} ax + by \\\\ cx + dy \\end{pmatrix}$$

## Unicode Math Symbols

Inline: α + β = γ, θ = π/2, ∑ᵢ₌₁ⁿ xᵢ

Display:
$$\\forall \\epsilon > 0, \\exists \\delta > 0 : |x - a| < \\delta \\implies |f(x) - L| < \\epsilon$$
"""
    
    print("=== TESTING MARKDOWN WIDGET ===")
    
    # Create the widget
    widget = EnhancedMarkdownTextWidget()
    
    # Get the HTML output
    widget.set_markdown_text(test_content)
    
    # Get the HTML content
    html_content = widget.toHtml()
    
    print("\n=== HTML OUTPUT ===")
    print(html_content)
    
    # Save to file for inspection
    with open("math_test_output.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n=== HTML saved to math_test_output.html ===")
    
    # Also test the markdown conversion directly
    print("\n=== TESTING DIRECT MARKDOWN CONVERSION ===")
    
    # Create markdown instance
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'mdx_math'
        ],
        extension_configs={
            'mdx_math': {
                'enable_dollar_delimiter': True,
                'add_preview': False
            }
        }
    )
    
    # Test preprocessing
    print("\n--- Original text ---")
    print(test_content[:500] + "...")
    
    # Test preprocessing step
    import re
    processed_text = re.sub(r'(?<!\$)\\([a-zA-Z]+)\{([^}]+)\}(?!\$)', r'$\1{\2}$', test_content)
    
    print("\n--- After preprocessing ---")
    print(processed_text[:500] + "...")
    
    # Convert to HTML
    html = md.convert(processed_text)
    
    print("\n--- Raw HTML from markdown ---")
    print(html[:1000] + "...")
    
    # Save raw HTML too
    with open("math_test_raw.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\n=== Raw HTML saved to math_test_raw.html ===")

if __name__ == "__main__":
    test_math_debug()
