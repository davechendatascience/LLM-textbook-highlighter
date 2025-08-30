"""
LLM Service
Handles communication with Perplexity API and research integration
"""

import json
import os
import re
import requests
from typing import Optional, List, Dict
from src.services.arxiv_service import ArxivService, ArxivPaper
from src.services.vector_store import VectorStoreService
from src.utils.language_support import LanguageSupport
from src.utils.citation_processor import process_perplexity_response, process_perplexity_response_with_external_links, process_generic_response


class LLMService:
    """Simplified LLM service using proper markdown parsing"""
    
    def __init__(self, language_support=None):
        self.language_support = language_support
        self.api_key = self.load_api_key()
        self.research_enabled = False  # Disabled since Perplexity already provides references
        self.arxiv_service = ArxivService()
        
        # Initialize vector store service
        self.vector_store = VectorStoreService()
        
        # Track current PDF for context
        self.current_pdf_name = None
        self.current_pdf_path = None
        
    def load_api_key(self) -> Optional[str]:
        """Load API key from secrets.json"""
        # Try multiple locations for secrets.json
        possible_paths = [
            "secrets.json",  # Current directory (development)
            os.path.join(os.path.expanduser("~"), "secrets.json"),  # Home directory
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "secrets.json"),  # Project root
        ]
        
        for secrets_path in possible_paths:
            try:
                if os.path.exists(secrets_path):
                    print(f"🔍 Loading API key from: {secrets_path}")
                    with open(secrets_path, "r") as f:
                        secrets = json.load(f)
                        api_key = secrets.get("perplexity_api_key")
                        if api_key:
                            print(f"✅ API key loaded successfully from {secrets_path}")
                            return api_key
            except Exception as e:
                print(f"⚠️ Error loading from {secrets_path}: {e}")
                continue
        
        print("❌ No API key found in any location")
        return None
            
    def save_api_key(self, api_key: str):
        """Save API key to secrets.json"""
        try:
            # Save to user's home directory for packaged app compatibility
            secrets_path = os.path.join(os.path.expanduser("~"), "secrets.json")
            
            # Load existing secrets if they exist
            secrets = {}
            if os.path.exists(secrets_path):
                with open(secrets_path, "r") as f:
                    secrets = json.load(f)
            
            secrets["perplexity_api_key"] = api_key
            
            # Save to home directory
            with open(secrets_path, "w") as f:
                json.dump(secrets, f, indent=2)
                
            self.api_key = api_key
            print(f"✅ API key saved successfully to {secrets_path}")
        except Exception as e:
            print(f"Error saving API key: {e}")
            
    def reload_api_key(self):
        """Reload API key from secrets.json"""
        self.api_key = self.load_api_key()
        print(f"🔄 API key reloaded: {'✅ Configured' if self.api_key else '❌ Not configured'}")
            
    def ask_question(self, question: str, selected_text: str = "", background_context: str = "", length: str = "medium") -> str:
        """Ask a question to the LLM with proper markdown parsing"""
        if not self.api_key:
            return "Error: No API key configured. Please configure your Perplexity API key."
            
        try:
            # Build the prompt
            prompt = self.build_prompt(question, selected_text, background_context)
            
            # Use unified API call method
            result = self._call_perplexity_api(prompt, length)
            llm_response = result["choices"][0]["message"]["content"]
            
            # Extract reference URLs and search results
            reference_urls, search_results = self._extract_references_from_response(result)
            
            # Parse markdown and extract references
            parsed_response = self.parse_markdown_response(llm_response, reference_urls, search_results)
            
            # Add research enhancement if enabled
            if self.research_enabled:
                parsed_response = self.enhance_with_research(parsed_response, question)
            
            return parsed_response
            
        except Exception as e:
            print(f"Error asking question: {e}")
            return f"Error: {str(e)}"
            
    def build_prompt(self, question: str, selected_text: str = "", background_context: str = "") -> str:
        """Build a prompt for the LLM"""
        # Get language-specific instructions if available
        language_instruction = ""
        if self.language_support and hasattr(self.language_support, 'current_language'):
            current_lang = self.language_support.current_language
            if current_lang != "English":
                language_instruction = f"\nPlease respond in {current_lang}.\n"
        
        prompt = f"Question: {question}\n\n"
        
        if selected_text:
            prompt += f"Selected Text: {selected_text}\n\n"
            
        if background_context:
            prompt += f"Background Context: {background_context}\n\n"
            
        prompt += f"Please provide a clear and comprehensive answer.{language_instruction} Include any references or sources at the end of your response."
        
        return prompt
    
    def _call_perplexity_api(self, prompt: str, length: str = "medium") -> Dict:
        """Unified method to call Perplexity API"""
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
        
        # Debug: Print the full response structure
        print(f"🔍 Full Perplexity API response keys: {list(result.keys())}")
        if "citations" in result:
            print(f"🔍 Citations structure: {result['citations']}")
        if "search_results" in result:
            print(f"🔍 Search results structure: {result['search_results']}")
        
        return result
    
    def _extract_references_from_response(self, result: Dict) -> tuple[List[str], List[Dict]]:
        """Extract reference URLs and search results from API response"""
        reference_urls = []
        search_results = []
        
        # Extract search_results if available
        if "search_results" in result:
            search_results = result["search_results"]
            for result_item in search_results:
                if "url" in result_item:
                    reference_urls.append(result_item["url"])
        
        # Extract citations if available (avoid duplicates)
        seen_urls = set(reference_urls)
        if "citations" in result:
            for citation in result["citations"]:
                if "url" in citation and citation["url"] not in seen_urls:
                    reference_urls.append(citation["url"])
                    seen_urls.add(citation["url"])
        
        print(f"🔍 Found {len(reference_urls)} reference URLs from Perplexity API")
        return reference_urls, search_results
        
    def parse_markdown_response(self, response: str, reference_urls: List[str], search_results: List[Dict] = None) -> str:
        """Parse markdown response using improved citation processor"""
        print(f"🔍 Parsing response with {len(reference_urls)} reference URLs")
        print(f"🔍 Response preview: {response[:300]}...")
        
        import re
        
        # First, convert context citations to standard numbered format
        print(f"🔍 Converting context citations to standard format...")
        
        # Convert [from the selected text] to [1]
        processed_response = re.sub(r'\[from the selected text\]', '[1]', response)
        
        # Convert [Context 1], [Context 2], etc. to [2], [3], etc.
        context_matches = re.findall(r'\[Context (\d+)\]', response)
        for i, context_num in enumerate(context_matches, 2):  # Start from 2 since [1] is used for selected text
            processed_response = re.sub(rf'\[Context {context_num}\]', f'[{i}]', processed_response)
        
        # For Perplexity, the citations are in the API response object, not in the text
        # We need to manually add the citation links to the text
        if reference_urls:
            print(f"🔍 Adding citation links to text...")
            
            # Find all citation numbers in the text [1], [2], [3], etc.
            citation_numbers = re.findall(r'\[(\d+)\]', processed_response)
            unique_citations = list(set(citation_numbers))
            unique_citations.sort(key=int)
            
            print(f"🔍 Found citation numbers: {unique_citations}")
            print(f"🔍 Available URLs: {reference_urls}")
            
            # Convert plain citations to direct external URLs with titles
            for i, citation_num in enumerate(unique_citations):
                if i < len(reference_urls):
                    url = reference_urls[i]
                    
                    # Try to get title from search_results if available
                    title = None
                    if search_results and i < len(search_results):
                        title = search_results[i].get('title', '')
                    
                    # Create display text: use title if available, otherwise domain
                    if title:
                        # Truncate title if too long
                        display_text = title[:50] + "..." if len(title) > 50 else title
                    else:
                        # Extract domain from URL
                        try:
                            from urllib.parse import urlparse
                            parsed_url = urlparse(url)
                            domain = parsed_url.netloc
                            if domain.startswith('www.'):
                                domain = domain[4:]
                            display_text = domain
                        except:
                            display_text = f"Reference {citation_num}"
                    
                    # Convert [1] to [1](url) - direct external links
                    pattern = rf'\[{citation_num}\]'
                    replacement = f'[{citation_num}]({url})'
                    processed_response = re.sub(pattern, replacement, processed_response)
                    print(f"🔗 Converted [{citation_num}] to [{citation_num}]({url}) with title: {display_text}")
        
        # Use the citation processor that preserves external URLs
        processed_response = process_perplexity_response_with_external_links(processed_response)
        
        # Fix consecutive citation formatting
        processed_response = self.fix_consecutive_citations(processed_response)
        
        # Add proper reference section with actual URLs and titles
        if reference_urls:
            processed_response = self.add_reference_section(processed_response, reference_urls, search_results)
        
        print(f"🔍 Processed response preview: {processed_response[:300]}...")
        
        # Check for citation patterns in the processed response
        citation_patterns = re.findall(r'\[(\d+)\]\(([^)]+)\)', processed_response)
        print(f"🔍 Found {len(citation_patterns)} normalized citations: {citation_patterns}")
        
        return processed_response
    
    def fix_consecutive_citations(self, text: str) -> str:
        """Fix consecutive citation formatting to ensure proper spacing and formatting"""
        import re
        
        # Pattern to match consecutive citations: [1](url1)[2](url2)[3](url3)
        # This ensures proper spacing and consistent formatting
        pattern = r'\[(\d+)\]\(([^)]+)\)\[(\d+)\]\(([^)]+)\)'
        
        def replace_consecutive(match):
            num1, url1, num2, url2 = match.groups()
            # Ensure proper spacing between consecutive citations
            return f'[{num1}]({url1}) [{num2}]({url2})'
        
        # Apply the fix multiple times to handle longer sequences
        fixed_text = text
        for _ in range(10):  # Limit iterations to prevent infinite loops
            new_text = re.sub(pattern, replace_consecutive, fixed_text)
            if new_text == fixed_text:
                break
            fixed_text = new_text
        
        return fixed_text
    
    def add_reference_section(self, text: str, reference_urls: List[str], search_results: List[Dict] = None) -> str:
        """Add a proper reference section with actual URLs and titles"""
        # Remove any existing reference section
        import re
        text = re.sub(r'\n\n## References?\s*\n.*', '', text, flags=re.DOTALL)
        
        # Add new reference section
        ref_section = "\n\n## References\n\n"
        
        for i, url in enumerate(reference_urls, 1):
            # Try to get title from search_results if available
            title = None
            if search_results and i-1 < len(search_results):
                title = search_results[i-1].get('title', '')
            
            # Create display text: use title if available, otherwise domain
            if title:
                # Truncate title if too long
                display_text = title[:80] + "..." if len(title) > 80 else title
            else:
                # Extract domain from URL
                try:
                    from urllib.parse import urlparse
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    display_text = domain
                except:
                    display_text = f"Reference {i}"
            
            # Create markdown link
            ref_section += f"{i}. [{display_text}]({url})\n\n"
        
        return text + ref_section
        
    # Note: Removed duplicate citation processing methods that were not being used
    # The main citation processing is now handled in parse_markdown_response and add_reference_section
        
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
        if not self.api_key:
            return "Error: No API key configured. Please configure your Perplexity API key."
            
        try:
            # Get language-specific instructions if available
            language_instruction = ""
            if self.language_support and hasattr(self.language_support, 'current_language'):
                current_lang = self.language_support.current_language
                if current_lang != "English":
                    language_instruction = f" Please generate the questions in {current_lang}."
            
            base_prompt = f"Based on the following text, generate 3-5 thoughtful questions that could help someone understand the key concepts better:{language_instruction}\n\n{text}"
            
            # Use unified API call method
            result = self._call_perplexity_api(base_prompt, "short")
            llm_response = result["choices"][0]["message"]["content"]
            
            # Return raw response without reference processing for questions
            return llm_response
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return f"Error: {str(e)}"
    
    # Vector Store Integration Methods
    
    def set_current_pdf(self, pdf_path: str, pdf_name: str = None):
        """Set the current PDF for vector store operations"""
        self.current_pdf_path = pdf_path
        self.current_pdf_name = pdf_name or os.path.basename(pdf_path)
        print(f"📄 Set current PDF: {self.current_pdf_name}")
    
    def process_current_pdf(self) -> bool:
        """Process the current PDF and add chunks to vector store"""
        if not self.current_pdf_path:
            print("❌ No current PDF set")
            return False
        
        try:
            # Check if PDF is already processed
            existing_chunks = self.vector_store.get_chunks_by_pdf(self.current_pdf_name)
            if existing_chunks:
                print(f"ℹ️ PDF {self.current_pdf_name} already processed with {len(existing_chunks)} chunks")
                return True
            
            # Process the PDF
            chunks = self.vector_store.process_pdf(self.current_pdf_path, self.current_pdf_name)
            
            if chunks:
                # Add chunks to vector store
                success = self.vector_store.add_document_chunks(chunks)
                if success:
                    print(f"✅ Successfully processed and indexed {len(chunks)} chunks from {self.current_pdf_name}")
                    return True
                else:
                    print(f"❌ Failed to add chunks to vector store for {self.current_pdf_name}")
                    return False
            else:
                print(f"❌ No chunks created from {self.current_pdf_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return False
    
    def search_relevant_chunks(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for relevant chunks in the current PDF"""
        if not self.current_pdf_name:
            print("❌ No current PDF set")
            return []
        
        try:
            # Search with PDF filter
            filter_metadata = {"pdf_name": self.current_pdf_name}
            results = self.vector_store.search_similar_chunks(query, n_results, filter_metadata)
            return results
        except Exception as e:
            print(f"❌ Error searching chunks: {e}")
            return []
    
    def ask_question_with_context(self, question: str, selected_text: str = "", length: str = "medium") -> str:
        """Ask a question with enhanced context from vector store"""
        if not self.api_key:
            return "Error: No API key configured. Please configure your Perplexity API key."
        
        try:
            # Use selected text as query to find similar chunks in vector store
            enhanced_context = ""
            if selected_text and self.current_pdf_name:
                # Search for chunks similar to the selected text
                similar_chunks = self.search_relevant_chunks(selected_text, n_results=3)
                
                if similar_chunks:
                    enhanced_context = "\n\n**Relevant Context from Document (found using semantic search):**\n\n"
                    for i, chunk in enumerate(similar_chunks, 1):
                        enhanced_context += f"**Context {i} (Page {chunk['metadata']['page_number']}):**\n"
                        enhanced_context += f"{chunk['text']}\n\n"
                else:
                    print(f"ℹ️ No similar chunks found for selected text in {self.current_pdf_name}")
            
            # Combine with selected text
            if selected_text:
                enhanced_context = f"**Selected Text:**\n{selected_text}\n\n" + enhanced_context
            
            # Build the prompt with enhanced context
            prompt = self.build_prompt(question, "", enhanced_context)
            
            # Use unified API call method
            result = self._call_perplexity_api(prompt, length)
            
            # Validate API response structure
            if "choices" not in result or not result["choices"]:
                print(f"⚠️ Unexpected API response structure: {result}")
                return "Error: Unexpected response format from API"
            
            if "message" not in result["choices"][0] or "content" not in result["choices"][0]["message"]:
                print(f"⚠️ Missing content in API response: {result['choices'][0]}")
                return "Error: No content in API response"
            
            llm_response = result["choices"][0]["message"]["content"]
            
            # Extract reference URLs and search results using unified method
            reference_urls, search_results = self._extract_references_from_response(result)
            
            # Process response with references
            processed_response = self.parse_markdown_response(llm_response, reference_urls, search_results)
            
            return processed_response
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error asking question with context: {e}")
            return f"Error: Network error - {str(e)}"
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error asking question with context: {e}")
            return f"Error: Invalid response format - {str(e)}"
        except KeyError as e:
            print(f"❌ Missing key in API response: {e}")
            return f"Error: Unexpected response structure - {str(e)}"
        except Exception as e:
            print(f"❌ Unexpected error asking question with context: {e}")
            return f"Error: {str(e)}"
    
    def get_vector_store_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return self.vector_store.get_collection_stats()
    
    def clear_vector_store(self) -> bool:
        """Clear all data from the vector store"""
        return self.vector_store.clear_collection()
    
    def delete_pdf_from_store(self, pdf_name: str) -> bool:
        """Delete a specific PDF from the vector store"""
        return self.vector_store.delete_pdf_chunks(pdf_name)