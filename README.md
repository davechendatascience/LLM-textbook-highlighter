# LLM PDF Reader

A modern, intelligent PDF reader powered by Perplexity AI. Features cross-platform compatibility, fast text extraction, interactive GUI, and smart question generation with customizable answer lengths. Optimized for reliability and ease of use.

## 🚀 Quick Start

### Install from Package (Recommended)
Download the latest installer from the [GitHub Releases](https://github.com/yourusername/LLM-textbook-highlighter/releases):
- **macOS**: `LLM-PDF-Reader-Installer.dmg` (~70MB) - Professional drag & drop installation
- **All Platforms**: `LLM-PDF-Reader-Installer.zip` (~65MB) - Extract and run

### Run from Source
```bash
# Install dependencies
pip install -r requirements.txt

# Launch the application
python run_reader.py
```

**Features:**
- **Professional UI**: Native look and feel on Windows, macOS, and Linux
- **Fast PDF rendering**: Uses PyMuPDF for efficient text extraction
- **Cross-platform compatibility**: Works identically on all operating systems
- **Built-in API configuration**: Easy setup for Perplexity API key



## 🏗️ Project Structure

```
LLM-textbook-highlighter/
├── src/                     # Core application modules
│   ├── config.py           # Configuration and settings
│   ├── reader.py           # Main GUI application
│   ├── llm.py              # Perplexity API integration  
│   └── utils.py            # Utility functions
├── tests/                   # Test PDFs for development
├── run_reader.py           # Application launcher
├── build_mac_installer.py  # Unified packaging script
├── create_release.py       # Release helper script
├── requirements.txt        # Python dependencies
└── secrets.json            # API keys (create this file)
```

## 🔧 Installation

### Dependencies
The application requires the following Python packages:
- PySide6 (cross-platform GUI)
- PyMuPDF (PDF processing)
- Pillow (image processing)
- requests (API communication)
- markdown (text formatting and rendering)

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## 🔑 API Configuration

Create a `secrets.json` file in the root directory:

```json
{
    "perplexity_api_key": "your_perplexity_api_key_here"
}
```

**Getting a Perplexity API Key:**
1. Visit [Perplexity AI](https://www.perplexity.ai/)
2. Sign up for an account
3. Go to your account settings
4. Generate an API key
5. Add it to your `secrets.json` file

**Available Models:**
- **sonar**: Fast question generation and short/medium answers (~$1 per 1,000 queries)
- **sonar-reasoning**: Detailed answers for complex questions (~$5 per 1,000 queries)

**Model Selection:**
- **Question Generation**: Always uses `sonar` for speed and clean formatting
- **Answer Generation**: 
  - `sonar` for short/medium answers (faster, cheaper)
  - `sonar-reasoning` for long/comprehensive answers (better reasoning)
- **Response Cleaning**: Automatically removes `<think>` tags from `sonar-reasoning` responses

**Features:**
- Web search enabled for comprehensive responses
- Automatic response cleaning and formatting

**Note:** The application will show clear error messages if the API key is missing or invalid.

## 🚀 Features

### Core Functionality
- **PDF Text Extraction**: Extract text from selected regions with multiple extraction methods
- **LLM Integration**: Ask questions about extracted text using Perplexity API
- **Multi-language Support**: Automatic language detection and response in user's preferred language
- **Smart Question Generation**: AI-powered question suggestions based on extracted content

### Enhanced Text Display
- **Markdown Rendering**: Rich text formatting with support for bold, italic, headers, lists, and code blocks
- **LaTeX Support**: Mathematical expressions and symbols rendered properly
- **Automatic Citations**: References are automatically displayed as clickable links in the response
- **Font Size Control**: Adjustable text size for better readability

### Context Management
- **Context Window**: Extract additional pages as background context (±0 to ±5 pages)
- **Smart Text Separation**: Selected text (red box) is always the main focus, context pages provide background
- **Clear Prompt Structure**: LLM receives clear distinction between selected text and background context

### User Experience
- **Intuitive Interface**: Clean, modern UI with easy-to-use controls
- **Real-time Feedback**: Status updates and progress indicators
- **Error Handling**: Comprehensive error messages and fallback options

## 🧪 Testing

The application includes test PDFs in the `tests/` directory for development and validation.

## 📊 Mathematical Symbol Support

The system supports mathematical notation through PyMuPDF text extraction:

- **Greek Letters**: α, β, γ, δ, λ, μ, σ, θ, ω, Γ, Δ, Λ, Σ, Θ, Ω
- **Operators**: ∑, ∫, ∂, ∇, ≈, ≠, ≤, ≥, ∞
- **Sets**: ∈, ∉, ⊆, ∪, ∩

## 📦 Package Installation

### macOS Users
1. Download `LLM-PDF-Reader-Installer.dmg` from [GitHub Releases](https://github.com/yourusername/LLM-textbook-highlighter/releases)
2. Double-click to mount the DMG
3. Drag "LLM PDF Reader.app" to your Applications folder
4. Launch from Applications or Spotlight

### All Platforms
1. Download `LLM-PDF-Reader-Installer.zip` from [GitHub Releases](https://github.com/yourusername/LLM-textbook-highlighter/releases)
2. Extract the ZIP file
3. Run the application directly

### First-Time Setup
1. **Configure API Key**: Enter your Perplexity API key in the configuration section
2. **Save Settings**: Click "Save" to store your API key
3. **Start Reading**: Open a PDF and begin using the LLM features

## 🔍 Usage Examples

### PDF Reader with LLM Integration
1. **Launch**: Open the installed application or run `python run_reader.py`
2. **Configure API**: Enter your Perplexity API key (first time only)
3. **Load PDF**: Use "Open PDF" button to select a file
4. **Navigate**: Use Previous/Next buttons or page input
5. **Select Text**: Click and drag to create a red selection box
6. **Extract Text**: Click "Extract Text" to get selected content
7. **Generate Questions**: Click "Generate Questions" for AI-suggested questions
8. **Ask Questions**: Type custom questions or select from dropdown
9. **Click Links**: Click any URL or citation link in the response to open it directly in your browser
10. **Adjust Settings**: Use font size and answer length controls



## 🛠️ Development

### Architecture
- **GUI**: PySide6-based cross-platform interface
- **PDF Processing**: PyMuPDF for text extraction and rendering
- **LLM Integration**: Perplexity API with smart model selection
- **Configuration**: JSON-based settings and API key management

### Building Packages
The project includes a unified packaging system for creating macOS installers:

```bash
# Build all packages (app bundle, DMG, ZIP)
python build_mac_installer.py

# Build only app bundle
python build_mac_installer.py --no-dmg --no-zip

# Create PKG installer (requires installer/ directory)
python build_mac_installer.py --pkg

# Clean build directories
python build_mac_installer.py --clean
```

For more details, see [PACKAGING.md](PACKAGING.md).

### Key Components
- `src/reader.py`: Main application with GUI and PDF handling
- `src/llm.py`: Perplexity API integration
- `src/config.py`: Configuration and secrets management
- `src/utils.py`: Utility functions

## 📈 Performance

- **Cross-platform**: Consistent performance on Windows, macOS, and Linux
- **Memory efficient**: Processes one page at a time
- **Fast rendering**: PyMuPDF provides quick PDF display
- **Smart caching**: Avoids redundant API calls

## 🚀 Future Development Roadmap

### 📚 PDF Library & Vector Store Integration

**Vision**: Transform from single-PDF processing to a comprehensive PDF library management system with intelligent context retrieval.

#### **Phase 1: Vector Store Foundation**
- **Embedding Generation**: Convert PDF text chunks into high-dimensional vectors
- **Vector Database**: Implement local vector storage (ChromaDB, FAISS, or Pinecone)
- **Chunking Strategy**: Intelligent text segmentation preserving semantic meaning
- **Metadata Storage**: Store PDF metadata, page numbers, and chunk relationships

#### **Phase 2: Multi-PDF Library Management**
- **Library Interface**: GUI for managing multiple PDF collections
- **Batch Processing**: Upload and process entire PDF libraries
- **Collection Organization**: Create themed collections (e.g., "Mathematics", "Physics", "Computer Science")
- **Search Across Library**: Find relevant content across all PDFs in the library

#### **Phase 3: Advanced Context Retrieval**
- **Semantic Search**: Find the most relevant PDF chunks for any question
- **Context-Aware Responses**: LLM responses based on content from multiple PDFs
- **Cross-Reference Detection**: Automatically identify related concepts across different documents
- **Citation Tracking**: Track which PDFs and pages contributed to each response

#### **Phase 4: Intelligent Features**
- **Knowledge Graph**: Build relationships between concepts across the entire library
- **Concept Clustering**: Group related topics and concepts automatically
- **Learning Paths**: Suggest reading sequences based on topic dependencies
- **Collaborative Annotations**: Share highlights and notes across users

#### **Technical Architecture**
```
PDF Library System
├── Vector Store Layer
│   ├── Embedding Engine (OpenAI, SentenceTransformers)
│   ├── Vector Database (ChromaDB/FAISS)
│   └── Chunking Pipeline
├── Library Management
│   ├── PDF Collection Manager
│   ├── Metadata Indexer
│   └── Search Engine
├── Context Retrieval
│   ├── Semantic Search
│   ├── Relevance Ranking
│   └── Context Assembly
└── Enhanced LLM Integration
    ├── Multi-PDF Context Injection
    ├── Citation Generation
    └── Knowledge Synthesis
```

#### **Benefits of Vector Store Integration**
- **📖 Comprehensive Knowledge**: Access information across entire PDF libraries
- **🎯 Precise Context**: Retrieve the most relevant content for any question
- **⚡ Fast Retrieval**: Vector similarity search for instant results
- **🔗 Cross-Document Insights**: Connect concepts across multiple sources
- **📊 Scalable**: Handle libraries with thousands of PDFs efficiently
- **🧠 Intelligent**: AI-powered content discovery and relationship mapping

#### **Implementation Timeline**
- **Q1 2024**: Vector store foundation and single-PDF enhancement
- **Q2 2024**: Multi-PDF library management interface
- **Q3 2024**: Advanced context retrieval and semantic search
- **Q4 2024**: Knowledge graph and collaborative features

This roadmap will transform the application from a single-PDF reader into a comprehensive knowledge management system for academic and research workflows.

  

