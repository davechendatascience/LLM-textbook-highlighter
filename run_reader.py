#!/usr/bin/env python3
"""
Launcher for Cross-Platform PDF Highlighter using PySide6
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from reader import main
    print("Starting LLM PDF Reader...")
    main()
except ImportError as e:
    print(f"Error: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
