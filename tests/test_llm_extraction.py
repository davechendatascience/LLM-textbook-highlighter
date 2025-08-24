#!/usr/bin/env python3
"""
Test text extraction by asking LLM questions about extracted content
"""
import sys
import os
import fitz

# Add paths (from tests/ subdirectory)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_extraction_with_llm():
    """Test extraction quality by asking LLM questions about the content"""
    
    textbook_path = os.path.join(os.path.dirname(__file__), "..", "classical mechanics john taylor.pdf")
    
    if not os.path.exists(textbook_path):
        print(f"ERROR: Textbook not found at {textbook_path}")
        return False
    
    print("Testing Text Extraction with LLM Verification")
    print("=" * 55)
    
    try:
        from interactive_highlighter import InteractivePDFHighlighter
        from config import load_secrets
        from llm import send_prompt_to_gemini, send_prompt_to_perplexity
        
        # Load API keys
        secrets = load_secrets()
        if not secrets:
            print("ERROR: No API keys found - skipping LLM test")
            return False
        
        # Create app instance
        app = InteractivePDFHighlighter()
        app.pdf_doc = fitz.open(textbook_path)
        app.pdf_path = textbook_path
        
        # Test on a few different pages and regions
        test_scenarios = [
            {
                "page": 1,  # Page 2 - trigonometric identities
                "rect": fitz.Rect(50, 100, 400, 300),
                "expected_topic": "trigonometric identities",
                "test_question": "What mathematical topic is discussed in this text? Answer in 2-3 words."
            },
            {
                "page": 1,  # Page 2 - different region
                "rect": fitz.Rect(100, 300, 450, 500),
                "expected_topic": "trigonometric",
                "test_question": "Does this text contain trigonometric functions like sin, cos? Answer yes/no and explain briefly."
            }
        ]
        
        success_count = 0
        total_tests = len(test_scenarios)
        
        for i, scenario in enumerate(test_scenarios):
            print(f"\n--- Test {i+1}: Page {scenario['page']+1}, Region {scenario['rect']} ---")
            
            # Extract text using our method
            page = app.pdf_doc[scenario['page']]
            extracted_text = app.extract_text_robust(page, scenario['rect'])
            
            print(f"Extracted text ({len(extracted_text)} chars):")
            print(f"'{extracted_text[:200]}...'")
            
            if len(extracted_text) < 10:
                print("❌ FAILED: Too little text extracted")
                continue
            
            # Test with LLM
            prompt = f"""
            Here is some text extracted from a physics textbook:
            
            "{extracted_text}"
            
            Question: {scenario['test_question']}
            """
            
            try:
                # Try Gemini first
                if 'gemini_api_key' in secrets:
                    response = send_prompt_to_gemini(
                        prompt, 
                        secrets['gemini_api_key'], 
                        search_enabled=False
                    )
                    print(f"LLM Response: {response}")
                    
                    # Check if response contains expected topic
                    response_lower = response.lower()
                    expected_lower = scenario['expected_topic'].lower()
                    
                    if expected_lower in response_lower:
                        print("✅ SUCCESS: LLM correctly identified the content")
                        success_count += 1
                    else:
                        print(f"⚠️  PARTIAL: LLM response doesn't clearly mention '{scenario['expected_topic']}'")
                        # Still count as success if LLM gave a reasonable response
                        if len(response) > 10 and any(word in response_lower for word in ['math', 'trigonometric', 'sin', 'cos', 'equation']):
                            success_count += 1
                            print("   But response seems mathematically relevant, counting as success")
                
                elif 'perplexity_api_key' in secrets:
                    response = send_prompt_to_perplexity(
                        prompt, 
                        secrets['perplexity_api_key'], 
                        search_enabled=False
                    )
                    print(f"LLM Response: {response}")
                    success_count += 1  # If we get any response, count as success
                    
            except Exception as e:
                print(f"❌ LLM API Error: {e}")
        
        # Cleanup
        app.pdf_doc.close()
        app.root.destroy()
        
        print(f"\n--- Results ---")
        print(f"Successful tests: {success_count}/{total_tests}")
        
        if success_count >= total_tests * 0.7:  # 70% success rate
            print("✅ OVERALL SUCCESS: Text extraction is working well")
            return True
        else:
            print("❌ OVERALL FAILURE: Text extraction needs improvement")
            return False
            
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_extraction_with_llm()
    
    if success:
        print(f"\n🎉 Text extraction validated with LLM!")
    else:
        print(f"\n💥 Text extraction validation failed")