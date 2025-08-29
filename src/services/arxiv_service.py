"""
Direct ArXiv API Service
Uses the ArXiv API directly for better reliability
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class ArxivPaper:
    """Data class for ArXiv paper information"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: str
    pdf_url: str
    arxiv_url: str

class ArxivService:
    """Direct ArXiv API service - more reliable than MCP"""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.max_results = 10
        
    def search_papers(self, query: str, max_results: int = 10, 
                     categories: Optional[List[str]] = None) -> List[ArxivPaper]:
        """
        Search for papers using ArXiv API
        
        Args:
            query: Search query
            max_results: Maximum number of results
            categories: List of ArXiv categories (e.g., ['cs.AI', 'cs.LG'])
            
        Returns:
            List of ArxivPaper objects
        """
        try:
            # Build query parameters
            params = {
                'search_query': query,
                'start': 0,
                'max_results': min(max_results, 100),  # ArXiv API limit
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            # Add categories if specified
            if categories:
                category_query = " OR ".join([f"cat:{cat}" for cat in categories])
                params['search_query'] = f"({params['search_query']}) AND ({category_query})"
            
            print(f"🔍 Searching ArXiv for: {query}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Extract papers
            papers = []
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                paper = self._parse_entry(entry)
                if paper:
                    papers.append(paper)
            
            print(f"✅ Found {len(papers)} papers")
            return papers
            
        except Exception as e:
            print(f"❌ ArXiv API search failed: {e}")
            return []
    
    def _parse_entry(self, entry) -> Optional[ArxivPaper]:
        """Parse an ArXiv API entry into ArxivPaper object"""
        try:
            # Extract ID
            id_elem = entry.find('.//{http://www.w3.org/2005/Atom}id')
            if id_elem is None:
                return None
            paper_id = id_elem.text.split('/')[-1]
            
            # Extract title
            title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
            title = title_elem.text.strip() if title_elem is not None else "No title"
            
            # Extract authors
            authors = []
            for author in entry.findall('.//{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name'):
                authors.append(author.text.strip())
            
            # Extract abstract
            summary_elem = entry.find('.//{http://www.w3.org/2005/Atom}summary')
            abstract = summary_elem.text.strip() if summary_elem is not None else "No abstract"
            
            # Extract categories
            categories = []
            for category in entry.findall('.//{http://arxiv.org/schemas/atom}primary_category'):
                cat = category.get('term')
                if cat:
                    categories.append(cat)
            
            # Extract published date
            published_elem = entry.find('.//{http://www.w3.org/2005/Atom}published')
            published_date = published_elem.text[:10] if published_elem is not None else "Unknown"
            
            # Build URLs
            arxiv_url = f"https://arxiv.org/abs/{paper_id}"
            pdf_url = f"https://arxiv.org/pdf/{paper_id}"
            
            return ArxivPaper(
                id=paper_id,
                title=title,
                authors=authors,
                abstract=abstract,
                categories=categories,
                published_date=published_date,
                pdf_url=pdf_url,
                arxiv_url=arxiv_url
            )
            
        except Exception as e:
            print(f"❌ Failed to parse ArXiv entry: {e}")
            return None
    
    def get_paper_info(self, paper_id: str) -> Optional[ArxivPaper]:
        """Get detailed information about a specific paper"""
        try:
            params = {
                'id_list': paper_id,
                'start': 0,
                'max_results': 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            entry = root.find('.//{http://www.w3.org/2005/Atom}entry')
            
            if entry is not None:
                return self._parse_entry(entry)
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to get paper info for {paper_id}: {e}")
            return None

# Convenience functions for synchronous use
def search_papers_sync(query: str, max_results: int = 10, 
                      categories: Optional[List[str]] = None) -> List[ArxivPaper]:
    """Synchronous wrapper for paper search"""
    service = ArxivService()
    return service.search_papers(query, max_results, categories)

def get_paper_info_sync(paper_id: str) -> Optional[ArxivPaper]:
    """Synchronous wrapper for getting paper info"""
    service = ArxivService()
    return service.get_paper_info(paper_id)
