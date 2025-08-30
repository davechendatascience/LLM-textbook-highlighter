"""
Enhanced Markdown Widget Component
Handles markdown rendering with LaTeX math support using mdx_math extension
"""

import re
import os
import subprocess
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QTextBrowser, QMenu, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QTextCursor, QTextCharFormat, QColor, QFont
import webbrowser
import markdown
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree

# Try to import pypandoc for LaTeX processing
try:
    import pypandoc
    HAS_PYPANDOC = True
except ImportError:
    HAS_PYPANDOC = False

# Try to import sympy for LaTeX parsing
try:
    from sympy.parsing.latex import parse_latex
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

class LatexInlineProcessor(InlineProcessor):
    """Custom inline processor to detect and wrap standalone LaTeX commands"""
    
    def __init__(self, pattern, md=None):
        super().__init__(pattern, md)
        # Common LaTeX commands that should be wrapped
        self.latex_commands = [
            'sqrt', 'frac', 'sum', 'int', 'prod', 'lim',
            'sin', 'cos', 'tan', 'log', 'ln', 'exp',
            'partial', 'nabla', 'infty', 'alpha', 'beta',
            'gamma', 'delta', 'epsilon', 'theta', 'lambda',
            'mu', 'pi', 'sigma', 'phi', 'psi', 'omega',
            'begin', 'end', 'left', 'right', 'big',
            'Big', 'bigg', 'Bigg', 'text', 'mathrm',
            'mathbf', 'mathit', 'mathcal', 'mathbb',
            'vec', 'hat', 'bar', 'tilde', 'dot', 'ddot'
        ]
    
    def handleMatch(self, m, data):
        """Handle matched LaTeX command"""
        command = m.group(1)
        
        # Check if this is a LaTeX command we want to wrap
        if command in self.latex_commands:
            # Get the full match including braces if present
            full_match = m.group(0)
            
            # Create a math element
            el = etree.Element('script')
            el.set('type', 'math/tex')
            el.text = full_match
            return el, m.start(0), m.end(0)
        
        return None, None, None

class LatexExtension(Extension):
    """Markdown extension to handle standalone LaTeX commands"""
    
    def extendMarkdown(self, md):
        # Pattern to match LaTeX commands: \command{...} or \command
        pattern = r'\\(' + '|'.join([
            'sqrt', 'frac', 'sum', 'int', 'prod', 'lim',
            'sin', 'cos', 'tan', 'log', 'ln', 'exp',
            'partial', 'nabla', 'infty', 'alpha', 'beta',
            'gamma', 'delta', 'epsilon', 'theta', 'lambda',
            'mu', 'pi', 'sigma', 'phi', 'psi', 'omega',
            'begin', 'end', 'left', 'right', 'big',
            'Big', 'bigg', 'Bigg', 'text', 'mathrm',
            'mathbf', 'mathit', 'mathcal', 'mathbb',
            'vec', 'hat', 'bar', 'tilde', 'dot', 'ddot'
        ]) + r')(?:\{[^}]*\})?'
        
        # Create the processor and add it to the inline patterns
        latex_processor = LatexInlineProcessor(pattern, md)
        md.inlinePatterns.register(latex_processor, 'latex_commands', 185)

class MathRenderer(ABC):
    """Abstract base class for math rendering strategies"""
    
    @abstractmethod
    def render_math(self, html: str) -> str:
        """Render math expressions in HTML"""
        pass

