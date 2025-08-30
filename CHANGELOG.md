# Changelog

## [Unreleased]

### 🚀 Major Features: Vector Store Management & Multilingual Support
- **🗄️ Vector Store Management**: Complete vector store administration system
  - **Vector Store Dialog**: Dedicated UI for managing indexed PDFs and chunks
  - **PDF Reindexing**: Rebuild entire vector store with improved multilingual tokenizer
  - **Individual PDF Management**: Delete specific PDFs or clear all data
  - **Progress Tracking**: Real-time progress bars for reindexing operations
  - **Smart Path Detection**: Automatically detects and validates PDF file paths for reindexing
- **🌍 Multilingual Tokenizer**: Enhanced language support for better text chunking
  - **Robust Language Detection**: Character-counting based detection for Chinese, Japanese, Korean, etc.
  - **Language-Aware Chunking**: Optimal chunk boundaries for different writing systems
  - **Cross-Language Compatibility**: Maintains tiktoken compatibility for LLM token counting
  - **Improved Context Retrieval**: Better semantic search across multiple languages
- **🔍 Show Context Chunks**: Enhanced debugging and transparency
  - **Chunk Visualization**: Display which document chunks are used for context
  - **Similarity Scores**: Show semantic similarity between query and retrieved chunks
  - **Chunk Preview**: Preview of chunk content with metadata (PDF, page, chunk number)
  - **UI Toggle**: Easy on/off switch for chunk visibility in responses

### 🚀 Major Features: Research Integration & Modular Architecture
- **📚 ArXiv Research Integration**: Direct ArXiv API integration for automatic paper search and citation
  - **Smart Search Term Extraction**: Intelligent keyword extraction focusing on mathematical concepts
  - **Automatic Research Enhancement**: LLM responses automatically enhanced with related research papers
  - **Clickable Paper Links**: Direct links to ArXiv pages and PDF downloads
  - **Research Panel**: Dedicated UI for manual paper search and exploration
- **🏗️ Modular Architecture**: Complete codebase refactoring for maintainability
  - **Separated GUI Components**: `PDFViewer`, `TextPanel`, `ResearchPanel`, `MainWindow`
  - **Service Layer**: `ArxivService`, `LLMService`, `PDFProcessor`
  - **Utility Modules**: `LanguageSupport`, `MarkdownTextWidget`
  - **Clean Imports**: Proper package structure with `__init__.py` files

### Enhanced Text Display
- **Automatic Citations**: References are now automatically displayed as clickable links in the response
- **Context Window Logic**: Fixed context window to properly separate selected text from background context
- **Improved Link Processing**: Enhanced markdown link rendering with proper HTML generation
- **Better URL Handling**: Cleaned up URL processing to remove artifacts and ensure proper link functionality

### Bug Fixes
- **Fixed Vector Store Operations**: Resolved ChromaDB deletion errors and method name mismatches
- **Fixed Context Window**: Selected text now always shows only the red box content, while context pages are used as background for LLM
- **Fixed Citation Links**: URLs no longer have trailing `)` characters or extra `[` symbols
- **Fixed Mouse Click Errors**: Resolved `AttributeError` with `anchorName()` vs `anchorNames()`
- **Fixed Markdown Processing**: Improved order of operations to prevent link processing conflicts
- **Fixed Search Term Extraction**: Improved mathematical concept recognition and filtering

### Technical Improvements
- **Cleaner Prompt Structure**: Enhanced LLM prompts to clearly distinguish between selected text and background context
- **Better Debug Output**: Improved console logging for easier troubleshooting
- **Simplified HTML Generation**: Removed inline styles in favor of CSS styling for better link rendering
- **Direct ArXiv API**: Replaced problematic MCP integration with reliable direct API calls

### 🔮 Future Improvements (Planned)
- **Enhanced Search Algorithms**: 
  - **ML-based Keyword Extraction**: 
    - **Phraseformer approach**: BERT + graph embeddings for multimodal key-phrase extraction
    - **Hybrid NLP pipeline**: SpaCy NER + FinBERT-based KeyBERT embeddings + YAKE + EmbedRank
    - **Zshot framework**: Zero-shot NER and relation extraction using large language models
  - **Semantic Search & Embeddings**:
    - **Game-theoretic compression**: Optimize latent-space compression for transformer-based vector search
    - **Multi-task embeddings**: Unified query/paper embeddings like OmniSearchSage
    - **Citation-aware search**: MP-BERT4CR for multi-positive citation recommendation
    - **Multilingual Embedding Models**: Support for better cross-language similarity search
      - **paraphrase-multilingual-MiniLM-L12-v2**: Enhanced multilingual semantic understanding
      - **distiluse-base-multilingual-cased-v2**: Improved cross-language document retrieval
      - **Language-specific embeddings**: Specialized models for Chinese, Japanese, Korean, etc.
  - **Academic Research Integration**:
    - **IntellectSeeker approach**: LLM-based semantic enhancement with probabilistic filtering
    - **Citation network analysis**: CQBG-R for citation-query blended graph ranking
    - **Multi-database support**: Expand beyond ArXiv to PubMed, IEEE, ACM, and other research databases
- **Research Panel Enhancements**:
  - Add paper filtering by date, category, and relevance score
  - Implement paper comparison and side-by-side viewing
  - Add paper bookmarking and personal library features
  - Export research findings to citation managers (Zotero, Mendeley)
- **AI Research Assistant**:
  - Automatic paper summarization and key point extraction
  - Research trend analysis and visualization
  - Citation recommendation based on selected text
  - Integration with academic writing tools
