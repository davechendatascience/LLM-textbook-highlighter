# LLM Textbook Highlighter

A simplified, intelligent PDF highlighting and question-answering tool powered by Perplexity AI. The system features fast text extraction, interactive GUI, and smart question generation with customizable answer lengths. Optimized for reliability and ease of use.

## 🚀 Quick Start

### Cross-Platform Mode (Recommended)
```bash
python run_reader.py
```

**Features:**
- **Reliable dropdowns**: PySide6 provides consistent dropdown functionality across all platforms
- **Professional UI**: Native look and feel on Windows, macOS, and Linux
- **Fast PDF rendering**: Uses PyMuPDF for efficient text extraction
- **Cross-platform compatibility**: Works identically on all operating systems
- **Better Mac compatibility**: PySide6 has improved compatibility with macOS

### Legacy Tkinter Mode
```bash
python run_interactive.py
```

**Note**: The Tkinter version has known dropdown responsiveness issues on some platforms. Use the PyQt6 version for the best experience.

### Legacy Notice
The batch processing mode has been removed for system simplification and to prevent credit waste on non-functional features. Use the interactive mode for all PDF processing needs.

## 🏗️ Project Structure

```
LLM-textbook-highlighter/
├── src/                     # Core application modules
│   ├── config.py           # Configuration and settings
│   ├── reader.py  # Cross-platform GUI
│   ├── llm.py              # Perplexity API integration  
│   └── utils.py            # Utility functions
├── tests/                   # Test PDFs for development
├── run_reader.py  # Cross-platform launcher
├── main.py                 # Textbook highlighter
└── secrets.json            # API keys (create this file)
```

## 🔧 Installation

### Cross-Platform Installation
```bash
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
./install.ps1
```

### Manual Installation
```bash
pip install PyQt6 PyMuPDF Pillow requests
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
- 🔍 **Zoom controls**: Adjust PDF zoom level (50% to 300%) with mouse wheel or buttons
- 📐 **Panel sizing**: Adjust left/right panel widths with keyboard shortcuts or buttons

### Removed Features
- **Batch Processing**: Removed to prevent credit waste and focus on reliable interactive mode
- **Hybrid OCR**: Simplified to fitz-only extraction for better reliability and performance

### Simplified Text Extraction
- ⚡ **Fast and reliable**: Uses PyMuPDF (fitz) for consistent text extraction
- 🎯 **Word wrapping**: Text properly contained within display areas
- 📋 **No complex setup**: Works out of the box without OCR dependencies
- 🔍 **Consistent results**: Predictable extraction across different PDF types

### Display Controls
- **Zoom**: Use Ctrl+MouseWheel, toolbar dropdown (50%-300%), or Zoom In/Out buttons
- **Panel Sizing**: Use Ctrl+Left/Right arrows or Wider/Narrower PDF buttons
- **Reset Zoom**: Press Ctrl+0 to reset to 100% zoom
- **Status Display**: Current zoom level shown in the control panel

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

