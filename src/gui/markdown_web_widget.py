"""
Enhanced Markdown Web Widget Component
QWebEngineView implementation with MathJax support
"""

from .markdown_widget import BaseMarkdownWidget, MathJaxRenderer
from PySide6.QtWidgets import QMenu, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent

# Note: This requires PySide6-WebEngine to be installed
# pip install PySide6-WebEngine

class EnhancedMarkdownWebWidget(BaseMarkdownWidget):
    """Enhanced markdown widget using QWebEngineView with MathJax support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
            self.QWebEngineView = QWebEngineView
            self.QWebEnginePage = QWebEnginePage
        except ImportError:
            raise ImportError(
                "PySide6-WebEngine is required for EnhancedMarkdownWebWidget. "
                "Install it with: pip install PySide6-WebEngine"
            )
        
        self.web_view = self.QWebEngineView(self)
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.web_view)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Use MathJax renderer by default
        self.set_math_renderer(MathJaxRenderer())
        
    def _set_content(self, html: str, font_size: int):
        """Set the HTML content in QWebEngineView"""
        # QWebEngineView can handle full HTML with JavaScript
        self.web_view.setHtml(html)
    
    def copy(self):
        """Copy selected text"""
        self.web_view.page().triggerAction(self.QWebEnginePage.Copy)
    
    def contextMenuEvent(self, event: QMouseEvent):
        """Custom context menu for web view"""
        # QWebEngineView has its own context menu, but we can customize it
        menu = QMenu(self)
        
        # Add copy action
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.copy)
        
        # Show the menu
        menu.exec(event.globalPos())

# Migration guide:
# 
# To migrate from EnhancedMarkdownTextWidget to EnhancedMarkdownWebWidget:
# 
# 1. Install PySide6-WebEngine:
#    pip install PySide6-WebEngine
# 
# 2. Replace the import:
#    from src.gui.markdown_widget import EnhancedMarkdownTextWidget
#    # becomes:
#    from src.gui.markdown_web_widget import EnhancedMarkdownWebWidget
# 
# 3. The API remains the same:
#    widget = EnhancedMarkdownWebWidget()
#    widget.set_markdown_text("Your markdown with math: $x^2 + y^2 = z^2$")
# 
# 4. Benefits:
#    - Full MathJax support for perfect LaTeX rendering
#    - JavaScript execution
#    - Better HTML/CSS support
# 
# 5. Considerations:
#    - Larger memory footprint
#    - Additional dependency
#    - Different context menu behavior
