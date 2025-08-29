"""
Research Panel Component
Provides UI for ArXiv paper search and research features
"""

import asyncio
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QLineEdit, QTextEdit, QComboBox,
                               QListWidget, QListWidgetItem, QProgressBar,
                               QMessageBox, QSplitter)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont

from src.services.arxiv_service import ArxivService, ArxivPaper


class SearchWorker(QThread):
    """Worker thread for paper search"""
    results_ready = Signal(list)
    error_occurred = Signal(str)
    
    def __init__(self, arxiv_service: ArxivService, query: str, max_results: int, categories: list):
        super().__init__()
        self.arxiv_service = arxiv_service
        self.query = query
        self.max_results = max_results
        self.categories = categories
        
    def run(self):
        """Run the search in a separate thread"""
        try:
            # Use the synchronous search method directly
            papers = self.arxiv_service.search_papers(
                self.query, 
                self.max_results, 
                self.categories
            )
            self.results_ready.emit(papers)
                
        except Exception as e:
            self.error_occurred.emit(str(e))


class DownloadWorker(QThread):
    """Worker thread for paper download"""
    download_complete = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, arxiv_service: ArxivService, paper_id: str, output_dir: str):
        super().__init__()
        self.arxiv_service = arxiv_service
        self.paper_id = paper_id
        self.output_dir = output_dir
        
    def run(self):
        """Run the download in a separate thread"""
        try:
            # Note: download_paper method doesn't exist in our direct API service
            # For now, we'll just emit an error
            self.error_occurred.emit("Download functionality not implemented in direct API")
                
        except Exception as e:
            self.error_occurred.emit(str(e))


