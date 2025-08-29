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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
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
        
    def load_secrets(self):
        """Load current secrets from secrets.json"""
        secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "secrets.json")
        try:
            with open(secrets_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
            
    def load_current_settings(self):
        """Load current settings into the UI"""
        # Load API keys
        self.perplexity_key_input.setText(self.current_secrets.get("perplexity_api_key", ""))
        
        # Load general settings
        self.default_length_combo.setCurrentText(self.current_secrets.get("default_answer_length", "Medium"))
        self.enable_research_checkbox.setChecked(self.current_secrets.get("enable_research_by_default", True))
        self.enable_web_search_checkbox.setChecked(self.current_secrets.get("enable_web_search_by_default", False))
        
    def save_settings(self):
        """Save settings to secrets.json"""
        try:
            # Prepare secrets data
            secrets_data = {
                "perplexity_api_key": self.perplexity_key_input.text().strip(),
                "default_answer_length": self.default_length_combo.currentText(),
                "enable_research_by_default": self.enable_research_checkbox.isChecked(),
                "enable_web_search_by_default": self.enable_web_search_checkbox.isChecked()
            }
            
            # Save to secrets.json
            secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "secrets.json")
            with open(secrets_path, 'w') as f:
                json.dump(secrets_data, f, indent=2)
                
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
            
        except Exception as e:
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
