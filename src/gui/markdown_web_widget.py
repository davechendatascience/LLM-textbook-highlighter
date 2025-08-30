"""
Enhanced Markdown Web Widget Component
QWebEngineView implementation with MathJax support
"""

from .markdown_widget import BaseMarkdownWidget, MathJaxRenderer, PandocMarkdownProcessor
from PySide6.QtWidgets import QMenu, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent

# Note: This requires PySide6-WebEngine to be installed
# pip install PySide6-WebEngine

# Import at module level to catch import errors early
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEnginePage
    from PySide6.QtGui import QDesktopServices
    from PySide6.QtCore import QUrl
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False

class CustomWebEnginePage(QWebEnginePage):
    """Custom web engine page to handle external links"""
    
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            if url.scheme() in ['http', 'https']:
                # Open external links in default browser
                QDesktopServices.openUrl(url)
                return False  # Don't navigate in the web view
            elif url.scheme() == '' and url.fragment():
                # Allow internal anchor links (like #ref1)
                return True
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class EnhancedMarkdownWebWidget(BaseMarkdownWidget):
    """Enhanced markdown widget using QWebEngineView with MathJax support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not WEBENGINE_AVAILABLE:
            raise ImportError(
                "PySide6-WebEngine is required for EnhancedMarkdownWebWidget. "
                "Install it with: pip install PySide6-Addons"
            )
        
        # Create web view with custom page for external link handling
        self.web_view = QWebEngineView(self)
        self.web_page = CustomWebEnginePage(self)
        self.web_view.setPage(self.web_page)
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.web_view)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Use Pandoc processor for better LaTeX support
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
        """Set the HTML content in QWebEngineView"""
        # HTML citation fixes are already applied in set_markdown_text
        
        # Add JavaScript to fix MathJax loader error
        script = """
        <script>
        // Fix MathJax loader error
        if (typeof MathJax !== 'undefined' && MathJax.Hub) {
            MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
        }
        </script>
        """
        
        # Insert the script into the HTML
        html_with_script = html.replace('</body>', script + '</body>')
        if '</body>' not in html_with_script:
            html_with_script = html + script
        
        # Use the debug function from run_reader.py
        try:
            debug_print_html_content(html_with_script, "EnhancedMarkdownWebWidget HTML Content")
        except NameError:
            # Fallback if debug function not available
            print("🔍 HTML Content Preview:")
            print("=" * 50)
            print(html_with_script[:1000] + "..." if len(html_with_script) > 1000 else html_with_script)
            print("=" * 50)
            
            import re
            link_matches = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', html_with_script)
            print(f"🔍 Found {len(link_matches)} link tags in HTML: {link_matches[:5]}")
        
        # Set the HTML content
        self.web_view.setHtml(html_with_script)
    
    def copy(self):
        """Copy selected text"""
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
