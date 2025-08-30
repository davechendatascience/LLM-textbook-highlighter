"""
Text Panel Component
Handles text display, LLM integration, and markdown rendering
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QComboBox, QSpinBox,
                               QTabWidget, QSplitter)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from src.llm import LLMService
from src.gui.markdown_widget import EnhancedMarkdownTextWidget


class TextPanel(QWidget):
    """Text display and LLM interaction panel"""
    
    def __init__(self, language_support=None):
        super().__init__()
        self.language_support = language_support
        self.llm_service = LLMService(language_support)
        self.extracted_text = ""
        self.current_font_size = 12
        self.current_markdown_content = ""  # Store current markdown content
        
        self.setup_ui()
        self.update_api_status()
        
    def setup_ui(self):
        """Setup the text panel UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Extracted text tab
        self.extracted_tab = self.create_extraction_tab()
        self.tab_widget.addTab(self.extracted_tab, self.language_support.get_text("extracted_text_tab") if self.language_support else "Extracted Text")
        
        # LLM response tab
        self.response_tab = self.create_response_tab()
        self.tab_widget.addTab(self.response_tab, self.language_support.get_text("ai_response_tab") if self.language_support else "AI Response")
        
        layout.addWidget(self.tab_widget)
        
    def create_extraction_tab(self):
        """Create the text extraction tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Font size controls
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel(self.language_support.get_text("font_size") if self.language_support else "Font Size:"))
        self.font_size_combo = QComboBox()
        if self.language_support:
            self.font_size_combo.addItems(self.language_support.get_font_size_options())
        else:
            self.font_size_combo.addItems(["Small (10pt)", "Medium (12pt)", "Large (14pt)", "Extra Large (20pt)"])
        self.font_size_combo.setCurrentText("Medium (12pt)")
        self.font_size_combo.currentTextChanged.connect(self.on_font_size_changed)
        font_layout.addWidget(self.font_size_combo)
        
        layout.addLayout(font_layout)
        
        # Extracted text display
        self.extracted_text_edit = QTextEdit()
        self.extracted_text_edit.setReadOnly(True)
        placeholder = self.language_support.get_text("select_text_placeholder") if self.language_support else "Select text from PDF to extract..."
        self.extracted_text_edit.setPlaceholderText(placeholder)
        layout.addWidget(self.extracted_text_edit)
        
        return widget
        
    def create_response_tab(self):
        """Create the LLM response tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Question input
        question_layout = QHBoxLayout()
        question_layout.addWidget(QLabel(self.language_support.get_text("question_label") if self.language_support else "Question:"))
        
        self.question_input = QTextEdit()
        self.question_input.setMaximumHeight(60)
        placeholder = self.language_support.get_text("ask_question_placeholder") if self.language_support else "Ask a question about the extracted text..."
        self.question_input.setPlaceholderText(placeholder)
        question_layout.addWidget(self.question_input)
        
        layout.addLayout(question_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.ask_button = QPushButton(self.language_support.get_text("ask_question_btn") if self.language_support else "Ask Question")
        self.ask_button.clicked.connect(self.ask_question)
        controls_layout.addWidget(self.ask_button)
        
        self.generate_button = QPushButton(self.language_support.get_text("generate_questions_btn") if self.language_support else "Generate Questions")
        self.generate_button.clicked.connect(self.generate_questions)
        controls_layout.addWidget(self.generate_button)
        
        controls_layout.addWidget(QLabel(self.language_support.get_text("answer_length_label") if self.language_support else "Answer Length:"))
        self.length_combo = QComboBox()
        if self.language_support:
            self.length_combo.addItems(self.language_support.get_answer_length_options())
        else:
            self.length_combo.addItems(["Short", "Medium", "Long"])
        self.length_combo.setCurrentText("Medium")
        controls_layout.addWidget(self.length_combo)
        
        layout.addLayout(controls_layout)
        
        # API Key Status Section
        api_layout = QHBoxLayout()
        
        # API Key Status Label
        api_label_text = self.language_support.get_text("api_key_label") if self.language_support else "API Key:"
        self.api_status_label = QLabel(api_label_text)
        self.api_status_label.setStyleSheet("font-weight: bold;")
        api_layout.addWidget(self.api_status_label)
        
        # API Key Status Indicator
        self.api_status_indicator = QLabel()
        self.api_status_indicator.setMinimumWidth(100)
        api_layout.addWidget(self.api_status_indicator)
        
        # Configure API Key Button
        configure_text = self.language_support.get_text("configure_api_key") if self.language_support else "Configure API Key"
        self.configure_api_button = QPushButton(configure_text)
        self.configure_api_button.clicked.connect(self.open_api_settings)
        api_layout.addWidget(self.configure_api_button)
        
        # Test API Connection Button
        test_text = self.language_support.get_text("test_connection") if self.language_support else "Test Connection"
        self.test_api_button = QPushButton(test_text)
        self.test_api_button.clicked.connect(self.test_api_connection)
        api_layout.addWidget(self.test_api_button)
        
        # Add stretch to push everything to the left
        api_layout.addStretch()
        
        layout.addLayout(api_layout)
        
        # Response display
        self.response_widget = EnhancedMarkdownTextWidget()
        layout.addWidget(self.response_widget)
        
        return widget
        
    def set_extracted_text(self, text: str):
        """Set the extracted text"""
        self.extracted_text = text
        self.extracted_text_edit.setText(text)
        
    def on_font_size_changed(self, font_size_text: str):
        """Handle font size change"""
        # Extract font size from text
        if "10pt" in font_size_text:
            self.current_font_size = 10
        elif "12pt" in font_size_text:
            self.current_font_size = 12
        elif "14pt" in font_size_text:
            self.current_font_size = 14
        elif "20pt" in font_size_text:
            self.current_font_size = 20
        else:
            self.current_font_size = 12
            
        # Apply font size to text displays
        self.apply_font_size()
        
    def apply_font_size(self):
        """Apply current font size to text displays"""
        font = self.extracted_text_edit.font()
        font.setPointSize(self.current_font_size)
        self.extracted_text_edit.setFont(font)
        
        # Reapply the current markdown content with new font size
        if self.current_markdown_content:
            self.response_widget.set_markdown_text(self.current_markdown_content, self.current_font_size)
        
    def ask_question(self):
        """Ask a question to the LLM"""
        question = self.question_input.toPlainText().strip()
        if not question or not self.extracted_text:
            return
            
        # Get answer length preference
        length = self.length_combo.currentText().lower()
        
        try:
            # Check if we have a current PDF and vector store is available
            if (hasattr(self.llm_service, 'current_pdf_name') and 
                self.llm_service.current_pdf_name and
                hasattr(self.llm_service, 'ask_question_with_context')):
                
                # Use vector store enhanced question answering
                response = self.llm_service.ask_question_with_context(
                    question, self.extracted_text, length
                )
            else:
                # Use regular question answering
                prompt = self.build_prompt(question)
                response = self.llm_service.ask_question(prompt, length)
            
            # Check if it's an API key error
            if "No API key configured" in response:
                error_response = f"{response}\n\n**To configure your API key:**\n" \
                               "1. Go to **Settings > Configure API Keys** in the menu bar\n" \
                               "2. Enter your Perplexity API key\n" \
                               "3. Click **Save**\n" \
                               "4. Try asking your question again"
                self.current_markdown_content = error_response
                self.response_widget.set_markdown_text(error_response, self.current_font_size)
            else:
                # Display response
                self.current_markdown_content = response
                self.response_widget.set_markdown_text(response, self.current_font_size)
            
        except Exception as e:
            error_response = f"Error: {str(e)}"
            self.current_markdown_content = error_response
            self.response_widget.set_markdown_text(error_response, self.current_font_size)
            
    def generate_questions(self):
        """Generate questions based on extracted text"""
        if not self.extracted_text:
            return
            
        try:
            # Generate questions using LLM
            questions = self.llm_service.generate_questions(self.extracted_text)
            
            # Display questions
            self.current_markdown_content = questions
            self.response_widget.set_markdown_text(questions, self.current_font_size)
            
        except Exception as e:
            error_response = f"Error generating questions: {str(e)}"
            self.current_markdown_content = error_response
            self.response_widget.set_markdown_text(error_response, self.current_font_size)
            
    def build_prompt(self, question: str) -> str:
        """Build the prompt for the LLM"""
        prompt = f"""Please answer the following question based on the provided text.

**Selected Text (Main Focus - The specific text you selected):**
{self.extracted_text}

"""
            
        prompt += f"""**Question:**
{question}

**Important:** Please focus primarily on the selected text when answering the question. Use the background context only for additional information if needed.

Please provide a clear, well-structured answer."""
        
        return prompt

    def update_api_status(self):
        """Update the API key status display"""
        if self.llm_service.api_key:
            # Show API key is configured
            status_text = self.language_support.get_text("api_key_configured") if self.language_support else "✅ Configured"
            self.api_status_indicator.setText(status_text)
            self.api_status_indicator.setStyleSheet("color: green; font-weight: bold;")
            self.configure_api_button.setText(
                self.language_support.get_text("change_api_key") if self.language_support else "Change API Key"
            )
        else:
            # Show API key is not configured
            status_text = self.language_support.get_text("api_key_not_configured") if self.language_support else "❌ Not Configured"
            self.api_status_indicator.setText(status_text)
            self.api_status_indicator.setStyleSheet("color: red; font-weight: bold;")
            self.configure_api_button.setText(
                self.language_support.get_text("configure_api_key") if self.language_support else "Configure API Key"
            )
    
    def open_api_settings(self):
        """Open the API settings dialog"""
        from src.gui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self, self.llm_service)
        if dialog.exec() == SettingsDialog.Accepted:
            # Reload API key
            self.llm_service.reload_api_key()
            # Update status display
            self.update_api_status()
            # Show success message
            success_msg = self.language_support.get_text("api_key_saved") if self.language_support else "API key saved successfully!"
            self.response_widget.set_markdown_text(f"**{success_msg}**")
    
    def test_api_connection(self):
        """Test the API connection"""
        if not self.llm_service.api_key:
            error_msg = self.language_support.get_text("no_api_key_to_test") if self.language_support else "No API key configured to test."
            self.response_widget.set_markdown_text(f"**Error:** {error_msg}", self.current_font_size)
            return
        
        try:
            # Test with a simple query
            test_response = self.llm_service.ask_question("Hello, this is a test message.", "short")
            
            if "Error:" in test_response:
                # API test failed
                error_msg = self.language_support.get_text("api_test_failed") if self.language_support else "API test failed"
                self.response_widget.set_markdown_text(f"**{error_msg}:** {test_response}", self.current_font_size)
            else:
                # API test successful
                success_msg = self.language_support.get_text("api_test_successful") if self.language_support else "API connection test successful!"
                self.response_widget.set_markdown_text(f"**{success_msg}**\n\nTest response: {test_response[:100]}...", self.current_font_size)
                
        except Exception as e:
            error_msg = self.language_support.get_text("api_test_error") if self.language_support else "API test error"
            self.response_widget.set_markdown_text(f"**{error_msg}:** {str(e)}", self.current_font_size)
