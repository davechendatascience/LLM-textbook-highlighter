import fitz  # PyMuPDF
import re
from PIL import Image
from transformers import TrOCRProcessor
from optimum.onnxruntime import ORTModelForVision2Seq
import io
import unicodedata
from nltk.tokenize import sent_tokenize
from collections import defaultdict

class MathOCRProcessor:
    def __init__(self):
        """Initialize the math OCR processor with pix2text model"""
        self.processor = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the pix2text OCR model for math formulas"""
        try:
            self.processor = TrOCRProcessor.from_pretrained('breezedeus/pix2text-mfr-1.5')
            self.model = ORTModelForVision2Seq.from_pretrained('breezedeus/pix2text-mfr-1.5', use_cache=False)
            print("Math OCR model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load math OCR model: {e}")
            self.processor = None
            self.model = None

    def is_math_heavy_page(self, page_text):
        """Determine if a page is math-heavy and would benefit from OCR"""
        if not page_text or len(page_text.strip()) < 5:
            return False
            
        # Count different types of math indicators
        advanced_math_symbols = ['∑', '∏', '∫', '√', '∞', '≠', '≤', '≥', '∴', '∵', '±', '×', '÷', '∈', '∅', '∇']
        basic_math_symbols = ['=', '+', '-', '*', '/']
        
        advanced_math_count = sum(page_text.count(sym) for sym in advanced_math_symbols)
        basic_math_count = sum(page_text.count(sym) for sym in basic_math_symbols)
        
        # Look for complex fraction patterns (not just simple ones like "1/2")
        complex_fraction_patterns = [
            r'[a-zA-Z0-9]+\s*/\s*[a-zA-Z0-9]+\s*[+\-*/]',  # Fractions in equations
            r'\([^)]+\)\s*/\s*\([^)]+\)',  # Parenthetical fractions
            r'[a-zA-Z]+\d*\s*/\s*[a-zA-Z]+\d*'  # Variable fractions like x/y
        ]
        complex_fraction_count = sum(len(re.findall(pattern, page_text)) for pattern in complex_fraction_patterns)
        
        # Look for actual mathematical equations (not just lists)
        equation_patterns = [
            r'[a-zA-Z]\s*=\s*[a-zA-Z0-9\+\-\*/\(\)]+',  # Variable equations
            r'\d+\s*[+\-*/]\s*\d+\s*=',  # Arithmetic equations
            r'[a-zA-Z]+\([^)]+\)\s*=',  # Function definitions
            r'∫|∑|∏',  # Integral/sum notation
        ]
        equation_count = sum(len(re.findall(pattern, page_text)) for pattern in equation_patterns)
        
        # Check word characteristics
        words = page_text.split()
        word_count = len(words)
        
        if word_count == 0:
            return False
            
        # Calculate different density measures
        advanced_math_density = advanced_math_count / word_count if word_count > 0 else 0
        equation_density = (equation_count + complex_fraction_count) / word_count if word_count > 0 else 0
        
        # Count English words vs math symbols
        english_words = [w for w in words if len(w) > 2 and w.isalpha() and w.lower() in 
                        ['the', 'and', 'or', 'in', 'of', 'to', 'for', 'with', 'by', 'is', 'are', 'we', 'can', 
                         'will', 'have', 'has', 'this', 'that', 'from', 'what', 'when', 'where', 'how']]
        english_ratio = len(english_words) / word_count if word_count > 0 else 0
        
        # Decision logic - be more conservative about using OCR
        # Only use OCR for clearly mathematical content, not mixed text
        if advanced_math_count > 2:  # Has advanced math symbols
            return True
        elif equation_count > 1:  # Has multiple equations
            return True
        elif complex_fraction_count > 0 and basic_math_count > 2:  # Complex fractions with math
            return True
        elif english_ratio < 0.3 and (basic_math_count > 3 or equation_count > 0):  # Low English, high math
            return True
        else:
            return False  # Likely mixed content or simple text with basic symbols

    def extract_page_with_ocr(self, page, page_num):
        """Extract text from a page using OCR, fallback to regular extraction"""
        if not self.processor or not self.model:
            # Fallback to regular extraction if OCR not available
            return self._extract_page_regular(page, page_num)
        
        try:
            # Convert page to image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR quality
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(img_data)).convert('RGB')
            
            # Apply OCR
            pixel_values = self.processor(images=[image], return_tensors="pt").pixel_values
            generated_ids = self.model.generate(pixel_values)
            ocr_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Post-process OCR text
            cleaned_text = self._clean_ocr_output(ocr_text)
            
            # Create synthetic word mapping for the OCR text
            words = self._create_synthetic_word_mapping(cleaned_text, page)
            
            return words, cleaned_text
            
        except Exception as e:
            print(f"OCR failed for page {page_num}, falling back to regular extraction: {e}")
            return self._extract_page_regular(page, page_num)

    def _extract_page_regular(self, page, page_num):
        """Regular PyMuPDF extraction as fallback"""
        words_raw = page.get_text("words")
        words = []
        for w in words_raw:
            words.append({
                "text": w[4],
                "x0": w[0],
                "y0": w[1],
                "x1": w[2],
                "y1": w[3],
                "block_no": w[5],
                "line_no": w[6],
                "word_no": w[7],
            })
        page_text = " ".join(w["text"] for w in words)
        return words, page_text

    def _clean_ocr_output(self, ocr_text):
        """Clean OCR output that treats everything as math"""
        if not ocr_text:
            return ""
        
        # The pix2text model often wraps everything in LaTeX, even simple text
        # We need to be more aggressive in cleaning this up
        
        # Remove common LaTeX artifacts for simple text
        cleaned = ocr_text
        
        # Remove \begin{aligned} and \end{aligned} blocks if they contain simple text
        aligned_pattern = r'\\begin\{aligned\}(.*?)\\end\{aligned\}'
        matches = re.findall(aligned_pattern, cleaned, re.DOTALL)
        for match in matches:
            # Check if the content inside is actually simple text
            inner_content = match.strip()
            if self._contains_mostly_simple_text(inner_content):
                # Extract just the text content
                simple_text = self._extract_text_from_latex(inner_content)
                cleaned = cleaned.replace(f'\\begin{{aligned}}{match}\\end{{aligned}}', simple_text)
        
        # Remove excessive LaTeX formatting around simple words
        # Remove \mathrm{...} around simple text
        cleaned = re.sub(r'\\mathrm\s*\{\s*([A-Za-z\s:;,.\-+*=()]+?)\s*\}', r'\1', cleaned)
        
        # Remove standalone braces and LaTeX artifacts
        cleaned = re.sub(r'\{\s*\}\s*&\s*\{\s*\{\s*\}', '', cleaned)  # Remove { } & { { }
        cleaned = re.sub(r'\\\\', '\n', cleaned)  # Convert LaTeX line breaks
        cleaned = re.sub(r'\s*&\s*', ' ', cleaned)  # Remove alignment markers
        
        # Clean up specific patterns that indicate over-processing
        cleaned = re.sub(r'\\[{}]', '', cleaned)  # Remove escaped braces
        cleaned = re.sub(r'\{\s*\}', '', cleaned)  # Remove empty braces
        
        # Remove excessive spacing and normalize
        lines = cleaned.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = re.sub(r'\s+', ' ', line.strip())
            if line and line not in ['{', '}', '\\', '&']:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def _contains_mostly_simple_text(self, text):
        """Check if LaTeX content actually contains mostly simple text"""
        # Remove LaTeX commands to get the actual content
        content = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
        content = re.sub(r'[\\{}]', '', content)
        content = re.sub(r'&', '', content)
        content = content.strip()
        
        if not content:
            return False
            
        # Check if it's mostly letters and basic punctuation
        letter_count = sum(1 for c in content if c.isalpha())
        total_chars = len(re.sub(r'\s', '', content))
        
        if total_chars == 0:
            return False
            
        letter_ratio = letter_count / total_chars
        return letter_ratio > 0.6
    
    def _extract_text_from_latex(self, latex_content):
        """Extract plain text from LaTeX content"""
        # Remove LaTeX commands and extract just the text
        text = latex_content
        
        # Remove \mathrm{...} and extract content
        text = re.sub(r'\\mathrm\s*\{\s*([^}]+)\s*\}', r'\1', text)
        
        # Remove other LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
        text = re.sub(r'\\\\', '\n', text)
        text = re.sub(r'[\\{}]', '', text)
        text = re.sub(r'\s*&\s*', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def _is_likely_text_line(self, line):
        """Determine if a line is likely regular text (not a formula)"""
        if not line:
            return False
            
        # Remove math delimiters for analysis
        clean_line = re.sub(r'[\$\\()\[\]{}]', ' ', line)
        words = clean_line.split()
        
        if not words:
            return False
        
        # Count letters vs symbols/numbers
        letter_count = sum(1 for char in clean_line if char.isalpha())
        total_chars = len(re.sub(r'\s', '', clean_line))
        
        if total_chars == 0:
            return False
            
        letter_ratio = letter_count / total_chars
        
        # If mostly letters and contains common English words, likely text
        common_words = ['the', 'and', 'or', 'in', 'of', 'to', 'for', 'with', 'by', 'is', 'are', 'we', 'can']
        has_common_words = any(word.lower() in common_words for word in words)
        
        return letter_ratio > 0.6 or (letter_ratio > 0.4 and has_common_words)

    def _create_synthetic_word_mapping(self, text, page):
        """Create synthetic word bounding boxes for OCR text"""
        words = []
        text_words = text.split()
        
        # Get page dimensions
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height
        
        # Estimate word positions (simple left-to-right, top-to-bottom layout)
        words_per_line = max(1, int(page_width / 80))  # Rough estimate
        line_height = 20
        word_width = 60
        margin = 50
        
        for i, word in enumerate(text_words):
            line_num = i // words_per_line
            word_in_line = i % words_per_line
            
            x0 = margin + word_in_line * word_width
            x1 = x0 + len(word) * 8  # Rough character width
            y0 = margin + line_num * line_height
            y1 = y0 + 15
            
            words.append({
                "text": word,
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "block_no": 0,
                "line_no": line_num,
                "word_no": word_in_line,
            })
        
        return words

def extract_with_smart_ocr(pdf_path, chunk_size=40, ocr_threshold=0.1):
    """
    Extract text with intelligent OCR usage for math-heavy pages
    
    Args:
        pdf_path: Path to PDF file
        chunk_size: Sentences per chunk
        ocr_threshold: Math density threshold for OCR usage
    """
    doc = fitz.open(pdf_path)
    page_word_map = {}
    sentences = []
    global_idx = 0
    
    # Initialize OCR processor
    ocr_processor = MathOCRProcessor()
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # First try regular extraction to assess math content
        words_regular, page_text_regular = ocr_processor._extract_page_regular(page, page_num)
        
        # Decide whether to use OCR based on math density
        if ocr_processor.is_math_heavy_page(page_text_regular):
            print(f"Page {page_num + 1}: Math-heavy content detected, using OCR")
            words, page_text = ocr_processor.extract_page_with_ocr(page, page_num)
        else:
            print(f"Page {page_num + 1}: Regular text, using PyMuPDF")
            words, page_text = words_regular, page_text_regular
        
        page_word_map[page_num] = words
        
        if not words or not page_text.strip():
            continue
        
        # Process sentences
        sents = sent_tokenize(page_text)
        word_pointer = 0
        
        for s in sents:
            s_words = s.split()
            indices = []
            idx_pointer = word_pointer
            
            for word in s_words:
                target = normalize_word(word)
                while idx_pointer < len(words):
                    source = normalize_word(words[idx_pointer]["text"])
                    if source == target:
                        indices.append(idx_pointer)
                        idx_pointer += 1
                        break
                    idx_pointer += 1
            
            if indices:
                sentences.append({
                    "global_idx": global_idx,
                    "page_num": page_num,
                    "sentence": s,
                    "word_indices": indices
                })
                global_idx += 1
                word_pointer = idx_pointer
    
    # Chunk sentences for LLM prompt
    chunks = []
    for start in range(0, len(sentences), chunk_size):
        chunks.append(sentences[start:start+chunk_size])
    
    doc.close()
    return sentences, chunks, page_word_map

def normalize_word(word):
    """Normalize a word for robust matching"""
    word_norm = unicodedata.normalize('NFKD', word)
    word_norm = word_norm.encode('ascii', 'ignore').decode("ascii")
    word_norm = re.sub(r"^\W+|\W+$", "", word_norm.lower())
    return word_norm