#!/usr/bin/env python3
"""
Test script to verify math rendering in the markdown widget.
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.markdown_widget import EnhancedMarkdownTextWidget

def test_math_rendering():
    """Test various math expressions in the markdown widget."""
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Math Rendering Test")
    window.setGeometry(100, 100, 800, 600)
    
    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Create markdown widget
    markdown_widget = EnhancedMarkdownTextWidget()
    layout.addWidget(markdown_widget)
    
    # Test content with various math expressions
    test_content = """
# Math Rendering Test

## Inline Math Tests

This is inline math with dollar signs: $x^2 + y^2 = z^2$

This is inline math with parentheses: \\(\\frac{a}{b} + c\\)

This is inline math without delimiters: α + β = γ

This is inline math with subscripts: x₁ + x₂ = x₃

This is inline math with Greek letters: θ = π/2

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
    
    # Set the test content
    markdown_widget.set_markdown_text(test_content)
    
    # Show the window
    window.show()
    
    print("Math rendering test window opened.")
    print("Check if:")
    print("1. Inline math with $...$ is rendered correctly")
    print("2. Inline math with \\(...\\) is rendered correctly")
    print("3. Display math with $$...$$ is rendered correctly")
    print("4. Display math with \\[...\\] is rendered correctly")
    print("5. Unicode math symbols are displayed properly")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    test_math_rendering()
