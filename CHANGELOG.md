# Changelog

## [Unreleased]

### Enhanced Text Display
- **Automatic Citations**: References are now automatically displayed as clickable links in the response
- **Context Window Logic**: Fixed context window to properly separate selected text from background context
- **Improved Link Processing**: Enhanced markdown link rendering with proper HTML generation
- **Better URL Handling**: Cleaned up URL processing to remove artifacts and ensure proper link functionality

### Bug Fixes
- **Fixed Context Window**: Selected text now always shows only the red box content, while context pages are used as background for LLM
- **Fixed Citation Links**: URLs no longer have trailing `)` characters or extra `[` symbols
- **Fixed Mouse Click Errors**: Resolved `AttributeError` with `anchorName()` vs `anchorNames()`
- **Fixed Markdown Processing**: Improved order of operations to prevent link processing conflicts

### Technical Improvements
- **Cleaner Prompt Structure**: Enhanced LLM prompts to clearly distinguish between selected text and background context
- **Better Debug Output**: Improved console logging for easier troubleshooting
- **Simplified HTML Generation**: Removed inline styles in favor of CSS styling for better link rendering

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