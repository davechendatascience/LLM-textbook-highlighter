from utils import *
from llm import *
import json
from highlight_utils import *

if __name__ == "__main__":
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)
    api_key = secrets['perplexity_api_key']

    from tkinter import Tk, filedialog
    root = Tk(); root.withdraw()
    file_path = filedialog.askopenfilename()
    root.withdraw()
    output_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                               filetypes=[("PDF files", "*.pdf")],
                                               title="Save PDF as")

    if file_path:
        sentences, chunks, page_word_map = extract_sentences_and_chunks(file_path, chunk_size=100)

        all_highlights = []
        print(f"total chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            prompt = build_contextual_highlight_prompt(chunk)
            llm_output = send_prompt_to_perplexity(prompt, api_key, model="sonar-pro", search_enabled=True)
            highlighted_sents = parse_llm_highlight_indices(llm_output, chunk)
            all_highlights.extend(highlighted_sents)
            print("Processed Percentage:", int((i+1) / len(chunks) * 100), "%")
        print("Highlighting Completed!")

        if output_path:
            highlight_sentences_in_pdf(file_path, all_highlights, page_word_map, output_path)
            print(f"PDF will be saved to: {output_path}")
        else:
            print("Save operation cancelled.")
