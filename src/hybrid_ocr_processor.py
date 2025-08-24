"""
Hybrid OCR processor that combines general OCR with specialized math OCR
Strategy: Use general OCR first, then identify and re-process math regions with pix2text
"""

import fitz
import re
from PIL import Image
import io
import unicodedata
from collections import defaultdict

class HybridOCRProcessor:
    def __init__(self):
        """Initialize both general OCR and math OCR processors"""
        self.general_ocr = None
        self.math_ocr = None
        self._load_processors()
    
    def _load_processors(self):
        """Load general OCR (Tesseract/EasyOCR) and math OCR (pix2text)"""
        # Try Tesseract first (lighter weight)
        try:
            import pytesseract
            # Test if tesseract executable is available
            try:
                pytesseract.get_tesseract_version()
                self.general_ocr = "tesseract"
                print("General OCR (Tesseract) loaded successfully")
            except:
                print("Tesseract executable not found. Please install Tesseract:")
                print("Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
                print("Or install via: choco install tesseract (if you have Chocolatey)")
                self.general_ocr = None
        except ImportError:
            print("pytesseract not available. Install with: pip install pytesseract")
            self.general_ocr = None
        
        # Fallback to EasyOCR if Tesseract not available
        if not self.general_ocr:
            try:
                import easyocr
                self.general_ocr = easyocr.Reader(['en'])
                print("Fallback: General OCR (EasyOCR) loaded successfully")
            except ImportError:
                print("EasyOCR also not available. Install with: pip install easyocr")
                self.general_ocr = None
        
        # Load math OCR (pix2text)
        try:
            from transformers import TrOCRProcessor
            from optimum.onnxruntime import ORTModelForVision2Seq
            self.math_processor = TrOCRProcessor.from_pretrained('breezedeus/pix2text-mfr-1.5')
            self.math_model = ORTModelForVision2Seq.from_pretrained('breezedeus/pix2text-mfr-1.5', use_cache=False)
            print("Math OCR (pix2text) loaded successfully")
        except Exception as e:
            print(f"Math OCR not available: {e}")
            self.math_processor = None
            self.math_model = None

    def is_scanned_document(self, pdf_path, check_pages=3):
        """Detect if document is scanned (image-based) vs text-based"""
        doc = fitz.open(pdf_path)
        total_text_length = 0
        total_area = 0
        
        for page_num in range(min(check_pages, len(doc))):
            page = doc[page_num]
            text = page.get_text().strip()
            total_text_length += len(text)
            total_area += page.rect.width * page.rect.height
        
        doc.close()
        
        # If very little text extracted relative to page area, likely scanned
        text_density = total_text_length / total_area if total_area > 0 else 0
        is_scanned = text_density < 0.01  # Threshold for "scanned"
        
        print(f"Document analysis: text_density={text_density:.6f}, is_scanned={is_scanned}")
        return is_scanned

    def extract_region_with_hybrid_ocr(self, page, rect):
        """
        Extract text from a region using two-stage OCR:
        1. General OCR for the whole region
        2. Math OCR for identified math sub-regions
        3. Merge results intelligently
        """
        if not self.general_ocr:
            return self._fallback_extraction(page, rect)
        
        try:
            # Stage 1: General OCR for the whole region
            general_result = self._extract_with_general_ocr(page, rect)
            
            if not general_result:
                return self._fallback_extraction(page, rect)
            
            # Stage 2: Identify math regions in the general OCR result
            math_regions = self._identify_math_regions_in_text(general_result)
            
            if not math_regions or not (self.math_processor and self.math_model):
                # No math regions or math OCR unavailable, return general OCR result
                return {
                    'text': general_result,
                    'method': 'general_ocr_only',
                    'confidence': 0.8
                }
            
            # Stage 3: Re-process math regions with specialized OCR
            enhanced_result = self._enhance_math_regions(page, rect, general_result, math_regions)
            
            return {
                'text': enhanced_result,
                'method': 'hybrid_ocr',
                'confidence': 0.9,
                'math_regions_found': len(math_regions)
            }
            
        except Exception as e:
            print(f"Hybrid OCR failed: {e}")
            return self._fallback_extraction(page, rect)

    def _extract_with_general_ocr(self, page, rect):
        """Extract text using general OCR (EasyOCR or Tesseract)"""
        # Convert page region to image
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
        pix = page.get_pixmap(matrix=mat, clip=rect)
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data)).convert('RGB')
        
        if hasattr(self.general_ocr, 'readtext'):  # EasyOCR
            results = self.general_ocr.readtext(img_data)
            # Combine all text results
            text_parts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Filter low-confidence results
                    text_parts.append(text)
            return ' '.join(text_parts)
        
        elif self.general_ocr == "tesseract":  # Tesseract
            import pytesseract
            return pytesseract.image_to_string(image)
        
        return ""

    def _identify_math_regions_in_text(self, text):
        """
        Identify regions in the general OCR text that likely contain math
        Returns list of (start_pos, end_pos, math_type) tuples
        """
        math_regions = []
        
        # Pattern 1: Equations (variable = expression)
        equation_pattern = r'[a-zA-Z]\s*=\s*[a-zA-Z0-9+\-*/()^]+'
        for match in re.finditer(equation_pattern, text):
            math_regions.append((match.start(), match.end(), 'equation'))
        
        # Pattern 2: Complex fractions
        fraction_pattern = r'\([^)]+\)\s*/\s*\([^)]+\)|[a-zA-Z0-9]+\s*/\s*[a-zA-Z0-9]+\s*[+\-*/]'
        for match in re.finditer(fraction_pattern, text):
            math_regions.append((match.start(), match.end(), 'fraction'))
        
        # Pattern 3: Mathematical symbols that general OCR might miss
        symbol_pattern = r'[∑∏∫√±×÷≠≤≥∈∅∇]'
        for match in re.finditer(symbol_pattern, text):
            # Expand to include surrounding context
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            math_regions.append((start, end, 'symbols'))
        
        # Pattern 4: Dense mathematical expressions
        dense_math_pattern = r'[a-zA-Z0-9\s]*[+\-*/=]{2,}[a-zA-Z0-9\s]*'
        for match in re.finditer(dense_math_pattern, text):
            if len(match.group()) > 5:  # Avoid single operators
                math_regions.append((match.start(), match.end(), 'expression'))
        
        # Merge overlapping regions
        math_regions = self._merge_overlapping_regions(math_regions)
        
        print(f"Identified {len(math_regions)} math regions: {[r[2] for r in math_regions]}")
        return math_regions

    def _merge_overlapping_regions(self, regions):
        """Merge overlapping or adjacent math regions"""
        if not regions:
            return []
        
        # Sort by start position
        regions.sort(key=lambda x: x[0])
        merged = [regions[0]]
        
        for current in regions[1:]:
            last = merged[-1]
            # If regions overlap or are close (within 10 characters), merge them
            if current[0] <= last[1] + 10:
                # Merge: extend the end position, combine types
                new_end = max(last[1], current[1])
                combined_type = f"{last[2]},{current[2]}" if last[2] != current[2] else last[2]
                merged[-1] = (last[0], new_end, combined_type)
            else:
                merged.append(current)
        
        return merged

    def _enhance_math_regions(self, page, rect, general_text, math_regions):
        """
        Re-process identified math regions with specialized math OCR
        and merge back into the general text
        """
        enhanced_text = general_text
        
        # Process math regions from right to left to preserve indices
        for start_pos, end_pos, math_type in reversed(math_regions):
            try:
                # Extract just the math region for specialized OCR
                math_text_region = general_text[start_pos:end_pos]
                
                # Estimate where this text appears in the image (rough approximation)
                # For now, we'll re-process the whole region - in practice, you'd want
                # to estimate sub-region coordinates
                math_ocr_result = self._extract_math_subregion(page, rect, math_text_region)
                
                if math_ocr_result and len(math_ocr_result.strip()) > 0:
                    # Replace the general OCR result with math OCR result for this region
                    enhanced_text = (enhanced_text[:start_pos] + 
                                   math_ocr_result + 
                                   enhanced_text[end_pos:])
                    
                    print(f"Enhanced {math_type} region: '{math_text_region}' → '{math_ocr_result}'")
                
            except Exception as e:
                print(f"Failed to enhance math region: {e}")
                continue
        
        return enhanced_text

    def _extract_math_subregion(self, page, rect, context_text):
        """Extract a sub-region using math OCR"""
        try:
            # For simplicity, re-process the whole region with math OCR
            # In practice, you'd estimate sub-region coordinates based on text layout
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat, clip=rect)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data)).convert('RGB')
            
            # Apply math OCR
            pixel_values = self.math_processor(images=[image], return_tensors="pt").pixel_values
            generated_ids = self.math_model.generate(pixel_values)
            math_result = self.math_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Clean the math OCR result
            cleaned_result = self._clean_math_ocr_output(math_result, context_text)
            return cleaned_result
            
        except Exception as e:
            print(f"Math sub-region OCR failed: {e}")
            return ""

    def _clean_math_ocr_output(self, math_result, context):
        """Clean math OCR output based on context from general OCR"""
        if not math_result:
            return ""
        
        # If the context suggests this should be simple text, clean aggressively
        if self._context_suggests_simple_text(context):
            # Remove LaTeX formatting and return plain text
            cleaned = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', math_result)
            cleaned = re.sub(r'[\\{}]', '', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned.strip())
            return cleaned
        else:
            # Keep mathematical formatting but clean up excessive LaTeX
            cleaned = math_result
            cleaned = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', cleaned)
            cleaned = re.sub(r'\\text\{([^}]*)\}', r'\1', cleaned)
            return cleaned.strip()

    def _context_suggests_simple_text(self, context):
        """Check if the context suggests this should be plain text, not math"""
        if not context:
            return False
        
        # Look for common English words
        common_words = ['the', 'and', 'or', 'in', 'of', 'to', 'for', 'with', 'is', 'are']
        context_lower = context.lower()
        word_count = sum(1 for word in common_words if word in context_lower)
        
        return word_count > 2  # If multiple common English words, likely text

    def _fallback_extraction(self, page, rect):
        """Fallback to regular fitz extraction"""
        try:
            text = page.get_text("text", clip=rect).strip()
            return {
                'text': text,
                'method': 'fitz_fallback',
                'confidence': 0.7
            }
        except Exception as e:
            return {
                'text': "",
                'method': 'failed',
                'confidence': 0.0,
                'error': str(e)
            }

def normalize_word(word):
    """Normalize a word for robust matching"""
    word_norm = unicodedata.normalize('NFKD', word)
    word_norm = word_norm.encode('ascii', 'ignore').decode("ascii")
    word_norm = re.sub(r"^\W+|\W+$", "", word_norm.lower())
    return word_norm