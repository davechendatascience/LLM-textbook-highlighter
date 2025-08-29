"""
LLM Service
Handles communication with Perplexity API and research integration
"""

import json
import os
import re
import requests
from typing import Optional, List
from src.services.arxiv_service import ArxivService, ArxivPaper
from src.utils.language_support import LanguageSupport


class LLMService:
    """Simplified LLM service using proper markdown parsing"""
    
    def __init__(self, language_support=None):
        self.language_support = language_support
        self.api_key = self.load_api_key()
        self.research_enabled = True
        self.arxiv_service = ArxivService()
        
    def load_api_key(self) -> Optional[str]:
        """Load API key from secrets.json"""
        try:
            if os.path.exists("secrets.json"):
                with open("secrets.json", "r") as f:
                    secrets = json.load(f)
                    return secrets.get("perplexity_api_key")
        except Exception as e:
            print(f"Error loading API key: {e}")
            return None
            
    def save_api_key(self, api_key: str):
        """Save API key to secrets.json"""
        try:
            secrets = {}
            if os.path.exists("secrets.json"):
                with open("secrets.json", "r") as f:
                    secrets = json.load(f)
            
            secrets["perplexity_api_key"] = api_key
            
            with open("secrets.json", "w") as f:
                json.dump(secrets, f, indent=2)
                
            self.api_key = api_key
            print("✅ API key saved successfully")
        except Exception as e:
            print(f"Error saving API key: {e}")
            
    def ask_question(self, question: str, selected_text: str = "", background_context: str = "", length: str = "medium") -> str:
        """Ask a question to the LLM with proper markdown parsing"""
        if not self.api_key:
            return "Error: No API key configured. Please configure your Perplexity API key."
            
        try:
            # Build the prompt
            prompt = self.build_prompt(question, selected_text, background_context)
            
            # Choose model based on length
            if length.lower() == "long":
                model = "sonar-reasoning"
            else:
                model = "sonar"
            
            # Get response from Perplexity API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000 if length.lower() == "short" else 2000,
                "temperature": 0.1
            }
            
            response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"]
            
            # Debug: Print the full response structure
            print(f"🔍 Full Perplexity API response keys: {list(result.keys())}")
            if "citations" in result:
                print(f"🔍 Citations structure: {result['citations']}")
            if "search_results" in result:
                print(f"🔍 Search results structure: {result['search_results']}")
            
            # Debug: Check for inline citations in the LLM response
            print(f"🔍 LLM Response content: {llm_response}")
            inline_citations = re.findall(r'\[(\d+)\]', llm_response)
            print(f"🔍 Found inline citations: {inline_citations}")
            
            # Also check for [Selected Text] and other citation patterns
            selected_text_citations = re.findall(r'\[Selected Text\]', llm_response)
            print(f"🔍 Found [Selected Text] citations: {selected_text_citations}")
            
            # Check for any other citation patterns
            all_citations = re.findall(r'\[([^\]]+)\]', llm_response)
            print(f"🔍 All citation patterns found: {all_citations}")
            
            # Extract reference URLs from Perplexity API response
            reference_urls = []
            if "citations" in result:
                for citation in result["citations"]:
                    if "url" in citation:
                        reference_urls.append(citation["url"])
                        
            if "search_results" in result:
                for result_item in result["search_results"]:
                    if "url" in result_item:
                        reference_urls.append(result_item["url"])
            
            print(f"🔍 Found {len(reference_urls)} reference URLs from Perplexity API")
            
            # Parse markdown and extract references
            parsed_response = self.parse_markdown_response(llm_response, reference_urls)
            
            # Add research enhancement if enabled
            if self.research_enabled:
                parsed_response = self.enhance_with_research(parsed_response, question)
            
            return parsed_response
            
        except Exception as e:
            print(f"Error asking question: {e}")
            return f"Error: {str(e)}"
            
    def build_prompt(self, question: str, selected_text: str = "", background_context: str = "") -> str:
        """Build a prompt for the LLM"""
        prompt = f"Question: {question}\n\n"
        
        if selected_text:
            prompt += f"Selected Text: {selected_text}\n\n"
            
        if background_context:
            prompt += f"Background Context: {background_context}\n\n"
            
        prompt += "Please provide a clear and comprehensive answer. Include any references or sources at the end of your response."
        
        return prompt
        
    def parse_markdown_response(self, response: str, reference_urls: List[str]) -> str:
        """Parse markdown response and extract references"""
        print(f"🔍 Parsing response with {len(reference_urls)} reference URLs")
        print(f"🔍 Response preview: {response[:300]}...")
        
        # Split response into main content and references
        parts = response.split("## References")
        
        print(f"🔍 Found {len(parts)} parts after splitting by '## References'")
        
        main_content = parts[0].strip()
        references_text = parts[1].strip() if len(parts) > 1 else ""
        
        print(f"🔍 Main content length: {len(main_content)}")
        print(f"🔍 References text length: {len(references_text)}")
        
        # Parse references from the markdown
        references = self.extract_references_from_markdown(references_text, reference_urls)
        
        # If no references were found in the text but we have URLs, create references
        if not references and reference_urls:
            print(f"🔍 Creating references from {len(reference_urls)} URLs")
            references = []
            for i, url in enumerate(reference_urls, 1):
                # Extract domain name for display
                from urllib.parse import urlparse
                try:
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    ref_text = f"Reference {i} - {domain}"
                except:
                    ref_text = f"Reference {i}"
                
                references.append(f"{ref_text} - [Link]({url})")
        
        # Process inline citations in main content
        main_content = self.process_inline_citations(main_content, references, reference_urls)
        
        # Keep as markdown and add references section
        markdown_content = main_content
        
        # Add references section
        if references:
            print(f"🔍 Adding {len(references)} references to response")
            markdown_content += "\n\n## References\n\n"
            for i, ref in enumerate(references, 1):
                markdown_content += f"{i}. {ref}\n\n"
        else:
            print("🔍 No references to add")
        
        return markdown_content
        
    def process_inline_citations(self, content: str, references: List[str], reference_urls: List[str]) -> str:
        """Process inline citations like [1], [2], etc. and make them clickable HTML links"""
        print(f"🔍 Processing inline citations. Content preview: {content[:200]}...")
        
        # First, handle [Selected Text] citations by converting them to a search link
        if "[Selected Text]" in content:
            print("🔍 Found [Selected Text] citation, converting to search link")
            # Create a search link for the selected text
            search_url = "https://scholar.google.com/scholar?q=selected+text"
            content = content.replace("[Selected Text]", f'<a href="{search_url}">Selected Text</a>')
        
        # Convert citations directly to HTML links to avoid markdown conflicts
        citation_count = 0
        
        def replace_citation(match):
            nonlocal citation_count
            citation_num = match.group(1)
            citation_count += 1
            
            try:
                index = int(citation_num) - 1  # Convert to 0-based index
                
                # The citations array order corresponds to citation numbers
                # [1] maps to citations[0], [2] maps to citations[1], etc.
                if index < len(reference_urls):
                    url = reference_urls[index]
                    html_link = f'<a href="{url}">[{citation_num}]</a>'
                    print(f"🔗 Creating HTML link: {html_link}")
                    return html_link
                else:
                    print(f"⚠️ Citation [{citation_num}] has no corresponding URL")
                    return f"[{citation_num}]"
            except (ValueError, IndexError):
                print(f"⚠️ Invalid citation number: {citation_num}")
                return f"[{citation_num}]"
        
        # Replace inline citations with HTML links
        content = re.sub(r'\[(\d+)\]', replace_citation, content)
        
        print(f"🔍 Final processed content preview: {content[:300]}...")
        return content
        
    def extract_references_from_markdown(self, references_text: str, reference_urls: List[str]) -> List[str]:
        """Extract references from markdown text"""
        references = []
        
        print(f"🔍 Processing references text: {references_text[:200]}...")
        print(f"🔍 Available reference URLs: {reference_urls}")
        
        # Split by lines and process each reference
        lines = references_text.split('\n')
        current_ref = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_ref:
                    references.append(current_ref.strip())
                    current_ref = ""
                continue
                
            # Check if this is a numbered reference
            if re.match(r'^\d+\.', line):
                if current_ref:
                    references.append(current_ref.strip())
                current_ref = line
            else:
                current_ref += " " + line
                
        # Add the last reference
        if current_ref:
            references.append(current_ref.strip())
            
        print(f"🔍 Extracted {len(references)} references: {references}")
        
        # If we have reference URLs from the API, enhance the references
        if reference_urls and len(reference_urls) >= len(references):
            enhanced_references = []
            for i, (ref, url) in enumerate(zip(references, reference_urls)):
                # Extract the reference text (remove the number prefix)
                ref_text = re.sub(r'^\d+\.\s*', '', ref)
                # Create a proper markdown link
                enhanced_ref = f"{ref_text} - [Link]({url})"
                enhanced_references.append(enhanced_ref)
            return enhanced_references
            
        return references
        
    def enhance_with_research(self, response: str, question: str) -> str:
        """Add research papers and web resources to the response"""
        try:
            # Extract search terms from the question
            search_terms = self.extract_search_terms(question)
            
            if not search_terms:
                words = question.split()
                search_terms = ' '.join([word for word in words if len(word) > 3][:2])
            
            print(f"🔍 Searching for: {search_terms}")
            
            # Find related papers from ArXiv
            related_papers = self.arxiv_service.search_papers(search_terms, max_results=3)
            
            # Add research section if papers found
            if related_papers:
                research_section = "\n\n## Related Research Papers\n\n"
                
                for i, paper in enumerate(related_papers, 1):
                    research_section += f"**{i}. {paper.title}**\n\n"
                    research_section += f"*Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}*\n"
                    research_section += f"*Published: {paper.published_date}*\n\n"
                    research_section += f"*Abstract: {paper.abstract[:200]}{'...' if len(paper.abstract) > 200 else ''}*\n\n"
                    research_section += f"*[ArXiv]({paper.arxiv_url}) | [PDF]({paper.pdf_url})*\n\n"
                    research_section += "---\n\n"
                
                response += research_section
            
            return response
            
        except Exception as e:
            print(f"Error enhancing with research: {e}")
            return response
            
    def extract_search_terms(self, text: str) -> str:
        """Extract meaningful search terms from text"""
        # Simple approach: take words longer than 3 characters
        words = re.findall(r'\b\w{4,}\b', text.lower())
        
        # Filter out common words
        stop_words = {'this', 'that', 'with', 'from', 'they', 'have', 'been', 'will', 'would', 'could', 'should'}
        meaningful_words = [word for word in words if word not in stop_words]
        
        # Return first 3 meaningful words
        return ' '.join(meaningful_words[:3])
        
    def generate_questions(self, text: str) -> str:
        """Generate questions based on text"""
        base_prompt = f"Based on the following text, generate 3-5 thoughtful questions that could help someone understand the key concepts better:\n\n{text}"
        return self.ask_question(base_prompt, length="short")