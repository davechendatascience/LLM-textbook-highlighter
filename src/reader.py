#!/usr/bin/env python3
"""
LLM PDF Reader - Modular Version
Main entry point that uses the new modular architecture
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from gui.main_window import MainWindow
from gui.language_dialog import LanguageSelectionDialog


def main():
    """Main application entry point - maintains backward compatibility"""
    print("Starting LLM PDF Reader (Modular Version)...")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("LLM PDF Reader")
    app.setApplicationVersion("1.0")
    
    # Show language selection dialog
    language = "English"  # Default language
    
    dialog = LanguageSelectionDialog()
    if dialog.exec() == LanguageSelectionDialog.Accepted:
        language = dialog.get_selected_language()
    else:
        sys.exit(0)
    
    # Create and show main window
    window = MainWindow(language)
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
