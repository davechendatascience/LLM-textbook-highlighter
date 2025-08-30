#!/usr/bin/env python3
"""
Launcher for Cross-Platform PDF Highlighter using PySide6
"""

import sys
import os
import re

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_print_html_content(html_content, title="HTML Content Debug"):
    """Debug function to print HTML content and link information"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    
    # Print HTML preview
    print("📄 HTML Preview (first 1000 chars):")
    print("-" * 40)
    print(html_content[:1000] + "..." if len(html_content) > 1000 else html_content)
    print("-" * 40)
    
    # Find all link tags
    link_matches = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', html_content)
    print(f"🔗 Found {len(link_matches)} link tags:")
    for i, (url, text) in enumerate(link_matches[:10]):  # Show first 10
        print(f"   {i+1}. [{text}] -> {url}")
    
    # Find any unconverted markdown links
    markdown_links = re.findall(r'\[(\d+)\]\(([^)]+)\)', html_content)
    if markdown_links:
        print(f"⚠️  Found {len(markdown_links)} unconverted markdown links:")
        for i, (num, url) in enumerate(markdown_links[:5]):
            print(f"   {i+1}. [{num}]({url})")
    
    # Check for MathJax scripts
    mathjax_count = html_content.count('MathJax')
    print(f"🧮 MathJax references found: {mathjax_count}")
    
    # Check HTML structure
    doctype_count = html_content.count('<!DOCTYPE html>')
    html_count = html_content.count('<html')
    body_count = html_content.count('<body>')
    print(f"🏗️  HTML structure: DOCTYPE={doctype_count}, HTML={html_count}, BODY={body_count}")
    
    print(f"{'='*60}\n")

try:
    from reader import main
    print("Starting LLM PDF Reader...")
    
    # Add the debug function to the global scope so it can be imported
    import builtins
    builtins.debug_print_html_content = debug_print_html_content
    
    main()
except ImportError as e:
    print(f"Error: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
