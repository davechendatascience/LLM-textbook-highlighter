#!/usr/bin/env python3
"""
Manual test script for quick functionality verification
"""
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import extract_sentences_and_chunks
from highlight_utils import build_contextual_highlight_prompt, parse_llm_highlight_groups
from llm import send_prompt_to_gemini, send_prompt_to_perplexity

def test_with_sample_data():
    """Test core functions without API calls"""
    print("=== Testing Core Functions ===")
    
    # Test highlight utils with sample data
    sample_chunk = [
        {"sentence": "DNA is the genetic material in cells.", "word_indices": [0, 1, 2, 3, 4, 5, 6, 7]},
        {"sentence": "It contains four chemical bases.", "word_indices": [8, 9, 10, 11, 12]},
        {"sentence": "These bases store genetic information.", "word_indices": [13, 14, 15, 16, 17]}
    ]
    
    # Test prompt building
    prompt = build_contextual_highlight_prompt(sample_chunk)
    print("✓ Prompt built successfully")
    print(f"Prompt length: {len(prompt)} characters")
    
    # Test LLM output parsing
    sample_llm_output = """1,2: explains DNA structure and composition
3: describes information storage"""
    
    groups = parse_llm_highlight_groups(sample_llm_output, sample_chunk)
    print(f"✓ Parsed {len(groups)} highlight groups")
    
    for i, group in enumerate(groups):
        print(f"  Group {i+1}: {group['explanation']} (sentences: {group['group_indices']})")

def test_with_real_pdf():
    """Test with actual PDF if available"""
    print("\n=== Testing with PDF ===")
    
    # Check if test PDF exists (look in parent directory too)
    test_pdf = "test_document.pdf"
    parent_test_pdf = os.path.join("..", "test_document.pdf")
    
    if os.path.exists(test_pdf):
        pdf_path = test_pdf
    elif os.path.exists(parent_test_pdf):
        pdf_path = parent_test_pdf
    else:
        print("Creating test PDF...")
        from create_test_pdf import create_test_pdf
        pdf_path = create_test_pdf(test_pdf)
    
    try:
        sentences, chunks, page_word_map = extract_sentences_and_chunks(pdf_path, chunk_size=5)
        print(f"✓ Extracted {len(sentences)} sentences from PDF")
        print(f"✓ Created {len(chunks)} chunks")
        print(f"✓ Mapped {len(page_word_map)} pages")
        
        if chunks:
            sample_chunk = chunks[0]
            print(f"✓ First chunk has {len(sample_chunk)} sentences")
            
    except Exception as e:
        print(f"✗ PDF processing failed: {e}")

def test_with_api():
    """Test API calls if keys are available"""
    print("\n=== Testing API Calls ===")
    
    secrets_path = 'secrets.json'
    parent_secrets_path = os.path.join('..', 'secrets.json')
    
    if os.path.exists(secrets_path):
        secrets_file = secrets_path
    elif os.path.exists(parent_secrets_path):
        secrets_file = parent_secrets_path
    else:
        print("⚠ No secrets.json found - skipping API tests")
        print("Create secrets.json with API keys to test API functionality")
        return
    
    try:
        with open(secrets_file, 'r') as f:
            secrets = json.load(f)
        
        test_prompt = "Explain the importance of DNA in 2-3 sentences."
        
        # Test Gemini if key available
        if 'gemini_api_key' in secrets:
            print("Testing Gemini API...")
            try:
                response = send_prompt_to_gemini(test_prompt, secrets['gemini_api_key'])
                print(f"✓ Gemini response: {response[:100]}...")
            except Exception as e:
                print(f"✗ Gemini API failed: {e}")
        
        # Test Perplexity if key available  
        if 'perplexity_api_key' in secrets:
            print("Testing Perplexity API...")
            try:
                response = send_prompt_to_perplexity(test_prompt, secrets['perplexity_api_key'])
                print(f"✓ Perplexity response: {response[:100]}...")
            except Exception as e:
                print(f"✗ Perplexity API failed: {e}")
                
    except Exception as e:
        print(f"✗ API test setup failed: {e}")

if __name__ == "__main__":
    print("Manual Test Suite for LLM Textbook Highlighter")
    print("=" * 50)
    
    test_with_sample_data()
    test_with_real_pdf() 
    test_with_api()
    
    print("\n" + "=" * 50)
    print("Manual testing complete!")
    print("\nTo test the full workflow:")
    print("1. Run: python tests/create_test_pdf.py")
    print("2. Run: python main.py")
    print("3. Select the test_document.pdf file")
    print("4. Save the highlighted output")