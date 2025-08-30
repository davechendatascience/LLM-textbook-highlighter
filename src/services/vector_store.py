"""
Vector Store Service
Handles PDF chunking, embedding generation, and semantic search using ChromaDB
"""

import os
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import tiktoken
import fitz  # PyMuPDF
from src.utils.multilingual_tokenizer import get_tokenizer


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document"""
    text: str
    page_number: int
    chunk_id: str
    metadata: Dict
    embedding: Optional[List[float]] = None


class VectorStoreService:
    """Service for managing document chunks and semantic search"""
    
    def __init__(self, persist_directory: str = "./vector_store", use_multilingual_tokenizer: bool = True):
        self.persist_directory = persist_directory
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize tokenizer for chunking
        self.tokenizer = get_tokenizer(use_multilingual=use_multilingual_tokenizer)
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="pdf_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"✅ Vector store initialized at: {persist_directory}")
        if use_multilingual_tokenizer:
            print("🌍 Using multilingual tokenizer for better multi-language support")
        else:
            print("🔤 Using standard tiktoken tokenizer")
    
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
        # Use the tokenizer's chunk_text method if available
        if hasattr(self.tokenizer, 'chunk_text'):
            return self.tokenizer.chunk_text(text, max_tokens, overlap)
        
        # Fallback to original implementation for tiktoken
        tokens = self.tokenizer.encode(text)
        
        if len(tokens) <= max_tokens:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = start + max_tokens
            
            # Extract tokens for this chunk
            chunk_tokens = tokens[start:end]
            
            # Decode tokens back to text
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            # Clean up the chunk (remove partial words at boundaries)
            if start > 0:  # Not the first chunk
                # Find the first complete word
                first_space = chunk_text.find(' ')
                if first_space != -1:
                    chunk_text = chunk_text[first_space + 1:]
            
            if end < len(tokens):  # Not the last chunk
                # Find the last complete word
                last_space = chunk_text.rfind(' ')
                if last_space != -1:
                    chunk_text = chunk_text[:last_space]
            
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
            
            # Move start position with overlap
            start = end - overlap
        
        return chunks
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Tuple[str, int]]:
        """
        Extract text from PDF with page numbers
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of (text, page_number) tuples
        """
        text_pages = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():
                    text_pages.append((text.strip(), page_num + 1))
            
            doc.close()
            print(f"✅ Extracted text from {len(text_pages)} pages of {pdf_path}")
            
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {e}")
        
        return text_pages
    
    def process_pdf(self, pdf_path: str, pdf_name: str = None) -> List[DocumentChunk]:
        """
        Process a PDF file: extract text, chunk it, and generate embeddings
        
        Args:
            pdf_path: Path to PDF file
            pdf_name: Name for the PDF (defaults to filename)
            
        Returns:
            List of DocumentChunk objects
        """
        if pdf_name is None:
            pdf_name = os.path.basename(pdf_path)
        
        print(f"🔄 Processing PDF: {pdf_name}")
        
        # Extract text from PDF
        text_pages = self.extract_text_from_pdf(pdf_path)
        
        chunks = []
        chunk_counter = 0
        
        for page_text, page_num in text_pages:
            # Chunk the page text
            page_chunks = self.chunk_text(page_text)
            
            for chunk_text in page_chunks:
                chunk_counter += 1
                
                # Create unique chunk ID
                chunk_id = f"{pdf_name}_page_{page_num}_chunk_{chunk_counter}"
                
                # Create metadata
                metadata = {
                    "pdf_name": pdf_name,
                    "pdf_path": pdf_path,
                    "page_number": page_num,
                    "chunk_number": chunk_counter,
                    "text_length": len(chunk_text),
                    "token_count": self.tokenizer.count_tokens(chunk_text) if hasattr(self.tokenizer, 'count_tokens') else len(self.tokenizer.encode(chunk_text))
                }
                
                # Create document chunk
                chunk = DocumentChunk(
                    text=chunk_text,
                    page_number=page_num,
                    chunk_id=chunk_id,
                    metadata=metadata
                )
                
                chunks.append(chunk)
        
        print(f"✅ Created {len(chunks)} chunks from {pdf_name}")
        return chunks
    
    def add_document_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """
        Add document chunks to the vector store
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for ChromaDB
            texts = [chunk.text for chunk in chunks]
            ids = [chunk.chunk_id for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            
            # Generate embeddings
            print("🔄 Generating embeddings...")
            embeddings = self.embedding_model.encode(texts)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Added {len(chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            print(f"❌ Error adding chunks to vector store: {e}")
            return False
    
    def search_similar_chunks(self, query: str, n_results: int = 5, 
                            filter_metadata: Dict = None) -> List[Dict]:
        """
        Search for similar chunks based on a query
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of search results with chunks and metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'chunk_id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                }
                formatted_results.append(result)
            
            print(f"✅ Found {len(formatted_results)} similar chunks for query: '{query}'")
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching vector store: {e}")
            return []
    
    def get_chunks_by_pdf(self, pdf_name: str) -> List[Dict]:
        """
        Get all chunks for a specific PDF
        
        Args:
            pdf_name: Name of the PDF
            
        Returns:
            List of chunks for the PDF
        """
        try:
            results = self.collection.get(
                where={"pdf_name": pdf_name}
            )
            
            chunks = []
            for i in range(len(results['ids'])):
                chunk = {
                    'chunk_id': results['ids'][i],
                    'text': results['documents'][i],
                    'metadata': results['metadatas'][i]
                }
                chunks.append(chunk)
            
            print(f"✅ Retrieved {len(chunks)} chunks for PDF: {pdf_name}")
            return chunks
            
        except Exception as e:
            print(f"❌ Error retrieving chunks: {e}")
            return []
    
    def delete_pdf_chunks(self, pdf_name: str) -> bool:
        """
        Delete all chunks for a specific PDF
        
        Args:
            pdf_name: Name of the PDF to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get chunks to delete
            chunks = self.get_chunks_by_pdf(pdf_name)
            chunk_ids = [chunk['chunk_id'] for chunk in chunks]
            
            if chunk_ids:
                self.collection.delete(ids=chunk_ids)
                print(f"✅ Deleted {len(chunk_ids)} chunks for PDF: {pdf_name}")
            else:
                print(f"ℹ️ No chunks found for PDF: {pdf_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error deleting chunks: {e}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the vector store collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get unique PDFs
            all_metadata = self.collection.get()['metadatas']
            unique_pdfs = set()
            total_pages = 0
            
            for metadata in all_metadata:
                if metadata:
                    unique_pdfs.add(metadata.get('pdf_name', 'Unknown'))
                    total_pages = max(total_pages, metadata.get('page_number', 0))
            
            stats = {
                'total_chunks': count,
                'unique_pdfs': len(unique_pdfs),
                'pdf_names': list(unique_pdfs),
                'max_pages': total_pages
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting collection stats: {e}")
            return {}
    
    def clear_collection(self) -> bool:
        """
        Clear all data from the collection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all IDs first, then delete them
            all_data = self.collection.get()
            if all_data['ids']:
                self.collection.delete(ids=all_data['ids'])
                print("✅ Cleared all data from vector store")
            else:
                print("ℹ️ No data to clear from vector store")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing collection: {e}")
            return False
