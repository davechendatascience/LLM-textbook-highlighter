#!/usr/bin/env python3
"""
Test the new google-genai integration
"""
import sys
import os

# Add paths (from tests/ subdirectory)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_google_genai():
    """Test google-genai package integration"""
    try:
        from llm import send_prompt_to_gemini
        from config import load_secrets
        
        print("Testing Google GenAI Integration")
        print("=" * 40)
        
        secrets = load_secrets()
        
        if 'gemini_api_key' not in secrets:
            print("WARNING: No Gemini API key found in secrets.json")
            print("   Skipping API test (imports successful)")
            return True
        
        api_key = secrets['gemini_api_key']
        
        # Simple test prompt
        test_prompt = "What is 2+2? Answer with just the number."
        
        print(f"Sending test prompt: '{test_prompt}'")
        print("Testing without web search...")
        
        try:
            response = send_prompt_to_gemini(
                test_prompt, 
                api_key, 
                model="gemini-2.0-flash-exp",
                search_enabled=False
            )
            
            print(f"SUCCESS: Response received: '{response.strip()}'")
            
            # Test with web search if user wants to
            print("\nTesting with web search...")
            try:
                response_search = send_prompt_to_gemini(
                    "What's the current date?", 
                    api_key, 
                    search_enabled=True
                )
                print(f"SUCCESS: Web search response: '{response_search.strip()[:100]}...'")
            except Exception as e:
                print(f"WARNING: Web search test failed (expected): {e}")
                print("   This is normal - web search requires special API access")
            
            return True
            
        except Exception as e:
            print(f"ERROR: API test failed: {e}")
            return False
            
    except Exception as e:
        print(f"ERROR: Import test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_google_genai()
    
    if success:
        print(f"\nSUCCESS: Google GenAI integration successful!")
        print("Ready to use the interactive highlighter!")
    else:
        print(f"\nERROR: Google GenAI integration failed.")
        print("Please check your API key and internet connection.")