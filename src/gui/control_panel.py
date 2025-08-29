"""
Control Panel Component
Handles basic controls and actions
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QComboBox, QSpinBox)
from PySide6.QtCore import Qt, Signal


class ControlPanel(QWidget):
    """Control panel for basic actions"""
    
    # Signals
    extract_requested = Signal()
    question_requested = Signal()
    generate_questions_requested = Signal()
    
    def __init__(self, language_support=None):
        super().__init__()
        self.language_support = language_support
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the control panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self.language_support.get_text("controls") if self.language_support else "Controls")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Action buttons
        self.extract_button = QPushButton(self.language_support.get_text("extract_text_btn") if self.language_support else "Extract Text")
        self.extract_button.clicked.connect(self.extract_requested.emit)
        layout.addWidget(self.extract_button)
        
        self.ask_button = QPushButton(self.language_support.get_text("ask_question_btn") if self.language_support else "Ask Question")
        self.ask_button.clicked.connect(self.question_requested.emit)
        layout.addWidget(self.ask_button)
        
        self.generate_button = QPushButton(self.language_support.get_text("generate_questions_btn") if self.language_support else "Generate Questions")
        self.generate_button.clicked.connect(self.generate_questions_requested.emit)
        layout.addWidget(self.generate_button)
        
        # Page info
        self.page_info_label = QLabel("Page: 1 of 1")
        layout.addWidget(self.page_info_label)
        
        layout.addStretch()
        
    def update_page_info(self, page_num: int):
        """Update page information display"""
        # This will be called from the PDF viewer
        pass
