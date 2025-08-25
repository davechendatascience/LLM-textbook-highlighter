#!/usr/bin/env python3
"""
Cross-Platform PDF Highlighter using PySide6
Provides reliable dropdown functionality and professional UI across all platforms
"""

import sys
import os
import platform
from datetime import datetime
from typing import Optional, List, Dict, Any

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QPushButton, QLabel, QComboBox, QTextEdit, QLineEdit,
    QScrollArea, QFrame, QFileDialog, QMessageBox, QSlider
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QObject
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QImage

# PDF processing
import fitz  # PyMuPDF
from PIL import Image
import io

# Add paths for imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm import send_prompt_to_perplexity
from config import load_secrets, get_available_apis, DEFAULT_SETTINGS


class PDFRenderer(QObject):
    """Thread-safe PDF rendering"""
    page_rendered = Signal(QPixmap, int, int)  # pixmap, width, height
    
    def __init__(self):
        super().__init__()
        self.pdf_doc = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.fit_to_panel_zoom = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        self.zoom_step = 0.25
    
    def load_pdf(self, file_path: str):
        """Load PDF document"""
        try:
            self.pdf_doc = fitz.open(file_path)
            self.current_page = 0
            return len(self.pdf_doc)
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return 0
    
    def render_page(self, page_num: int, canvas_width: int, canvas_height: int):
        """Render PDF page with current zoom"""
        if not self.pdf_doc or page_num >= len(self.pdf_doc):
            return
        
        try:
            self.current_page = page_num
            page = self.pdf_doc[page_num]
            
            # Calculate fit-to-panel zoom
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            padding = 20
            fit_width_zoom = (canvas_width - padding) / page_width
            fit_height_zoom = (canvas_height - padding) / page_height
            self.fit_to_panel_zoom = max(min(fit_width_zoom, fit_height_zoom), 0.5)
            
            # Calculate actual zoom
            actual_zoom = self.fit_to_panel_zoom * self.zoom_level
            
            # Render page
            mat = fitz.Matrix(actual_zoom, actual_zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            # Convert to QPixmap
            image = Image.open(io.BytesIO(img_data))
            qimage = QImage(image.tobytes(), image.width, image.height, 
                          image.width * 3, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            
            self.page_rendered.emit(pixmap, image.width, image.height)
            
        except Exception as e:
            print(f"Error rendering page: {e}")
    
    def set_zoom(self, zoom_level: float):
        """Set zoom level"""
        self.zoom_level = max(self.min_zoom, min(zoom_level, self.max_zoom))
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level + self.zoom_step, self.max_zoom)
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level - self.zoom_step, self.min_zoom)
    
    def reset_zoom(self):
        """Reset to fit panel"""
        self.zoom_level = 1.0
    
    def get_zoom_percentage(self) -> int:
        """Get zoom as percentage"""
        return int(self.zoom_level * 100)


