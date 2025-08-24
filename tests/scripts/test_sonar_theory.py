#!/usr/bin/env python3
"""
Test the theory: Does Sonar web search help reconstruct mathematical notation?
Let's try sending garbled mathematical text to both APIs with/without web search
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm import send_prompt_to_gemini, send_prompt_to_perplexity

def test_mathematical_reconstruction():
    """Test if LLMs can reconstruct mathematical notation from garbled text"""
    
    # Load API keys
    try:
        with open('secrets.json', 'r') as f:
            secrets = json.load(f)
    except:
        print("No secrets.json found")
        return
    
    # Test cases: garbled mathematical text (simulating bad PDF extraction)
    test_cases = [
        {
            "garbled": "·E = /ε J + με (∂E/∂t)",  # Missing nabla, subscripts
            "context": "This appears to be from Maxwell's equations in electromagnetism.",
            "expected": "∇·E = ρ/ε₀, ∇×B = μ₀J + μ₀ε₀(∂E/∂t)"
        },
        {
            "garbled": "( i=1 n) x_i = x + x + ... + x",  # Missing summation symbol  
            "context": "This appears to be summation notation from mathematics.",
            "expected": "Σ(i=1 to n) x_i = x₁ + x₂ + ... + xₙ"
        },
        {
            "garbled": "f(x)dx = lim n→∞ ( k=1 n) f(x_k)x",  # Missing integral, summation
            "context": "This appears to be the definition of definite integral using Riemann sums.",
            "expected": "∫f(x)dx = lim(n→∞) Σ(k=1 to n) f(x_k)Δx"
        },
        {
            "garbled": "ψ/∂t) = ψ where is the Hamiltonian",  # Missing symbols
            "context": "This appears to be the Schrödinger equation from quantum mechanics.", 
            "expected": "iℏ(∂ψ/∂t) = Ĥψ where Ĥ is the Hamiltonian"
        }
    ]
    
    print("Testing Mathematical Notation Reconstruction")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Garbled Input: '{test['garbled']}'")
        print(f"Context: {test['context']}")
        print(f"Expected: {test['expected']}")
        print("-" * 40)
        
        # Create prompts
        prompt_no_search = f"""
        This text was extracted from a PDF but some mathematical symbols may be missing or corrupted:
        "{test['garbled']}"
        
        {test['context']}
        
        Please provide the correct mathematical notation with proper symbols.
        """
        
        prompt_with_search = f"""
        This text was extracted from a PDF but some mathematical symbols are missing:
        "{test['garbled']}"
        
        {test['context']}
        
        Please look up the correct mathematical notation and provide the complete, properly formatted equation with all symbols.
        """
        
        # Test without web search
        if 'gemini_api_key' in secrets:
            try:
                print("Gemini WITHOUT web search:")
                response = send_prompt_to_gemini(prompt_no_search, secrets['gemini_api_key'], search_enabled=False)
                print(f"Response: {response[:200]}...")
                print()
                
                print("Gemini WITH web search:")
                response = send_prompt_to_gemini(prompt_with_search, secrets['gemini_api_key'], search_enabled=True)
                print(f"Response: {response[:200]}...")
                print()
                
            except Exception as e:
                print(f"Gemini error: {e}")
        
        # Test with Perplexity
        if 'perplexity_api_key' in secrets:
            try:
                print("Perplexity WITHOUT web search:")
                response = send_prompt_to_perplexity(prompt_no_search, secrets['perplexity_api_key'], search_enabled=False)
                print(f"Response: {response[:200]}...")
                print()
                
                print("Perplexity WITH web search:")
                response = send_prompt_to_perplexity(prompt_with_search, secrets['perplexity_api_key'], search_enabled=True)
                print(f"Response: {response[:200]}...")
                print()
                
            except Exception as e:
                print(f"Perplexity error: {e}")
        
        print("=" * 60)

def test_actual_pdf_extraction():
    """Test what our current extraction actually produces"""
    import fitz
    
    print("\nTesting Actual PDF Extraction:")
    print("=" * 40)
    
    test_files = ["realistic_math_test.pdf", "latex_math_test.pdf"]
    
    for filename in test_files:
        if os.path.exists(filename):
            print(f"\nFile: {filename}")
            doc = fitz.open(filename)
            
            # Test first page
            page = doc[0]
            full_text = page.get_text("text")
            
            print(f"Full text length: {len(full_text)}")
            print(f"Sample: '{full_text[:300]}...'")
            
            # Look for mathematical symbols
            math_symbols = ["∑", "∫", "∂", "∇", "π", "α", "β", "σ", "λ", "μ", "δ", "θ", "ω", "≠", "≤", "≥", "∞"]
            found_symbols = [s for s in math_symbols if s in full_text]
            print(f"Mathematical symbols found: {found_symbols}")
            
            doc.close()

if __name__ == "__main__":
    test_mathematical_reconstruction()
    test_actual_pdf_extraction()