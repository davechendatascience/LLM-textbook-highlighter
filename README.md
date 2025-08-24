# LLM Textbook Highlighter

An intelligent PDF highlighting tool powered by Google's Gemini AI that can process textbooks and documents of any size. The system features advanced mathematical symbol extraction, interactive GUI, and both automated batch processing and manual highlighting modes. Built with the modern `google-genai` SDK for optimal performance and web search capabilities.

## 🚀 Quick Start

### Interactive Mode (Recommended)
```bash
python run_interactive.py
```

### Batch Processing Mode  
```bash
python main.py
```

## 🏗️ Project Structure

```
LLM-textbook-highlighter/
├── src/                     # Core application modules
│   ├── config.py           # Configuration and settings
│   ├── interactive_highlighter.py  # GUI application
│   ├── llm.py              # LLM API integrations  
│   ├── pdf_processor.py    # Centralized PDF processing
│   └── utils.py            # Utility functions
├── extraction_methods/      # PDF text extraction algorithms
│   ├── advanced_extraction.py  # Multi-method extraction testing
│   └── symbol_fixer.py     # Mathematical symbol correction
├── utils/                   # Shared utilities
├── tests/                   # Test suite and sample PDFs
├── run_interactive.py       # Interactive GUI launcher
├── main.py                 # Batch processing entry point
└── test_restructured.py    # System validation script
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
    "gemini_api_key": "your_gemini_api_key_here",
    "perplexity_api_key": "your_perplexity_api_key_here"
}
```

**Cost Optimization:**
- Gemini 2.0 Flash (without web search): ~$0.0075 per query (recommended)
- Gemini with web search grounding: $35 per 1,000 queries  
- Perplexity with search: $5 per 1,000 queries
- Perplexity without search: $1 per 1,000 queries

**Note:** Built with the modern `google-genai` SDK (v1.31+) which provides cleaner API access and better web search integration compared to the older `google-generativeai` package.

## ✨ Features

### Interactive GUI Mode
- 📖 Visual PDF navigation and rendering  
- 🖱️ Click-and-drag text selection
- 🔍 Advanced mathematical symbol extraction
- 🤖 AI-powered question generation
- 💬 Custom Q&A with web search toggle
- 📝 Session notes with export capabilities
- 🧮 Smart text extraction for LaTeX/mathematical content

### Batch Processing Mode  
- 📚 Process entire textbooks (hundreds of pages)
- 🎯 Automated highlight generation
- 💬 Contextual explanation comments
- 📊 Grouped highlight organization

### Advanced Text Extraction
- 🔬 Multiple PyMuPDF extraction methods (standard, dictionary, blocks, words, rawdict)
- 🔧 Automatic symbol corruption fixing (�P → ≠, Sum( → Σ)
- 📐 Mathematical notation preservation
- 🎯 Smart extraction method selection based on content analysis

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
2. Load PDF using the file menu
3. Navigate pages with the page selector
4. Click and drag to select text regions
5. Get AI explanations and suggested questions
6. Export session notes

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

