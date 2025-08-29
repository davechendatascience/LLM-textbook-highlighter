# Vector Store Integration for LLM PDF Reader

## Overview

The LLM PDF Reader now includes a powerful vector store integration using ChromaDB for enhanced document understanding and semantic search capabilities. This feature allows the application to process PDFs into searchable chunks and provide more contextually relevant answers to user questions.

## Features

### 🔍 **Semantic Search**
- Search through PDF content using natural language queries
- Find relevant text chunks based on semantic similarity
- Retrieve context from specific pages and sections

### 📄 **PDF Processing**
- Automatic text extraction and chunking
- Intelligent token-based segmentation with overlap
- Metadata tracking (page numbers, chunk IDs, etc.)

### 🧠 **Enhanced Question Answering**
- Context-aware responses using relevant document chunks
- Improved answer quality with document-specific information
- Reduced token usage through focused context retrieval

### 📊 **Vector Store Management**
- Process multiple PDFs
- View statistics and manage stored documents
- Clear and manage vector store data

## Architecture

```
PDF Document → Text Extraction → Chunking → Embedding Generation → ChromaDB Storage
                                                      ↓
User Question → Semantic Search → Relevant Chunks → LLM Context → Enhanced Answer
```

## Components

### 1. VectorStoreService (`src/services/vector_store.py`)
Core service handling:
- PDF text extraction and chunking
- Embedding generation using SentenceTransformers
- ChromaDB integration for vector storage
- Semantic search functionality

### 2. VectorStorePanel (`src/gui/vector_store_panel.py`)
GUI component providing:
- PDF selection and processing interface
- Semantic search functionality
- Vector store statistics and management
- Real-time progress tracking

### 3. Enhanced LLMService (`src/llm.py`)
Extended with:
- Vector store integration methods
- Context-enhanced question answering
- PDF tracking and management

## Usage

### Basic Workflow

1. **Open the Application**
   - Launch the LLM PDF Reader
   - The vector store panel appears as the third panel

2. **Select and Process a PDF**
   - Click "Select PDF" in the Vector Store Management panel
   - Choose your PDF file
   - Click "Process PDF" to extract and index the content
   - Wait for processing to complete

3. **Ask Questions with Enhanced Context**
   - Select text in the PDF viewer (optional)
   - Type your question in the text panel
   - Click "Ask Question"
   - The system will automatically use vector store context for better answers

4. **Search Document Content**
   - Use the semantic search feature in the vector store panel
   - Enter natural language queries
   - View relevant chunks from the document

### Advanced Features

#### Semantic Search
- Enter queries like "What are the main concepts in chapter 3?"
- Find relevant content across the entire document
- View results with page numbers and context

#### Vector Store Statistics
- Monitor total chunks and indexed PDFs
- Track document processing status
- Manage stored data

#### Multi-PDF Support
- Process multiple PDFs in the same session
- Search across all indexed documents
- Maintain separate metadata for each document

## Technical Details

### Chunking Strategy
- **Token-based segmentation**: Uses tiktoken for accurate token counting
- **Overlap**: 50 tokens overlap between chunks for context continuity
- **Maximum chunk size**: 512 tokens per chunk
- **Boundary cleaning**: Removes partial words at chunk boundaries

### Embedding Model
- **Model**: `all-MiniLM-L6-v2` (SentenceTransformers)
- **Dimensions**: 384-dimensional embeddings
- **Performance**: Fast inference with good quality
- **Size**: ~90MB model size

### Vector Database
- **Database**: ChromaDB with persistent storage
- **Similarity metric**: Cosine similarity
- **Storage location**: `./vector_store/` (configurable)
- **Collection**: `pdf_chunks` with metadata indexing

### Performance Considerations
- **Processing time**: ~1-2 seconds per page (depending on content)
- **Memory usage**: ~1-2MB per 1000 chunks
- **Storage**: ~10-50KB per chunk (including embeddings)
- **Search speed**: Sub-second response for typical queries

## Configuration

### Dependencies
```bash
pip install chromadb sentence-transformers tiktoken
```

### Environment Variables
- `VECTOR_STORE_PATH`: Custom path for vector store data (default: `./vector_store/`)
- `CHUNK_MAX_TOKENS`: Maximum tokens per chunk (default: 512)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)

### Model Configuration
The embedding model can be changed in `src/services/vector_store.py`:
```python
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
```

Alternative models:
- `BAAI/bge-small-en-v1.5` (better performance, larger size)
- `text-embedding-ada-002` (OpenAI, requires API key)
- `all-mpnet-base-v2` (higher quality, slower)

## API Reference

### VectorStoreService Methods

#### `process_pdf(pdf_path, pdf_name=None)`
Process a PDF file and create chunks:
```python
chunks = vector_store.process_pdf("document.pdf", "My Document")
```

#### `search_similar_chunks(query, n_results=5, filter_metadata=None)`
Search for relevant chunks:
```python
results = vector_store.search_similar_chunks("machine learning", n_results=3)
```

#### `get_collection_stats()`
Get vector store statistics:
```python
stats = vector_store.get_collection_stats()
print(f"Total chunks: {stats['total_chunks']}")
```

#### `clear_collection()`
Clear all data from the vector store:
```python
success = vector_store.clear_collection()
```

### LLMService Vector Store Methods

#### `set_current_pdf(pdf_path, pdf_name=None)`
Set the current PDF for operations:
```python
llm_service.set_current_pdf("document.pdf")
```

#### `process_current_pdf()`
Process the current PDF:
```python
success = llm_service.process_current_pdf()
```

#### `ask_question_with_context(question, selected_text="", length="medium")`
Ask questions with enhanced context:
```python
response = llm_service.ask_question_with_context("What is this about?", selected_text)
```

## Troubleshooting

### Common Issues

1. **Processing fails**
   - Check if PDF is corrupted or password-protected
   - Ensure sufficient disk space
   - Verify PDF contains extractable text

2. **Search returns no results**
   - Confirm PDF has been processed successfully
   - Check vector store statistics
   - Try different search terms

3. **Performance issues**
   - Reduce chunk size for large documents
   - Clear vector store if it becomes too large
   - Restart application if memory usage is high

### Debug Information
Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Hybrid search**: Combine vector and keyword search
- **Cross-document search**: Find connections between multiple PDFs
- **Query expansion**: Automatically expand search terms
- **Caching**: Cache frequently accessed embeddings
- **Batch processing**: Process multiple PDFs simultaneously

### Performance Optimizations
- **Async processing**: Non-blocking PDF processing
- **Incremental updates**: Update only changed sections
- **Compression**: Compress embeddings for storage efficiency
- **Indexing**: Advanced indexing for faster search

## Contributing

To contribute to the vector store functionality:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This vector store integration is part of the LLM PDF Reader project and follows the same licensing terms.
