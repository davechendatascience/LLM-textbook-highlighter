#!/usr/bin/env python3
"""
Multilingual tokenizer for better handling of non-English text
"""

import re
import sys
import unicodedata
from typing import List, Optional
import tiktoken


class MultilingualTokenizer:
    """Tokenizer that handles multiple languages better than tiktoken alone"""
    
    def __init__(self, fallback_to_tiktoken: bool = True):
        """
        Initialize the multilingual tokenizer
        
        Args:
            fallback_to_tiktoken: Whether to fall back to tiktoken if other methods fail
        """
        self.fallback_to_tiktoken = fallback_to_tiktoken
        self._tiktoken_encoder = None  # Lazy loading
        
        # Language-specific patterns for better tokenization
        self.language_patterns = {
            'chinese': re.compile(r'[\u4e00-\u9fff]+'),  # Chinese characters
            'japanese': re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]+'),  # Japanese
            'korean': re.compile(r'[\uac00-\ud7af]+'),  # Korean
            'thai': re.compile(r'[\u0e00-\u0e7f]+'),  # Thai
            'arabic': re.compile(r'[\u0600-\u06ff]+'),  # Arabic
            'hebrew': re.compile(r'[\u0590-\u05ff]+'),  # Hebrew
            'devanagari': re.compile(r'[\u0900-\u097f]+'),  # Devanagari (Hindi, etc.)
            'cyrillic': re.compile(r'[\u0400-\u04ff]+'),  # Cyrillic
        }
    
    @property
    def tiktoken_encoder(self):
        """Lazy load tiktoken encoder"""
        if self._tiktoken_encoder is None:
            print("📥 Loading tiktoken model...")
            try:
                # Set environment variable for tiktoken cache
                import os
                if getattr(sys, 'frozen', False):
                    # Running from PyInstaller executable
                    cache_dir = os.path.join(sys._MEIPASS, "tiktoken_cache")
                    os.makedirs(cache_dir, exist_ok=True)
                    os.environ['TIKTOKEN_CACHE_DIR'] = cache_dir
                    print(f"📁 Using tiktoken cache: {cache_dir}")
                
                self._tiktoken_encoder = tiktoken.get_encoding("cl100k_base")
                print("✅ tiktoken model loaded")
            except Exception as e:
                print(f"❌ Failed to load tiktoken model: {e}")
                # Try without cache directory
                try:
                    self._tiktoken_encoder = tiktoken.get_encoding("cl100k_base")
                    print("✅ tiktoken model loaded (fallback)")
                except Exception as e2:
                    print(f"❌ Fallback also failed: {e2}")
                    # Use fallback tokenizer
                    from src.utils.fallback_tokenizer import get_fallback_tokenizer
                    self._tiktoken_encoder = get_fallback_tokenizer()
                    print("✅ Using fallback tokenizer")
        return self._tiktoken_encoder
    
    def detect_language_robust(self, text: str) -> str:
        """
        Robust language detection using character counting
        More reliable than langdetect for short texts
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'zh', 'ja', etc.)
        """
        if not text:
            return 'en'
        
        # Count characters by script
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', text))
        korean_chars = len(re.findall(r'[\uac00-\ud7af]', text))
        arabic_chars = len(re.findall(r'[\u0600-\u06ff]', text))
        cyrillic_chars = len(re.findall(r'[\u0400-\u04ff]', text))
        thai_chars = len(re.findall(r'[\u0e00-\u0e7f]', text))
        devanagari_chars = len(re.findall(r'[\u0900-\u097f]', text))
        
        # Count total non-ASCII characters
        total_non_ascii = len(re.findall(r'[^\x00-\x7f]', text))
        
        # Determine language based on character counts
        if chinese_chars > 2:
            return 'zh'
        elif japanese_chars > 2:
            return 'ja'
        elif korean_chars > 2:
            return 'ko'
        elif arabic_chars > 2:
            return 'ar'
        elif cyrillic_chars > 2:
            return 'ru'
        elif thai_chars > 2:
            return 'th'
        elif devanagari_chars > 2:
            return 'hi'
        elif total_non_ascii > 5:
            return 'mixed'
        else:
            return 'en'
    
    def is_mixed_language(self, text: str) -> bool:
        """
        Check if text contains multiple language scripts
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains multiple language scripts
        """
        detected_scripts = set()
        
        for script_name, pattern in self.language_patterns.items():
            if pattern.search(text):
                detected_scripts.add(script_name)
        
        # Also check for Latin script
        if re.search(r'[a-zA-Z]', text):
            detected_scripts.add('latin')
        
        return len(detected_scripts) > 1
    
    def get_chunk_boundaries(self, text: str, max_tokens: int = 512, overlap: int = 50) -> List[tuple]:
        """
        Get chunk boundaries based on language-aware splitting
        This is the key improvement - we use language detection for boundaries,
        but still use tiktoken for actual tokenization
        
        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk
            overlap: Number of overlapping tokens between chunks
            
        Returns:
            List of (start_char, end_char) tuples
        """
        # First, get the actual token boundaries using tiktoken
        tokens = self.tiktoken_encoder.encode(text)
        
        if len(tokens) <= max_tokens:
            return [(0, len(text))]
        
        # Find character positions for token boundaries
        char_positions = []
        current_pos = 0
        
        # This is a simplified approach - in practice, you'd want to map tokens to char positions
        # For now, we'll use a reasonable approximation
        avg_chars_per_token = len(text) / len(tokens)
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = start + max_tokens
            
            # Convert token positions to character positions (approximate)
            start_char = int(start * avg_chars_per_token)
            end_char = min(int(end * avg_chars_per_token), len(text))
            
            # Adjust boundaries for better chunking
            start_char, end_char = self.adjust_chunk_boundaries(text, start_char, end_char)
            
            chunks.append((start_char, end_char))
            
            # Move start position with overlap
            start = end - overlap
        
        return chunks
    
    def adjust_chunk_boundaries(self, text: str, start_char: int, end_char: int) -> tuple:
        """
        Adjust chunk boundaries to break at better positions
        
        Args:
            text: Full text
            start_char: Start character position
            end_char: End character position
            
        Returns:
            Adjusted (start_char, end_char) tuple
        """
        # For CJK text, try to break at character boundaries
        if self.is_cjk_script(text[start_char:end_char]):
            # Find better start position
            for i in range(start_char, min(start_char + 50, end_char)):
                if not unicodedata.combining(text[i]):
                    start_char = i
                    break
            
            # Find better end position
            for i in range(end_char - 1, max(end_char - 50, start_char), -1):
                if not unicodedata.combining(text[i]):
                    end_char = i + 1
                    break
        else:
            # For other scripts, try to break at word boundaries
            # Find better start position
            first_space = text.find(' ', start_char, end_char)
            if first_space != -1 and first_space - start_char < 50:
                start_char = first_space + 1
            
            # Find better end position
            last_space = text.rfind(' ', start_char, end_char)
            if last_space != -1 and end_char - last_space < 50:
                end_char = last_space
        
        return start_char, end_char
    
    def is_cjk_script(self, text: str) -> bool:
        """
        Check if text contains CJK (Chinese, Japanese, Korean) characters
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains CJK characters
        """
        return bool(re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', text))
    
    def encode(self, text: str) -> List[int]:
        """
        Encode text to token IDs - always use tiktoken for compatibility
        
        Args:
            text: Text to encode
            
        Returns:
            List of token IDs
        """
        return self.tiktoken_encoder.encode(text)
    
    def decode(self, token_ids: List[int]) -> str:
        """
        Decode token IDs back to text
        
        Args:
            token_ids: List of token IDs
            
        Returns:
            Decoded text
        """
        return self.tiktoken_encoder.decode(token_ids)
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        return len(self.encode(text))
    
    def chunk_text(self, text: str, max_tokens: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks based on token count
        Uses language-aware boundaries but maintains tiktoken compatibility
        
        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk
            overlap: Number of overlapping tokens between chunks
            
        Returns:
            List of text chunks
        """
        # Get chunk boundaries
        boundaries = self.get_chunk_boundaries(text, max_tokens, overlap)
        
        # Extract chunks
        chunks = []
        for start_char, end_char in boundaries:
            chunk_text = text[start_char:end_char]
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
        
        return chunks


# Convenience function to get the appropriate tokenizer
def get_tokenizer(language: Optional[str] = None, use_multilingual: bool = True):
    """
    Get the appropriate tokenizer based on language and preferences
    
    Args:
        language: Specific language code (e.g., 'en', 'zh', 'ja')
        use_multilingual: Whether to use multilingual tokenizer
        
    Returns:
        Tokenizer instance
    """
    if use_multilingual:
        return MultilingualTokenizer()
    else:
        return tiktoken.get_encoding("cl100k_base")
