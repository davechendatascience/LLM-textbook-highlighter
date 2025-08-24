# LLM Textbook Highlighter

A simplified, intelligent PDF highlighting and question-answering tool powered by Perplexity AI. The system features fast text extraction, interactive GUI, and smart question generation with customizable answer lengths. Optimized for reliability and ease of use.

## 🚀 Quick Start

### Interactive Mode (Recommended)
```bash
python run_interactive.py
```

Features a clean, intuitive interface using **fitz (PyMuPDF)** for fast and reliable text extraction from PDF documents.

### Batch Processing Mode  
```bash
python main.py
```

## 🏗️ Project Structure

```
LLM-textbook-highlighter/
├── src/                     # Core application modules
│   ├── config.py           # Configuration and settings
│   ├── simple_interactive_highlighter.py  # Simplified GUI application
│   ├── llm.py              # Perplexity API integration  
│   └── utils.py            # Utility functions
├── tests/                   # Test PDFs for development
├── run_interactive.py       # Interactive GUI launcher
├── main.py                 # Batch processing entry point
└── secrets.json            # API keys (create this file)
```

## 🔧 Installation

### Windows (PowerShell)
```powershell
./install.ps1
```

### Manual Installation
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

**Available Models:**
- **sonar**: Fast question generation (~$1 per 1,000 queries)
- **sonar-reasoning**: Detailed answers (~$5 per 1,000 queries)
- Web search enabled for comprehensive responses

## ✨ Features

### Interactive GUI Mode
- 📖 Visual PDF navigation with page selector
- 🖱️ Click-and-drag text selection  
- 🎯 **Fast fitz extraction**: Reliable PyMuPDF text extraction
- 🤖 **Smart question generation**: AI suggests relevant questions
- 💬 **Custom Q&A**: Ask your own questions with web search
- 🔧 **Answer length control**: Choose short, medium, long, or comprehensive responses
- 📝 **Session tracking**: Automatic note-keeping with timestamps
- 🎨 **Font size control**: Adjustable text size for better readability
- 📜 **Resizable panels**: Drag dividers to customize layout

### Batch Processing Mode  
- 📚 Process entire textbooks (hundreds of pages)
- 🎯 Automated highlight generation
- 💬 Contextual explanation comments
- 📊 Grouped highlight organization

### Simplified Text Extraction
- ⚡ **Fast and reliable**: Uses PyMuPDF (fitz) for consistent text extraction
- 🎯 **Word wrapping**: Text properly contained within display areas
- 📋 **No complex setup**: Works out of the box without OCR dependencies
- 🔍 **Consistent results**: Predictable extraction across different PDF types

## 🧪 Testing

```bash
# Validate restructured codebase
python tests/test_restructured.py

# Test Google GenAI integration
python tests/test_google_genai.py

# Test interactive highlighter functionality
python tests/test_interactive_launch.py

# Test with real textbook (classical mechanics)
python tests/test_real_textbook.py

# Run comprehensive test suite
python tests/run_tests.py

# Manual testing with generated PDFs
python tests/manual_test.py

# Create test PDFs with mathematical content
python tests/create_realistic_math_pdf.py
```

## 📊 Mathematical Symbol Support

The system includes advanced support for mathematical notation:

- **Greek Letters**: α, β, γ, δ, λ, μ, σ, θ, ω, Γ, Δ, Λ, Σ, Θ, Ω
- **Operators**: ∑, ∫, ∂, ∇, ≈, ≠, ≤, ≥, ∞
- **Sets**: ∈, ∉, ⊆, ∪, ∩
- **Corrupted Symbol Recovery**: Automatic fixing of PDF extraction artifacts

## 🔍 Usage Examples

### Interactive Highlighting
1. Launch: `python run_interactive.py`
2. **Check OCR Status**: System displays available OCR capabilities on startup
   - "General + Math": Full hybrid OCR with mathematical enhancement
   - "General only": Standard OCR without specialized math processing  
   - "Traditional": PyMuPDF extraction only
3. Load PDF using the file menu
4. Navigate pages with the page selector
5. **Enable Hybrid OCR** (optional): Toggle for enhanced text extraction
6. Click and drag to select text regions
7. Get AI explanations and suggested questions
8. Export session notes

### Batch Processing
1. Run: `python main.py`
2. Select input PDF file
3. Choose output location
4. System automatically processes entire document
5. Receive highlighted PDF with grouped annotations

## 🛠️ Development

### Adding New Extraction Methods
1. Implement in `extraction_methods/`
2. Register in `pdf_processor.py`
3. Add tests in `tests/`

### Extending Symbol Support
1. Update `symbol_fixer.py` mapping tables
2. Add pattern recognition rules
3. Test with mathematical PDFs

## 📈 Performance

- **Large Documents**: Optimized for textbooks (800+ pages)
- **Memory Efficient**: Processes one page at a time
- **Smart Caching**: Avoids redundant API calls
- **Configurable Chunking**: Adjustable for cost vs accuracy  

