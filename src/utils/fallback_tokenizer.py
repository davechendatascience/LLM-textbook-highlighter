#!/usr/bin/env python3
"""
Fallback tokenizer for when tiktoken is not available
"""

import re
from typing import List

class FallbackTokenizer:
    """Simple fallback tokenizer that works without internet access"""
    
    def __init__(self):
        """Initialize the fallback tokenizer"""
        # Simple word-based tokenization
        self.word_pattern = re.compile(r'\b\w+\b')
        self.punctuation_pattern = re.compile(r'[^\w\s]')
        
    def encode(self, text: str) -> List[int]:
        """
        Encode text to token IDs using simple word-based tokenization
        
        Args:
            text: Text to encode
            
        Returns:
            List of token IDs (simple hash-based)
        """
        if not text:
            return []
        
        # Split into words and punctuation
        words = self.word_pattern.findall(text)
        punctuation = self.punctuation_pattern.findall(text)
        
        # Combine and create simple token IDs
        tokens = []
        for word in words:
            # Simple hash-based token ID
            token_id = hash(word.lower()) % 100000
            tokens.append(token_id)
        
        for punct in punctuation:
            token_id = hash(punct) % 100000
            tokens.append(token_id)
        
        return tokens
    
    def decode(self, token_ids: List[int]) -> str:
        """
        Decode token IDs back to text (simplified)
        
        Args:
            token_ids: List of token IDs
            
        Returns:
            Decoded text (approximate)
        """
        # This is a simplified decode - in practice, you'd need a mapping
        # For now, just return a placeholder
        return f"[Decoded {len(token_ids)} tokens]"
    
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
        
        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk
            overlap: Number of overlapping tokens between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Simple character-based chunking as fallback
        chars_per_token = 4  # Rough estimate
        max_chars = max_tokens * chars_per_token
        overlap_chars = overlap * chars_per_token
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_chars
            
            # Extract chunk
            chunk = text[start:end]
            
            # Clean up boundaries
            if start > 0:  # Not the first chunk
                first_space = chunk.find(' ')
                if first_space != -1:
                    chunk = chunk[first_space + 1:]
            
            if end < len(text):  # Not the last chunk
                last_space = chunk.rfind(' ')
                if last_space != -1:
                    chunk = chunk[:last_space]
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            # Move start position with overlap
            start = end - overlap_chars
        
        return chunks

def get_fallback_tokenizer():
    """Get a fallback tokenizer when tiktoken is not available"""
    return FallbackTokenizer()
