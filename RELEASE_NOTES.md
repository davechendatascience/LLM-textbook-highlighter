# Release Notes v2.0.0 - Google GenAI Integration

## 🚀 Major Release: Complete Refactoring & Modern SDK Integration

This release represents a complete architectural overhaul of the LLM Textbook Highlighter, introducing modern Google GenAI SDK integration, enhanced mathematical symbol processing, and a restructured codebase for better maintainability.

## 🎯 Key Highlights

### ✨ Google GenAI SDK Integration
- **Migrated to `google-genai`** - Modern, lighter-weight SDK with cleaner API
- **Enhanced web search** - Improved grounding capabilities with `Tool(google_search={})`
- **Better error handling** - More robust API interaction with proper exception management
- **Cost optimization** - Web search disabled by default to reduce API costs by ~80%

### 🔧 Mathematical Symbol Processing
- **Advanced symbol corruption recovery** - Fixes common PDF extraction artifacts (`�P` → `≠`)
- **Comprehensive Unicode support** - Proper handling of Greek letters (α, β, γ, δ, Σ, Ω)
- **Context-aware replacements** - Intelligent reconstruction of mathematical expressions
- **Multi-method extraction** - 6 different PyMuPDF approaches with auto-selection

### 🏗️ Code Architecture Improvements
- **Modular structure** - Clean separation with `src/`, `extraction_methods/`, `utils/`
- **Centralized configuration** - Single source of truth in `src/config.py`
- **Unified PDF processing** - `PDFProcessor` class consolidates all extraction methods
- **Enhanced testing** - Comprehensive validation suite with multiple test scenarios

## 📋 What's New

### New Entry Points
```bash
# Interactive GUI (recommended)
python run_interactive.py

# Batch processing
python main.py

# API testing
python test_google_genai.py
```

### Enhanced Features
- **Smart text extraction** with automatic method selection
- **Mathematical notation preservation** for LaTeX-rendered content
- **Flexible API configuration** with cost optimization settings
- **Improved error handling** and debugging capabilities

### Testing & Validation
- **`test_restructured.py`** - Core module integration
- **`test_google_genai.py`** - API functionality with/without web search
- **`test_interactive_launch.py`** - GUI and text extraction validation

## 🐛 Fixes
- ✅ Fixed missing `extract_text_by_intersection` method reference
- ✅ Resolved Unicode encoding issues in Windows console output
- ✅ Corrected import paths in restructured codebase
- ✅ Fixed PDF coordinate conversion for text selection

## 📦 Installation & Migration

### New Installation
```bash
pip install -r requirements.txt
python test_restructured.py  # Validate setup
```

### Migration from v1.x
1. **Dependencies**: Will automatically install `google-genai` (replaces `google-generativeai`)
2. **API keys**: Keep same `secrets.json` format
3. **Usage**: Use new entry points (`run_interactive.py`)
4. **Testing**: Run validation scripts to confirm setup

## 💰 Cost Optimization

| API Configuration | Cost per Query | Recommended Use |
|------------------|----------------|-----------------|
| Gemini 2.0 Flash | ~$0.0075 | Default (best value) |
| Gemini + Web Search | $0.035 | Research queries |
| Perplexity + Search | $0.005 | Alternative with search |
| Perplexity Basic | $0.001 | Budget option |

## 🔄 Breaking Changes

⚠️ **Important**: This is a major version with breaking changes:

- **Package dependency** changed from `google-generativeai` to `google-genai`
- **File structure** completely reorganized
- **Some internal method names** changed for consistency
- **Configuration system** centralized (affects custom integrations)

## 🎉 Ready to Use

The system is fully operational and tested with:
- ✅ All core functionality preserved
- ✅ Enhanced mathematical symbol support
- ✅ Modern SDK integration
- ✅ Comprehensive test coverage
- ✅ Updated documentation

**Start here**: `python run_interactive.py`