class StyledMathRenderer(MathRenderer):
    """Renders math expressions with CSS styling"""
    
    def render_math(self, html: str) -> str:
        """Post-process HTML to style math expressions"""
        # Handle Pandoc's math output format first
        # Inline math: <span class="math inline">\(...\)</span>
        html = re.sub(r'<span class="math inline">(.*?)</span>', 
                     r'<span style="font-family: Times New Roman, serif; font-style: italic; color: #2E86AB;">\1</span>', 
                     html, flags=re.DOTALL)
        
        # Display math: <span class="math display">\[...\]</span>
        html = re.sub(r'<span class="math display">(.*?)</span>', 
                     r'<div style="text-align: center; font-family: Times New Roman, serif; font-style: italic; color: #2E86AB; margin: 1em 0; font-size: 1.1em;">\1</div>', 
                     html, flags=re.DOTALL)
        
        # Handle mdx_math script tags - convert them to styled spans/divs
        # Inline math: <script type="math/tex">...</script>
        html = re.sub(r'<script type="math/tex">(.*?)</script>', 
                     r'<span style="font-family: Times New Roman, serif; font-style: italic; color: #2E86AB;">\1</span>', 
                     html, flags=re.DOTALL)
        
        # Display math: <script type="math/tex; mode=display">...</script>
        html = re.sub(r'<script type="math/tex; mode=display">(.*?)</script>', 
                     r'<div style="text-align: center; font-family: Times New Roman, serif; font-style: italic; color: #2E86AB; margin: 1em 0; font-size: 1.1em;">\1</div>', 
                     html, flags=re.DOTALL)
        
        # Also handle any remaining raw math delimiters (fallback)
        # Handle inline math with \(...\) - style as italic math
        html = re.sub(r'\\\((.*?)\\\)', r'<span style="font-family: Times New Roman, serif; font-style: italic; color: #2E86AB;">\1</span>', html)
        
        # Handle inline math with $...$ - style as italic math
        html = re.sub(r'\$(.*?)\$', r'<span style="font-family: Times New Roman, serif; font-style: italic; color: #2E86AB;">\1</span>', html)
        
        # Handle display math with \[...\] - style as centered math
        html = re.sub(r'\\\[(.*?)\\\]', r'<div style="text-align: center; font-family: Times New Roman, serif; font-style: italic; color: #2E86AB; margin: 1em 0; font-size: 1.1em;">\1</div>', html)
        
        # Handle display math with $$...$$ - style as centered math
        html = re.sub(r'\$\$(.*?)\$\$', r'<div style="text-align: center; font-family: Times New Roman, serif; font-style: italic; color: #2E86AB; margin: 1em 0; font-size: 1.1em;">\1</div>', html)
        
        return html

class MathJaxRenderer(MathRenderer):
    """Renders math expressions using MathJax (for QWebEngineView)"""
    
    def render_math(self, html: str) -> str:
        """Add MathJax to HTML for math rendering"""
        # Check if HTML already has a complete structure (from Pandoc)
        if html.strip().startswith('<!DOCTYPE html>'):
            # HTML already has complete structure, just add MathJax script to head
            mathjax_script = """
            <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML"></script>
            <script>
                MathJax.Hub.Config({
                    tex2jax: {
                        inlineMath: [['$', '$'], ['\\(', '\\)']],
                        displayMath: [['$$', '$$'], ['\\[', '\\]']],
                        processEscapes: true
                    }
                });
            </script>
            """
            # Insert MathJax script into the head section
            html_with_mathjax = html.replace('</head>', mathjax_script + '</head>')
            if '</head>' not in html_with_mathjax:
                # If no head tag found, add it after the opening html tag
                html_with_mathjax = html.replace('<html', '<html><head>' + mathjax_script + '</head>')
            return html_with_mathjax
        else:
            # Simple HTML fragment, wrap it with complete HTML structure
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML"></script>
                <script>
                    MathJax.Hub.Config({{
                        tex2jax: {{
                            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                            processEscapes: true
                        }}
                    }});
                </script>
            </head>
            <body>
            {html}
            </body>
            </html>
            """

class PandocMarkdownProcessor:
    """Markdown processor using Pandoc for robust LaTeX math support"""
    
    # Class-level cache for Pandoc availability
    _pandoc_available = None
    _pandoc_checked = False
    
    def __init__(self):
        self.use_pandoc = self._check_pandoc_availability()
    
    @classmethod
    def _check_pandoc_availability(cls):
        """Check if Pandoc is available (cached at class level)"""
        if cls._pandoc_checked:
            return cls._pandoc_available
        
        cls._pandoc_checked = True
        
        try:
            import pypandoc
            # Test if pypandoc can actually access Pandoc
            version = pypandoc.get_pandoc_version()
            cls._pandoc_available = True
            print(f"✅ Pandoc {version} detected - enhanced LaTeX math support available!")
            return True
        except Exception as e:
            cls._pandoc_available = False
            print(f"⚠️  Pandoc not available: {e}")
            return False
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text to handle citations and LaTeX math"""
        # Handle LLM-style citations: [[1]](url) -> [1](#ref1)
        # This converts external links to internal anchor links
        text = re.sub(r'\[\[(\d+)\]\]\(([^)]+)\)', r'[\1](#ref\1)', text)
        
        # Handle regular citations: [1] -> [1](#ref1)
        # But only if they're not already in a link format
        text = re.sub(r'(?<!\]\()\[(\d+)\](?!\()', r'[\1](#ref\1)', text)
        
        # Handle reference sections: [1] Title -> <div id="ref1">[1] Title</div>
        # But only at the beginning of lines (not inline)
        text = re.sub(r'^\[(\d+)\]\s+(.+)$', r'<div id="ref\1">[\1] \2</div>', text, flags=re.MULTILINE)
        
        return text
    
    def convert_to_html(self, text: str) -> str:
        """Convert markdown text to HTML using Pandoc or fallback"""
        if not self.use_pandoc:
            # Fallback to standard markdown processor
            fallback_processor = MarkdownProcessor()
            return fallback_processor.convert_to_html(text)
        
        try:
            # Preprocess text for citations
            text = self.preprocess_text(text)
            
            # Use pypandoc to convert markdown to HTML with math support
            # Note: We don't use --mathjax to avoid the \f prefix bug
            html = pypandoc.convert_text(
                text,
                'html',
                format='markdown',
                extra_args=[
                    '--standalone',
                    '--from=markdown+tex_math_dollars+tex_math_single_backslash+autolink_bare_uris',
                    '--to=html5'
                ]
            )
            
            # Apply post-processing fixes
            html = self.apply_post_processing_fixes(html)
            return html
                
        except Exception as e:
            print(f"Pandoc conversion failed: {e}")
            # Fallback to standard markdown processor
            fallback_processor = MarkdownProcessor()
            return fallback_processor.convert_to_html(text)
    
    def apply_post_processing_fixes(self, html: str) -> str:
        """Apply post-processing fixes for math and citations"""
        # Fix citation links to ensure they render as [1] format
        # Pandoc converts [1](#ref1) to <a href="#ref1">1</a>
        # We want to change it to <a href="#ref1">[1]</a>
        
        # First, handle any links that are missing brackets
        html = re.sub(
            r'<a href="#ref(\d+)">(\d+)</a>',
            r'<a href="#ref\1">[\2]</a>',
            html
        )
        
        # Also handle cases where Pandoc might have already processed the link
        # but the brackets are missing or malformed
        html = re.sub(
            r'<a href="#ref(\d+)">\[(\d+)\]</a>',
            r'<a href="#ref\1">[\2]</a>',
            html
        )
        
        # Handle any remaining citation patterns that weren't converted to links
        html = re.sub(
            r'\[(\d+)\]\(#ref\1\)',
            r'<a href="#ref\1">[\1]</a>',
            html
        )
        
        # Add CSS styling for citations
        citation_css = """
        <style>
        .citation-link {
            color: #0066cc;
            text-decoration: none;
            font-weight: bold;
            background-color: #f0f8ff;
            padding: 2px 6px;
            border-radius: 3px;
        }
        .citation-link:hover {
            text-decoration: underline;
            background-color: #e6f3ff;
        }
        .reference {
            background-color: #f0f8ff;
            border-left: 4px solid #0066cc;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .reference-number {
            color: #0066cc;
            font-weight: bold;
            font-size: 1.1em;
        }
        </style>
        """
        
        # Insert CSS into head section
        if '</head>' in html:
            html = html.replace('</head>', citation_css + '</head>')
        else:
            # If no head tag, add it after opening html tag
            html = html.replace('<html>', '<html><head>' + citation_css + '</head>')
        
        return html

