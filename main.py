import sys
import os

# Add src and utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from utils import *
from llm import send_prompt_to_perplexity
from config import load_secrets, get_available_apis
from highlight_utils import build_contextual_highlight_prompt, parse_llm_highlight_groups
from tkinter import Tk, filedialog

if __name__ == "__main__":
    secrets = load_secrets()
    available_apis = get_available_apis()
    
    if not available_apis or 'perplexity' not in available_apis:
        raise ValueError("No Perplexity API key found. Add 'perplexity_api_key' to secrets.json")
    
    api_key = secrets['perplexity_api_key']
    print("Using Perplexity API")

    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.withdraw()
    output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Save PDF as")

    if file_path:
        sentences, chunks, page_word_map = extract_sentences_and_chunks(file_path, chunk_size=100)
        all_groups = []
        print(f"Total chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            prompt = build_contextual_highlight_prompt(chunk)
            # Web search disabled by default for cost savings - textbook content is self-contained
            use_web_search = False  # Set to True if you need real-time web context
            
            llm_output = send_prompt_to_perplexity(prompt, api_key, search_enabled=use_web_search)
            group_highlights = parse_llm_highlight_groups(llm_output, chunk)
            all_groups.extend(group_highlights)
            print(f"Processed chunk {i+1}/{len(chunks)} ({int((i+1)/len(chunks)*100)}%)")
        print("Annotating PDF with highlights and grouped comments...")
        if output_path:
            highlight_sentences_in_pdf(file_path, all_groups, page_word_map, output_path)
            print(f"PDF saved to: {output_path}")
        else:
            print("Save operation cancelled.")
    else:
        print("No PDF selected.")
