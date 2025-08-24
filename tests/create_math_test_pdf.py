#!/usr/bin/env python3
"""
Create a test PDF with mathematical symbols for testing text extraction
"""
import fitz  # PyMuPDF
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_math_test_pdf(filename="math_test_document.pdf"):
    """Create a PDF with mathematical content for testing symbol extraction"""
    
    doc = fitz.open()  # Create new PDF
    
    # Page 1 - Mathematical formulas and symbols
    page1 = doc.new_page()
    
    # Add mathematical content with various symbols
    text1 = """
    Mathematical Concepts and Formulas
    
    1. Summation: The sum of a series can be written as Σ(i=1 to n) xi where xi represents each term.
    
    2. Integration: The definite integral ∫[a to b] f(x)dx represents the area under the curve f(x).
    
    3. Greek Letters in Mathematics:
       - Alpha (α) is commonly used for angles
       - Beta (β) represents another angle or parameter  
       - Pi (π ≈ 3.14159) is the ratio of circumference to diameter
       - Delta (Δ) represents change or difference
       - Sigma (σ) represents standard deviation
       - Lambda (λ) represents wavelength or eigenvalues
    
    4. Mathematical Operations:
       - Square root: √x or x^(1/2)
       - Infinity: ∞
       - Approximately equal: ≈
       - Not equal: ≠
       - Less than or equal: ≤
       - Greater than or equal: ≥
    
    5. Set Theory:
       - Element of: x ∈ S means x is an element of set S
       - Not element of: x ∉ S
       - Subset: A ⊆ B means A is a subset of B
       - Union: A ∪ B
       - Intersection: A ∩ B
    """
    
    # Insert text using a font that supports mathematical symbols
    # Try different fonts that might have better symbol support
    try:
        # First try with a font that has better Unicode support
        page1.insert_text((50, 50), text1, fontsize=11, fontname="symb")  # Symbol font
    except:
        try:
            # Fallback to Times which has some math symbols
            page1.insert_text((50, 50), text1, fontsize=11, fontname="tiro")
        except:
            # Last fallback to default
            page1.insert_text((50, 50), text1, fontsize=11, fontname="helv")
    
    # Page 2 - More advanced mathematical content
    page2 = doc.new_page()
    
    text2 = """
    Advanced Mathematical Expressions with Complex Symbols
    
    1. Complex Numbers and Powers: 
       z = a + bi where i² = -1 and i = √(-1)
       Euler's formula: e^(iπ) + 1 = 0
    
    2. Calculus with Summations and Limits:
       - Derivative: f'(x) = df/dx = lim[h→0] (f(x+h) - f(x))/h
       - Riemann sum: ∫[a,b] f(x)dx = lim[n→∞] Σ[k=1,n] f(x_k)Δx
       - Taylor series: f(x) = Σ[n=0,∞] (f^(n)(a)/n!)(x-a)^n
       - Partial derivatives: ∂²f/∂x∂y, ∇f = (∂f/∂x, ∂f/∂y, ∂f/∂z)
       - Multiple integrals: ∬∬ f(x,y)dxdy, ∭∭∭ f(x,y,z)dxdydz
    
    3. Advanced Summation Notation:
       - Finite sum: S = Σ[i=1,n] i² = n(n+1)(2n+1)/6  
       - Infinite series: Σ[n=1,∞] 1/n² = π²/6
       - Double sum: Σ[i=1,m] Σ[j=1,n] a_ij
       - Product notation: Π[i=1,n] x_i = x₁ × x₂ × ... × x_n
    
    4. Set Theory and Logic:
       - Universal quantifier: ∀x ∈ S, P(x)
       - Existential quantifier: ∃x ∈ S such that P(x)
       - Empty set: ∅, Power set: ℘(S)
       - Cardinality: |S|, ℵ₀ (aleph-null)
    
    5. Number Theory:
       - Congruence: a ≡ b (mod n)
       - Divisibility: a | b means a divides b
       - Floor/Ceiling: ⌊x⌋, ⌈x⌉
       - Number sets: ℕ, ℤ, ℚ, ℝ, ℂ
    
    6. Probability and Statistics:
       - Expected value: E[X] = Σ x·P(X=x)
       - Variance: Var(X) = E[(X-μ)²] = σ²
       - Normal distribution: φ(x) = (1/√(2πσ²))e^(-(x-μ)²/(2σ²))
       - Correlation coefficient: ρ = Cov(X,Y)/(σ_x·σ_y)
    
    7. Advanced Physics Symbols:
       - Schrödinger equation: iℏ(∂Ψ/∂t) = ĤΨ
       - Maxwell equations: ∇·E = ρ/ε₀, ∇×B = μ₀J + μ₀ε₀(∂E/∂t)
       - Einstein field equations: Gμν = 8πTμν
       - Dirac notation: |ψ⟩, ⟨φ|ψ⟩
    """
    
    page2.insert_text((50, 50), text2, fontsize=11, fontname="helv")
    
    # Page 3 - Most challenging mathematical symbols
    page3 = doc.new_page()
    
    text3 = """
    Extremely Complex Mathematical Notation
    
    1. Advanced Calculus and Analysis:
       - Contour integral: ∮_C f(z)dz around closed curve C
       - Laplacian: ∇²f = ∂²f/∂x² + ∂²f/∂y² + ∂²f/∂z²
       - D'Alembertian: □ = ∂²/∂t² - ∇²
       - Functional derivative: δF/δf(x)
    
    2. Topology and Geometry:
       - Homeomorphic: X ≅ Y
       - Homotopy: f ≃ g
       - Fundamental group: π₁(X,x₀)
       - Cohomology: H^n(X;G)
    
    3. Abstract Algebra:
       - Group operation: (G,∗), identity: e, inverse: a⁻¹
       - Quotient group: G/H
       - Direct product: G × H, semidirect product: G ⋉ H
       - Tensor product: V ⊗ W
    
    4. Category Theory:
       - Morphism: f: X → Y
       - Natural transformation: η: F ⟹ G
       - Adjunction: F ⊣ G
       - Limit: lim←─ Dᵢ, Colimit: lim──→ Dᵢ
    
    5. Measure Theory:
       - Measure: μ(E), σ-algebra: 𝒜
       - Lebesgue integral: ∫_E f dμ
       - Almost everywhere: a.e.
       - Essential supremum: ess sup f
    
    6. Special Functions:
       - Gamma function: Γ(z) = ∫₀^∞ t^(z-1)e^(-t)dt
       - Bessel functions: J_ν(x), Y_ν(x)
       - Elliptic integrals: K(k) = ∫₀^(π/2) dθ/√(1-k²sin²θ)
       - Riemann zeta: ζ(s) = Σ[n=1,∞] 1/n^s
    
    7. Mathematical Logic:
       - Turnstile: ⊢ (proves), ⊨ (models)
       - Provability: □P, consistency: Con(T)
       - Gödel numbering: ⌜φ⌝
       - Forcing: p ⊩ φ
    
    8. Combinatorics:
       - Binomial coefficient: (n choose k) = C(n,k) = n!/(k!(n-k)!)
       - Stirling numbers: S(n,k), s(n,k)
       - Catalan numbers: C_n = (1/(n+1))(2n choose n)
       - Ramsey number: R(s,t)
    """
    
    page3.insert_text((50, 50), text3, fontsize=11, fontname="helv")
    
    # Save the PDF
    doc.save(filename)
    doc.close()
    
    print(f"Mathematical test PDF created: {filename}")
    print("This PDF contains various mathematical symbols for testing extraction accuracy.")
    
    return filename

if __name__ == "__main__":
    create_math_test_pdf()