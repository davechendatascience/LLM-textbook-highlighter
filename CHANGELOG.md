# Changelog

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