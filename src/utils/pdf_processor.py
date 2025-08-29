"""
PDF Processor Utility
Handles PDF loading and text extraction
"""

import fitz
from typing import List, Optional


class PDFProcessor:
    """Handles PDF processing operations"""
    
    def __init__(self):
        self.current_pdf = None
        
    def load_pdf(self, file_path: str) -> fitz.Document:
        """Load a PDF file"""
        try:
            self.current_pdf = fitz.open(file_path)
            return self.current_pdf
        except Exception as e:
            print(f"Error loading PDF: {e}")
            raise
            
    def extract_text_from_region(self, page: fitz.Page, rect: fitz.Rect) -> str:
        """Extract text from a specific region on a page"""
        try:
            # Extract text from the specified rectangle
            text = page.get_text("text", clip=rect)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from region: {e}")
            return ""
            
    def extract_text_from_page(self, page: fitz.Page) -> str:
        """Extract all text from a page"""
        try:
            text = page.get_text("text")
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from page: {e}")
            return ""
            
    def get_page_count(self) -> int:
        """Get the total number of pages"""
        if self.current_pdf:
            return len(self.current_pdf)
        return 0
        
    def get_page(self, page_num: int) -> Optional[fitz.Page]:
        """Get a specific page"""
        if self.current_pdf and 0 <= page_num < len(self.current_pdf):
            return self.current_pdf[page_num]
        return None
        
    def close(self):
        """Close the current PDF"""
        if self.current_pdf:
            self.current_pdf.close()
            self.current_pdf = None