class SelectionOverlay(QWidget):
    """Overlay widget for drawing selection rectangle"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        
        # Make overlay transparent
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
    def set_selection(self, start, end, selecting=False):
        """Update selection coordinates"""
        self.selection_start = start
        self.selection_end = end
        self.is_selecting = selecting
        self.update()
        
    def paintEvent(self, event):
        """Paint selection rectangle"""
        if not self.selection_start or not self.selection_end:
            return
            
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 0, 0), 3))
        
        # Calculate rectangle coordinates
        x1 = min(self.selection_start.x(), self.selection_end.x())
        y1 = min(self.selection_start.y(), self.selection_end.y())
        x2 = max(self.selection_start.x(), self.selection_end.x())
        y2 = max(self.selection_start.y(), self.selection_end.y())
        
        # Draw selection rectangle
        painter.drawRect(x1, y1, x2 - x1, y2 - y1)


class PDFViewer(QWidget):
    """PDF display widget with selection capabilities"""
    
    def __init__(self, renderer: PDFRenderer):
        super().__init__()
        self.renderer = renderer
        self.current_pixmap = None
        self.is_selecting = False
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the PDF viewer UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # PDF display area
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setMinimumSize(400, 600)
        self.pdf_label.setStyleSheet("QLabel { background-color: #f5f5f5; border: 2px dashed #ccc; }")
        
        # Set placeholder text when no PDF is loaded
        self.pdf_label.setText("No PDF loaded\n\nClick 'Open PDF' to load a document")
        self.pdf_label.setStyleSheet("QLabel { background-color: #f5f5f5; border: 2px dashed #ccc; color: #666; font-size: 14px; }")
        
        # Scroll area for PDF with visible scrollbars
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.pdf_label)
        scroll_area.setWidgetResizable(False)  # Don't resize widget automatically
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMinimumSize(400, 600)
        layout.addWidget(scroll_area)
        
        # Store reference to scroll area
        self.scroll_area = scroll_area
        
        # Connect scrollbar value changes to clear selection
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.clear_selection_on_scroll)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.clear_selection_on_scroll)
        
        # Create selection overlay
        self.selection_overlay = SelectionOverlay(self.scroll_area.viewport())
        self.selection_overlay.setGeometry(0, 0, 400, 600)
        self.selection_overlay.show()
        
        # Mouse tracking for selection
        self.pdf_label.setMouseTracking(True)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.renderer.page_rendered.connect(self.display_page)
    
    def display_page(self, pixmap: QPixmap, width: int, height: int):
        """Display rendered PDF page"""
        self.current_pixmap = pixmap
        self.pdf_label.setPixmap(pixmap)
        self.pdf_label.resize(width, height)
        
        # Clear placeholder text and update styling when PDF is displayed
        self.pdf_label.setText("")
        self.pdf_label.setStyleSheet("QLabel { background-color: white; border: 1px solid #ccc; }")
        
        # Resize the selection overlay to match the PDF content
        if hasattr(self, 'selection_overlay'):
            self.selection_overlay.setGeometry(0, 0, width, height)
            self.selection_overlay.raise_()  # Ensure overlay is on top
        
        # Ensure scrollbars appear when needed
        if hasattr(self, 'scroll_area'):
            # Force scroll area to update its scroll region
            self.scroll_area.viewport().update()
            
            # Explicitly set scrollbar policies based on content size
            viewport_width = self.scroll_area.viewport().width()
            viewport_height = self.scroll_area.viewport().height()
            
            if width > viewport_width:
                self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            else:
                self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                
            if height > viewport_height:
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            else:
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        if event.button() == Qt.LeftButton and self.current_pixmap:
            self.is_selecting = True
            # Get position relative to this widget
            self.selection_start = event.pos()
            self.selection_end = event.pos()
            # Update the overlay
            if hasattr(self, 'selection_overlay'):
                self.selection_overlay.set_selection(self.selection_start, self.selection_end, True)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for selection"""
        if self.is_selecting and self.current_pixmap:
            # Get position relative to this widget
            self.selection_end = event.pos()
            # Update the overlay
            if hasattr(self, 'selection_overlay'):
                self.selection_overlay.set_selection(self.selection_start, self.selection_end, True)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release for selection"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            # Get position relative to this widget
            self.selection_end = event.pos()
            # Update the overlay
            if hasattr(self, 'selection_overlay'):
                self.selection_overlay.set_selection(self.selection_start, self.selection_end, False)
            # Emit selection signal
            if self.selection_start and self.selection_end:
                self.selection_completed.emit(self.selection_start, self.selection_end)
    

    
    def force_update(self):
        """Force update of the PDF viewer"""
        self.update()
        if hasattr(self, 'pdf_label'):
            self.pdf_label.update()
    
    def clear_selection_on_scroll(self):
        """Clear selection when scrolling"""
        if hasattr(self, 'selection_overlay'):
            self.selection_overlay.set_selection(None, None, False)
        # Reset selection state
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
    
    # Signal for selection completion
    selection_completed = Signal(object, object)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.renderer = PDFRenderer()
        self.session_notes = []
        self.suggested_questions = []
        
        # Initialize flags to prevent recursive changes
        self._font_size_changing = False
        self._question_selection_changing = False
        
        # API configuration
        self.api_keys = load_secrets()
        self.available_apis = get_available_apis()
        
        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Cross-Platform PDF Reader")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Toolbar (fixed height)
        toolbar_widget = self.setup_toolbar()
        toolbar_widget.setFixedHeight(50)
        main_layout.addWidget(toolbar_widget)
        
        # Content area
        content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter)
        
        # PDF viewer
        self.pdf_viewer = PDFViewer(self.renderer)
        content_splitter.addWidget(self.pdf_viewer)
        
        # Control panel
        self.setup_control_panel(content_splitter)
        
        # Set splitter proportions
        content_splitter.setSizes([800, 400])
    
    def setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout.setSpacing(5)
        
        # File operations
        self.open_btn = QPushButton("Open PDF")
        self.open_btn.setFixedHeight(30)
        toolbar_layout.addWidget(self.open_btn)
        
        # Navigation
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.page_label = QLabel("Page: 0 / 0")
        self.prev_btn.setFixedHeight(30)
        self.next_btn.setFixedHeight(30)
        toolbar_layout.addWidget(self.prev_btn)
        toolbar_layout.addWidget(self.page_label)
        toolbar_layout.addWidget(self.next_btn)
        
        # Page input
        toolbar_layout.addWidget(QLabel("Go to:"))
        self.page_input = QLineEdit()
        self.page_input.setMaximumWidth(60)
        self.page_input.setFixedHeight(30)
        toolbar_layout.addWidget(self.page_input)
        self.go_btn = QPushButton("Go")
        self.go_btn.setFixedHeight(30)
        toolbar_layout.addWidget(self.go_btn)
        
        toolbar_layout.addStretch()
        
        # Zoom controls
        toolbar_layout.addWidget(QLabel("Zoom:"))
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["25%", "50%", "75%", "Fit", "125%", "150%", "200%", "300%", "400%"])
        self.zoom_combo.setCurrentText("Fit")
        self.zoom_combo.setMaximumWidth(80)
        self.zoom_combo.setFixedHeight(30)
        toolbar_layout.addWidget(self.zoom_combo)
        
        self.zoom_in_btn = QPushButton("Zoom In")
        self.zoom_out_btn = QPushButton("Zoom Out")
        self.zoom_in_btn.setFixedHeight(30)
        self.zoom_out_btn.setFixedHeight(30)
        toolbar_layout.addWidget(self.zoom_in_btn)
        toolbar_layout.addWidget(self.zoom_out_btn)
        
        # Panel controls
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(QLabel("Panel:"))
        self.wider_btn = QPushButton("Wider PDF")
        self.narrower_btn = QPushButton("Narrower PDF")
        self.wider_btn.setFixedHeight(30)
        self.narrower_btn.setFixedHeight(30)
        toolbar_layout.addWidget(self.wider_btn)
        toolbar_layout.addWidget(self.narrower_btn)
        
        return toolbar
    
    def setup_control_panel(self, splitter):
        """Setup the right control panel"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # Instructions
        instructions = QLabel("Instructions:")
        instructions.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout.addWidget(instructions)
        
        instruction_text = QLabel(
            "1. Open a PDF file\n"
            "2. Drag to select text region\n"
            "3. Click 'Extract Text' to get content\n"
            "4. Ask questions about the selected text\n\n"
            "Zoom: Use Ctrl+MouseWheel or toolbar buttons\n"
            "- 'Fit' = Automatically fits PDF to panel\n"
            "- Zoom percentages are relative to fit-to-panel size\n"
            "- PDF automatically refits when window is resized\n\n"
            "Panel: Use Ctrl+Left/Right arrows or toolbar buttons\n\n"
            "Cross-platform compatible with reliable dropdown functionality"
        )
        instruction_text.setWordWrap(True)
        control_layout.addWidget(instruction_text)
        
        # Status
        self.status_label = QLabel("No selection")
        self.status_label.setStyleSheet("color: gray;")
        control_layout.addWidget(self.status_label)
        
        # Selection controls
        selection_layout = QHBoxLayout()
        self.clear_selection_btn = QPushButton("Clear Selection")
        self.extract_text_btn = QPushButton("Extract Text")
        selection_layout.addWidget(self.clear_selection_btn)
        selection_layout.addWidget(self.extract_text_btn)
        control_layout.addLayout(selection_layout)
        
        # Extracted text
        control_layout.addWidget(QLabel("Extracted Text:"))
        self.extracted_text = QTextEdit()
        self.extracted_text.setMaximumHeight(100)
        control_layout.addWidget(self.extracted_text)
        
        # Question input
        control_layout.addWidget(QLabel("Ask a question:"))
        self.question_input = QLineEdit()
        control_layout.addWidget(self.question_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ask_btn = QPushButton("Ask Question")
        self.generate_questions_btn = QPushButton("Generate Questions")
        button_layout.addWidget(self.ask_btn)
        button_layout.addWidget(self.generate_questions_btn)
        control_layout.addLayout(button_layout)
        
        # Suggested questions
        control_layout.addWidget(QLabel("Suggested Questions:"))
        self.suggested_questions_combo = QComboBox()
        control_layout.addWidget(self.suggested_questions_combo)
        
        # Font size
        control_layout.addWidget(QLabel("Font size:"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([
            "Small (10pt)",
            "Medium (12pt)",
            "Large (14pt)",
            "Extra Large (20pt)"
        ])
        self.font_size_combo.setCurrentText("Medium (12pt)")
        self.font_size_combo.setEditable(False)  # Prevent editing to avoid instability
        control_layout.addWidget(self.font_size_combo)
        
        # Answer length
        control_layout.addWidget(QLabel("Answer length:"))
        self.answer_length_combo = QComboBox()
        self.answer_length_combo.addItems([
            "Short (< 250 tokens)",
            "Medium (250-500 tokens)",
            "Long (500-1000 tokens)",
            "Comprehensive (> 1000 tokens)"
        ])
        self.answer_length_combo.setCurrentText("Medium (250-500 tokens)")
        control_layout.addWidget(self.answer_length_combo)
        
        # Ask selected question
        self.ask_selected_btn = QPushButton("Ask Selected Question")
        control_layout.addWidget(self.ask_selected_btn)
        
        # Response
        control_layout.addWidget(QLabel("LLM Response:"))
        self.response_text = QTextEdit()
        control_layout.addWidget(self.response_text)
        
        splitter.addWidget(control_widget)
    
    def setup_connections(self):
        """Setup signal connections"""
        # File operations
        self.open_btn.clicked.connect(self.open_pdf)
        
        # Navigation
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        self.go_btn.clicked.connect(self.go_to_page)
        
        # Zoom controls
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_change)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        # Font size control
        self.font_size_combo.currentTextChanged.connect(self.on_font_size_change)
        
        # Question selection control
        self.suggested_questions_combo.currentTextChanged.connect(self.on_question_selection_change)
        
        # Panel controls
        self.wider_btn.clicked.connect(self.widen_panel)
        self.narrower_btn.clicked.connect(self.narrow_panel)
        
        # Selection
        self.pdf_viewer.selection_completed.connect(self.on_selection_completed)
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        self.extract_text_btn.clicked.connect(self.extract_selected_text)
        
        # LLM operations
        self.ask_btn.clicked.connect(self.ask_question)
        self.generate_questions_btn.clicked.connect(self.generate_questions)
        self.ask_selected_btn.clicked.connect(self.ask_selected_question)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Zoom shortcuts
        self.zoom_in_btn.setShortcut("Ctrl++")
        self.zoom_out_btn.setShortcut("Ctrl+-")
        
        # Panel shortcuts
        self.wider_btn.setShortcut("Ctrl+Right")
        self.narrower_btn.setShortcut("Ctrl+Left")
    
    def open_pdf(self):
        """Open PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF files (*.pdf)"
        )
        if file_path:
            try:
                num_pages = self.renderer.load_pdf(file_path)
                if num_pages > 0:
                    self.update_page_label()
                    self.render_current_page()
                    self.status_label.setText(f"Opened PDF: {os.path.basename(file_path)} ({num_pages} pages)")
                else:
                    QMessageBox.warning(self, "Error", "Failed to open PDF file.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open PDF: {e}")
    
    def render_current_page(self):
        """Render the current page"""
        if hasattr(self, 'pdf_viewer'):
            canvas_width = self.pdf_viewer.width()
            canvas_height = self.pdf_viewer.height()
            self.renderer.render_page(self.renderer.current_page, canvas_width, canvas_height)
    
    def update_page_label(self):
        """Update page label"""
        if self.renderer.pdf_doc:
            self.page_label.setText(f"Page: {self.renderer.current_page + 1} / {len(self.renderer.pdf_doc)}")
        else:
            self.page_label.setText("Page: 0 / 0")
    
    def prev_page(self):
        """Go to previous page"""
        if self.renderer.pdf_doc and self.renderer.current_page > 0:
            self.renderer.current_page -= 1
            self.render_current_page()
            self.update_page_label()
            # Clear selection when changing pages
            self.clear_selection()
    
    def next_page(self):
        """Go to next page"""
        if self.renderer.pdf_doc and self.renderer.current_page < len(self.renderer.pdf_doc) - 1:
            self.renderer.current_page += 1
            self.render_current_page()
            self.update_page_label()
            # Clear selection when changing pages
            self.clear_selection()
    
    def go_to_page(self):
        """Go to specific page"""
        try:
            page_num = int(self.page_input.text()) - 1
            if self.renderer.pdf_doc and 0 <= page_num < len(self.renderer.pdf_doc):
                self.renderer.current_page = page_num
                self.render_current_page()
                self.update_page_label()
                self.page_input.clear()
                # Clear selection when changing pages
                self.clear_selection()
            else:
                QMessageBox.warning(self, "Invalid Page", "Page number out of range.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid page number.")
    
    def on_zoom_change(self, zoom_text: str):
        """Handle zoom dropdown change"""
        if zoom_text == "Fit":
            self.renderer.reset_zoom()
        elif zoom_text and '%' in zoom_text:
            try:
                zoom_percent = int(zoom_text.replace('%', ''))
                zoom_level = zoom_percent / 100.0
                self.renderer.set_zoom(zoom_level)
            except ValueError:
                return
        
        self.render_current_page()
        self.update_zoom_status()
        # Clear selection when zooming since coordinates change
        self.clear_selection()
    
    def zoom_in(self):
        """Zoom in"""
        self.renderer.zoom_in()
        self.update_zoom_display()
        self.render_current_page()
        self.update_zoom_status()
        # Clear selection when zooming since coordinates change
        self.clear_selection()
    
    def zoom_out(self):
        """Zoom out"""
        self.renderer.zoom_out()
        self.update_zoom_display()
        self.render_current_page()
        self.update_zoom_status()
        # Clear selection when zooming since coordinates change
        self.clear_selection()
    
    def update_zoom_display(self):
        """Update zoom dropdown display"""
        zoom_percent = self.renderer.get_zoom_percentage()
        zoom_text = f"{zoom_percent}%"
        
        # Update combo box if value exists, otherwise add it
        if zoom_text in [self.zoom_combo.itemText(i) for i in range(self.zoom_combo.count())]:
            self.zoom_combo.setCurrentText(zoom_text)
        else:
            self.zoom_combo.addItem(zoom_text)
            self.zoom_combo.setCurrentText(zoom_text)
    
    def update_zoom_status(self):
        """Update zoom status"""
        if self.renderer.zoom_level == 1.0:
            self.status_label.setText("Zoom: Fit to panel")
        else:
            zoom_percent = self.renderer.get_zoom_percentage()
            self.status_label.setText(f"Zoom: {zoom_percent}%")
    
    def on_font_size_change(self, font_size_text):
        """Handle font size dropdown selection"""
        # Prevent recursive changes
        if self._font_size_changing:
            return
        
        self._font_size_changing = True
        
        try:
            # Extract font size from text (e.g., "Medium (12pt)" -> 12)
            if "Small" in font_size_text:
                font_size = 10
            elif "Medium" in font_size_text:
                font_size = 12
            elif "Extra Large" in font_size_text:
                font_size = 20
            elif "Large" in font_size_text:
                font_size = 14
            else:
                font_size = 12  # Default
            
            # Apply font size to text areas
            font = QFont("Arial", font_size)
            self.extracted_text.setFont(font)
            self.response_text.setFont(font)
            
            # Update status
            self.status_label.setText(f"Font size changed to {font_size}pt")
        except Exception as e:
            print(f"Error changing font size: {e}")
        finally:
            self._font_size_changing = False
    
    def on_question_selection_change(self, selected_question):
        """Handle question selection dropdown change"""
        # Prevent automatic changes from programmatic updates
        if self._question_selection_changing:
            return
        
        # Only update status if there's actually a selection
        if selected_question:
            self.status_label.setText(f"Selected question: {selected_question}")
    
    def widen_panel(self):
        """Make PDF panel wider"""
        splitter = self.findChild(QSplitter)
        if splitter:
            sizes = splitter.sizes()
            new_width = min(sizes[0] + 50, splitter.width() - 300)
            splitter.setSizes([new_width, splitter.width() - new_width])
    
    def narrow_panel(self):
        """Make PDF panel narrower"""
        splitter = self.findChild(QSplitter)
        if splitter:
            sizes = splitter.sizes()
            new_width = max(sizes[0] - 50, 200)
            splitter.setSizes([new_width, splitter.width() - new_width])
    
    def on_selection_completed(self, start_pos, end_pos):
        """Handle text selection completion"""
        self.status_label.setText("Selection completed. Click 'Extract Text' to get content.")
        # Store selection coordinates for text extraction
        self.selection_start = start_pos
        self.selection_end = end_pos
    
    def clear_selection(self):
        """Clear the current selection"""
        self.selection_start = None
        self.selection_end = None
        self.extracted_text.clear()
        self.status_label.setText("Selection cleared")
        
        # Clear visual selection by clearing the overlay
        if hasattr(self, 'pdf_viewer') and hasattr(self.pdf_viewer, 'selection_overlay'):
            self.pdf_viewer.selection_overlay.set_selection(None, None, False)
    
    def extract_selected_text(self):
        """Extract text from the selected region using fitz"""
        if not self.selection_start or not self.selection_end:
            QMessageBox.warning(self, "No Selection", "Please select a text region first.")
            return
        
        if not self.renderer.pdf_doc:
            QMessageBox.warning(self, "No PDF", "Please open a PDF first.")
            return
        
        try:
            # Get the current page
            page = self.renderer.pdf_doc[self.renderer.current_page]
            
            # Convert screen coordinates to PDF coordinates
            # We need to account for the current zoom and fit-to-panel scaling
            scale_factor = self.renderer.fit_to_panel_zoom * self.renderer.zoom_level
            
            # Get scroll area offsets
            scroll_x = self.pdf_viewer.scroll_area.horizontalScrollBar().value()
            scroll_y = self.pdf_viewer.scroll_area.verticalScrollBar().value()
            
            # Convert screen coordinates to PDF coordinates (accounting for scroll position)
            # The selection coordinates are relative to the PDF viewer widget, so we need to add scroll offsets
            pdf_x1 = (min(self.selection_start.x(), self.selection_end.x()) + scroll_x) / scale_factor
            pdf_y1 = (min(self.selection_start.y(), self.selection_end.y()) + scroll_y) / scale_factor
            pdf_x2 = (max(self.selection_start.x(), self.selection_end.x()) + scroll_x) / scale_factor
            pdf_y2 = (max(self.selection_start.y(), self.selection_end.y()) + scroll_y) / scale_factor
            
            # Create a rectangle for text extraction
            rect = fitz.Rect(pdf_x1, pdf_y1, pdf_x2, pdf_y2)
            
            # Extract text from the selected region
            extracted_text = page.get_text("text", clip=rect)
            
            if extracted_text.strip():
                self.extracted_text.setText(extracted_text.strip())
                self.status_label.setText(f"Text extracted: {len(extracted_text.strip())} characters")
            else:
                self.extracted_text.setText("No text found in the selected region.")
                self.status_label.setText("No text found in selection")
                
        except Exception as e:
            self.extracted_text.setText(f"Error extracting text: {e}")
            self.status_label.setText("Error during text extraction")
            print(f"Text extraction error: {e}")
    
    def ask_question(self):
        """Ask a question about the selected text"""
        question = self.question_input.text().strip()
        if not question:
            QMessageBox.warning(self, "No Question", "Please enter a question.")
            return
        
        extracted_text = self.extracted_text.toPlainText().strip()
        if not extracted_text:
            QMessageBox.warning(self, "No Text", "Please extract some text first.")
            return
        
        try:
            # Check if API key is available
            api_key = self.api_keys.get('perplexity_api_key')
            if not api_key:
                self.llm_response.setText("Error: Perplexity API key not found. Please check your secrets.json file.")
                self.status_label.setText("API key missing")
                return
            
            # Prepare the prompt for the LLM
            prompt = f"""Based on the following text, please answer this question:

Text: {extracted_text}

Question: {question}

Please provide a clear and accurate answer based only on the information in the text above."""

            # Get answer length preference and choose appropriate model
            answer_length = self.answer_length_combo.currentText()
            
            # Choose model based on answer length
            if "Short" in answer_length or "Medium" in answer_length:
                model = "sonar"  # Faster for shorter answers
            else:
                model = "sonar-reasoning"  # Better reasoning for longer answers
            
            # Call the LLM
            response = send_prompt_to_perplexity(prompt, api_key, model=model)
            
            if response:
                # Clean up response - remove <think> tags if present
                cleaned_response = self.clean_llm_response(response)
                self.response_text.setText(cleaned_response)
                self.status_label.setText(f"Question answered ({len(cleaned_response)} characters)")
            else:
                self.response_text.setText("Error: Could not get response from LLM. Please check your API key.")
                self.status_label.setText("LLM error")
                
        except Exception as e:
            self.response_text.setText(f"Error: {str(e)}")
            self.status_label.setText("Error occurred")
            print(f"LLM error: {e}")
    
    def generate_questions(self):
        """Generate suggested questions"""
        extracted_text = self.extracted_text.toPlainText().strip()
        if not extracted_text:
            QMessageBox.warning(self, "No Text", "Please extract some text first.")
            return
        
        try:
            # Check if API key is available
            api_key = self.api_keys.get('perplexity_api_key')
            if not api_key:
                QMessageBox.warning(self, "Error", "Perplexity API key not found. Please check your secrets.json file.")
                self.status_label.setText("API key missing")
                return
            
            # Prepare the prompt for question generation
            prompt = f"""Based on the following text, generate exactly 5 relevant questions that could be asked about this content. 
            Make the questions diverse and interesting, covering different aspects of the text.

Text: {extracted_text}

Instructions:
- Generate exactly 5 questions
- Each question should be on its own line
- Do not use numbering (1., 2., etc.)
- Do not use bullet points (-, •, *)
- Make questions clear and specific
- Cover different aspects of the content

Questions:"""

            # Call the LLM - use sonar for question generation (faster and cleaner)
            response = send_prompt_to_perplexity(prompt, api_key, model="sonar")
            
            if response:
                # Parse the response to extract questions
                # Clean up the response and split by lines
                lines = response.strip().split('\n')
                questions = []
                
                for line in lines:
                    line = line.strip()
                    # Skip empty lines and common prefixes
                    if line and not line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '*')):
                        # Remove any numbering at the start
                        if line[0].isdigit() and '. ' in line:
                            line = line.split('. ', 1)[1]
                        questions.append(line)
                
                # Limit to 5 questions and filter out duplicates
                unique_questions = []
                seen = set()
                for q in questions[:5]:
                    if q and q not in seen:
                        unique_questions.append(q)
                        seen.add(q)
                
                # Update the suggested questions dropdown
                self._question_selection_changing = True
                self.suggested_questions_combo.clear()
                if unique_questions:
                    self.suggested_questions_combo.addItems(unique_questions)
                    self.status_label.setText(f"Generated {len(unique_questions)} questions")
                else:
                    self.status_label.setText("No valid questions generated")
                self._question_selection_changing = False
            else:
                QMessageBox.warning(self, "Error", "Could not generate questions. Please check your API key.")
                self.status_label.setText("Question generation failed")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error generating questions: {str(e)}")
            self.status_label.setText("Error occurred")
            print(f"Question generation error: {e}")
    
    def clean_llm_response(self, response):
        """Clean up LLM response by removing <think> tags and other formatting"""
        if not response:
            return response
        
        # Remove <think> tags and their content
        import re
        # Remove <think>...</think> blocks
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        # Remove any remaining <think> tags
        response = re.sub(r'<think>', '', response)
        response = re.sub(r'</think>', '', response)
        
        # Clean up extra whitespace
        response = re.sub(r'\n\s*\n', '\n\n', response)
        response = response.strip()
        
        return response
    
    def ask_selected_question(self):
        """Ask the selected suggested question"""
        selected_question = self.suggested_questions_combo.currentText()
        if not selected_question:
            QMessageBox.warning(self, "No Question", "Please select a question from the dropdown.")
            return
        
        extracted_text = self.extracted_text.toPlainText().strip()
        if not extracted_text:
            QMessageBox.warning(self, "No Text", "Please extract some text first.")
            return
        
        try:
            # Check if API key is available
            api_key = self.api_keys.get('perplexity_api_key')
            if not api_key:
                self.response_text.setText("Error: Perplexity API key not found. Please check your secrets.json file.")
                self.status_label.setText("API key missing")
                return
            
            # Prepare the prompt for the LLM
            prompt = f"""Based on the following text, please answer this question:

Text: {extracted_text}

Question: {selected_question}

Please provide a clear and accurate answer based only on the information in the text above."""

            # Get answer length preference and choose appropriate model
            answer_length = self.answer_length_combo.currentText()
            
            # Choose model based on answer length
            if "Short" in answer_length or "Medium" in answer_length:
                model = "sonar"  # Faster for shorter answers
            else:
                model = "sonar-reasoning"  # Better reasoning for longer answers
            
            # Call the LLM
            response = send_prompt_to_perplexity(prompt, api_key, model=model)
            
            if response:
                # Clean up response - remove <think> tags if present
                cleaned_response = self.clean_llm_response(response)
                self.response_text.setText(cleaned_response)
                self.status_label.setText(f"Question answered ({len(cleaned_response)} characters)")
            else:
                self.response_text.setText("Error: Could not get response from LLM. Please check your API key.")
                self.status_label.setText("LLM error")
                
        except Exception as e:
            self.response_text.setText(f"Error: {str(e)}")
            self.status_label.setText("Error occurred")
            print(f"LLM error: {e}")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
