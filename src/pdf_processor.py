#!/usr/bin/env python3
"""
Simplified PDF processing for the cleaned up codebase
"""
import fitz
from typing import Optional, Dict, Any

class PDFProcessor:
    """Simplified PDF processing without legacy dependencies"""
    
    def __init__(self, use_advanced_extraction=False):
        # Simplified constructor - no legacy dependencies
        self.use_advanced_extraction = use_advanced_extraction
        
    def extract_text_from_region(self, pdf_path: str, page_num: int, rect: fitz.Rect, method: str = "standard") -> str:
        """
        Extract text from a specific region using PyMuPDF
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
            rect: Rectangle coordinates
            method: Extraction method ("standard" or "dictionary")
            
        Returns:
            Extracted text
        """
        doc = fitz.open(pdf_path)
        try:
            page = doc[page_num]
            
            if method == "dictionary":
                # Use dictionary method for detailed extraction
                text_dict = page.get_text("dict", clip=rect)
                text_parts = []
                
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span.get("text", "")
                                if text.strip():
                                    text_parts.append(text)
                
                return " ".join(text_parts)
            else:
                # Standard text extraction
                return page.get_text("text", clip=rect).strip()
                
        finally:
            doc.close()
    
    def get_page_image(self, pdf_path: str, page_num: int, zoom: float = 2.0) -> bytes:
        """Get page as image for display"""
        doc = fitz.open(pdf_path)
        try:
            page = doc[page_num]
            matrix = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix)
            return pix.tobytes("png")
        finally:
            doc.close()
    
    def get_page_count(self, pdf_path: str) -> int:
        """Get total number of pages"""
        doc = fitz.open(pdf_path)
        try:
            return doc.page_count
        finally:
            doc.close()
    
    def analyze_pdf_extraction_quality(self, pdf_path: str, page_num: int = 0) -> Dict[str, Any]:
        """Simple extraction quality analysis"""
        doc = fitz.open(pdf_path)
        try:
            page = doc[page_num]
            text = page.get_text("text")
            
            # Basic mathematical content detection
            math_symbols = ['Σ', '∫', '∇', '∂', 'α', 'β', 'π', '±', '≠', '≤', '≥', '∞']
            math_count = sum(1 for symbol in math_symbols if symbol in text)
            
            return {
                "method": "standard",
                "confidence": 80 if math_count > 0 else 90,
                "math_symbols_found": math_count,
                "text_length": len(text)
            }
        finally:
            doc.close()