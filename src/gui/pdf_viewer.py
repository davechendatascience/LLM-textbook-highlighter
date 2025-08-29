"""
PDF Viewer Component
Handles PDF display, text selection, and extraction
"""

import fitz
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSpinBox, QSlider, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QMouseEvent, QImage

from src.utils.pdf_processor import PDFProcessor


class PDFLabel(QLabel):
    """Custom QLabel for PDF display with selection painting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection_start = None
        self.selection_end = None
        
    def set_selection(self, start_pos, end_pos):
        """Set the selection rectangle"""
        self.selection_start = start_pos
        self.selection_end = end_pos
        self.update()
        
    def clear_selection(self):
        """Clear the selection"""
        self.selection_start = None
        self.selection_end = None
        self.update()
        
    def paintEvent(self, event):
        """Paint the PDF image and selection rectangle"""
        super().paintEvent(event)
        
        if self.selection_start and self.selection_end and self.pixmap():
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 0, 0, 128), 2))
            
            x1 = min(self.selection_start.x(), self.selection_end.x())
            y1 = min(self.selection_start.y(), self.selection_end.y())
            x2 = max(self.selection_start.x(), self.selection_end.x())
            y2 = max(self.selection_start.y(), self.selection_end.y())
            
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)


class PDFViewer(QWidget):
    """PDF display and text selection widget"""
    
    # Signals
    text_extracted = Signal(str)  # Emitted when text is extracted
    page_changed = Signal(int)    # Emitted when page changes
    
    def __init__(self, language_support=None):
        super().__init__()
        self.language_support = language_support
        self.pdf_processor = PDFProcessor()
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.selection_start = None
        self.selection_end = None
        self.page_rect = None  # Store the actual page rectangle
        self.pdf_width_ratio = 0.6  # Default PDF panel width ratio
        
        self.setup_ui()
        self.setup_mouse_tracking()
        
    def setup_ui(self):
        """Setup the PDF viewer UI"""
        layout = QVBoxLayout(self)
        
        # Navigation controls
        nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton(self.language_support.get_text("previous") if self.language_support else "Previous")
        self.prev_button.clicked.connect(self.previous_page)
        nav_layout.addWidget(self.prev_button)
        
        self.page_label = QLabel(f"{self.language_support.get_text('page') if self.language_support else 'Page'} 1 of 1")
        nav_layout.addWidget(self.page_label)
        
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.valueChanged.connect(self.go_to_page)
        nav_layout.addWidget(self.page_spinbox)
        
        self.next_button = QPushButton(self.language_support.get_text("next") if self.language_support else "Next")
        self.next_button.clicked.connect(self.next_page)
        nav_layout.addWidget(self.next_button)
        
        # Zoom controls
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(25)
        self.zoom_slider.setMaximum(400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.set_zoom)
        nav_layout.addWidget(QLabel(self.language_support.get_text("zoom") if self.language_support else "Zoom:"))
        nav_layout.addWidget(self.zoom_slider)
        
        # PDF width controls
        nav_layout.addWidget(QLabel(self.language_support.get_text("pdf_width") if self.language_support else "PDF Width:"))
        self.wider_button = QPushButton(self.language_support.get_text("wider_pdf") if self.language_support else "Wider")
        self.wider_button.clicked.connect(self.make_pdf_wider)
        nav_layout.addWidget(self.wider_button)
        
        self.narrower_button = QPushButton(self.language_support.get_text("narrower_pdf") if self.language_support else "Narrower")
        self.narrower_button.clicked.connect(self.make_pdf_narrower)
        nav_layout.addWidget(self.narrower_button)
        
        layout.addLayout(nav_layout)
        
        # PDF display area with proper scroll handling
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Don't auto-resize
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create a container widget for the PDF label
        self.pdf_container = QWidget()
        self.pdf_container_layout = QVBoxLayout(self.pdf_container)
        self.pdf_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use custom PDF label
        self.pdf_label = PDFLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setText("Open a PDF to begin")
        self.pdf_label.setMinimumSize(400, 600)
        # Set size policy to allow expansion but maintain scrollbars
        self.pdf_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        self.pdf_container_layout.addWidget(self.pdf_label)
        self.scroll_area.setWidget(self.pdf_container)
        
        layout.addWidget(self.scroll_area)
        
    def setup_mouse_tracking(self):
        """Setup mouse tracking for text selection"""
        self.pdf_label.setMouseTracking(True)
        self.pdf_label.mousePressEvent = self.mouse_press_event
        self.pdf_label.mouseMoveEvent = self.mouse_move_event
        self.pdf_label.mouseReleaseEvent = self.mouse_release_event
        
        # Connect scroll area signals to reset selection
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.reset_selection)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.reset_selection)
        
    def reset_selection(self):
        """Reset the selection when scrolling"""
        if self.selection_start or self.selection_end:
            self.selection_start = None
            self.selection_end = None
            self.pdf_label.clear_selection()
            
    def load_pdf(self, file_path):
        """Load a PDF file"""
        try:
            self.current_pdf = self.pdf_processor.load_pdf(file_path)
            self.total_pages = len(self.current_pdf)
            self.current_page = 0
            self.page_spinbox.setMaximum(self.total_pages)
            self.display_current_page()
            self.update_navigation()
        except Exception as e:
            print(f"Error loading PDF: {e}")
            
    def display_current_page(self):
        """Display the current page"""
        if not self.current_pdf or self.current_page >= self.total_pages:
            return
            
        try:
            # Get page image with proper zoom
            page = self.current_pdf[self.current_page]
            
            # Calculate zoom factor
            zoom_factor = self.zoom_level
            
            # Create transformation matrix
            mat = fitz.Matrix(zoom_factor, zoom_factor)
            
            # Get page pixmap
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to QImage for better handling
            img_data = pix.tobytes("ppm")
            qimage = QImage()
            qimage.loadFromData(img_data)
            
            # Convert to QPixmap
            pixmap = QPixmap.fromImage(qimage)
            
            # Store the page rectangle for coordinate conversion
            self.page_rect = pixmap.rect()
            
            # Set the pixmap
            self.pdf_label.setPixmap(pixmap)
            
            # Resize the container to fit the pixmap
            self.pdf_container.resize(pixmap.size())
            
            # Force scroll area to update
            self.scroll_area.viewport().update()
            
            self.update_page_info()
            
        except Exception as e:
            print(f"Error displaying page: {e}")
            
    def make_pdf_wider(self):
        """Make the PDF panel wider"""
        if self.pdf_width_ratio < 0.9:  # Max 90% of window width
            self.pdf_width_ratio += 0.1
            self.adjust_pdf_width()
            
    def make_pdf_narrower(self):
        """Make the PDF panel narrower"""
        if self.pdf_width_ratio > 0.3:  # Min 30% of window width
            self.pdf_width_ratio -= 0.1
            self.adjust_pdf_width()
            
    def adjust_pdf_width(self):
        """Adjust the PDF panel width"""
        # This will be called by the main window to adjust splitter sizes
        # The actual implementation depends on how the main window handles the splitter
        pass
            
    def update_navigation(self):
        """Update navigation controls"""
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < self.total_pages - 1)
        self.page_spinbox.setValue(self.current_page + 1)
        self.update_page_info()
        
    def update_page_info(self):
        """Update page information display"""
        page_text = self.language_support.get_text("page") if self.language_support else "Page"
        self.page_label.setText(f"{page_text} {self.current_page + 1} of {self.total_pages}")
        self.page_changed.emit(self.current_page)
        
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
            self.update_navigation()
            
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_current_page()
            self.update_navigation()
            
    def go_to_page(self, page_num):
        """Go to specific page"""
        page_index = page_num - 1
        if 0 <= page_index < self.total_pages:
            self.current_page = page_index
            self.display_current_page()
            self.update_navigation()
            
    def set_zoom(self, zoom_percent):
        """Set zoom level"""
        self.zoom_level = zoom_percent / 100.0
        self.display_current_page()
        
    def mouse_press_event(self, event: QMouseEvent):
        """Handle mouse press for text selection"""
        if event.button() == Qt.LeftButton:
            self.selection_start = event.pos()
            self.selection_end = None
            self.pdf_label.set_selection(self.selection_start, self.selection_end)
            
    def mouse_move_event(self, event: QMouseEvent):
        """Handle mouse move for text selection"""
        if self.selection_start:
            self.selection_end = event.pos()
            self.pdf_label.set_selection(self.selection_start, self.selection_end)
            
    def mouse_release_event(self, event: QMouseEvent):
        """Handle mouse release for text selection"""
        if event.button() == Qt.LeftButton and self.selection_start:
            self.selection_end = event.pos()
            self.extract_selected_text()
            self.selection_start = None
            self.selection_end = None
            self.pdf_label.clear_selection()
            
    def extract_selected_text(self):
        """Extract text from selected region"""
        if not self.current_pdf or not self.selection_start or not self.selection_end:
            return
            
        try:
            # Get the page
            page = self.current_pdf[self.current_page]
            
            # Convert screen coordinates to PDF coordinates
            pdf_rect = self.screen_to_pdf_coords(self.selection_start, self.selection_end)
            
            if pdf_rect:
                # Extract text using PDF processor
                text = self.pdf_processor.extract_text_from_region(page, pdf_rect)
                
                if text.strip():
                    self.text_extracted.emit(text)
                    
        except Exception as e:
            print(f"Error extracting text: {e}")
            
    def screen_to_pdf_coords(self, start_pos, end_pos):
        """Convert screen coordinates to PDF coordinates"""
        if not self.page_rect:
            return None
            
        # Get the pixmap rect
        pixmap_rect = self.page_rect
        
        # Calculate selection rectangle in screen coordinates
        x1 = min(start_pos.x(), end_pos.x())
        y1 = min(start_pos.y(), end_pos.y())
        x2 = max(start_pos.x(), end_pos.x())
        y2 = max(start_pos.y(), end_pos.y())
        
        # Convert to PDF coordinates
        # Get the original page size
        page = self.current_pdf[self.current_page]
        page_rect = page.rect
        
        # Calculate scale factors
        scale_x = page_rect.width / pixmap_rect.width()
        scale_y = page_rect.height / pixmap_rect.height()
        
        # Convert coordinates
        pdf_x1 = x1 * scale_x
        pdf_y1 = y1 * scale_y
        pdf_x2 = x2 * scale_x
        pdf_y2 = y2 * scale_y
        
        return fitz.Rect(pdf_x1, pdf_y1, pdf_x2, pdf_y2)
