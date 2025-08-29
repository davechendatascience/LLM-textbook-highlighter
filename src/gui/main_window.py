"""
Main Window - Core GUI application
Handles the main window, layout, and high-level UI management
"""

import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QSplitter, QMenuBar, QStatusBar, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence

# Use absolute imports
from src.gui.pdf_viewer import PDFViewer
from src.gui.text_panel import TextPanel
from src.utils.language_support import LanguageSupport


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, language: str = "English"):
        super().__init__()
        
        # Initialize language support
        self.language_support = LanguageSupport(language)
        
        # Set window title
        self.setWindowTitle(self.language_support.get_text("window_title"))
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components
        self.pdf_viewer = PDFViewer(self.language_support)
        self.text_panel = TextPanel(self.language_support)
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Main splitter - PDF viewer and text panel only
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.pdf_viewer)
        self.main_splitter.addWidget(self.text_panel)
        self.main_splitter.setSizes([800, 600])
        
        main_layout.addWidget(self.main_splitter)
        
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(self.language_support.get_text("open_pdf"))
        
        open_action = QAction(self.language_support.get_text("open_pdf"), self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_pdf)
        file_menu.addAction(open_action)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def connect_signals(self):
        """Connect signals between components"""
        # PDF viewer signals
        self.pdf_viewer.text_extracted.connect(self.text_panel.set_extracted_text)
        self.pdf_viewer.page_changed.connect(self.on_page_changed)
        
        # Text panel signals
        # self.text_panel.research_requested.connect(self.research_panel.search_papers) # Removed
        
        # PDF width adjustment signals
        self.pdf_viewer.wider_button.clicked.connect(self.adjust_pdf_width_wider)
        self.pdf_viewer.narrower_button.clicked.connect(self.adjust_pdf_width_narrower)
        
    def on_page_changed(self, page_num):
        """Handle page changes"""
        # Update status bar with page information
        if hasattr(self, 'pdf_viewer') and hasattr(self.pdf_viewer, 'total_pages'):
            self.status_bar.showMessage(f"Page {page_num + 1} of {self.pdf_viewer.total_pages}")
        else:
            self.status_bar.showMessage(f"Page {page_num + 1}")
            
    def adjust_pdf_width_wider(self):
        """Make the PDF panel wider"""
        current_sizes = self.main_splitter.sizes()
        total_width = sum(current_sizes)
        
        # Increase PDF panel width by 10% of total width
        increase = int(total_width * 0.1)
        new_pdf_width = current_sizes[0] + increase
        new_text_width = current_sizes[1] - increase
        
        # Ensure minimum sizes
        if new_text_width >= 200:  # Minimum 200px for text panel
            self.main_splitter.setSizes([new_pdf_width, new_text_width])
            
    def adjust_pdf_width_narrower(self):
        """Make the PDF panel narrower"""
        current_sizes = self.main_splitter.sizes()
        total_width = sum(current_sizes)
        
        # Decrease PDF panel width by 10% of total width
        decrease = int(total_width * 0.1)
        new_pdf_width = current_sizes[0] - decrease
        new_text_width = current_sizes[1] + decrease
        
        # Ensure minimum sizes
        if new_pdf_width >= 300:  # Minimum 300px for PDF panel
            self.main_splitter.setSizes([new_pdf_width, new_text_width])
        
    def open_pdf(self):
        """Open PDF file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.language_support.get_text("open_pdf"), "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.pdf_viewer.load_pdf(file_path)
            self.status_bar.showMessage(f"Loaded: {file_path}")
            
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, 
            self.language_support.get_text("about_title"),
            self.language_support.get_text("about_text")
        )