class MarkdownProcessor:
    """Handles markdown processing and math preprocessing"""
    
    def __init__(self):
        # Create a Markdown instance with the math extension and our custom extension
        self.md = markdown.Markdown(
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'mdx_math',  # Name of the extension
                LatexExtension()  # Our custom extension for standalone LaTeX commands
            ],
            extension_configs={
                'mdx_math': {
                    'enable_dollar_delimiter': True,  # Enable dollar-sign delimiters
                    'add_preview': False  # Don't add preview text
                }
            }
        )
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text to identify and properly format math expressions"""
        # No preprocessing needed - our custom extension handles LaTeX commands
        return text
    
    def convert_to_html(self, text: str) -> str:
        """Convert markdown text to HTML"""
        return self.md.convert(text)

class BaseMarkdownWidget(QWidget):
    """Base class for markdown widgets with common functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.markdown_processor = MarkdownProcessor()
        self.math_renderer = StyledMathRenderer()  # Default renderer
        self.math_cache = {}  # Cache for rendered math images
        
    def set_math_renderer(self, renderer: MathRenderer):
        """Set the math rendering strategy"""
        self.math_renderer = renderer
    
    def set_markdown_text(self, text: str, font_size: int = 12):
        """Set markdown text with enhanced math support"""
        if not text:
            return
        
        # Preprocess text
        text = self.markdown_processor.preprocess_text(text)
        
        # Convert markdown to HTML
        html = self.markdown_processor.convert_to_html(text)
        
        # Render math expressions
        html = self.math_renderer.render_math(html)
        
        # Set the content (to be implemented by subclasses)
        self._set_content(html, font_size)
    
    @abstractmethod
    def _set_content(self, html: str, font_size: int):
        """Set the HTML content (to be implemented by subclasses)"""
        pass
    
    @abstractmethod
    def copy(self):
        """Copy selected text (to be implemented by subclasses)"""
        pass
    
    def copy_link(self, link: str):
        """Copy link to clipboard"""
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(link)
        
    def open_link(self, link: str):
        """Open link in default browser"""
        webbrowser.open(link)

