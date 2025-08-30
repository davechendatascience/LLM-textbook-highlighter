#!/usr/bin/env python3
"""
Pandoc detection utility
Provides simple detection and helpful warnings for Pandoc availability
"""

import subprocess
import sys
from typing import Optional, Tuple

def check_pandoc_availability() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if Pandoc is available on the system
    
    Returns:
        Tuple of (is_available, version, error_message)
    """
    try:
        # Try to get pandoc version
        result = subprocess.run(
            ['pandoc', '--version'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode == 0:
            # Extract version from output
            version_line = result.stdout.split('\n')[0]
            version = version_line.replace('pandoc', '').strip()
            return True, version, None
        else:
            return False, None, f"Pandoc command failed with return code {result.returncode}"
            
    except FileNotFoundError:
        return False, None, "Pandoc not found in system PATH"
    except subprocess.TimeoutExpired:
        return False, None, "Pandoc command timed out"
    except Exception as e:
        return False, None, f"Error checking Pandoc: {str(e)}"

def get_pandoc_installation_instructions() -> str:
    """Get platform-specific installation instructions for Pandoc"""
    platform = sys.platform
    
    if platform.startswith('win'):
        return """
To install Pandoc on Windows:
1. Download from: https://pandoc.org/installing.html
2. Run the installer
3. Restart your terminal/application
"""
    elif platform.startswith('darwin'):  # macOS
        return """
To install Pandoc on macOS:
1. Using Homebrew: brew install pandoc
2. Or download from: https://pandoc.org/installing.html
"""
    else:  # Linux
        return """
To install Pandoc on Linux:
1. Ubuntu/Debian: sudo apt-get install pandoc
2. CentOS/RHEL: sudo yum install pandoc
3. Or download from: https://pandoc.org/installing.html
"""

def get_pandoc_warning_message() -> str:
    """Get a user-friendly warning message about Pandoc"""
    is_available, version, error = check_pandoc_availability()
    
    if is_available:
        return f"✅ Pandoc {version} detected - enhanced LaTeX math support available"
    else:
        instructions = get_pandoc_installation_instructions()
        return f"""
⚠️  Pandoc not detected - LaTeX math rendering will be limited

{instructions}

Note: The application will still work without Pandoc, but LaTeX math expressions 
may not render properly. For the best experience, please install Pandoc.
"""

if __name__ == "__main__":
    is_available, version, error = check_pandoc_availability()
    print(f"Pandoc available: {is_available}")
    if is_available:
        print(f"Version: {version}")
    else:
        print(f"Error: {error}")
        print(get_pandoc_warning_message())
