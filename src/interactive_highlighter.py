#!/usr/bin/env python3
"""
Simplified Interactive PDF Highlighter with GUI - only fitz text extraction
Allows users to select regions and get LLM explanations using Perplexity API only
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import json
import os
import sys
from datetime import datetime

# Add paths for imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from llm import send_prompt_to_perplexity
from config import load_secrets, get_available_apis, DEFAULT_SETTINGS

class SimpleInteractivePDFHighlighter:
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
        self.root.title("Simple Interactive PDF Highlighter - Fitz Only")
        self.root.geometry(f"{DEFAULT_SETTINGS['window_width']}x{DEFAULT_SETTINGS['window_height']}")
        
        # PDF and session state
        self.pdf_doc = None
        self.current_page = 0
        self.pdf_path = ""
        self.session_notes = []
        
        # Simple selection system - only text selection
        self.is_selecting = False
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        self.selection_complete = False
        
        # LLM configuration - Perplexity only
        self.api_keys = load_secrets()
        self.available_apis = get_available_apis()
        
        # Store suggested questions
        self.suggested_questions_list = []
        
        # Store text widgets for font size control
        self.text_widgets = []
        
        # UI scaling factors (image to PDF coordinate conversion)
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.image_width = 800
        self.image_height = 600
        
        self.setup_ui()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top toolbar
        self.setup_toolbar(main_frame)
        
        # Content area with paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - PDF viewer
        self.setup_pdf_viewer(paned)
        
        # Right panel - Controls and text output
        self.setup_control_panel(paned)
    
    def setup_toolbar(self, parent):
        """Setup the toolbar with file operations"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="Previous Page", command=self.prev_page).pack(side=tk.LEFT, padx=(0, 5))
        
        self.page_label = ttk.Label(toolbar, text="Page: 0 / 0")
        self.page_label.pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Button(toolbar, text="Next Page", command=self.next_page).pack(side=tk.LEFT, padx=(5, 5))
        
        # Page selector
        ttk.Label(toolbar, text="Go to:").pack(side=tk.LEFT, padx=(10, 5))
        self.page_entry = tk.Entry(toolbar, width=5)
        self.page_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.page_entry.bind("<Return>", self.go_to_page)
        ttk.Button(toolbar, text="Go", command=self.go_to_page).pack(side=tk.LEFT, padx=(0, 10))
        
        # Selection controls
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=(10, 10))
        ttk.Button(toolbar, text="Clear Selection", command=self.clear_selection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="Extract Text", command=self.extract_selected_text).pack(side=tk.LEFT, padx=(0, 10))
        
        # Font size selector
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=(10, 10))
        ttk.Label(toolbar, text="Font size:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.font_size_var = tk.StringVar(value="10")
        self.font_size_dropdown = ttk.Combobox(toolbar, textvariable=self.font_size_var, width=8, state="readonly")
        self.font_size_dropdown['values'] = ["8", "9", "10", "11", "12", "14", "16", "18", "20"]
        self.font_size_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        self.font_size_dropdown.bind("<<ComboboxSelected>>", self.on_font_size_change)
        
        # API status
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=(10, 10))
        api_status = "✓ Perplexity" if 'perplexity' in self.available_apis else "✗ No API"
        ttk.Label(toolbar, text=f"API: {api_status}").pack(side=tk.LEFT)
    
    def setup_pdf_viewer(self, parent):
        """Setup the PDF viewer canvas"""
        pdf_frame = ttk.Frame(parent)
        parent.add(pdf_frame, weight=2)
        
        # Create canvas with scrollbars
        canvas_frame = ttk.Frame(pdf_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.pdf_canvas = tk.Canvas(canvas_frame, bg='white')
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.pdf_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.pdf_canvas.xview)
        self.pdf_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.pdf_canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mouse events for selection
        self.pdf_canvas.bind("<Button-1>", self.on_mouse_down)
        self.pdf_canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.pdf_canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # Bind mousewheel for PDF canvas scrolling
        def _on_pdf_mousewheel(event):
            self.pdf_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.pdf_canvas.bind("<MouseWheel>", _on_pdf_mousewheel)
        
        # Also bind to the frame to catch mouse wheel when over scrollbars
        canvas_frame.bind("<MouseWheel>", _on_pdf_mousewheel)
    
    def setup_control_panel(self, parent):
        """Setup the right control panel with master scrollbar"""
        # Create frame with scrollbar for entire control panel
        control_outer_frame = ttk.Frame(parent)
        parent.add(control_outer_frame, weight=1)
        
        # Create canvas and scrollbar for master scroll
        canvas = tk.Canvas(control_outer_frame)
        master_scrollbar = ttk.Scrollbar(control_outer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=master_scrollbar.set)
        
        def _configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Ensure the canvas width matches the frame width
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:  # Avoid errors during initialization
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", _configure_scroll_region)
        canvas.bind("<Configure>", _configure_scroll_region)
        
        canvas.pack(side="left", fill="both", expand=True)
        master_scrollbar.pack(side="right", fill="y")
        
        # Remove global mousewheel binding - only drag scrollbar to scroll
        
        # Now use scrollable_frame as the control_frame
        control_frame = scrollable_frame
        
        # Instructions
        instructions = ttk.Label(control_frame, text="Instructions:", font=('Arial', 12, 'bold'))
        instructions.pack(anchor='w', pady=(0, 5))
        
        instructions_text = ttk.Label(control_frame, text="1. Open a PDF file\n2. Drag to select text region\n3. Click 'Extract Text' to get content\n4. Ask questions about the selected text", wraplength=300, justify='left')
        instructions_text.pack(anchor='w', pady=(0, 15))
        
        # Selection status
        self.status_label = ttk.Label(control_frame, text="No selection", foreground="gray")
        self.status_label.pack(anchor='w', pady=(0, 10))
        
        # Create a vertical paned window for resizable text areas
        text_paned = ttk.PanedWindow(control_frame, orient=tk.VERTICAL)
        text_paned.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Top section: Extracted text
        top_frame = ttk.Frame(text_paned)
        text_paned.add(top_frame, weight=1)
        
        text_label = ttk.Label(top_frame, text="Extracted Text:", font=('Arial', 10, 'bold'))
        text_label.pack(anchor='w', pady=(0, 5))
        
        # Create text widget with proper word wrapping
        self.text_display = scrolledtext.ScrolledText(top_frame, height=6, wrap=tk.WORD, font=('Arial', 10))
        self.text_display.pack(fill=tk.BOTH, expand=True)
        self.text_widgets.append(self.text_display)
        
        # Middle section: Controls
        controls_frame = ttk.Frame(text_paned)
        text_paned.add(controls_frame, weight=0)
        
        # Question input
        question_label = ttk.Label(controls_frame, text="Ask a question:", font=('Arial', 10, 'bold'))
        question_label.pack(anchor='w', pady=(10, 5))
        
        self.question_entry = tk.Entry(controls_frame, width=40)
        self.question_entry.pack(fill=tk.X, pady=(0, 10))
        self.question_entry.bind("<Return>", self.ask_question)
        
        ttk.Button(controls_frame, text="Ask Question", command=self.ask_question).pack(pady=(0, 5))
        ttk.Button(controls_frame, text="Generate Suggested Questions", command=self.generate_suggested_questions).pack(pady=(0, 5))
        
        # Suggested questions dropdown
        suggested_label = ttk.Label(controls_frame, text="Suggested Questions:", font=('Arial', 10, 'bold'))
        suggested_label.pack(anchor='w', pady=(10, 5))
        
        self.suggested_questions_var = tk.StringVar()
        self.suggested_questions_dropdown = ttk.Combobox(controls_frame, textvariable=self.suggested_questions_var, width=50, state="readonly")
        self.suggested_questions_dropdown.pack(fill=tk.X, pady=(0, 5))
        
        # Answer length selector
        answer_frame = ttk.Frame(controls_frame)
        answer_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(answer_frame, text="Answer length:").pack(side=tk.LEFT)
        
        self.answer_length_var = tk.StringVar(value="Medium (250-500 tokens)")
        self.answer_length_dropdown = ttk.Combobox(answer_frame, textvariable=self.answer_length_var, width=25, state="readonly")
        self.answer_length_dropdown['values'] = [
            "Short (< 250 tokens)",
            "Medium (250-500 tokens)", 
            "Long (500-1000 tokens)",
            "Comprehensive (> 1000 tokens)"
        ]
        self.answer_length_dropdown.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        ttk.Button(controls_frame, text="Ask Selected Question", command=self.ask_selected_question).pack(pady=(5, 20))
        
        # Add extra padding at the bottom to ensure everything is scrollable
        ttk.Label(controls_frame, text="").pack(pady=(0, 50))
        
        # Bottom section: Response display (larger weight for more space)
        bottom_frame = ttk.Frame(text_paned)
        text_paned.add(bottom_frame, weight=2)  # Double weight for more space
        
        response_label = ttk.Label(bottom_frame, text="LLM Response:", font=('Arial', 10, 'bold'))
        response_label.pack(anchor='w', pady=(10, 5))
        
        # Create response widget with proper word wrapping
        self.response_display = scrolledtext.ScrolledText(bottom_frame, height=12, wrap=tk.WORD, font=('Arial', 10))
        self.response_display.pack(fill=tk.BOTH, expand=True)
        self.text_widgets.append(self.response_display)
        
        # Add bottom padding to ensure master scrollbar can reach the end
        bottom_spacer = ttk.Label(control_frame, text="")
        bottom_spacer.pack(pady=(20, 100))
    
    def open_pdf(self):
        """Open a PDF file"""
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                self.pdf_doc = fitz.open(file_path)
                self.pdf_path = file_path
                self.current_page = 0
                self.clear_selection()
                self.display_page()
                self.update_page_label()
                print(f"Opened PDF: {file_path} ({len(self.pdf_doc)} pages)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF: {e}")
    
    def display_page(self):
        """Display the current PDF page"""
        if not self.pdf_doc:
            return
        
        try:
            page = self.pdf_doc[self.current_page]
            
            # Get page as image
            mat = fitz.Matrix(1.5, 1.5)  # Zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            # Convert to PIL Image and then to PhotoImage
            import io
            image = Image.open(io.BytesIO(img_data))
            
            # Resize to fit display
            self.image_width, self.image_height = image.size
            if self.image_width > DEFAULT_SETTINGS['pdf_display_width']:
                ratio = DEFAULT_SETTINGS['pdf_display_width'] / self.image_width
                new_width = int(self.image_width * ratio)
                new_height = int(self.image_height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.image_width, self.image_height = new_width, new_height
            
            # Calculate scaling factors for coordinate conversion
            page_rect = page.rect
            self.scale_x = page_rect.width / self.image_width
            self.scale_y = page_rect.height / self.image_height
            
            self.photo = ImageTk.PhotoImage(image)
            
            # Clear canvas and display image
            self.pdf_canvas.delete("all")
            self.pdf_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.pdf_canvas.config(scrollregion=(0, 0, self.image_width, self.image_height))
            
        except Exception as e:
            print(f"Error displaying page: {e}")
    
    def prev_page(self):
        """Go to previous page"""
        if self.pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self.clear_selection()
            self.display_page()
            self.update_page_label()
    
    def next_page(self):
        """Go to next page"""
        if self.pdf_doc and self.current_page < len(self.pdf_doc) - 1:
            self.current_page += 1
            self.clear_selection()
            self.display_page()
            self.update_page_label()
    
    def go_to_page(self, event=None):
        """Go to specific page number"""
        if not self.pdf_doc:
            messagebox.showwarning("No PDF", "Please open a PDF first.")
            return
        
        try:
            page_num = int(self.page_entry.get().strip())
            # Convert to 0-based index
            page_index = page_num - 1
            
            if page_index < 0 or page_index >= len(self.pdf_doc):
                messagebox.showwarning("Invalid Page", f"Page number must be between 1 and {len(self.pdf_doc)}.")
                return
            
            self.current_page = page_index
            self.clear_selection()
            self.display_page()
            self.update_page_label()
            self.page_entry.delete(0, tk.END)  # Clear the entry
            
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid page number.")
    
    def update_page_label(self):
        """Update the page count label"""
        if self.pdf_doc:
            self.page_label.config(text=f"Page: {self.current_page + 1} / {len(self.pdf_doc)}")
        else:
            self.page_label.config(text="Page: 0 / 0")
    
    def on_mouse_down(self, event):
        """Handle mouse down for selection start"""
        canvas_x = self.pdf_canvas.canvasx(event.x)
        canvas_y = self.pdf_canvas.canvasy(event.y)
        
        self.is_selecting = True
        
        # Clear existing selection
        if self.selection_rect:
            self.pdf_canvas.delete(self.selection_rect)
        
        self.selection_start = (canvas_x, canvas_y)
        self.selection_complete = False
        self.update_status("Selection started...")
    
    def on_mouse_drag(self, event):
        """Handle mouse drag for selection"""
        if not self.is_selecting or not self.selection_start:
            return
            
        canvas_x = self.pdf_canvas.canvasx(event.x)
        canvas_y = self.pdf_canvas.canvasy(event.y)
        
        # Remove previous selection rectangle
        if self.selection_rect:
            self.pdf_canvas.delete(self.selection_rect)
        
        # Draw selection rectangle
        x1, y1 = self.selection_start
        x2, y2 = canvas_x, canvas_y
        self.selection_rect = self.pdf_canvas.create_rectangle(
            x1, y1, x2, y2, outline="red", width=2, fill="", tags="selection"
        )
    
    def on_mouse_up(self, event):
        """Handle mouse up for selection end"""
        if not self.is_selecting:
            return
        
        canvas_x = self.pdf_canvas.canvasx(event.x)
        canvas_y = self.pdf_canvas.canvasy(event.y)
        
        self.selection_end = (canvas_x, canvas_y)
        self.selection_complete = True
        self.is_selecting = False
        
        self.update_status("Selection completed. Click 'Extract Text' to get content.")
    
    def clear_selection(self):
        """Clear all selections"""
        if self.selection_rect:
            self.pdf_canvas.delete(self.selection_rect)
        
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        self.selection_complete = False
        self.text_display.delete('1.0', tk.END)
        self.response_display.delete('1.0', tk.END)
        
        # Clear suggested questions
        self.suggested_questions_list = []
        self.suggested_questions_dropdown['values'] = []
        self.suggested_questions_var.set("")
        
        self.update_status("No selection")
    
    def canvas_to_pdf_rect(self, start_pos, end_pos):
        """Convert canvas coordinates to PDF rectangle"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Convert to PDF coordinates
        pdf_x1 = x1 * self.scale_x
        pdf_y1 = y1 * self.scale_y
        pdf_x2 = x2 * self.scale_x
        pdf_y2 = y2 * self.scale_y
        
        # Ensure correct ordering
        pdf_x1, pdf_x2 = min(pdf_x1, pdf_x2), max(pdf_x1, pdf_x2)
        pdf_y1, pdf_y2 = min(pdf_y1, pdf_y2), max(pdf_y1, pdf_y2)
        
        return fitz.Rect(pdf_x1, pdf_y1, pdf_x2, pdf_y2)
    
    def extract_selected_text(self):
        """Extract text from the selected region using fitz"""
        if not self.selection_complete or not self.pdf_doc:
            messagebox.showwarning("No Selection", "Please select a region first.")
            return
        
        try:
            page = self.pdf_doc[self.current_page]
            rect = self.canvas_to_pdf_rect(self.selection_start, self.selection_end)
            
            # Extract text using fitz
            text = page.get_text("text", clip=rect).strip()
            
            if not text:
                text = "No text found in selected region."
            
            # Display extracted text
            self.text_display.delete('1.0', tk.END)
            self.text_display.insert('1.0', text)
            
            self.update_status(f"Extracted {len(text)} characters using fitz")
            print(f"Extracted text ({len(text)} chars): {text[:100]}...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract text: {e}")
    
    def ask_question(self, event=None):
        """Ask a question about the extracted text"""
        question = self.question_entry.get().strip()
        extracted_text = self.text_display.get('1.0', tk.END).strip()
        
        if not question:
            messagebox.showwarning("No Question", "Please enter a question.")
            return
        
        if not extracted_text or extracted_text == "No text found in selected region.":
            messagebox.showwarning("No Text", "Please extract text first.")
            return
        
        if 'perplexity' not in self.available_apis:
            messagebox.showerror("API Error", "Perplexity API key not available.")
            return
        
        try:
            # Create prompt with context
            prompt = f"""Based on the following text extracted from a PDF:

{extracted_text}

Question: {question}

Please provide a clear and helpful answer based on the content above."""

            self.response_display.delete('1.0', tk.END)
            self.response_display.insert('1.0', "Getting response from Perplexity...")
            self.root.update()
            
            # Send to Perplexity
            api_key = self.api_keys['perplexity_api_key']
            response = send_prompt_to_perplexity(prompt, api_key, search_enabled=True)
            
            # Display response
            self.response_display.delete('1.0', tk.END)
            self.response_display.insert('1.0', response)
            
            # Clear question for next use
            self.question_entry.delete(0, tk.END)
            
            # Add to session notes
            self.session_notes.append({
                "timestamp": datetime.now().isoformat(),
                "page": self.current_page + 1,
                "question": question,
                "text": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
                "response": response[:500] + "..." if len(response) > 500 else response
            })
            
        except Exception as e:
            self.response_display.delete('1.0', tk.END)
            self.response_display.insert('1.0', f"Error: {e}")
            messagebox.showerror("API Error", f"Failed to get response: {e}")
    
    def generate_suggested_questions(self):
        """Generate suggested questions about the extracted text using sonar"""
        extracted_text = self.text_display.get('1.0', tk.END).strip()
        
        if not extracted_text or extracted_text == "No text found in selected region.":
            messagebox.showwarning("No Text", "Please extract text first.")
            return
        
        if 'perplexity' not in self.available_apis:
            messagebox.showerror("API Error", "Perplexity API key not available.")
            return
        
        try:
            # Create prompt to generate suggested questions
            prompt = f"""Based on the following text extracted from a PDF, generate exactly 5 relevant and insightful questions that would help someone understand the key concepts, important details, or implications of this content:

{extracted_text}

Please provide:
1. Questions that focus on the main concepts
2. Questions that explore deeper understanding
3. Questions that might connect to broader topics

Format your response EXACTLY as follows (one question per line, no numbering):
What are the key concepts discussed in this text?
How does this relate to broader theoretical frameworks?
What are the practical implications of these ideas?
What evidence supports the main arguments presented?
How might this information be applied in real-world scenarios?

IMPORTANT: Return ONLY the questions, one per line, no additional text or formatting."""

            # Show loading message
            self.response_display.delete('1.0', tk.END)
            self.response_display.insert('1.0', "Generating suggested questions...")
            self.root.update()
            
            # Send to Perplexity using sonar model for question generation
            api_key = self.api_keys['perplexity_api_key']
            response = send_prompt_to_perplexity(prompt, api_key, model="sonar", search_enabled=False)
            
            # Parse questions from response
            questions = [q.strip() for q in response.strip().split('\n') if q.strip() and not q.strip().startswith('Q') and '?' in q]
            
            if questions:
                self.suggested_questions_list = questions
                self.suggested_questions_dropdown['values'] = questions
                self.response_display.delete('1.0', tk.END)
                self.response_display.insert('1.0', f"Generated {len(questions)} suggested questions. Select one from the dropdown above.")
            else:
                self.response_display.delete('1.0', tk.END)
                self.response_display.insert('1.0', "No questions could be parsed from the response.")
            
        except Exception as e:
            self.response_display.delete('1.0', tk.END)
            self.response_display.insert('1.0', f"Error generating suggested questions: {e}")
            messagebox.showerror("API Error", f"Failed to generate suggestions: {e}")
    
    def ask_selected_question(self):
        """Ask the selected question from the dropdown with length control and model selection"""
        selected_question = self.suggested_questions_var.get().strip()
        extracted_text = self.text_display.get('1.0', tk.END).strip()
        answer_length = self.answer_length_var.get()
        
        if not selected_question:
            messagebox.showwarning("No Question Selected", "Please select a question from the dropdown.")
            return
        
        if not extracted_text or extracted_text == "No text found in selected region.":
            messagebox.showwarning("No Text", "Please extract text first.")
            return
        
        if 'perplexity' not in self.available_apis:
            messagebox.showerror("API Error", "Perplexity API key not available.")
            return
        
        try:
            # Determine model and length instruction based on selection
            if "Short" in answer_length:
                model = "sonar"
                length_instruction = "Please provide a concise answer in less than 250 tokens (about 2-3 sentences)."
            else:
                model = "sonar-reasoning"
                if "Medium" in answer_length:
                    length_instruction = "Please provide a detailed answer in 250-500 tokens (about 1-2 paragraphs)."
                elif "Long" in answer_length:
                    length_instruction = "Please provide a comprehensive answer in 500-1000 tokens (about 3-4 paragraphs)."
                else:  # Comprehensive
                    length_instruction = "Please provide a thorough, comprehensive answer with detailed explanations, examples, and context (1000+ tokens)."
            
            # Create prompt with context and length instruction
            prompt = f"""Based on the following text extracted from a PDF:

{extracted_text}

Question: {selected_question}

{length_instruction} Base your answer on the content above and use web search to find additional context and examples if helpful."""

            self.response_display.delete('1.0', tk.END)
            model_display = "sonar" if model == "sonar" else "sonar-reasoning"
            self.response_display.insert('1.0', f"Getting {answer_length.lower()} response using {model_display}...")
            self.root.update()
            
            # Send to Perplexity using selected model
            api_key = self.api_keys['perplexity_api_key']
            response = send_prompt_to_perplexity(prompt, api_key, model=model, search_enabled=True)
            
            # Display response
            self.response_display.delete('1.0', tk.END)
            self.response_display.insert('1.0', response)
            
            # Add to session notes
            self.session_notes.append({
                "timestamp": datetime.now().isoformat(),
                "page": self.current_page + 1,
                "question": selected_question,
                "answer_length": answer_length,
                "model_used": model,
                "text": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
                "response": response[:500] + "..." if len(response) > 500 else response
            })
            
        except Exception as e:
            self.response_display.delete('1.0', tk.END)
            self.response_display.insert('1.0', f"Error: {e}")
            messagebox.showerror("API Error", f"Failed to get response: {e}")
    
    def on_font_size_change(self, event=None):
        """Change font size for all text widgets"""
        try:
            font_size = int(self.font_size_var.get())
            new_font = ('Arial', font_size)
            
            for widget in self.text_widgets:
                widget.config(font=new_font)
                
        except ValueError:
            pass  # Invalid font size, ignore
    
    def update_status(self, message):
        """Update the status label"""
        self.status_label.config(text=message)

def main():
    """Main function to run the application"""
    app = SimpleInteractivePDFHighlighter()
    app.run()

if __name__ == "__main__":
    main()