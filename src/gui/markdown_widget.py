"""
Markdown Widget Component
Handles markdown rendering and LaTeX support
"""

import re
from PySide6.QtWidgets import QTextBrowser, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QTextCursor, QTextCharFormat, QColor, QFont
import webbrowser
import markdown


class MarkdownTextWidget(QTextBrowser):
    """Simplified markdown widget for displaying text with basic formatting and links"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self.setOpenLinks(True)
        
    def set_markdown_text(self, text: str, font_size: int = 12):
        """Set markdown text and convert to HTML"""
        if not text:
            return
            
        # Convert markdown to HTML using the markdown library
        html = markdown.markdown(text)
        
        # Set the HTML content
        self.setHtml(html)
        
        # Set font size
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Handle link clicks"""
        if event.button() == Qt.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            char_format = cursor.charFormat()
            
            if char_format.isAnchor():
                link_url = char_format.anchorHref()
                if link_url:
                    print(f"🔗 Opening link: {link_url}")
                    webbrowser.open(link_url)
                    event.accept()
                    return
                    
        super().mousePressEvent(event)
        
    def contextMenuEvent(self, event):
        """Custom context menu for links"""
        cursor = self.cursorForPosition(event.pos())
        char_format = cursor.charFormat()
        
        if char_format.isAnchor():
            link_url = char_format.anchorHref()
            if link_url:
                menu = QMenu(self)
                
                open_action = menu.addAction("Open Link")
                copy_action = menu.addAction("Copy URL")
                
                action = menu.exec(event.globalPos())
                
                if action == open_action:
                    webbrowser.open(link_url)
                elif action == copy_action:
                    from PySide6.QtGui import QGuiApplication
                    QGuiApplication.clipboard().setText(link_url)
        else:
            super().contextMenuEvent(event)