class EnhancedMarkdownTextWidget(BaseMarkdownWidget):
    """Enhanced markdown widget using QTextBrowser"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setOpenLinks(True)
        
        # Set up layout
        from PySide6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_browser)
        layout.setContentsMargins(0, 0, 0, 0)
        
    def _set_content(self, html: str, font_size: int):
        """Set the HTML content in QTextBrowser"""
        self.text_browser.setHtml(html)
        
        # Set font size
        font = self.text_browser.font()
        font.setPointSize(font_size)
        self.text_browser.setFont(font)
    
    def copy(self):
        """Copy selected text"""
        self.text_browser.copy()
    
    def contextMenuEvent(self, event: QMouseEvent):
        """Custom context menu with copy and open link options"""
        menu = QMenu(self)
        
        # Get the cursor at the click position
        cursor = self.text_browser.cursorForPosition(event.pos())
        
        # Add copy action
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.copy)
        
        # Add open link action if there's a link under cursor
        cursor.select(QTextCursor.WordUnderCursor)
        link_text = cursor.selectedText()
        
        if link_text.startswith('http'):
            open_link_action = menu.addAction(f"Open {link_text}")
            open_link_action.triggered.connect(lambda: webbrowser.open(link_text))
        
        menu.exec(event.globalPos())

class PandocMarkdownTextWidget(BaseMarkdownWidget):
    """Markdown text widget using Pandoc for robust LaTeX math support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setOpenLinks(True)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_browser)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Use Pandoc processor instead of the default one
        self.markdown_processor = PandocMarkdownProcessor()
        
        # Use MathJax renderer for proper math rendering
        self.set_math_renderer(MathJaxRenderer())
    
    def set_markdown_text(self, text: str, font_size: int = 12):
        """Set markdown text and render it using Pandoc"""
        if not text:
            return
        
        try:
            # Convert markdown to HTML using Pandoc
            html = self.markdown_processor.convert_to_html(text)
            
            # Apply citation fixes to HTML
            from src.utils.citation_processor import CitationProcessor
            citation_processor = CitationProcessor()
            html = citation_processor.fix_html_citations(html)
            
            self._set_content(html, font_size)
        except Exception as e:
            print(f"Error rendering markdown with Pandoc: {e}")
            # Fallback to plain text
            self._set_content(f"<p>{text}</p>", font_size)
    
    def _set_content(self, html: str, font_size: int):
        """Set the HTML content with specified font size"""
        self.text_browser.setHtml(html)
        
        # Set font size
        font = self.text_browser.font()
        font.setPointSize(font_size)
        self.text_browser.setFont(font)
    
    def copy(self):
        """Copy selected text to clipboard"""
        self.text_browser.copy()
    
    def contextMenuEvent(self, event: QMouseEvent):
        """Handle right-click context menu"""
        menu = QMenu(self)
        
        # Add copy action
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.copy)
        
        # Add open link action if there's a link under cursor
        cursor = self.text_browser.cursorForPosition(event.pos())
        cursor.select(QTextCursor.WordUnderCursor)
        link_text = cursor.selectedText()
        
        if link_text.startswith('http'):
            open_link_action = menu.addAction(f"Open {link_text}")
            open_link_action.triggered.connect(lambda: webbrowser.open(link_text))
        
        menu.exec(event.globalPos())

class EnhancedMarkdownWebWidget(BaseMarkdownWidget):
    """Enhanced markdown widget using QWebEngineView with MathJax support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtWidgets import QVBoxLayout
        
        self.web_view = QWebEngineView(self)
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.web_view)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Use MathJax renderer by default
        self.set_math_renderer(MathJaxRenderer())
        
    def _set_content(self, html: str, font_size: int):
        """Set the HTML content in QWebEngineView"""
        # Apply citation fixes to HTML
        from src.utils.citation_processor import CitationProcessor
        citation_processor = CitationProcessor()
        html = citation_processor.fix_html_citations(html)
        
        # QWebEngineView can handle full HTML with JavaScript
        self.web_view.setHtml(html)
    
    def copy(self):
        """Copy selected text"""
        # Use the standard copy action
        self.web_view.page().triggerAction(self.web_view.page().Copy)
    
    def contextMenuEvent(self, event: QMouseEvent):
        """Custom context menu for web view"""
        # QWebEngineView has its own context menu, but we can customize it
        menu = QMenu(self)
        
        # Add copy action
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.copy)
        
        # Show the menu
        menu.exec(event.globalPos())