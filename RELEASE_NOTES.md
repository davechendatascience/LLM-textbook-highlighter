# Release Notes

## [v1.0] - 2025-08-27

### 🎉 Initial Release

LLM PDF Reader v1.0 is the first stable release of our AI-powered PDF reading application. This release provides a complete, production-ready solution for extracting text from PDFs and asking questions using the Perplexity API.

### ✨ Key Features

#### Core Functionality
- **PDF Text Extraction**: Extract text from selected regions with multiple PyMuPDF extraction methods
- **LLM Integration**: Ask questions about extracted text using Perplexity API
- **Visual PDF Navigation**: Page selector and zoom controls (25% to 400%)
- **Interactive Text Selection**: Click-and-drag text selection with visual feedback
- **Smart Question Generation**: AI-powered question suggestions based on extracted content

#### Enhanced Text Display
- **Markdown Rendering**: Rich text formatting with support for bold, italic, headers, lists, and code blocks
- **LaTeX Support**: Mathematical expressions and symbols rendered properly
- **Font Size Control**: Adjustable text size for better readability
- **Clickable Hyperlinks**: URLs in responses are automatically converted to clickable links

#### User Experience
- **Intuitive Interface**: Clean, modern UI with easy-to-use controls
- **Real-time Feedback**: Status updates and progress indicators
- **Error Handling**: Comprehensive error messages and fallback options
- **Resizable Panels**: Drag dividers for custom layout
- **Keyboard Shortcuts**: Panel sizing with Ctrl+Left/Right

### 🔧 Technical Features

#### LLM Integration
- **Smart Model Selection**: Uses `sonar` for questions, `sonar-reasoning` for complex answers
- **Response Cleaning**: Automatically removes `<think>` tags from LLM responses
- **Cost Optimization**: Chooses appropriate models based on answer length
- **Error Handling**: Clear feedback for missing or invalid API keys

#### Text Extraction
- **Multi-Method Extraction**: 6 different PyMuPDF approaches with auto-selection
- **Fast and Reliable**: Uses PyMuPDF for consistent text extraction
- **Visual Selection**: Red selection box shows exactly what will be extracted
- **Cross-platform**: Consistent behavior on Windows, macOS, and Linux

#### Performance
- **Optimized Rendering**: Efficient PDF display with smooth scrolling
- **Memory Management**: Proper cleanup of resources
- **Fast Startup**: Quick application launch and PDF loading

### 📱 Platform Support

#### macOS
- **Native App Bundle**: Standalone `.app` bundle with all dependencies
- **DMG Installer**: Professional drag-and-drop installation
- **ZIP Installer**: Alternative distribution method
- **Universal Binary**: Supports both Intel and Apple Silicon Macs

#### System Requirements
- **macOS**: 10.15 (Catalina) and later
- **Python**: 3.11+ (bundled in app)
- **Memory**: 4GB RAM recommended
- **Storage**: 100MB for application, additional space for PDFs

### 🚀 Installation

#### Quick Start
1. Download the appropriate installer for your system
2. Follow the installation instructions
3. Configure your Perplexity API key
4. Start reading PDFs with AI assistance

#### API Configuration
- **Perplexity API Key**: Required for LLM functionality
- **Easy Setup**: Built-in configuration panel
- **Secure Storage**: API key stored locally

### 📋 Usage Guide

#### Basic Workflow
1. **Open PDF**: Use File → Open or drag and drop
2. **Select Text**: Click and drag to select text regions
3. **Extract Text**: Click "Extract Text" to get selected content
4. **Ask Questions**: Type questions or use generated suggestions
5. **Get Answers**: Receive AI-powered responses with citations

#### Advanced Features
- **Context Window**: Extract additional pages as background context (±0 to ±5 pages)
- **Language Detection**: Automatic language detection for multilingual responses
- **Question Generation**: AI-powered question suggestions
- **Citation Links**: Clickable reference links in responses

### 🔍 What's New in v1.0

#### Initial Release Features
- Complete PDF reading and text extraction functionality
- Full LLM integration with Perplexity API
- Rich text rendering with markdown and LaTeX support
- Professional macOS installer packages
- Comprehensive error handling and user feedback
- Multi-language support framework

#### Documentation
- Complete README with installation and usage instructions
- Comprehensive packaging guide for developers
- API configuration documentation
- Troubleshooting guide

### 🐛 Known Issues

#### Limitations
- **PDF Compatibility**: Some complex PDFs may have extraction issues
- **Large Files**: Very large PDFs (>100MB) may load slowly
- **Network Dependency**: Requires internet connection for LLM features
- **API Limits**: Subject to Perplexity API rate limits

#### Platform Specific
- **macOS Only**: This release is optimized for macOS
- **Permission Issues**: May require manual quarantine attribute removal on first run

### 🔮 Future Roadmap

#### Planned Features
- **Vector Store Integration**: Store and search across entire PDF libraries
- **Cross-platform Support**: Windows and Linux versions
- **Advanced AI Features**: Document summarization and analysis
- **Cloud Integration**: Sync settings and preferences across devices
- **Plugin System**: Extensible architecture for custom features

#### Technical Improvements
- **Performance Optimization**: Faster text extraction and rendering
- **Memory Efficiency**: Reduced memory footprint
- **Offline Mode**: Basic functionality without internet connection
- **Advanced Search**: Full-text search across multiple documents

### 📊 File Information

#### Installer Sizes
- **App Bundle**: ~60-80 MB
- **DMG Installer**: ~70 MB
- **ZIP Installer**: ~65 MB

#### Dependencies
- **PySide6**: Qt-based GUI framework
- **PyMuPDF**: PDF processing and text extraction
- **Pillow**: Image processing and manipulation
- **Requests**: HTTP client for API communication
- **NumPy**: Numerical computing (optimized version)

### 🙏 Acknowledgments

#### Open Source Libraries
- **PyMuPDF**: PDF processing capabilities
- **PySide6**: Cross-platform GUI framework
- **Perplexity API**: LLM integration and responses
- **Python Community**: Rich ecosystem of libraries and tools

#### Contributors
- Development team for the initial implementation
- Beta testers for feedback and bug reports
- Open source community for inspiration and tools

### 📞 Support

#### Getting Help
- **Documentation**: Check README.md and PACKAGING.md
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join community discussions on GitHub

#### Troubleshooting
- **Installation Issues**: See PACKAGING.md for detailed instructions
- **API Problems**: Verify Perplexity API key and internet connection
- **Performance**: Check system requirements and available memory

---

**Note**: This is the initial release of LLM PDF Reader. We welcome feedback and suggestions for future improvements. The application is designed to be user-friendly while providing powerful AI-assisted PDF reading capabilities.