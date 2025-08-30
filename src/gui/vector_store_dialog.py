#!/usr/bin/env python3
"""
Vector Store Management Dialog
Provides a dedicated interface for managing the vector store
"""

import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QListWidget, QMessageBox,
                               QGroupBox, QProgressBar, QSplitter, QWidget)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont


class VectorStoreDialog(QDialog):
    """Dialog for managing vector store"""
    
    def __init__(self, parent=None, llm_service=None):
        super().__init__(parent)
        self.llm_service = llm_service
        
        # Get language support from parent if available
        if parent and hasattr(parent, 'language_support'):
            self.language_support = parent.language_support
        else:
            from src.utils.language_support import LanguageSupport
            self.language_support = LanguageSupport()
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(self.language_support.get_text("vector_store_management"))
        self.setGeometry(100, 100, 800, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create splitter for better layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - PDF list
        left_panel = self.create_pdf_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Statistics and actions
        right_panel = self.create_stats_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(refresh_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def create_pdf_list_panel(self):
        """Create the PDF list panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel(self.language_support.get_text("indexed_pdfs"))
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # PDF list
        self.pdf_list = QListWidget()
        self.pdf_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.pdf_list)
        
        # PDF actions
        pdf_actions_group = QGroupBox(self.language_support.get_text("pdf_actions"))
        pdf_actions_layout = QVBoxLayout(pdf_actions_group)
        
        self.delete_pdf_button = QPushButton(self.language_support.get_text("delete_selected_pdf"))
        self.delete_pdf_button.clicked.connect(self.delete_selected_pdf)
        self.delete_pdf_button.setEnabled(False)
        pdf_actions_layout.addWidget(self.delete_pdf_button)
        
        self.view_pdf_details_button = QPushButton(self.language_support.get_text("view_pdf_details"))
        self.view_pdf_details_button.clicked.connect(self.view_pdf_details)
        self.view_pdf_details_button.setEnabled(False)
        pdf_actions_layout.addWidget(self.view_pdf_details_button)
        
        layout.addWidget(pdf_actions_group)
        
        # Connect list selection
        self.pdf_list.itemSelectionChanged.connect(self.on_pdf_selection_changed)
        
        return widget
    
    def create_stats_panel(self):
        """Create the statistics panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Statistics group
        stats_group = QGroupBox(self.language_support.get_text("vector_store_statistics"))
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_display = QTextEdit()
        self.stats_display.setMaximumHeight(200)
        self.stats_display.setReadOnly(True)
        stats_layout.addWidget(self.stats_display)
        
        layout.addWidget(stats_group)
        
        # Management actions group
        management_group = QGroupBox("Vector Store Management")
        management_layout = QVBoxLayout(management_group)
        
        self.clear_all_button = QPushButton("Clear All Data")
        self.clear_all_button.clicked.connect(self.clear_all_data)
        management_layout.addWidget(self.clear_all_button)
        
        self.rebuild_index_button = QPushButton(self.language_support.get_text("rebuild_index"))
        self.rebuild_index_button.setToolTip(self.language_support.get_text("rebuild_index_tooltip"))
        self.rebuild_index_button.clicked.connect(self.rebuild_index)
        management_layout.addWidget(self.rebuild_index_button)
        
        layout.addWidget(management_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        return widget
    
    def refresh_data(self):
        """Refresh the vector store data"""
        if not self.llm_service:
            return
        
        try:
            # Get vector store statistics
            stats = self.llm_service.get_vector_store_stats()
            
            # Update statistics display
            stats_text = f"Total Chunks: {stats.get('total_chunks', 0)}\n"
            stats_text += f"Unique PDFs: {stats.get('unique_pdfs', 0)}\n"
            stats_text += f"Max Pages: {stats.get('max_pages', 0)}\n\n"
            
            pdf_names = stats.get('pdf_names', [])
            if pdf_names:
                stats_text += "Indexed PDFs:\n"
                for pdf_name in pdf_names:
                    stats_text += f"• {pdf_name}\n"
            else:
                stats_text += "No PDFs indexed yet."
            
            self.stats_display.setPlainText(stats_text)
            
            # Update PDF list
            self.pdf_list.clear()
            for pdf_name in pdf_names:
                self.pdf_list.addItem(pdf_name)
            
        except Exception as e:
            error_msg = f"Error loading vector store data: {str(e)}"
            self.stats_display.setPlainText(error_msg)
            QMessageBox.warning(self, "Error", error_msg)
    
    def on_pdf_selection_changed(self):
        """Handle PDF selection change"""
        has_selection = len(self.pdf_list.selectedItems()) > 0
        self.delete_pdf_button.setEnabled(has_selection)
        self.view_pdf_details_button.setEnabled(has_selection)
    
    def delete_selected_pdf(self):
        """Delete the selected PDF from vector store"""
        selected_items = self.pdf_list.selectedItems()
        if not selected_items:
            return
        
        pdf_name = selected_items[0].text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete '{pdf_name}' from the vector store?\n\nThis will remove all chunks and embeddings for this PDF.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.llm_service.delete_pdf_from_vector_store(pdf_name)
                if success:
                    QMessageBox.information(self, "Success", f"Successfully deleted '{pdf_name}' from vector store.")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete '{pdf_name}' from vector store.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting PDF: {str(e)}")
    
    def view_pdf_details(self):
        """View details of the selected PDF"""
        selected_items = self.pdf_list.selectedItems()
        if not selected_items:
            return
        
        pdf_name = selected_items[0].text()
        
        try:
            # Get chunks for this PDF
            chunks = self.llm_service.vector_store.get_chunks_by_pdf(pdf_name)
            
            if chunks:
                # Create details dialog
                details_dialog = PDFDetailsDialog(self, pdf_name, chunks)
                details_dialog.exec()
            else:
                QMessageBox.information(self, "No Data", f"No chunks found for '{pdf_name}'.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading PDF details: {str(e)}")
    
    def clear_all_data(self):
        """Clear all data from vector store"""
        # Confirm clearing
        reply = QMessageBox.question(
            self, 
            "Confirm Clear All", 
            "Are you sure you want to clear ALL data from the vector store?\n\nThis will remove all PDFs, chunks, and embeddings. This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)  # Indeterminate progress
                
                success = self.llm_service.clear_vector_store()
                
                self.progress_bar.setVisible(False)
                
                if success:
                    QMessageBox.information(self, "Success", "Successfully cleared all data from vector store.")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", "Failed to clear vector store.")
                    
            except Exception as e:
                self.progress_bar.setVisible(False)
                QMessageBox.critical(self, "Error", f"Error clearing vector store: {str(e)}")
    
    def rebuild_index(self):
        """Rebuild the vector store index with new multilingual tokenizer"""
        # Get current PDFs and their paths
        stats = self.llm_service.get_vector_store_stats()
        pdf_names = stats.get('pdf_names', [])
        
        if not pdf_names:
            QMessageBox.information(self, "Info", self.language_support.get_text("no_pdfs_to_reindex"))
            return
        
        # Get PDF paths from existing chunks
        pdf_paths = {}
        try:
            # Get a sample chunk for each PDF to extract the path
            for pdf_name in pdf_names:
                chunks = self.llm_service.vector_store.get_chunks_by_pdf(pdf_name)
                if chunks and len(chunks) > 0 and 'metadata' in chunks[0] and 'pdf_path' in chunks[0]['metadata']:
                    pdf_paths[pdf_name] = chunks[0]['metadata']['pdf_path']
                else:
                    pdf_paths[pdf_name] = None
        except Exception as e:
            print(f"Warning: Could not extract PDF paths: {e}")
        
        # Check which PDFs have stored paths
        pdfs_with_paths = {name: path for name, path in pdf_paths.items() if path and os.path.exists(path)}
        pdfs_without_paths = [name for name, path in pdf_paths.items() if not path or not os.path.exists(path)]
        
        if not pdfs_with_paths:
            limitation_message = (
                f"{self.language_support.get_text('reindexing_limitation_message')}\n\n"
                f"{self.language_support.get_text('use_reindex_script')}\n"
                f"{self.language_support.get_text('reindex_script_steps')}\n\n"
                f"{self.language_support.get_text('reindex_script_purpose')}"
            )
            QMessageBox.information(
                self, 
                self.language_support.get_text("reindexing_limitation"), 
                limitation_message
            )
            return
        
        # Show confirmation with details
        confirm_text = self.language_support.format_message("confirm_reindex_message", count=len(pdfs_with_paths)) + "\n\n"
        confirm_text += self.language_support.get_text("pdfs_to_reindex") + "\n"
        for pdf_name in pdfs_with_paths:
            confirm_text += f"• {pdf_name}\n"
        
        if pdfs_without_paths:
            confirm_text += f"\n{self.language_support.get_text('pdfs_cannot_reindex')}\n"
            for pdf_name in pdfs_without_paths:
                confirm_text += f"• {pdf_name}\n"
            confirm_text += f"\n{self.language_support.get_text('confirm_deletion_message').split('?')[0]}."
        
        confirm_text += f"\n\n{self.language_support.get_text('reindexing_will')}\n"
        confirm_text += f"{self.language_support.get_text('reindexing_delete_chunks')}\n"
        confirm_text += f"{self.language_support.get_text('reindexing_reprocess')}\n"
        confirm_text += f"{self.language_support.get_text('reindexing_time')}\n\n"
        confirm_text += self.language_support.get_text("reindexing_continue")
        
        reply = QMessageBox.question(
            self, 
            self.language_support.get_text("confirm_reindex"), 
            confirm_text,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, len(pdfs_with_paths))
                self.progress_bar.setValue(0)
                
                # Clear existing data first
                self.llm_service.clear_vector_store()
                
                # Reindex each PDF with a path
                for i, (pdf_name, pdf_path) in enumerate(pdfs_with_paths.items()):
                    self.progress_bar.setValue(i)
                    progress_text = self.language_support.format_message("reindexing_progress", 
                                                                        pdf_name=pdf_name, 
                                                                        current=i+1, 
                                                                        total=len(pdfs_with_paths))
                    self.progress_bar.setFormat(progress_text)
                    
                    # Process the PDF with the new multilingual tokenizer
                    chunks = self.llm_service.vector_store.process_pdf(pdf_path, pdf_name)
                    if chunks:
                        success = self.llm_service.vector_store.add_document_chunks(chunks)
                        if not success:
                            print(f"Warning: Failed to add chunks for {pdf_name}")
                    
                    # Update progress
                    self.progress_bar.setValue(i + 1)
                
                self.progress_bar.setVisible(False)
                
                # Show completion message
                completion_message = self.language_support.format_message("reindexing_complete_message", count=len(pdfs_with_paths))
                completion_message += f"\n\n{self.language_support.get_text('reindexed_pdfs')}\n"
                completion_message += "\n".join([f"• {name}" for name in pdfs_with_paths.keys()])
                
                QMessageBox.information(
                    self, 
                    self.language_support.get_text("reindexing_complete"), 
                    completion_message
                )
                
                # Refresh the display
                self.refresh_data()
                
            except Exception as e:
                self.progress_bar.setVisible(False)
                QMessageBox.critical(self, "Error", f"Error during reindexing: {str(e)}")


class PDFDetailsDialog(QDialog):
    """Dialog for viewing PDF details"""
    
    def __init__(self, parent=None, pdf_name="", chunks=None):
        super().__init__(parent)
        self.pdf_name = pdf_name
        self.chunks = chunks or []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(f"PDF Details - {self.pdf_name}")
        self.setGeometry(100, 100, 700, 500)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f"Details for: {self.pdf_name}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Statistics
        stats_text = f"Total Chunks: {len(self.chunks)}\n"
        if self.chunks:
            pages = set(chunk['metadata'].get('page_number', 0) for chunk in self.chunks)
            stats_text += f"Pages: {min(pages)} - {max(pages)}\n"
            total_tokens = sum(chunk['metadata'].get('token_count', 0) for chunk in self.chunks)
            stats_text += f"Total Tokens: {total_tokens:,}\n"
        
        stats_label = QLabel(stats_text)
        layout.addWidget(stats_label)
        
        # Chunks list
        chunks_label = QLabel("Chunks:")
        layout.addWidget(chunks_label)
        
        self.chunks_list = QListWidget()
        for i, chunk in enumerate(self.chunks, 1):
            metadata = chunk.get('metadata', {})
            page_num = metadata.get('page_number', 'Unknown')
            chunk_num = metadata.get('chunk_number', i)
            text_preview = chunk.get('text', '')[:100] + "..." if len(chunk.get('text', '')) > 100 else chunk.get('text', '')
            
            item_text = f"Chunk {chunk_num} (Page {page_num}): {text_preview}"
            self.chunks_list.addItem(item_text)
        
        layout.addWidget(self.chunks_list)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
