#!/usr/bin/env python3
"""
Launch the interactive PDF highlighter GUI
"""
import sys
import os

# Add src and utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from config import load_secrets, get_available_apis
from interactive_highlighter import SimpleInteractivePDFHighlighter

def main():
    """Launch the simplified interactive highlighter"""
    print("LLM Textbook Highlighter - Simplified Interactive Mode")
    print("=" * 55)
    
    # Check API availability
    secrets = load_secrets()
    available_apis = get_available_apis()
    
    if not available_apis or 'perplexity' not in available_apis:
        print("Warning: Perplexity API key not found in secrets.json")
        print("Interactive features will be limited to text extraction only")
        print("Add 'perplexity_api_key' to secrets.json for LLM features")
        print()
    else:
        print("✓ Perplexity API available")
        print("Using sonar-reasoning model with web search capability")
        print()
    
    print("Features:")
    print("• Fitz text extraction (fast and reliable)")
    print("• Perplexity AI for question answering")
    print("• Simple drag-to-select interface")
    print()
    
    # Launch the GUI
    try:
        app = SimpleInteractivePDFHighlighter()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Error launching application: {e}")
        print("Please check your Python environment and dependencies")

if __name__ == "__main__":
    main()