- **Performance Optimizations**:
  - Cache frequently searched papers and results
  - Implement background paper downloading
  - Add offline paper storage and management
  - Optimize search queries for better relevance
- **User Experience**:
  - Add research history and search suggestions
  - Implement paper recommendation system
  - Add research collaboration features
  - Create research project organization tools

## [2.1.0] - 2025-08-26

### ✨ New Features
- **📚 Enhanced Text Display**: Complete markdown and LaTeX rendering system
  - **Clickable Hyperlinks**: URLs automatically converted to clickable links in responses
  - **Markdown Support**: Full rendering of **bold**, *italic*, `code`, headers, and lists
  - **LaTeX Integration**: Mathematical expressions and symbols rendered properly
  - **Rich Formatting**: Professional text display with proper typography
  - **📖 Automatic Citations**: Perplexity API citations extracted and displayed as clickable links
- **Enhanced User Experience**: Direct link access without separate windows or buttons
- **🎨 Font Size Control**: Maintains font size changing feature with markdown rendering

### 🔧 Technical Improvements
- **MarkdownTextWidget**: Custom widget with markdown and LaTeX processing
- **HTML Rendering**: Advanced text-to-HTML conversion with link support
- **LaTeX Symbol Support**: Comprehensive mathematical notation rendering
- **Link Integration**: Seamless browser opening from within response text
- **Clean Interface**: Removed separate reference window for integrated experience

---

## [2.0.0] - 2025-08-23

### 🚀 Major Refactoring: Google GenAI Integration & Code Restructuring

#### ✨ New Features
- **Modern Google GenAI SDK**: Migrated from `google-generativeai` to `google-genai` (v1.31+)
  - Cleaner API with `Client()` and `generate_content()` interface
  - Enhanced web search grounding capabilities
  - Reduced dependency footprint
- **Centralized PDF Processing**: New `PDFProcessor` class consolidates all extraction methods
- **Advanced Symbol Fixing**: Comprehensive mathematical notation correction system
- **Multi-Method Text Extraction**: Automatic selection of best extraction method based on content

#### 🏗️ Code Architecture
- **Restructured Project Layout**:
  ```
  ├── src/                     # Core application modules
  ├── extraction_methods/      # PDF text extraction algorithms  
  ├── utils/                   # Shared utilities
  ├── tests/                   # Test suite and sample PDFs
  └── run_interactive.py       # New unified launcher
  ```
- **Modular Design**: Clean separation of concerns with specialized modules
- **Configuration Management**: Centralized settings in `src/config.py`
- **Enhanced Testing**: Comprehensive validation with multiple test scripts

#### 🔧 Technical Improvements
- **Mathematical Symbol Support**: Enhanced Unicode symbol preservation and corruption fixing
  - Automatic fixing: `�P` → `≠`, `Sum(` → `Σ(`, etc.
  - Support for Greek letters, operators, and mathematical notation
- **Smart Text Extraction**: Auto-selection from 6 different PyMuPDF extraction methods
- **Cost Optimization**: Web search disabled by default to reduce API costs
- **API Flexibility**: Support for both Gemini and Perplexity with configurable search options

#### 📚 Mathematical Notation Enhancement
- **Symbol Corruption Recovery**: Advanced pattern recognition for PDF extraction artifacts
- **Context-Aware Replacements**: Intelligent mathematical expression reconstruction
- **LaTeX Compatibility**: Better handling of LaTeX-rendered mathematical content
- **Unicode Preservation**: Proper handling of mathematical Unicode characters

#### 🧪 Testing & Validation
- **Comprehensive Test Suite**:
  - `test_restructured.py`: Core module integration validation
  - `test_google_genai.py`: API functionality testing with/without web search
  - `test_interactive_launch.py`: GUI initialization and cleanup testing
- **Sample PDF Generation**: Automated creation of test documents with mathematical content
- **Virtual Environment Support**: Full compatibility with isolated Python environments

#### 🐛 Bug Fixes
- Fixed missing `extract_text_by_intersection` method reference
- Corrected Unicode encoding issues in console output for Windows
- Resolved import path issues in restructured codebase
- Fixed coordinate conversion for PDF text selection

#### 📖 Documentation
- **Updated README**: Comprehensive project documentation with new structure
- **API Cost Guide**: Detailed breakdown of different API pricing tiers
- **Usage Examples**: Step-by-step instructions for both interactive and batch modes
- **Development Guide**: Instructions for extending functionality

#### 💸 Cost Optimization
- **Default Settings**: Web search disabled by default (saves ~80% on API costs)
- **Flexible Configuration**: Easy toggle between search and non-search modes
- **API Comparison**: Clear cost breakdown for different providers:
  - Gemini 2.0 Flash: ~$0.0075/query (recommended)
  - Gemini with search: $35/1000 queries
  - Perplexity with/without search: $1-5/1000 queries

#### ⚠️ Breaking Changes
- **Package Dependency**: Changed from `google-generativeai` to `google-genai`
- **Method Names**: Some internal methods renamed for consistency
- **File Structure**: Major reorganization - update any custom imports
- **Configuration**: New centralized config system replaces direct API key handling

#### 🔄 Migration Guide
1. **Update Dependencies**: `pip install -r requirements.txt` (will install `google-genai`)
2. **API Keys**: Ensure `secrets.json` format remains the same
3. **Imports**: Use new entry points (`run_interactive.py` vs direct module imports)
4. **Testing**: Run validation scripts to ensure proper setup

---

### Previous Versions
- **[1.x]**: Original implementation with `google-generativeai` and basic PDF processing
- **[0.x]**: Initial prototype with Perplexity integration