"""
Settings Dialog
Handles API key configuration and other settings
"""

import json
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QLineEdit, QTextEdit, QMessageBox,
                               QTabWidget, QWidget, QFormLayout, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SettingsDialog(QDialog):
    """Settings dialog for API configuration and other settings"""
    
    def __init__(self, parent=None, llm_service=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Store LLM service for vector store operations
        self.llm_service = llm_service
        
        # Load current settings
        self.current_secrets = self.load_secrets()
        
        self.setup_ui()
        self.load_current_settings()
        
    def setup_ui(self):
        """Setup the settings dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # API Settings tab
        self.api_tab = self.create_api_settings_tab()
        self.tab_widget.addTab(self.api_tab, "API Configuration")
        
        # General Settings tab
        self.general_tab = self.create_general_settings_tab()
        self.tab_widget.addTab(self.general_tab, "General Settings")
        
        # Vector Store Management tab
        if self.llm_service:
            self.vector_store_tab = self.create_vector_store_tab()
            self.tab_widget.addTab(self.vector_store_tab, "Vector Store Management")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def create_api_settings_tab(self):
        """Create the API settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Perplexity API Key
        layout.addRow(QLabel("Perplexity API Key:"))
        
        self.perplexity_key_input = QLineEdit()
        self.perplexity_key_input.setEchoMode(QLineEdit.Password)
        self.perplexity_key_input.setPlaceholderText("Enter your Perplexity API key...")
        layout.addRow(self.perplexity_key_input)
        
        # API Key help text
        help_text = QTextEdit()
        help_text.setMaximumHeight(120)
        help_text.setReadOnly(True)
        help_text.setPlainText(
            "To get a Perplexity API key:\n"
            "1. Visit https://www.perplexity.ai/\n"
            "2. Sign up for an account\n"
            "3. Go to your account settings\n"
            "4. Generate an API key\n"
            "5. Paste it here and click Save\n\n"
            "Available Models:\n"
            "• sonar: Fast responses (~$1 per 1,000 queries)\n"
            "• sonar-reasoning: Detailed answers (~$5 per 1,000 queries)"
        )
        layout.addRow(help_text)
        
        # Test API connection
        self.test_button = QPushButton("Test API Connection")
        self.test_button.clicked.connect(self.test_api_connection)
        layout.addRow(self.test_button)
        
        return widget
        
    def create_general_settings_tab(self):
        """Create the general settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Default answer length
        layout.addRow(QLabel("Default Answer Length:"))
        from PySide6.QtWidgets import QComboBox
        self.default_length_combo = QComboBox()
        self.default_length_combo.addItems(["Short", "Medium", "Long"])
        layout.addRow(self.default_length_combo)
        
        # Enable research enhancement by default
        self.enable_research_checkbox = QCheckBox("Enable research enhancement by default")
        layout.addRow(self.enable_research_checkbox)
        
        # Enable web search by default
        self.enable_web_search_checkbox = QCheckBox("Enable web search by default (increases API costs)")
        layout.addRow(self.enable_web_search_checkbox)
        
        return widget
        
    def create_vector_store_tab(self):
        """Create the vector store management tab"""
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QGroupBox, QProgressBar, QMessageBox
        from PySide6.QtCore import QThread, Signal
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Statistics Section
        stats_group = QGroupBox("Vector Store Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_display = QTextEdit()
        self.stats_display.setMaximumHeight(150)
        self.stats_display.setReadOnly(True)
        stats_layout.addWidget(self.stats_display)
        
        refresh_button = QPushButton("Refresh Statistics")
        refresh_button.clicked.connect(self.refresh_vector_store_stats)
        stats_layout.addWidget(refresh_button)
        
        layout.addWidget(stats_group)
        
        # Management Section
        management_group = QGroupBox("Vector Store Management")
        management_layout = QVBoxLayout(management_group)
        
        # Current PDF info
        self.current_pdf_label = QLabel("No PDF currently loaded")
        management_layout.addWidget(self.current_pdf_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.process_pdf_button = QPushButton("Process Current PDF")
        self.process_pdf_button.clicked.connect(self.process_current_pdf)
        self.process_pdf_button.setEnabled(False)
        button_layout.addWidget(self.process_pdf_button)
        
        self.clear_store_button = QPushButton("Clear All Data")
        self.clear_store_button.clicked.connect(self.clear_vector_store)
        button_layout.addWidget(self.clear_store_button)
        
        management_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        management_layout.addWidget(self.progress_bar)
        
        layout.addWidget(management_group)
        
        # Initialize statistics
        self.refresh_vector_store_stats()
        
        return widget
        
    def refresh_vector_store_stats(self):
        """Refresh vector store statistics"""
        if not self.llm_service:
            return
            
        try:
            stats = self.llm_service.vector_store.get_collection_stats()
            
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
            
        except Exception as e:
            self.stats_display.setPlainText(f"Error loading statistics: {str(e)}")
    
    def process_current_pdf(self):
        """Process the current PDF for vector store"""
        if not self.llm_service or not self.llm_service.current_pdf_path:
            QMessageBox.warning(self, "Warning", "No PDF currently loaded.")
            return
            
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.process_pdf_button.setEnabled(False)
            
            # Process the PDF
            success = self.llm_service.process_current_pdf()
            
            if success:
                QMessageBox.information(self, "Success", f"Successfully processed {self.llm_service.current_pdf_name}")
            else:
                QMessageBox.warning(self, "Warning", f"Failed to process {self.llm_service.current_pdf_name}")
            
            # Refresh statistics
            self.refresh_vector_store_stats()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing PDF: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            self.process_pdf_button.setEnabled(True)
    
    def clear_vector_store(self):
        """Clear all data from vector store"""
        if not self.llm_service:
            return
            
        reply = QMessageBox.question(
            self, 
            "Confirm Clear", 
            "Are you sure you want to clear all vector store data? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.llm_service.vector_store.clear_collection()
                if success:
                    QMessageBox.information(self, "Success", "Vector store cleared successfully.")
                    self.refresh_vector_store_stats()
                else:
                    QMessageBox.warning(self, "Warning", "Failed to clear vector store.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error clearing vector store: {str(e)}")
    
    def update_current_pdf_info(self):
        """Update the current PDF information display"""
        if not self.llm_service:
            return
            
        if self.llm_service.current_pdf_name:
            self.current_pdf_label.setText(f"Current PDF: {self.llm_service.current_pdf_name}")
            self.process_pdf_button.setEnabled(True)
        else:
            self.current_pdf_label.setText("No PDF currently loaded")
            self.process_pdf_button.setEnabled(False)
            
    def load_secrets(self):
        """Load current secrets from environment variables or project root secrets.json"""
        secrets = {}
        
        # First try environment variable
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if api_key:
            secrets["perplexity_api_key"] = api_key
            print("✅ API key loaded from environment variable")
        
        # Fallback to project root directory
        if not api_key:
            secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "secrets.json")
            try:
                if os.path.exists(secrets_path):
                    print(f"🔍 Loading settings from project root: {secrets_path}")
                    with open(secrets_path, 'r') as f:
                        file_secrets = json.load(f)
                        secrets.update(file_secrets)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"⚠️ Error loading from {secrets_path}: {e}")
        
        if not secrets:
            print("❌ No settings found, using defaults")
        
        return secrets
            
    def load_current_settings(self):
        """Load current settings into the UI"""
        # Load API keys
        self.perplexity_key_input.setText(self.current_secrets.get("perplexity_api_key", ""))
        
        # Load general settings
        self.default_length_combo.setCurrentText(self.current_secrets.get("default_answer_length", "Medium"))
        self.enable_research_checkbox.setChecked(self.current_secrets.get("enable_research_by_default", True))
        self.enable_web_search_checkbox.setChecked(self.current_secrets.get("enable_web_search_by_default", False))
        
        # Update vector store info if available
        if hasattr(self, 'update_current_pdf_info'):
            self.update_current_pdf_info()
            
    def save_settings(self):
        """Save settings to environment variables and project root secrets.json"""
        try:
            # Get API key from input
            api_key = self.perplexity_key_input.text().strip()
            
            # Set environment variable for current session
            if api_key:
                os.environ["PERPLEXITY_API_KEY"] = api_key
                print("✅ API key saved to environment variable")
            
            # Prepare secrets data
            secrets_data = {
                "perplexity_api_key": api_key,
                "default_answer_length": self.default_length_combo.currentText(),
                "enable_research_by_default": self.enable_research_checkbox.isChecked(),
                "enable_web_search_by_default": self.enable_web_search_checkbox.isChecked()
            }
            
            # Also save to project root secrets.json for persistence
            try:
                secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "secrets.json")
                with open(secrets_path, 'w') as f:
                    json.dump(secrets_data, f, indent=2)
                    
                print(f"✅ Settings also saved to {secrets_path}")
            except Exception as e:
                print(f"⚠️ Could not save to secrets.json: {e}")
                
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
            
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
            
    def test_api_connection(self):
        """Test the API connection"""
        api_key = self.perplexity_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter a Perplexity API key first.")
            return
            
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, this is a test message."
                    }
                ],
                "max_tokens": 50
            }
            
            response = requests.post("https://api.perplexity.ai/chat/completions", 
                                   headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "API connection test successful!")
            else:
                QMessageBox.critical(self, "Error", f"API connection failed: {response.status_code}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"API connection test failed: {str(e)}")
