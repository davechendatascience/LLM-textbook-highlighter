#!/usr/bin/env python3
"""
Create a realistic test PDF with mathematical content that actually renders properly
Using ASCII representations and standard symbols that work with basic fonts
"""
import fitz  # PyMuPDF
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_realistic_math_pdf(filename="realistic_math_test.pdf"):
    """Create a PDF with mathematical content that will actually render in standard fonts"""
    
    doc = fitz.open()  # Create new PDF
    
    # Page 1 - Mathematics with ASCII and basic symbols that render
    page1 = doc.new_page()
    
    text1 = """
    Mathematical Concepts and Formulas
    
    1. Summation Notation:
       The sum of a series: Sum(i=1 to n) of x_i represents adding all terms.
       Example: Sum(i=1 to 5) of i^2 = 1^2 + 2^2 + 3^2 + 4^2 + 5^2 = 55
    
    2. Integration and Calculus:
       The definite integral: Integral from a to b of f(x)dx
       Derivative: f'(x) = df/dx = limit as h approaches 0 of [f(x+h) - f(x)]/h
       Second derivative: f''(x) = d^2f/dx^2
    
    3. Greek Letters (written out):
       - Alpha (α) is commonly used for angles
       - Beta (β) represents another parameter  
       - Pi (π ≈ 3.14159) is the ratio of circumference to diameter
       - Delta (Δ) represents change: Delta_x = x_2 - x_1
       - Sigma (σ) represents standard deviation in statistics
       - Lambda (λ) represents wavelength in physics
    
    4. Mathematical Relationships:
       - Square root: sqrt(x) or x^(1/2)
       - Infinity: infinity symbol (∞)
       - Approximately equal: x ≈ y means x is approximately equal to y  
       - Not equal: x ≠ y means x does not equal y
       - Less than or equal: x ≤ y
       - Greater than or equal: x ≥ y
    
    5. Set Theory Notation:
       - Element of: x ∈ S means x is an element of set S
       - Union: A ∪ B represents all elements in either A or B
       - Intersection: A ∩ B represents elements in both A and B
       - Subset: A ⊆ B means every element of A is also in B
    """
    
    # Insert text with standard font
    page1.insert_text((50, 50), text1, fontsize=11, fontname="helv")
    
    # Page 2 - More complex mathematical expressions
    page2 = doc.new_page()
    
    text2 = """
    Advanced Mathematical Expressions
    
    1. Series and Sequences:
       Arithmetic series: S_n = Sum(k=1 to n) of a_k = n/2 * (2a + (n-1)d)
       Geometric series: S_n = a * (1 - r^n) / (1 - r) for r ≠ 1
       Taylor series: f(x) = Sum(n=0 to infinity) of [f^(n)(a)/n!] * (x-a)^n
    
    2. Calculus Applications:
       Area under curve: A = Integral from a to b of |f(x)| dx
       Volume of revolution: V = π * Integral from a to b of [f(x)]^2 dx
       Arc length: L = Integral from a to b of sqrt(1 + [f'(x)]^2) dx
    
    3. Linear Algebra:
       Matrix multiplication: C = A × B where C_ij = Sum(k=1 to n) of A_ik * B_kj
       Determinant of 2×2 matrix: det(A) = ad - bc for matrix [[a,b],[c,d]]
       Eigenvalue equation: A*v = λ*v where λ is eigenvalue, v is eigenvector
    
    4. Statistics and Probability:
       Sample mean: x̄ = (1/n) * Sum(i=1 to n) of x_i
       Sample variance: s^2 = [1/(n-1)] * Sum(i=1 to n) of (x_i - x̄)^2
       Standard deviation: s = sqrt(s^2)
       Normal distribution: f(x) = [1/(σ*sqrt(2π))] * exp[-(x-μ)^2/(2σ^2)]
    
    5. Physics Formulas:
       Newton's second law: F = ma (Force equals mass times acceleration)
       Kinetic energy: KE = (1/2)mv^2
       Gravitational force: F = G*m₁*m₂/r^2
       Wave equation: c = f*λ where c is speed, f is frequency, λ is wavelength
    
    6. Complex Numbers:
       Standard form: z = a + bi where i^2 = -1
       Magnitude: |z| = sqrt(a^2 + b^2)
       Euler's formula: e^(iθ) = cos(θ) + i*sin(θ)
    """
    
    page2.insert_text((50, 50), text2, fontsize=11, fontname="helv")
    
    # Page 3 - Test various symbol combinations that might render
    page3 = doc.new_page()
    
    text3 = """
    Mathematical Symbols Test (Mixed ASCII and Unicode)
    
    1. Basic Symbols That Usually Render:
       + - × ÷ = ≠ < > ≤ ≥ ± ∓
       
    2. Fractions and Exponents:
       1/2, 3/4, x^2, x^n, a₁, a₂, aₙ
       
    3. Greek Letters (if supported):
       α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω
       Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω
       
    4. Mathematical Operators:
       ∑ ∏ ∫ ∂ ∇ √ ∞ ∅ ∈ ∉ ⊂ ⊃ ∪ ∩ ∧ ∨ ¬
       
    5. Arrows and Relations:
       → ← ↑ ↓ ↔ ⇒ ⇐ ⇔ ≈ ≅ ≡ ∝ ∀ ∃
       
    6. Specialized Symbols:
       ℕ ℤ ℚ ℝ ℂ ℝⁿ ∅ ⊗ ⊕ ⊙ ∘ ° ′ ″ ‰ %
       
    7. Test Equations with Mixed Notation:
       ∑(i=1 to n) x_i = x₁ + x₂ + ... + xₙ
       ∫₋∞^∞ e^(-x²) dx = √π
       lim(x→0) (sin x)/x = 1
       ∂²u/∂x² + ∂²u/∂y² = 0 (Laplace equation)
    
    Note: Symbol rendering depends on the font and system capabilities.
    Some symbols may appear as squares or be missing if not supported.
    """
    
    page3.insert_text((50, 50), text3, fontsize=11, fontname="helv")
    
    # Save the PDF
    doc.save(filename)
    doc.close()
    
    print(f"Realistic mathematical test PDF created: {filename}")
    print("This PDF tests various mathematical notations with better font compatibility.")
    print("Page 1: ASCII representations that always work")  
    print("Page 2: Mixed notation with subscripts/superscripts")
    print("Page 3: Unicode symbol test to see what renders")
    
    return filename

if __name__ == "__main__":
    create_realistic_math_pdf()