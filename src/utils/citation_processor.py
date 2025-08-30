#!/usr/bin/env python3
"""
Generic Citation Processor
Handles citations from different LLM APIs (Perplexity, Gemini, etc.)
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Citation:
    """Represents a citation with its number and URL"""
    number: int
    url: str
    text: str = ""
    source: str = ""


class CitationProcessor:
    """Generic citation processor for different LLM APIs"""
    
    def __init__(self):
        # Citation patterns for different LLM APIs
        self.citation_patterns = {
            'perplexity': [
                r'\[(\d+)\]',                 # [1], [2], [3] - Perplexity's actual format
                r'\[\[(\d+)\]\]\(([^)]+)\)',  # [[1]](url) - fallback
                r'\[(\d+)\]\(([^)]+)\)',      # [1](url) - fallback
            ],
            'gemini': [
                r'\[(\d+)\]\(([^)]+)\)',      # [1](url)
                r'<a href="([^"]+)">\[(\d+)\]</a>',  # <a href="url">[1]</a>
            ],
            'openai': [
                r'\[(\d+)\]\(([^)]+)\)',      # [1](url)
                r'<a href="([^"]+)">\[(\d+)\]</a>',  # <a href="url">[1]</a>
            ],
            'generic': [
                r'\[(\d+)\]',                 # Plain citations [1], [2], [3]
                r'\[\[(\d+)\]\]\(([^)]+)\)',  # Double brackets
                r'\[(\d+)\]\(([^)]+)\)',      # Single brackets
                r'<a href="([^"]+)">\[(\d+)\]</a>',  # HTML links
            ]
        }
        
        # Reference section patterns
        self.reference_patterns = [
            r'## References?\s*\n(.*?)(?=\n\n|\n#|\Z)',
            r'### References?\s*\n(.*?)(?=\n\n|\n#|\Z)',
            r'References?\s*\n(.*?)(?=\n\n|\n#|\Z)',
            r'---\s*\n\*\*References?\*\*:\s*\n(.*?)(?=\n\n|\n#|\Z)',  # Perplexity format
            r'\*\*References?\*\*:\s*\n(.*?)(?=\n\n|\n#|\Z)',  # Perplexity format without dashes
        ]
    
    def extract_citations(self, text: str, api_type: str = 'generic') -> List[Citation]:
        """Extract citations from text based on API type"""
        citations = []
        patterns = self.citation_patterns.get(api_type, self.citation_patterns['generic'])
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                if len(match) == 2:
                    if pattern == r'<a href="([^"]+)">\[(\d+)\]</a>':
                        # HTML link format: url, number
                        url, number = match
                    else:
                        # Markdown format: number, url
                        number, url = match
                    
                    try:
                        citation = Citation(
                            number=int(number),
                            url=url.strip(),
                            source=api_type
                        )
                        citations.append(citation)
                    except ValueError:
                        continue
        
        # Remove duplicates and sort by number
        unique_citations = {}
        for citation in citations:
            if citation.number not in unique_citations:
                unique_citations[citation.number] = citation
        
        return sorted(unique_citations.values(), key=lambda x: x.number)
    
    def extract_references(self, text: str) -> List[str]:
        """Extract reference section from text"""
        references = []
        
        for pattern in self.reference_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if matches:
                reference_text = matches[0].strip()
                print(f"🔍 Found reference section: {reference_text[:200]}...")
                
                # Split into individual references
                ref_lines = [line.strip() for line in reference_text.split('\n') if line.strip()]
                
                # Handle Perplexity's format: "- Google Developers: Linear regression and gradient descent explanation[1]"
                for line in ref_lines:
                    if line.startswith('- ') or line.startswith('* '):
                        # Remove the bullet point and citation number
                        ref_text = re.sub(r'^[-*]\s*', '', line)  # Remove bullet
                        ref_text = re.sub(r'\[\d+\]$', '', ref_text)  # Remove citation number at end
                        ref_text = ref_text.strip()
                        if ref_text:
                            references.append(ref_text)
                    else:
                        references.append(line)
                break
        
        return references
    
    def normalize_citations(self, text: str, api_type: str = 'generic') -> str:
        """Convert citations to standard internal format [1](#ref1)"""
        patterns = self.citation_patterns.get(api_type, self.citation_patterns['generic'])
        
        # Process each pattern to convert to standard format
        for pattern in patterns:
            if pattern == r'\[\[(\d+)\]\]\(([^)]+)\)':
                # Double bracket format: [[1]](url) -> [1](#ref1)
                text = re.sub(pattern, r'[\1](#ref\1)', text)
            elif pattern == r'\[(\d+)\]\(([^)]+)\)':
                # Single bracket format: [1](url) -> [1](#ref1)
                text = re.sub(pattern, r'[\1](#ref\1)', text)
            elif pattern == r'<a href="([^"]+)">\[(\d+)\]</a>':
                # HTML format: <a href="url">[1]</a> -> [1](#ref1)
                text = re.sub(pattern, r'[\2](#ref\2)', text)
            elif pattern == r'\[(\d+)\]':
                # Plain citations: [1] -> [1](#ref1) (only if not already in a link)
                # This handles Perplexity's actual format
                text = re.sub(r'(?<!\]\()\[(\d+)\](?!\()', r'[\1](#ref\1)', text)
        
        # Fix consecutive citation formatting
        text = self.fix_consecutive_citations(text)
        
        return text
    
    def fix_consecutive_citations(self, text: str) -> str:
        """Fix consecutive citation formatting to ensure proper spacing"""
        # Pattern to match consecutive citations without spaces: [1](#ref1)[2](#ref2)
        pattern = r'\[(\d+)\]\(#ref\1\)\[(\d+)\]\(#ref\2\)'
        
        def replace_consecutive(match):
            num1, num2 = match.groups()
            # Add space between consecutive citations for better readability
            return f'[{num1}](#ref{num1}) [{num2}](#ref{num2})'
        
        # Apply the fix multiple times to handle longer sequences
        fixed_text = text
        for _ in range(10):  # Limit iterations to prevent infinite loops
            new_text = re.sub(pattern, replace_consecutive, fixed_text)
            if new_text == fixed_text:
                break
            fixed_text = new_text
        
        return fixed_text
    
    def fix_html_citations(self, html_content: str) -> str:
        """Fix inconsistent citation display in HTML"""
        # Fix citations that display as numbers without brackets
        # Use DOTALL flag to handle multi-line citations
        
        # Pattern for internal citations: <a href="#ref1">1</a>
        internal_pattern = r'<a href="#ref(\d+)">(\d+)</a>'
        internal_replacement = r'<a href="#ref\1">[\2]</a>'
        fixed_html = re.sub(internal_pattern, internal_replacement, html_content, flags=re.DOTALL)
        
        # Pattern for external citations: <a href="https://example.com">1</a>
        external_pattern = r'<a href="([^"]+)">(\d+)</a>'
        external_replacement = r'<a href="\1">[\2]</a>'
        fixed_html = re.sub(external_pattern, external_replacement, fixed_html, flags=re.DOTALL)
        
        # Pattern for incomplete internal citations: href="#ref1">1</a> (missing <a)
        incomplete_internal_pattern = r'href="#ref(\d+)">(\d+)</a>'
        incomplete_internal_replacement = r'href="#ref\1">[\2]</a>'
        fixed_html = re.sub(incomplete_internal_pattern, incomplete_internal_replacement, fixed_html, flags=re.DOTALL)
        
        # Pattern for incomplete external citations: href="https://example.com">1</a> (missing <a)
        incomplete_external_pattern = r'href="([^"]+)">(\d+)</a>'
        incomplete_external_replacement = r'href="\1">[\2]</a>'
        fixed_html = re.sub(incomplete_external_pattern, incomplete_external_replacement, fixed_html, flags=re.DOTALL)
        
        # Also fix any citations that might have different patterns with whitespace
        patterns_to_fix = [
            (r'<a href="#ref(\d+)">\s*(\d+)\s*</a>', r'<a href="#ref\1">[\2]</a>'),
            (r'<a href="([^"]+)">\s*(\d+)\s*</a>', r'<a href="\1">[\2]</a>'),
        ]
        
        for pattern, replacement in patterns_to_fix:
            fixed_html = re.sub(pattern, replacement, fixed_html, flags=re.DOTALL)
        
        return fixed_html
    
    def create_reference_section(self, citations: List[Citation], references: List[str]) -> str:
        """Create a standardized reference section"""
        if not citations and not references:
            return ""
        
        ref_section = "\n\n## References\n\n"
        
        # Use provided references if available, otherwise create from citations
        if references:
            for i, ref in enumerate(references, 1):
                ref_section += f"{i}. {ref}\n\n"
        else:
            for citation in citations:
                ref_section += f"{citation.number}. {citation.text or citation.url}\n\n"
        
        return ref_section
    
    def process_llm_response(self, text: str, api_type: str = 'generic') -> str:
        """Process LLM response to standardize citations"""
        # Extract citations and references
        citations = self.extract_citations(text, api_type)
        references = self.extract_references(text)
        
        print(f"🔍 Found {len(citations)} citations and {len(references)} references")
        
        # Normalize citations to internal format
        normalized_text = self.normalize_citations(text, api_type)
        
        # Remove existing reference section
        for pattern in self.reference_patterns:
            normalized_text = re.sub(pattern, '', normalized_text, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
        
        # Add standardized reference section
        ref_section = self.create_reference_section(citations, references)
        if ref_section:
            normalized_text += ref_section
        
        return normalized_text.strip()


# Convenience functions for different APIs
def process_perplexity_response(text: str) -> str:
    """Process Perplexity API response"""
    processor = CitationProcessor()
    return processor.process_llm_response(text, 'perplexity')


def process_perplexity_response_with_external_links(text: str) -> str:
    """Process Perplexity API response while preserving external URLs"""
    processor = CitationProcessor()
    
    # Extract citations and references
    citations = processor.extract_citations(text, 'perplexity')
    references = processor.extract_references(text)
    
    print(f"🔍 Found {len(citations)} citations and {len(references)} references")
    
    # Convert plain citations [1], [2], [3] to external links [1](url), [2](url), etc.
    # But only if they're not already in link format
    processed_text = text
    
    # Create a mapping of citation numbers to URLs
    citation_map = {}
    for citation in citations:
        if citation.url:
            citation_map[citation.number] = citation.url
    
    # Convert plain citations to external links
    for citation_num, url in citation_map.items():
        # Only convert if it's not already a link: [1] -> [1](url), but skip [1](url)
        pattern = rf'(?<!\]\()\[{citation_num}\](?!\()'
        replacement = f'[{citation_num}]({url})'
        processed_text = re.sub(pattern, replacement, processed_text)
    
    # Remove existing reference section
    for pattern in processor.reference_patterns:
        processed_text = re.sub(pattern, '', processed_text, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
    
    # Add standardized reference section
    ref_section = processor.create_reference_section(citations, references)
    if ref_section:
        processed_text += ref_section
    
    return processed_text.strip()


def process_gemini_response(text: str) -> str:
    """Process Gemini API response"""
    processor = CitationProcessor()
    return processor.process_llm_response(text, 'gemini')


def process_openai_response(text: str) -> str:
    """Process OpenAI API response"""
    processor = CitationProcessor()
    return processor.process_llm_response(text, 'openai')


def process_generic_response(text: str) -> str:
    """Process generic LLM response"""
    processor = CitationProcessor()
    return processor.process_llm_response(text, 'generic')
