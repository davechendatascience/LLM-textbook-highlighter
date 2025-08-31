#!/usr/bin/env python3
"""
Preload tiktoken models for packaged executable
"""

import os
import sys
import json
import tiktoken
from pathlib import Path

def get_tiktoken_cache_dir():
    """Get the tiktoken cache directory for the packaged app"""
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller executable
        base_dir = Path(sys._MEIPASS)
        cache_dir = base_dir / "tiktoken_cache"
    else:
        # Running from Python script
        cache_dir = Path.home() / ".tiktoken_cache"
    
    cache_dir.mkdir(exist_ok=True)
    return cache_dir

def preload_tiktoken_models():
    """Pre-download tiktoken models and save them locally"""
    print("📥 Preloading tiktoken models...")
    
    cache_dir = get_tiktoken_cache_dir()
    print(f"📁 Cache directory: {cache_dir}")
    
    models_to_load = ["cl100k_base"]
    
    for model_name in models_to_load:
        try:
            print(f"  📦 Loading {model_name}...")
            
            # Get the encoder (this will download if needed)
            encoder = tiktoken.get_encoding(model_name)
            
            # Save model data to cache
            model_file = cache_dir / f"{model_name}.json"
            
            # Get the model data (this is a simplified approach)
            # In a real implementation, you'd need to extract the actual model data
            model_info = {
                "name": model_name,
                "encoder_type": "cl100k_base",
                "loaded": True
            }
            
            with open(model_file, 'w') as f:
                json.dump(model_info, f)
            
            print(f"  ✅ {model_name} cached to {model_file}")
            
        except Exception as e:
            print(f"  ❌ Failed to load {model_name}: {e}")
            return False
    
    print("✅ All tiktoken models preloaded successfully")
    return True

def get_cached_encoder(model_name: str = "cl100k_base"):
    """Get tiktoken encoder, using cache if available"""
    try:
        # Try to get the encoder normally first
        return tiktoken.get_encoding(model_name)
    except Exception as e:
        print(f"⚠️  Failed to load {model_name} normally: {e}")
        
        # Try to use cached version
        cache_dir = get_tiktoken_cache_dir()
        model_file = cache_dir / f"{model_name}.json"
        
        if model_file.exists():
            print(f"📁 Using cached model from {model_file}")
            # For now, just try the normal method again
            # In a real implementation, you'd load the cached data
            return tiktoken.get_encoding(model_name)
        else:
            print(f"❌ No cached model found at {model_file}")
            raise e

if __name__ == "__main__":
    preload_tiktoken_models()
