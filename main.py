
from utils import *
from llm import *
from ollama import Client
import fasttext
import json

# Example usage (commented out)
if __name__ == "__main__":
    # api key
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)
    api_key = secrets['perplexity_api_key']

    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.withdraw()
    output_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Save PDF as"
    )
    if file_path:
        sentences = extract_sentences_with_indices(file_path)
        # For actual use, iterate over chunks:
        highlighted_indices = set()
        all_highlights = []

        # create the llm client
        client = Client()

        # filter unmeaningful chunks
        all_chunks = list(chunk_sentences_with_mapping(sentences, chunk_size=40))
        meaningful_chunks = [
            chunk for chunk in all_chunks if is_chunk_meaningful(chunk, min_length=250, min_sentences=4, ignore_patterns=None)
        ]
        print("total chunks:", len(all_chunks), "meaningful chunks:", len(meaningful_chunks))
        for i, chunk_with_idx in enumerate(meaningful_chunks):
            prompt = build_contextual_highlight_prompt(chunk_with_idx)
            llm_output = send_prompt_to_perplexity(prompt, api_key, model="sonar-pro")
            highlighted_meta = parse_llm_highlight_indices(llm_output, chunk_with_idx)
            all_highlights.extend(highlighted_meta)
            print("Processed Percentage:", int((i+1) / len(meaningful_chunks) * 100), "%")
        
        print("Highlighting Completed!")
        if output_path:
            # Use output_path to save your PDF
            highlight_sentences_in_pdf(file_path, all_highlights, 
                output_path)
            print(f"PDF will be saved to: {output_path}")
        else:
            print("Save operation cancelled.")
