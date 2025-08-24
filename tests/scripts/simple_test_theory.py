#!/usr/bin/env python3
"""
Simple test: Can AI reconstruct mathematical notation from broken text?
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm import send_prompt_to_gemini, send_prompt_to_perplexity

def test_simple_reconstruction():
    """Test if LLMs can reconstruct math notation from garbled text"""
    
    # Load API keys
    try:
        with open('secrets.json', 'r') as f:
            secrets = json.load(f)
    except:
        print("No secrets.json found")
        return
    
    # Simple test case
    garbled_text = "( i=1 n) x_i represents the sum of terms"
    
    prompt_no_search = f"""
    This text was extracted from a mathematical PDF but the summation symbol is missing:
    "{garbled_text}"
    
    What should the correct mathematical notation be?
    """
    
    prompt_with_search = f"""
    This text was extracted from a mathematical PDF but the summation symbol is missing:
    "{garbled_text}"
    
    Please look up the standard summation notation and provide the correct mathematical expression.
    """
    
    print("Simple Mathematical Reconstruction Test")
    print("=" * 50)
    print(f"Input: {garbled_text}")
    print()
    
    # Test Gemini
    if 'gemini_api_key' in secrets:
        try:
            print("GEMINI WITHOUT web search:")
            response = send_prompt_to_gemini(prompt_no_search, secrets['gemini_api_key'], search_enabled=False)
            print(response)
            print("-" * 30)
            
            print("GEMINI WITH web search:")
            response = send_prompt_to_gemini(prompt_with_search, secrets['gemini_api_key'], search_enabled=True)
            print(response)
            print("-" * 30)
            
        except Exception as e:
            print(f"Gemini error: {e}")
    
    # Test Perplexity
    if 'perplexity_api_key' in secrets:
        try:
            print("PERPLEXITY WITHOUT web search:")
            response = send_prompt_to_perplexity(prompt_no_search, secrets['perplexity_api_key'], search_enabled=False)
            print(response)
            print("-" * 30)
            
            print("PERPLEXITY WITH web search:")  
            response = send_prompt_to_perplexity(prompt_with_search, secrets['perplexity_api_key'], search_enabled=True)
            print(response)
            print("-" * 30)
            
        except Exception as e:
            print(f"Perplexity error: {e}")

if __name__ == "__main__":
    test_simple_reconstruction()