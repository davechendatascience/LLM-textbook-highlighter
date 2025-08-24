#!/usr/bin/env python3
"""
Batch processing mode has been removed in favor of the interactive mode.
This script now redirects to the interactive highlighter.
"""

print("=" * 60)
print("NOTICE: Batch processing mode has been removed")
print("=" * 60)
print()
print("The batch processing functionality has been removed to:")
print("• Prevent wasting credits on a non-functional feature")
print("• Focus development on the reliable interactive mode")
print("• Simplify the codebase and reduce complexity")
print()
print("Please use the interactive mode instead:")
print("  python run_interactive.py")
print()
print("The interactive mode provides:")
print("• Visual PDF navigation and text selection")
print("• Smart question generation with answer length control") 
print("• Session tracking and note-keeping")
print("• Cost-effective per-query usage")
print()
print("Redirecting to interactive mode in 3 seconds...")

import time
import subprocess
import sys
import os

time.sleep(3)

# Launch the interactive mode
script_dir = os.path.dirname(os.path.abspath(__file__))
interactive_script = os.path.join(script_dir, "run_interactive.py")

try:
    subprocess.run([sys.executable, interactive_script], check=True)
except FileNotFoundError:
    print("Error: run_interactive.py not found")
    print("Please run: python run_interactive.py")
except Exception as e:
    print(f"Error launching interactive mode: {e}")
    print("Please run manually: python run_interactive.py")
