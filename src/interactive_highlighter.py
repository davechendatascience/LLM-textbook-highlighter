#!/usr/bin/env python3
"""
Interactive PDF Highlighter with GUI
Allows users to select pages, highlight regions, and get LLM explanations
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

from llm import send_prompt_to_gemini, send_prompt_to_perplexity
from config import load_secrets, get_available_apis, DEFAULT_SETTINGS
from pdf_processor import PDFProcessor
from hybrid_ocr_processor import HybridOCRProcessor

class InteractivePDFHighlighter:
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
        self.root.title("Interactive PDF Highlighter")
        self.root.geometry(f"{DEFAULT_SETTINGS['window_width']}x{DEFAULT_SETTINGS['window_height']}")
        
        # PDF and session state
        self.pdf_doc = None
        self.current_page = 0
        self.pdf_path = ""
        self.session_notes = []
        self.highlights = []
        
        # Highlight selection state
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        self.is_selecting = False
        
        # LLM configuration
        self.api_keys = load_secrets()
        self.available_apis = get_available_apis()
        
        # PDF processor with advanced extraction
        self.pdf_processor = PDFProcessor(use_advanced_extraction=True)
        
        # Hybrid OCR processor for enhanced text and math extraction
        self.hybrid_ocr_processor = HybridOCRProcessor()
        self.use_hybrid_ocr = False  # Default to traditional extraction
        
        # UI scaling factors (image to PDF coordinate conversion)
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.image_width = 800
        self.image_height = 600
        
        self.setup_ui()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()
    
    def load_api_keys(self):
        """Load API keys from secrets.json (deprecated - now using config.py)"""
        # This method is now handled by config.py
        pass
    
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
        
        # Right panel - Notes and Q&A
        self.setup_notes_panel(paned)
    
    def setup_toolbar(self, parent):
        """Setup the top toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # File operations
        ttk.Button(toolbar, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save Session", command=self.save_session).pack(side=tk.LEFT, padx=5)
        
        # Page navigation
        ttk.Label(toolbar, text="Page:").pack(side=tk.LEFT, padx=(20, 5))
        self.page_var = tk.StringVar()
        self.page_combo = ttk.Combobox(toolbar, textvariable=self.page_var, width=5, state="readonly")
        self.page_combo.pack(side=tk.LEFT, padx=5)
        self.page_combo.bind('<<ComboboxSelected>>', self.on_page_change)
        
        ttk.Button(toolbar, text="◀ Prev", command=self.prev_page).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Next ▶", command=self.next_page).pack(side=tk.LEFT, padx=5)
        
        # Hybrid OCR toggle
        self.ocr_var = tk.BooleanVar(value=False)
        ocr_frame = ttk.Frame(toolbar)
        ocr_frame.pack(side=tk.LEFT, padx=(20, 5))
        
        ttk.Label(ocr_frame, text="Hybrid OCR:").pack(side=tk.LEFT, padx=(0, 2))
        ocr_check = ttk.Checkbutton(ocr_frame, variable=self.ocr_var, command=self.toggle_ocr)
        ocr_check.pack(side=tk.LEFT)
        
        # Check OCR availability
        ocr_available = (self.hybrid_ocr_processor.general_ocr is not None)
        math_ocr_available = (self.hybrid_ocr_processor.math_processor and self.hybrid_ocr_processor.math_model)
        
        if not ocr_available:
            ocr_check.configure(state='disabled')
            ttk.Label(ocr_frame, text="(not available)", foreground='gray').pack(side=tk.LEFT, padx=(2, 0))
        elif math_ocr_available:
            ttk.Label(ocr_frame, text="(General + Math)", foreground='green').pack(side=tk.LEFT, padx=(2, 0))
        else:
            ttk.Label(ocr_frame, text="(General only)", foreground='orange').pack(side=tk.LEFT, padx=(2, 0))
        
        # Status
        self.status_label = ttk.Label(toolbar, text="No PDF loaded")
        self.status_label.pack(side=tk.RIGHT, padx=10)
    
    def setup_pdf_viewer(self, parent):
        """Setup the PDF viewer panel"""
        pdf_frame = ttk.LabelFrame(parent, text="PDF Viewer", padding=10)
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(pdf_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.pdf_canvas = tk.Canvas(canvas_frame, bg='white', width=self.image_width, height=self.image_height)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.pdf_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.pdf_canvas.xview)
        
        self.pdf_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for canvas and scrollbars
        self.pdf_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)
        
        # Mouse events for highlighting
        self.pdf_canvas.bind("<Button-1>", self.on_mouse_down)
        self.pdf_canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.pdf_canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # Instructions
        instructions = ttk.Label(pdf_frame, text="Click and drag to select text regions. Enable Hybrid OCR for better math formula extraction.")
        instructions.pack(pady=(10, 0))
        
        parent.add(pdf_frame, weight=2)
    
    def setup_notes_panel(self, parent):
        """Setup the notes and Q&A panel"""
        notes_frame = ttk.LabelFrame(parent, text="Highlights & Notes", padding=10)
        
        # Notebook for tabs
        notebook = ttk.Notebook(notes_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Current highlight tab
        highlight_tab = ttk.Frame(notebook)
        notebook.add(highlight_tab, text="Current Highlight")
        self.setup_highlight_tab(highlight_tab)
        
        # Session notes tab
        notes_tab = ttk.Frame(notebook)
        notebook.add(notes_tab, text="Session Notes")
        self.setup_notes_tab(notes_tab)
        
        parent.add(notes_frame, weight=1)
    
    def setup_highlight_tab(self, parent):
        """Setup the current highlight analysis tab"""
        # Extracted text display
        ttk.Label(parent, text="Selected Text:").pack(anchor=tk.W)
        self.selected_text = scrolledtext.ScrolledText(parent, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.selected_text.pack(fill=tk.X, pady=(0, 10))
        
        # Suggested questions section
        question_frame = ttk.LabelFrame(parent, text="Questions", padding=5)
        question_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Generate suggestions button
        suggest_frame = ttk.Frame(question_frame)
        suggest_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(suggest_frame, text="🤔 Generate Question Ideas", 
                  command=self.generate_suggested_questions).pack(side=tk.LEFT)
        
        # Suggested questions dropdown
        ttk.Label(suggest_frame, text="Suggested:").pack(side=tk.LEFT, padx=(10, 5))
        self.suggested_questions = []
        self.suggested_var = tk.StringVar()
        self.suggested_combo = ttk.Combobox(suggest_frame, textvariable=self.suggested_var, 
                                          state="readonly", width=40)
        self.suggested_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.suggested_combo.bind('<<ComboboxSelected>>', self.on_suggestion_selected)
        
        # Custom question input
        ttk.Label(question_frame, text="Or ask your own question:").pack(anchor=tk.W, pady=(5, 0))
        self.question_entry = scrolledtext.ScrolledText(question_frame, height=3, wrap=tk.WORD)
        self.question_entry.pack(fill=tk.X, pady=(2, 0))
        
        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Explain Text", command=self.explain_text).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Ask Question", command=self.ask_question).pack(side=tk.LEFT, padx=5)
        
        # Web search option
        self.use_web_search = tk.BooleanVar()
        ttk.Checkbutton(button_frame, text="Use Web Search", variable=self.use_web_search).pack(side=tk.RIGHT)
        
        # Response display
        ttk.Label(parent, text="AI Response:").pack(anchor=tk.W)
        self.response_text = scrolledtext.ScrolledText(parent, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.response_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_notes_tab(self, parent):
        """Setup the session notes tab"""
        # Notes list
        notes_list_frame = ttk.Frame(parent)
        notes_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.notes_tree = ttk.Treeview(notes_list_frame, columns=('Time', 'Text', 'Response'), show='headings', height=15)
        self.notes_tree.heading('Time', text='Time')
        self.notes_tree.heading('Text', text='Highlighted Text')
        self.notes_tree.heading('Response', text='AI Response')
        
        self.notes_tree.column('Time', width=100)
        self.notes_tree.column('Text', width=200)
        self.notes_tree.column('Response', width=300)
        
        notes_scrollbar = ttk.Scrollbar(notes_list_frame, orient=tk.VERTICAL, command=self.notes_tree.yview)
        self.notes_tree.configure(yscrollcommand=notes_scrollbar.set)
        
        self.notes_tree.grid(row=0, column=0, sticky="nsew")
        notes_scrollbar.grid(row=0, column=1, sticky="ns")
        
        notes_list_frame.grid_columnconfigure(0, weight=1)
        notes_list_frame.grid_rowconfigure(0, weight=1)
        
        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="Export Notes", command=self.export_notes).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="Clear Session", command=self.clear_session).pack(side=tk.LEFT, padx=10)
    
    def open_pdf(self):
        """Open and load a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.pdf_doc = fitz.open(file_path)
                self.pdf_path = file_path
                self.current_page = 0
                
                # Update page selector  
                page_count = self.pdf_processor.get_page_count(file_path)
                page_list = [str(i+1) for i in range(page_count)]
                self.page_combo['values'] = page_list
                self.page_combo.set("1")
                
                # Load first page
                self.load_page()
                self.status_label.config(text=f"Loaded: {os.path.basename(file_path)} ({page_count} pages)")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF: {e}")
    
    def load_page(self):
        """Load and display the current page"""
        if not self.pdf_doc:
            return
        
        try:
            page = self.pdf_doc[self.current_page]
            
            # Render page as image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            # Convert to PIL Image and then to PhotoImage
            from io import BytesIO
            pil_image = Image.open(BytesIO(img_data))
            
            # Calculate scaling factors for coordinate conversion
            pdf_rect = page.rect
            self.scale_x = pdf_rect.width / pil_image.width
            self.scale_y = pdf_rect.height / pil_image.height
            
            print(f"DEBUG: PDF rect: {pdf_rect}")
            print(f"DEBUG: PIL image size: {pil_image.width} x {pil_image.height}")
            print(f"DEBUG: Scale factors: x={self.scale_x}, y={self.scale_y}")
            
            # Resize if too large
            max_width, max_height = 800, 1000
            if pil_image.width > max_width or pil_image.height > max_height:
                pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                # Recalculate scaling
                self.scale_x = pdf_rect.width / pil_image.width
                self.scale_y = pdf_rect.height / pil_image.height
            
            self.pdf_image = ImageTk.PhotoImage(pil_image)
            
            # Update canvas
            self.pdf_canvas.delete("all")
            self.pdf_canvas.configure(scrollregion=(0, 0, pil_image.width, pil_image.height))
            self.pdf_canvas.create_image(0, 0, anchor=tk.NW, image=self.pdf_image)
            
            # Clear selection
            self.clear_selection()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load page: {e}")
    
    def on_page_change(self, event=None):
        """Handle page selection change"""
        if self.page_var.get():
            try:
                new_page = int(self.page_var.get()) - 1
                if 0 <= new_page < len(self.pdf_doc):
                    self.current_page = new_page
                    self.load_page()
            except ValueError:
                pass
    
    def prev_page(self):
        """Go to previous page"""
        if self.pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self.page_combo.set(str(self.current_page + 1))
            self.load_page()
    
    def next_page(self):
        """Go to next page"""
        if self.pdf_doc and self.current_page < len(self.pdf_doc) - 1:
            self.current_page += 1
            self.page_combo.set(str(self.current_page + 1))
            self.load_page()
    
    def on_mouse_down(self, event):
        """Handle mouse down for selection start"""
        # Clear any existing selection rectangle only
        self.clear_selection(clear_coordinates=False)
        # Now set the new selection start
        self.selection_start = (self.pdf_canvas.canvasx(event.x), self.pdf_canvas.canvasy(event.y))
        self.is_selecting = True
        print(f"Mouse down at: {self.selection_start}")  # Debug
    
    def on_mouse_drag(self, event):
        """Handle mouse drag for selection"""
        if not self.is_selecting or not self.selection_start:
            return
        
        current_pos = (self.pdf_canvas.canvasx(event.x), self.pdf_canvas.canvasy(event.y))
        print(f"Mouse dragging to: {current_pos}")  # Debug
        
        # Remove previous selection rectangle
        if self.selection_rect:
            self.pdf_canvas.delete(self.selection_rect)
        
        # Draw selection rectangle
        x1, y1 = self.selection_start
        x2, y2 = current_pos
        self.selection_rect = self.pdf_canvas.create_rectangle(
            x1, y1, x2, y2, outline="red", width=2, fill="", dash=(5, 5)
        )
    
    def on_mouse_up(self, event):
        """Handle mouse up for selection end"""
        if not self.is_selecting:
            return
        
        self.selection_end = (self.pdf_canvas.canvasx(event.x), self.pdf_canvas.canvasy(event.y))
        self.is_selecting = False
        print(f"Mouse up at: {self.selection_end}")  # Debug
        
        # Extract text from selection
        self.extract_selected_text()
    
    def clear_selection(self, clear_coordinates=True):
        """Clear current selection"""
        if self.selection_rect:
            self.pdf_canvas.delete(self.selection_rect)
            self.selection_rect = None
        
        if clear_coordinates:
            self.selection_start = None
            self.selection_end = None
        
        # Clear text displays
        self.selected_text.config(state=tk.NORMAL)
        self.selected_text.delete(1.0, tk.END)
        self.selected_text.config(state=tk.DISABLED)
        
        # Clear suggested questions
        self.suggested_questions = []
        self.suggested_combo['values'] = []
        self.suggested_combo.set("")
        
        # Clear response text
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete(1.0, tk.END)
        self.response_text.config(state=tk.DISABLED)
    
    def extract_selected_text(self):
        """Extract text from the selected region"""
        if not self.selection_start or not self.selection_end or not self.pdf_doc:
            return
        
        try:
            # Convert image coordinates to PDF coordinates
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            
            # Debug: Print coordinate conversion details
            print(f"Image coordinates: ({x1}, {y1}) to ({x2}, {y2})")
            print(f"Scale factors: scale_x={self.scale_x}, scale_y={self.scale_y}")
            
            # Ensure proper ordering
            pdf_x1 = min(x1, x2) * self.scale_x
            pdf_y1 = min(y1, y2) * self.scale_y
            pdf_x2 = max(x1, x2) * self.scale_x
            pdf_y2 = max(y1, y2) * self.scale_y
            
            print(f"PDF coordinates: ({pdf_x1}, {pdf_y1}) to ({pdf_x2}, {pdf_y2})")
            
            # Create selection rectangle in PDF coordinates
            selection_rect = fitz.Rect(pdf_x1, pdf_y1, pdf_x2, pdf_y2)
            
            # SOLUTION: Instead of precise clipping, extract text by finding lines that intersect
            page = self.pdf_doc[self.current_page]
            
            # Use hybrid OCR for smart text extraction
            text = self.extract_text_with_hybrid_ocr(page, selection_rect)
            
            if text:
                # Display extracted text
                self.selected_text.config(state=tk.NORMAL)
                self.selected_text.delete(1.0, tk.END)
                self.selected_text.insert(1.0, text)
                self.selected_text.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("No Text", "No text found in selected region")
                self.clear_selection()
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not extract text: {e}")
            self.clear_selection()
    
    def extract_text_with_hybrid_ocr(self, page, rect):
        """Extract text using hybrid OCR approach"""
        try:
            print(f"DEBUG: Extracting from rect: {rect}")
            
            if self.use_hybrid_ocr and self.hybrid_ocr_processor.general_ocr:
                # Use hybrid OCR extraction
                result = self.hybrid_ocr_processor.extract_region_with_hybrid_ocr(page, rect)
                text = result.get('text', '')
                method = result.get('method', 'unknown')
                confidence = result.get('confidence', 0)
                
                print(f"DEBUG: Hybrid OCR used - Method: {method}, Confidence: {confidence}")
                print(f"DEBUG: Result: '{text[:100]}...' ({len(text)} chars)")
                
                if 'math_regions_found' in result:
                    print(f"DEBUG: Math regions enhanced: {result['math_regions_found']}")
                
                return text
            else:
                # Use standard fitz extraction
                text = page.get_text("text", clip=rect).strip()
                print(f"DEBUG: Using traditional fitz extraction")
                print(f"DEBUG: Result: '{text[:100]}...' ({len(text)} chars)")
                return text
            
        except Exception as e:
            print(f"Error in hybrid text extraction: {e}")
            # Fallback to regular extraction
            try:
                text = page.get_text("text", clip=rect).strip()
                print(f"DEBUG: Fallback extraction successful")
                return text
            except Exception as fallback_error:
                print(f"Error in fallback extraction: {fallback_error}")
                return ""
    
    def toggle_ocr(self):
        """Toggle hybrid OCR usage for text extraction"""
        self.use_hybrid_ocr = self.ocr_var.get()
        status = "enabled" if self.use_hybrid_ocr else "disabled"
        print(f"DEBUG: Hybrid OCR extraction {status}")
        
        # Update status
        if self.use_hybrid_ocr and self.hybrid_ocr_processor.general_ocr:
            if self.hybrid_ocr_processor.math_processor:
                self.status_label.config(text="Hybrid OCR enabled (General + Math)")
            else:
                self.status_label.config(text="Hybrid OCR enabled (General only)")
        else:
            self.status_label.config(text="Traditional extraction")
            if self.use_hybrid_ocr:
                print("WARNING: Hybrid OCR requested but not available")
    
    def minimal_symbol_fix(self, text):
        """Apply only minimal symbol fixing for clear PDF corruption artifacts"""
        if not text:
            return text
        
        # Only fix clear corruption patterns, not legitimate words
        corruption_fixes = {
            # Common PDF encoding corruption
            '�P': '≠',   # Only if clearly a corrupted not-equal symbol
            '��': '×',   # Corrupted multiplication
            '�': '',     # Remove standalone corruption characters
            
            # Only fix mathematical operators that are clearly corrupted
            # DO NOT convert "sum" to "Σ" - "sum" is often the correct word
        }
        
        fixed_text = text
        for corrupted, correct in corruption_fixes.items():
            fixed_text = fixed_text.replace(corrupted, correct)
        
        return fixed_text
    
    def get_selected_text(self):
        """Get the currently selected text"""
        return self.selected_text.get(1.0, tk.END).strip()
    
    def get_question(self):
        """Get the user's question"""
        return self.question_entry.get(1.0, tk.END).strip()
    
    def generate_suggested_questions(self):
        """Generate AI-suggested questions based on selected text"""
        selected_text = self.get_selected_text()
        if not selected_text:
            messagebox.showwarning("No Selection", "Please select some text first")
            return
        
        try:
            # Show loading in combo
            self.suggested_combo['values'] = ["Generating questions..."]
            self.suggested_combo.set("Generating questions...")
            self.root.update()
            
            # Create prompt for question generation
            prompt = f"""Based on the following text, generate 5-7 thoughtful questions that would help someone better understand the content. Include different types of questions: definition questions, explanation questions, application questions, and analysis questions.

Text: "{selected_text}"

Please provide only the questions, one per line, without numbering or bullet points."""
            
            # Use AI to generate questions (without web search for faster response)
            response = None
            if 'gemini_api_key' in self.api_keys:
                response = send_prompt_to_gemini(prompt, self.api_keys['gemini_api_key'], search_enabled=False)
            elif 'perplexity_api_key' in self.api_keys:
                response = send_prompt_to_perplexity(prompt, self.api_keys['perplexity_api_key'], search_enabled=False)
            else:
                messagebox.showerror("No API Key", "Please add gemini_api_key or perplexity_api_key to secrets.json")
                return
            
            # Parse questions from response
            questions = []
            for line in response.strip().split('\n'):
                question = line.strip()
                # Clean up the question (remove numbers, bullets, etc.)
                question = question.lstrip('0123456789.-• ')
                if question and question.endswith('?'):
                    questions.append(question)
            
            if questions:
                self.suggested_questions = questions
                self.suggested_combo['values'] = ["Select a question..."] + questions
                self.suggested_combo.set("Select a question...")
                print(f"Generated {len(questions)} questions")  # Debug
            else:
                self.suggested_combo['values'] = ["No questions generated"]
                self.suggested_combo.set("No questions generated")
                
        except Exception as e:
            self.suggested_combo['values'] = ["Error generating questions"]
            self.suggested_combo.set("Error generating questions")
            print(f"Error generating questions: {e}")
    
    def on_suggestion_selected(self, event=None):
        """Handle selection of a suggested question"""
        selected = self.suggested_var.get()
        if selected and selected not in ["Select a question...", "Generating questions...", 
                                       "No questions generated", "Error generating questions"]:
            # Put the selected question in the text area
            self.question_entry.delete(1.0, tk.END)
            self.question_entry.insert(1.0, selected)
            print(f"Selected question: {selected}")  # Debug
    
    def explain_text(self):
        """Get AI explanation of selected text"""
        selected_text = self.get_selected_text()
        if not selected_text:
            messagebox.showwarning("No Selection", "Please select some text first")
            return
        
        question = f"Explain this text in detail: {selected_text}"
        self.send_llm_request(question, selected_text)
    
    def ask_question(self):
        """Ask a custom question about selected text"""
        selected_text = self.get_selected_text()
        user_question = self.get_question()
        
        if not selected_text:
            messagebox.showwarning("No Selection", "Please select some text first")
            return
        
        if not user_question:
            messagebox.showwarning("No Question", "Please enter a question")
            return
        
        question = f"Given this text: '{selected_text}'\n\nQuestion: {user_question}"
        self.send_llm_request(question, selected_text)
    
    def send_llm_request(self, question, selected_text):
        """Send request to LLM and display response"""
        try:
            # Show loading
            self.response_text.config(state=tk.NORMAL)
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(1.0, "Getting AI response...")
            self.response_text.config(state=tk.DISABLED)
            self.root.update()
            
            use_search = self.use_web_search.get()
            
            # Try Gemini first, then Perplexity
            response = None
            if 'gemini_api_key' in self.api_keys:
                response = send_prompt_to_gemini(question, self.api_keys['gemini_api_key'], search_enabled=use_search)
            elif 'perplexity_api_key' in self.api_keys:
                response = send_prompt_to_perplexity(question, self.api_keys['perplexity_api_key'], search_enabled=use_search)
            else:
                messagebox.showerror("No API Key", "Please add gemini_api_key or perplexity_api_key to secrets.json")
                return
            
            # Display response
            self.response_text.config(state=tk.NORMAL)
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(1.0, response)
            self.response_text.config(state=tk.DISABLED)
            
            # Save to session notes
            self.add_to_session_notes(selected_text, question, response)
            
        except Exception as e:
            self.response_text.config(state=tk.NORMAL)
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(1.0, f"Error: {e}")
            self.response_text.config(state=tk.DISABLED)
    
    def add_to_session_notes(self, text, question, response):
        """Add Q&A to session notes"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        note = {
            'time': timestamp,
            'page': self.current_page + 1,
            'text': text[:100] + "..." if len(text) > 100 else text,
            'question': question,
            'response': response
        }
        self.session_notes.append(note)
        
        # Update notes tree
        self.notes_tree.insert('', 'end', values=(timestamp, note['text'], response[:100] + "..."))
    
    def save_session(self):
        """Save current session to file"""
        if not self.session_notes:
            messagebox.showwarning("No Notes", "No notes to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save session notes",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                session_data = {
                    'pdf_path': self.pdf_path,
                    'timestamp': datetime.now().isoformat(),
                    'notes': self.session_notes
                }
                
                with open(file_path, 'w') as f:
                    json.dump(session_data, f, indent=2)
                
                messagebox.showinfo("Success", "Session saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save session: {e}")
    
    def export_notes(self):
        """Export notes to text file"""
        if not self.session_notes:
            messagebox.showwarning("No Notes", "No notes to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export notes",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"PDF Highlighter Session Notes\n")
                    f.write(f"PDF: {os.path.basename(self.pdf_path)}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, note in enumerate(self.session_notes, 1):
                        f.write(f"Note {i} - Page {note['page']} - {note['time']}\n")
                        f.write(f"Selected Text: {note['text']}\n")
                        f.write(f"Question: {note['question']}\n")
                        f.write(f"AI Response: {note['response']}\n")
                        f.write("-" * 30 + "\n\n")
                
                messagebox.showinfo("Success", "Notes exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export notes: {e}")
    
    def clear_session(self):
        """Clear all session notes"""
        if messagebox.askyesno("Clear Session", "Are you sure you want to clear all notes?"):
            self.session_notes.clear()
            # Clear tree
            for item in self.notes_tree.get_children():
                self.notes_tree.delete(item)


def main():
    root = tk.Tk()
    app = InteractivePDFHighlighter(root)
    root.mainloop()


if __name__ == "__main__":
    main()