#!/usr/bin/env python3
"""
Reindex PDFs Utility
Reindexes all existing PDFs in the vector store with the new multilingual tokenizer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.vector_store import VectorStoreService
from src.llm import LLMService
import json


def get_existing_pdfs():
    """Get list of PDFs already in the vector store"""
    try:
        vector_store = VectorStoreService(use_multilingual_tokenizer=True)
        stats = vector_store.get_collection_stats()
        return stats.get('pdf_names', [])
    except Exception as e:
        print(f"Error getting existing PDFs: {e}")
        return []


def reindex_pdfs(pdf_paths=None, show_chunks=True):
    """
    Reindex PDFs with the new multilingual tokenizer
    
    Args:
        pdf_paths: List of PDF file paths to reindex (if None, uses existing PDFs)
        show_chunks: Whether to show chunk information during processing
    """
    print("🔄 Starting PDF reindexing with multilingual tokenizer...")
    
    # Initialize services
    vector_store = VectorStoreService(use_multilingual_tokenizer=True)
    llm_service = LLMService()
    
    if pdf_paths is None:
        # Get existing PDFs from vector store
        existing_pdfs = get_existing_pdfs()
        if not existing_pdfs:
            print("❌ No existing PDFs found in vector store")
            return
        
        print(f"📚 Found {len(existing_pdfs)} existing PDFs to reindex:")
        for pdf_name in existing_pdfs:
            print(f"  - {pdf_name}")
        
        # For now, we'll need the actual file paths
        # You might need to provide these manually or store them in metadata
        print("\n⚠️  Note: To reindex existing PDFs, you'll need to provide the file paths.")
        print("   Please run this script with specific PDF paths or use the main app to re-add PDFs.")
        return
    
    print(f"📚 Reindexing {len(pdf_paths)} PDFs...")
    
    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            print(f"❌ PDF not found: {pdf_path}")
            continue
        
        pdf_name = os.path.basename(pdf_path)
        print(f"\n🔄 Processing: {pdf_name}")
        
        try:
            # Process PDF with chunking information
            chunks = vector_store.process_pdf(pdf_path, pdf_name)
            
            if show_chunks:
                print(f"  📄 Created {len(chunks)} chunks:")
                for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                    preview = chunk.text[:100] + "..." if len(chunk.text) > 100 else chunk.text
                    print(f"    Chunk {i+1} (Page {chunk.page_number}): '{preview}'")
                if len(chunks) > 3:
                    print(f"    ... and {len(chunks) - 3} more chunks")
            
            # Add to vector store
            success = vector_store.add_document_chunks(chunks)
            if success:
                print(f"  ✅ Successfully indexed {pdf_name} ({len(chunks)} chunks)")
            else:
                print(f"  ❌ Failed to index {pdf_name}")
                
        except Exception as e:
            print(f"  ❌ Error processing {pdf_name}: {e}")


def show_chunk_debug_info(pdf_path):
    """Show detailed chunking information for a single PDF"""
    print(f"🔍 Debug chunking for: {os.path.basename(pdf_path)}")
    
    vector_store = VectorStoreService(use_multilingual_tokenizer=True)
    
    # Extract text first
    text_pages = vector_store.extract_text_from_pdf(pdf_path)
    print(f"📄 Extracted {len(text_pages)} pages")
    
    for page_num, (page_text, page_number) in enumerate(text_pages):
        print(f"\n📖 Page {page_number}:")
        print(f"  Length: {len(page_text)} characters")
        
        # Show chunking
        chunks = vector_store.chunk_text(page_text, max_tokens=200, overlap=50)
        print(f"  Chunks: {len(chunks)}")
        
        for i, chunk in enumerate(chunks):
            preview = chunk[:80] + "..." if len(chunk) > 80 else chunk
            print(f"    Chunk {i+1}: '{preview}'")


def main():
    """Main function"""
    print("🚀 PDF Reindexing Utility")
    print("=" * 40)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug" and len(sys.argv) > 2:
            # Debug mode for single PDF
            pdf_path = sys.argv[2]
            show_chunk_debug_info(pdf_path)
            return
        else:
            # Reindex specific PDFs
            pdf_paths = sys.argv[1:]
            reindex_pdfs(pdf_paths, show_chunks=True)
            return
    
    # Interactive mode
    print("Choose an option:")
    print("1. Show existing PDFs in vector store")
    print("2. Reindex specific PDFs (provide paths)")
    print("3. Debug chunking for a single PDF")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        existing_pdfs = get_existing_pdfs()
        if existing_pdfs:
            print(f"\n📚 Existing PDFs in vector store ({len(existing_pdfs)}):")
            for pdf_name in existing_pdfs:
                print(f"  - {pdf_name}")
        else:
            print("\n📚 No PDFs found in vector store")
    
    elif choice == "2":
        print("\nEnter PDF paths (one per line, empty line to finish):")
        pdf_paths = []
        while True:
            path = input("PDF path: ").strip()
            if not path:
                break
            pdf_paths.append(path)
        
        if pdf_paths:
            reindex_pdfs(pdf_paths, show_chunks=True)
        else:
            print("No PDF paths provided")
    
    elif choice == "3":
        pdf_path = input("Enter PDF path: ").strip()
        if pdf_path and os.path.exists(pdf_path):
            show_chunk_debug_info(pdf_path)
        else:
            print("Invalid PDF path")
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
