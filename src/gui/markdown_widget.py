"""
Enhanced Markdown Widget Component
Handles markdown rendering with LaTeX math support using mdx_math extension
"""

import re
import os
from abc import ABC, abstractmethod
from PySide6.QtWidgets import QTextBrowser, QMenu, QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QTextCursor, QTextCharFormat, QColor, QFont
import webbrowser
import markdown  # Import the main markdown library

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
        # Handle mdx_math script tags - convert them to styled spans/divs
        # Inline math: <script type="math/tex">...</script>
        html = re.sub(r'<script type="math/tex">(.*?)</script>', 
                     r'<span style="font-family: \'Times New Roman\', serif; font-style: italic; color: #2E86AB;">\1</span>', 
                     html, flags=re.DOTALL)
        
        # Display math: <script type="math/tex; mode=display">...</script>
        html = re.sub(r'<script type="math/tex; mode=display">(.*?)</script>', 
                     r'<div style="text-align: center; font-family: \'Times New Roman\', serif; font-style: italic; color: #2E86AB; margin: 1em 0; font-size: 1.1em;">\1</div>', 
                     html, flags=re.DOTALL)
        
        # Also handle any remaining raw math delimiters (fallback)
        # Handle inline math with \(...\) - style as italic math
        html = re.sub(r'\\\((.*?)\\\)', r'<span style="font-family: \'Times New Roman\', serif; font-style: italic; color: #2E86AB;">\1</span>', html)
        
        # Handle inline math with $...$ - style as italic math
        html = re.sub(r'\$(.*?)\$', r'<span style="font-family: \'Times New Roman\', serif; font-style: italic; color: #2E86AB;">\1</span>', html)
        
        # Handle display math with \[...\] - style as centered math
        html = re.sub(r'\\\[(.*?)\\\]', r'<div style="text-align: center; font-family: \'Times New Roman\', serif; font-style: italic; color: #2E86AB; margin: 1em 0; font-size: 1.1em;">\1</div>', html)
        
        # Handle display math with $$...$$ - style as centered math
        html = re.sub(r'\$\$(.*?)\$\$', r'<div style="text-align: center; font-family: \'Times New Roman\', serif; font-style: italic; color: #2E86AB; margin: 1em 0; font-size: 1.1em;">\1</div>', html)
        
        return html

class MathJaxRenderer(MathRenderer):
    """Renders math expressions using MathJax (for QWebEngineView)"""
    
    def render_math(self, html: str) -> str:
        """Wrap HTML with MathJax for math rendering"""
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

class MarkdownProcessor:
    """Handles markdown processing and math preprocessing"""
    
    def __init__(self):
        # Create a Markdown instance with the math extension
        self.md = markdown.Markdown(
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'mdx_math'  # Name of the extension
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
        # Simple preprocessing: wrap obvious LaTeX commands in $...$
        # Only handle standalone LaTeX commands that aren't already in math mode
        text = re.sub(r'(?<!\$)\\([a-zA-Z]+)\{([^}]+)\}(?!\$)', r'$\1{\2}$', text)
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
        
        # Check if we're over a link
        cursor.select(QTextCursor.WordUnderCursor)
        text = cursor.selectedText()
        
        # Add copy action
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.copy)
        
        # Add copy link action if we're over a link
        if text.startswith("http"):
            copy_link_action = menu.addAction("Copy Link")
            copy_link_action.triggered.connect(lambda: self.copy_link(text))
            
            open_link_action = menu.addAction("Open Link")
            open_link_action.triggered.connect(lambda: self.open_link(text))
        
        # Show the menu
        menu.exec(event.globalPos())

# Future QWebEngineView implementation (commented out for now)
# class EnhancedMarkdownWebWidget(BaseMarkdownWidget):
#     """Enhanced markdown widget using QWebEngineView with MathJax support"""
#     
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         from PySide6.QtWebEngineWidgets import QWebEngineView
#         self.web_view = QWebEngineView(self)
#         
#         # Set up layout
#         from PySide6.QtWidgets import QVBoxLayout
#         layout = QVBoxLayout(self)
#         layout.addWidget(self.web_view)
#         layout.setContentsMargins(0, 0, 0, 0)
#         
#         # Use MathJax renderer by default
#         self.set_math_renderer(MathJaxRenderer())
#         
#     def _set_content(self, html: str, font_size: int):
#         """Set the HTML content in QWebEngineView"""
#         # QWebEngineView can handle full HTML with JavaScript
#         self.web_view.setHtml(html)
#     
#     def copy(self):
#         """Copy selected text"""
#         self.web_view.page().triggerAction(QWebEnginePage.Copy)
#     
#     def contextMenuEvent(self, event: QMouseEvent):
#         """Custom context menu for web view"""
#         # Implementation would be different for QWebEngineView
#         pass
