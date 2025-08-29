"""
Vector Store Panel
GUI component for managing vector store operations
"""

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QLineEdit, QComboBox,
                               QProgressBar, QGroupBox, QScrollArea, QFrame,
                               QMessageBox, QFileDialog, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont


class VectorStoreWorker(QThread):
    """Worker thread for vector store operations"""
    
    progress_updated = Signal(str)
    operation_completed = Signal(bool, str)
    
    def __init__(self, operation, llm_service, **kwargs):
        super().__init__()
        self.operation = operation
        self.llm_service = llm_service
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.operation == "process_pdf":
                self.progress_updated.emit("Processing PDF...")
                success = self.llm_service.process_current_pdf()
                if success:
                    self.operation_completed.emit(True, "PDF processed successfully!")
                else:
                    self.operation_completed.emit(False, "Failed to process PDF")
                    
            elif self.operation == "search":
                self.progress_updated.emit("Searching...")
                query = self.kwargs.get('query', '')
                results = self.llm_service.search_relevant_chunks(query)
                if results:
                    result_text = f"Found {len(results)} relevant chunks:\n\n"
                    for i, result in enumerate(results, 1):
                        result_text += f"**Result {i} (Page {result['metadata']['page_number']}):**\n"
                        result_text += f"{result['text'][:200]}...\n\n"
                    self.operation_completed.emit(True, result_text)
                else:
                    self.operation_completed.emit(False, "No relevant chunks found")
                    
            elif self.operation == "get_stats":
                self.progress_updated.emit("Getting statistics...")
                stats = self.llm_service.get_vector_store_stats()
                if stats:
                    stats_text = f"**Vector Store Statistics:**\n\n"
                    stats_text += f"Total Chunks: {stats.get('total_chunks', 0)}\n"
                    stats_text += f"Unique PDFs: {stats.get('unique_pdfs', 0)}\n"
                    stats_text += f"Max Pages: {stats.get('max_pages', 0)}\n\n"
                    
                    if stats.get('pdf_names'):
                        stats_text += "**Indexed PDFs:**\n"
                        for pdf_name in stats['pdf_names']:
                            stats_text += f"- {pdf_name}\n"
                    
                    self.operation_completed.emit(True, stats_text)
                else:
                    self.operation_completed.emit(False, "Failed to get statistics")
                    
        except Exception as e:
            self.operation_completed.emit(False, f"Error: {str(e)}")


class VectorStorePanel(QWidget):
    """Panel for managing vector store operations"""
    
    def __init__(self, llm_service, parent=None):
        super().__init__(parent)
        self.llm_service = llm_service
        self.current_pdf_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the vector store panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Vector Store Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # PDF Processing Section
        self.create_pdf_processing_section(layout)
        
        # Search Section
        self.create_search_section(layout)
        
        # Statistics Section
        self.create_statistics_section(layout)
        
        # Results Display
        self.create_results_section(layout)
        
        # Initialize statistics
        self.update_statistics()
    
    def create_pdf_processing_section(self, parent_layout):
        """Create the PDF processing section"""
        group = QGroupBox("PDF Processing")
        layout = QVBoxLayout(group)
        
        # Current PDF display
        self.current_pdf_label = QLabel("No PDF selected")
        self.current_pdf_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.current_pdf_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_pdf_button = QPushButton("Select PDF")
        self.select_pdf_button.clicked.connect(self.select_pdf)
        button_layout.addWidget(self.select_pdf_button)
        
        self.process_pdf_button = QPushButton("Process PDF")
        self.process_pdf_button.clicked.connect(self.process_pdf)
        self.process_pdf_button.setEnabled(False)
        button_layout.addWidget(self.process_pdf_button)
        
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(group)
    
    def create_search_section(self, parent_layout):
        """Create the search section"""
        group = QGroupBox("Semantic Search")
        layout = QVBoxLayout(group)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter your search query...")
        self.search_input.returnPressed.connect(self.search_chunks)
        layout.addWidget(self.search_input)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_chunks)
        layout.addWidget(self.search_button)
        
        parent_layout.addWidget(group)
    
    def create_statistics_section(self, parent_layout):
        """Create the statistics section"""
        group = QGroupBox("Vector Store Statistics")
        layout = QVBoxLayout(group)
        
        # Stats display
        self.stats_display = QTextEdit()
        self.stats_display.setMaximumHeight(150)
        self.stats_display.setReadOnly(True)
        layout.addWidget(self.stats_display)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.refresh_stats_button = QPushButton("Refresh Stats")
        self.refresh_stats_button.clicked.connect(self.update_statistics)
        button_layout.addWidget(self.refresh_stats_button)
        
        self.clear_store_button = QPushButton("Clear Store")
        self.clear_store_button.clicked.connect(self.clear_vector_store)
        button_layout.addWidget(self.clear_store_button)
        
        layout.addLayout(button_layout)
        
        parent_layout.addWidget(group)
    
    def create_results_section(self, parent_layout):
        """Create the results display section"""
        group = QGroupBox("Results")
        layout = QVBoxLayout(group)
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)
        
        parent_layout.addWidget(group)
    
    def select_pdf(self):
        """Select a PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.current_pdf_path = file_path
            pdf_name = os.path.basename(file_path)
            self.current_pdf_label.setText(f"Selected: {pdf_name}")
            self.process_pdf_button.setEnabled(True)
            
            # Set current PDF in LLM service
            self.llm_service.set_current_pdf(file_path, pdf_name)
    
    def process_pdf(self):
        """Process the selected PDF"""
        if not self.current_pdf_path:
            QMessageBox.warning(self, "Warning", "Please select a PDF first.")
            return
        
        # Start worker thread
        self.worker = VectorStoreWorker("process_pdf", self.llm_service)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.operation_completed.connect(self.on_operation_completed)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.process_pdf_button.setEnabled(False)
        
        self.worker.start()
    
    def search_chunks(self):
        """Search for relevant chunks"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a search query.")
            return
        
        if not self.llm_service.current_pdf_name:
            QMessageBox.warning(self, "Warning", "Please select a PDF first.")
            return
        
        # Start worker thread
        self.worker = VectorStoreWorker("search", self.llm_service, query=query)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.operation_completed.connect(self.on_operation_completed)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.search_button.setEnabled(False)
        
        self.worker.start()
    
    def update_statistics(self):
        """Update the statistics display"""
        # Start worker thread
        self.worker = VectorStoreWorker("get_stats", self.llm_service)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.operation_completed.connect(self.on_stats_completed)
        
        self.worker.start()
    
    def clear_vector_store(self):
        """Clear the vector store"""
        reply = QMessageBox.question(
            self, "Confirm Clear", 
            "Are you sure you want to clear all data from the vector store?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.llm_service.clear_vector_store()
            if success:
                QMessageBox.information(self, "Success", "Vector store cleared successfully!")
                self.update_statistics()
            else:
                QMessageBox.critical(self, "Error", "Failed to clear vector store.")
    
    def update_progress(self, message):
        """Update progress display"""
        self.results_display.append(f"🔄 {message}")
    
    def on_operation_completed(self, success, message):
        """Handle operation completion"""
        self.progress_bar.setVisible(False)
        self.process_pdf_button.setEnabled(True)
        self.search_button.setEnabled(True)
        
        if success:
            self.results_display.append(f"✅ {message}")
        else:
            self.results_display.append(f"❌ {message}")
        
        # Update statistics after operations
        self.update_statistics()
    
    def on_stats_completed(self, success, message):
        """Handle statistics completion"""
        if success:
            self.stats_display.setMarkdown(message)
        else:
            self.stats_display.setPlainText(f"Error: {message}")
