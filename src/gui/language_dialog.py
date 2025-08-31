"""
Language Selection Dialog
Handles initial language selection on startup
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QPushButton, QDialogButtonBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.utils.language_support import LanguageSupport


class LanguageSelectionDialog(QDialog):
    """Dialog for selecting the application language"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language_support = LanguageSupport()
        self.selected_language = "English"
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Language Selection")
        self.setModal(True)
        self.setFixedSize(400, 150)
        
        # Center the dialog on screen and make it stay on top
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.center_on_screen()
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Please select your preferred language:")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(self.language_support.get_supported_languages())
        self.language_combo.setCurrentText("English")
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.language_combo)
        
        layout.addLayout(lang_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def on_language_changed(self, language: str):
        """Handle language selection change"""
        self.selected_language = language
        self.language_support.set_language(language)
        
    def get_selected_language(self) -> str:
        """Get the selected language"""
        return self.selected_language
    
    def center_on_screen(self):
        """Center the dialog on the screen"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
