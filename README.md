# Cross-Platform PDF Reader with LLM Integration

A modern, intelligent PDF reader powered by Perplexity AI. Features cross-platform compatibility, fast text extraction, interactive GUI, and smart question generation with customizable answer lengths. Optimized for reliability and ease of use.

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

### Installation
```bash
pip install -r requirements.txt
```

**Dependencies:**
- PySide6 (cross-platform GUI)
- PyMuPDF (PDF processing)
- Pillow (image processing)
- requests (API communication)

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

### Cross-Platform PDF Reader
- 📖 **Visual PDF navigation** with page selector and zoom controls
- 🖱️ **Click-and-drag text selection** with visual feedback
- 🎯 **Fast text extraction** using PyMuPDF (fitz)
- 🤖 **AI-powered question generation** from selected text
- 💬 **Interactive Q&A** with customizable answer lengths
- 🎨 **Font size controls** for better readability
- 📜 **Resizable panels** with drag dividers
- 🔍 **Zoom controls** (25% to 400%) with mouse wheel or buttons
- 📐 **Panel sizing** with keyboard shortcuts (Ctrl+Left/Right)

### LLM Integration
- **Smart model selection**: Uses `sonar` for questions, `sonar-reasoning` for complex answers
- **Response cleaning**: Automatically removes `<think>` tags from LLM responses
- **Cost optimization**: Chooses appropriate models based on answer length
- **Error handling**: Clear feedback for missing or invalid API keys

### Text Extraction
- ⚡ **Fast and reliable**: Uses PyMuPDF for consistent text extraction
- 🎯 **Visual selection**: Red selection box shows exactly what will be extracted
- 📋 **No setup required**: Works out of the box
- 🔍 **Cross-platform**: Consistent behavior on Windows, macOS, and Linux

## 🧪 Testing

The application includes test PDFs in the `tests/` directory for development and validation.

## 📊 Mathematical Symbol Support

The system supports mathematical notation through PyMuPDF text extraction:

- **Greek Letters**: α, β, γ, δ, λ, μ, σ, θ, ω, Γ, Δ, Λ, Σ, Θ, Ω
- **Operators**: ∑, ∫, ∂, ∇, ≈, ≠, ≤, ≥, ∞
- **Sets**: ∈, ∉, ⊆, ∪, ∩

## 🔍 Usage Examples

### PDF Reader with LLM Integration
1. **Launch**: `python run_reader.py`
2. **Load PDF**: Use "Open PDF" button to select a file
3. **Navigate**: Use Previous/Next buttons or page input
4. **Select Text**: Click and drag to create a red selection box
5. **Extract Text**: Click "Extract Text" to get selected content
6. **Generate Questions**: Click "Generate Questions" for AI-suggested questions
7. **Ask Questions**: Type custom questions or select from dropdown
8. **Adjust Settings**: Use font size and answer length controls

### Textbook Highlighter (Legacy)
For basic textbook highlighting functionality:
```bash
python main.py
```

## 🛠️ Development

### Architecture
- **GUI**: PySide6-based cross-platform interface
- **PDF Processing**: PyMuPDF for text extraction and rendering
- **LLM Integration**: Perplexity API with smart model selection
- **Configuration**: JSON-based settings and API key management

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

