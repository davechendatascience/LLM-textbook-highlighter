#!/usr/bin/env python3
"""
Configuration settings for the LLM Textbook Highlighter
"""
import os
import json

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
UTILS_DIR = os.path.join(PROJECT_ROOT, "utils")
EXTRACTION_DIR = os.path.join(PROJECT_ROOT, "extraction_methods")
TESTS_DIR = os.path.join(PROJECT_ROOT, "tests")

# Default settings
DEFAULT_SETTINGS = {
    "window_width": 1400,
    "window_height": 800,
    "pdf_display_width": 800,
    "selection_color": "#FFD700",
    "highlight_alpha": 0.3,
    "default_model": "sonar-reasoning",
    "enable_web_search": False,  # Cost optimization
    "max_text_length": 4000,
    "debug_mode": False
}

# API Configuration
API_COSTS = {
    "perplexity": {
        "with_search": 0.005,      # $5 per 1000 queries  
        "without_search": 0.001    # $1 per 1000 queries
    }
}

def load_secrets():
    """Load API keys from secrets.json"""
    secrets_path = os.path.join(PROJECT_ROOT, "secrets.json")
    try:
        with open(secrets_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {secrets_path} not found. API features will be disabled.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {secrets_path}")
        return {}

def get_available_apis():
    """Check which APIs are available based on secrets.json"""
    secrets = load_secrets()
    available = []
    
    if 'perplexity_api_key' in secrets:
        available.append('perplexity')
        
    return available