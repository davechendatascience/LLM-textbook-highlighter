"""
OCR-based text extraction for mathematical PDFs
"""
import os
import tempfile
import fitz
from typing import Optional, Dict, Any, List
from PIL import Image

class OCRProcessor:
    """Lightweight OCR processor using EasyOCR for mathematical text extraction"""
    
    def __init__(self):
        self._reader = None
        self._available = None
    
    def is_available(self) -> bool:
        """Check if OCR is available"""
        if self._available is None:
            try:
                import easyocr
                self._available = True
            except ImportError:
                self._available = False
        return self._available
    
    def _get_reader(self):
        """Lazy initialization of EasyOCR reader"""
        if self._reader is None and self.is_available():
            try:
                import easyocr
                self._reader = easyocr.Reader(['en'], verbose=False)
            except Exception as e:
                print(f"Failed to initialize EasyOCR: {e}")
                self._available = False
        return self._reader
    
    def extract_text_from_rect(self, page: fitz.Page, rect: fitz.Rect, zoom: float = 2.0) -> Optional[Dict[str, Any]]:
        """
        Extract text from a specific rectangle using OCR
        
        Args:
            page: PyMuPDF page object
            rect: Rectangle to extract from
            zoom: Zoom factor for better OCR accuracy (default 2.0)
            
        Returns:
            Dictionary with OCR results or None if OCR unavailable
        """
        if not self.is_available():
            return None
        
        reader = self._get_reader()
        if reader is None:
            return None
        
        try:
            # Convert the specified rectangle to high-res image
            matrix = fitz.Matrix(zoom, zoom)
            clip_rect = rect
            
            # Get pixmap for the clipped area
            pix = page.get_pixmap(matrix=matrix, clip=clip_rect)
            
            # Convert to PIL Image
            img_data = pix.pil_tobytes(format="PNG")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_file.write(img_data)
                temp_path = temp_file.name
            
            try:
                # Run OCR
                results = reader.readtext(temp_path)
                
                # Process results
                text_parts = []
                all_text = ""
                confidence_scores = []
                
                for bbox, text, confidence in results:
                    if confidence > 0.5:  # Filter low-confidence results
                        text_parts.append({
                            'text': text,
                            'confidence': confidence,
                            'bbox': bbox
                        })
                        all_text += text + " "
                        confidence_scores.append(confidence)
                
                avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
                
                return {
                    'text': all_text.strip(),
                    'parts': text_parts,
                    'avg_confidence': avg_confidence,
                    'method': 'easyocr'
                }
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"OCR extraction failed: {e}")
            return None
    
    def extract_with_fallback(self, page: fitz.Page, rect: fitz.Rect) -> Dict[str, Any]:
        """
        Extract text with OCR fallback to traditional extraction
        
        Args:
            page: PyMuPDF page object  
            rect: Rectangle to extract from
            
        Returns:
            Dictionary with extraction results
        """
        # Traditional extraction first (fast baseline)
        try:
            fitz_text = page.get_text("text", clip=rect).strip()
        except Exception as e:
            fitz_text = ""
            print(f"Traditional extraction failed: {e}")
        
        # OCR extraction
        ocr_result = self.extract_text_from_rect(page, rect)
        
        # Combine results
        result = {
            'fitz_text': fitz_text,
            'fitz_length': len(fitz_text),
            'ocr_available': self.is_available(),
            'method_used': 'fitz_only'
        }
        
        if ocr_result:
            result.update({
                'ocr_text': ocr_result['text'],
                'ocr_confidence': ocr_result['avg_confidence'],
                'ocr_parts': len(ocr_result['parts']),
                'method_used': 'fitz_and_ocr'
            })
            
            # Use OCR if it found more content or higher confidence mathematical text
            ocr_text = ocr_result['text']
            
            # Debug the recommendation logic
            print(f"DEBUG OCR: fitz_len={len(fitz_text)}, ocr_len={len(ocr_text)}, confidence={ocr_result['avg_confidence']:.2f}")
            
            # More aggressive OCR preference for mathematical content
            math_analysis = self.analyze_mathematical_content(ocr_text)
            fitz_math_analysis = self.analyze_mathematical_content(fitz_text)
            
            should_use_ocr = (
                # High confidence OCR
                ocr_result['avg_confidence'] > 0.7 or
                # OCR found more mathematical content
                math_analysis['complexity_score'] > fitz_math_analysis['complexity_score'] or
                # OCR text is significantly longer
                len(ocr_text) > len(fitz_text) * 1.2
            )
            
            if should_use_ocr:
                result['recommended_text'] = ocr_text
                result['method_used'] = 'ocr_preferred'
                print(f"DEBUG OCR: Using OCR text (math_score: {math_analysis['complexity_score']} vs {fitz_math_analysis['complexity_score']})")
            else:
                result['recommended_text'] = fitz_text
                print(f"DEBUG OCR: Using fitz text")
        else:
            result['recommended_text'] = fitz_text
            
        return result
    
    def analyze_mathematical_content(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for mathematical content patterns
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with mathematical content analysis
        """
        # Mathematical indicators
        math_symbols = ['Σ', '∫', '∇', '∂', 'α', 'β', 'γ', 'δ', 'θ', 'λ', 'μ', 'π', 'σ', 'ω', 'Ω']
        operators = ['±', '×', '÷', '≈', '≠', '≤', '≥', '∞', '√']
        fractions = ['½', '¼', '¾', '⅓', '⅔', '⅛']
        
        # Count occurrences
        symbol_count = sum(1 for symbol in math_symbols if symbol in text)
        operator_count = sum(1 for op in operators if op in text)
        fraction_count = sum(1 for frac in fractions if frac in text)
        
        # Look for fraction patterns like "a/b"
        import re
        inline_fractions = len(re.findall(r'\b\w+/\w+\b', text))
        
        # Mathematical complexity score
        complexity = symbol_count + operator_count + fraction_count + inline_fractions
        
        return {
            'has_math_symbols': symbol_count > 0,
            'has_operators': operator_count > 0,
            'has_fractions': fraction_count > 0 or inline_fractions > 0,
            'symbol_count': symbol_count,
            'operator_count': operator_count,
            'fraction_count': fraction_count,
            'inline_fractions': inline_fractions,
            'complexity_score': complexity,
            'is_mathematical': complexity > 0
        }


# Global OCR processor instance
_ocr_processor = None

def get_ocr_processor() -> OCRProcessor:
    """Get the global OCR processor instance"""
    global _ocr_processor
    if _ocr_processor is None:
        _ocr_processor = OCRProcessor()
    return _ocr_processor