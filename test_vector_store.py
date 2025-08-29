#!/usr/bin/env python3
"""
Test script for vector store functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.vector_store import VectorStoreService, DocumentChunk


def test_vector_store():
    """Test the vector store functionality"""
    print("🧪 Testing Vector Store Functionality")
    print("=" * 50)
    
    # Initialize vector store
    print("1. Initializing vector store...")
    vector_store = VectorStoreService("./test_vector_store")
    
    # Test text chunking
    print("\n2. Testing text chunking...")
    test_text = """
    This is a test document about machine learning and artificial intelligence. 
    Machine learning is a subset of artificial intelligence that focuses on algorithms 
    that can learn from data. Deep learning is a type of machine learning that uses 
    neural networks with multiple layers. Natural language processing is another 
    important area of AI that deals with human language understanding and generation.
    """
    
    chunks = vector_store.chunk_text(test_text, max_tokens=100, overlap=20)
    print(f"   Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks, 1):
        print(f"   Chunk {i}: {chunk[:50]}...")
    
    # Test collection statistics
    print("\n3. Testing collection statistics...")
    stats = vector_store.get_collection_stats()
    print(f"   Total chunks: {stats.get('total_chunks', 0)}")
    print(f"   Unique PDFs: {stats.get('unique_pdfs', 0)}")
    
    # Test search functionality (if we have data)
    if stats.get('total_chunks', 0) > 0:
        print("\n4. Testing search functionality...")
        results = vector_store.search_similar_chunks("machine learning", n_results=3)
        print(f"   Found {len(results)} results for 'machine learning'")
        for i, result in enumerate(results, 1):
            print(f"   Result {i}: {result['text'][:100]}...")
    
    print("\n✅ Vector store test completed!")
    return True


if __name__ == "__main__":
    test_vector_store()
