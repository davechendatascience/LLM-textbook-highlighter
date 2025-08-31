#!/usr/bin/env python3
"""
Preload models to ensure they're available when needed
"""

import os
import sys
import time
import tiktoken
from pathlib import Path

def preload_tiktoken_models():
    """Pre-download tiktoken models to avoid delays during use"""
    print("📥 Preloading tiktoken models...")
    
    models_to_load = ["cl100k_base"]
    
    for model_name in models_to_load:
        try:
            print(f"  📦 Loading {model_name}...")
            start_time = time.time()
            
            # This will download the model if not already cached
            encoder = tiktoken.get_encoding(model_name)
            
            elapsed = time.time() - start_time
            print(f"  ✅ {model_name} loaded in {elapsed:.2f}s")
            
            # Test the encoder
            test_text = "Hello world"
            tokens = encoder.encode(test_text)
            print(f"  🧪 Test encoding: {len(tokens)} tokens for '{test_text}'")
            
        except Exception as e:
            print(f"  ❌ Failed to load {model_name}: {e}")
            return False
    
    print("✅ All tiktoken models preloaded successfully")
    return True

def check_tiktoken_cache():
    """Check if tiktoken models are already cached"""
    print("🔍 Checking tiktoken cache...")
    
    # Common cache locations
    cache_locations = [
        os.path.expanduser("~/.cache/tiktoken"),
        os.path.expanduser("~/AppData/Local/tiktoken"),
        os.path.expanduser("~/AppData/Roaming/tiktoken"),
    ]
    
    for cache_dir in cache_locations:
        if os.path.exists(cache_dir):
            print(f"  📁 Found cache: {cache_dir}")
            try:
                contents = os.listdir(cache_dir)
                print(f"    📦 Contents: {contents}")
            except Exception as e:
                print(f"    ❌ Error listing: {e}")
        else:
            print(f"  ❌ No cache: {cache_dir}")
    
    # Try to load cl100k_base to see if it's cached
    try:
        start_time = time.time()
        encoder = tiktoken.get_encoding("cl100k_base")
        elapsed = time.time() - start_time
        
        if elapsed < 1.0:
            print(f"  ✅ cl100k_base is cached (loaded in {elapsed:.2f}s)")
        else:
            print(f"  ⏳ cl100k_base was downloaded (took {elapsed:.2f}s)")
            
    except Exception as e:
        print(f"  ❌ Failed to load cl100k_base: {e}")

def main():
    """Main function for testing"""
    print("🔧 Tiktoken Model Preloader")
    print("=" * 40)
    
    check_tiktoken_cache()
    print()
    preload_tiktoken_models()

if __name__ == "__main__":
    main()