class ResearchPanel(QWidget):
    """Research panel for ArXiv paper search and management"""
    
    results_ready = Signal(list)
    
    def __init__(self, language_support=None):
        super().__init__()
        self.language_support = language_support
        self.arxiv_service = ArxivService()
        self.current_papers = []
        self.search_worker = None
        self.download_worker = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the research panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(self.language_support.get_text("research_assistant") if self.language_support else "Research Assistant")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Search controls
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            self.language_support.get_text("search_for_papers") if self.language_support else "Search for papers..."
        )
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton(self.language_support.get_text("search") if self.language_support else "Search")
        self.search_button.clicked.connect(self.search_papers)
        search_layout.addWidget(self.search_button)
        
        layout.addLayout(search_layout)
        
        # Search options
        options_layout = QHBoxLayout()
        
        options_layout.addWidget(QLabel(self.language_support.get_text("category") if self.language_support else "Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "All Categories",
            "cs.AI - Artificial Intelligence",
            "cs.LG - Machine Learning", 
            "cs.CL - Computation and Language",
            "cs.CV - Computer Vision",
            "cs.RO - Robotics",
            "cs.MA - Multiagent Systems"
        ])
        options_layout.addWidget(self.category_combo)
        
        options_layout.addWidget(QLabel(self.language_support.get_text("max_results") if self.language_support else "Max Results:"))
        self.max_results_combo = QComboBox()
        self.max_results_combo.addItems(["5", "10", "20", "50"])
        self.max_results_combo.setCurrentText("10")
        options_layout.addWidget(self.max_results_combo)
        
        layout.addLayout(options_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results area
        results_splitter = QSplitter(Qt.Horizontal)
        
        # Paper list
        self.paper_list = QListWidget()
        self.paper_list.itemClicked.connect(self.on_paper_selected)
        results_splitter.addWidget(self.paper_list)
        
        # Paper details
        self.paper_details = QTextEdit()
        self.paper_details.setReadOnly(True)
        results_splitter.addWidget(self.paper_details)
        
        results_splitter.setSizes([300, 400])
        layout.addWidget(results_splitter)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.download_button = QPushButton(self.language_support.get_text("download_paper") if self.language_support else "Download Paper")
        self.download_button.clicked.connect(self.download_selected_paper)
        self.download_button.setEnabled(False)
        actions_layout.addWidget(self.download_button)
        
        self.find_related_button = QPushButton(self.language_support.get_text("find_related") if self.language_support else "Find Related")
        self.find_related_button.clicked.connect(self.find_related_papers)
        self.find_related_button.setEnabled(False)
        actions_layout.addWidget(self.find_related_button)
        
        layout.addLayout(actions_layout)
        
    def search_papers(self):
        """Search for papers using the ArXiv service"""
        query = self.search_input.text().strip()
        if not query:
            return
            
        # Get search parameters
        max_results = int(self.max_results_combo.currentText())
        category = self.category_combo.currentText()
        
        # Parse category
        categories = []
        if category != "All Categories":
            category_code = category.split(" - ")[0]
            categories = [category_code]
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.search_button.setEnabled(False)
        
        # Start search worker
        self.search_worker = SearchWorker(self.arxiv_service, query, max_results, categories)
        self.search_worker.results_ready.connect(self.on_search_results)
        self.search_worker.error_occurred.connect(self.on_search_error)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.start()
        
    def on_search_results(self, papers: list):
        """Handle search results"""
        self.current_papers = papers
        self.paper_list.clear()
        
        for paper in papers:
            item = QListWidgetItem(paper.title)
            item.setData(Qt.UserRole, paper)
            self.paper_list.addItem(item)
            
    def on_search_error(self, error: str):
        """Handle search error"""
        QMessageBox.warning(self, "Search Error", f"Failed to search papers: {error}")
        
    def on_search_finished(self):
        """Handle search completion"""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)
        
    def on_paper_selected(self, item: QListWidgetItem):
        """Handle paper selection"""
        paper = item.data(Qt.UserRole)
        if paper:
            self.display_paper_details(paper)
            self.download_button.setEnabled(True)
            self.find_related_button.setEnabled(True)
            
    def display_paper_details(self, paper: ArxivPaper):
        """Display paper details"""
        details = f"""
<b>{paper.title}</b><br><br>
<b>Authors:</b> {', '.join(paper.authors)}<br>
<b>Published:</b> {paper.published_date}<br>
<b>Categories:</b> {', '.join(paper.categories)}<br>
<b>ArXiv ID:</b> {paper.id}<br><br>
<b>Abstract:</b><br>
{paper.abstract}<br><br>
<b>Links:</b><br>
<a href="{paper.arxiv_url}">ArXiv Page</a><br>
<a href="{paper.pdf_url}">PDF Download</a>
"""
        self.paper_details.setHtml(details)
        
    def download_selected_paper(self):
        """Download the selected paper"""
        current_item = self.paper_list.currentItem()
        if not current_item:
            return
            
        paper = current_item.data(Qt.UserRole)
        if not paper:
            return
            
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.download_button.setEnabled(False)
        
        # Start download worker
        self.download_worker = DownloadWorker(self.arxiv_service, paper.id, "downloads")
        self.download_worker.download_complete.connect(self.on_download_complete)
        self.download_worker.error_occurred.connect(self.on_download_error)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.start()
        
    def on_download_complete(self, file_path: str):
        """Handle download completion"""
        QMessageBox.information(self, "Download Complete", f"Paper downloaded to: {file_path}")
        
    def on_download_error(self, error: str):
        """Handle download error"""
        QMessageBox.warning(self, "Download Error", f"Failed to download paper: {error}")
        
    def on_download_finished(self):
        """Handle download completion"""
        self.progress_bar.setVisible(False)
        self.download_button.setEnabled(True)
        
    def find_related_papers(self):
        """Find papers related to the selected paper"""
        current_item = self.paper_list.currentItem()
        if not current_item:
            return
            
        paper = current_item.data(Qt.UserRole)
        if not paper:
            return
            
        # Use the paper title as search query
        self.search_input.setText(paper.title)
        self.search_papers()
        
    def search_papers(self, query: str = None):
        """Search for papers (can be called externally)"""
        if query:
            self.search_input.setText(query)
        
        # Get search parameters
        search_query = self.search_input.text().strip()
        if not search_query:
            QMessageBox.warning(self, "Search Error", "Please enter a search query")
            return
            
        max_results = self.max_results_combo.currentText()
        try:
            max_results = int(max_results)
        except ValueError:
            max_results = 10
            
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.search_button.setEnabled(False)
        
        # Start search worker
        self.search_worker = SearchWorker(self.arxiv_service, search_query, max_results, [])
        self.search_worker.results_ready.connect(self.on_search_results)
        self.search_worker.error_occurred.connect(self.on_search_error)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.start()
