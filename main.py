from tkinter import Tk, filedialog
import pdfplumber
from nltk.tokenize import sent_tokenize

def extract_sentences_with_indices(pdf_path):
    sentences = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                page_sentences = sent_tokenize(text)
                for idx, sent in enumerate(page_sentences):
                    # (global_index, page_number, local_index, sentence)
                    sentences.append((len(sentences)+1, page_num, idx, sent))
    return sentences  # (global index, page number, in-page index, sentence)

def chunk_sentences(sentences, chunk_size=40):
    for i in range(0, len(sentences), chunk_size):
        yield sentences[i:i+chunk_size]

def prompt_llm_for_indices(chunk):
    # Example prompt construction
    prompt = "Which sentences (by index) are most important?\n\n"
    prompt += "\n".join([f"{s[0]}: {s[1]}" for s in chunk])
    # Send to Ollama and get output (not shown, mock here):
    # Example output: "Indices: 1, 5, 7"
    return [1, 5, 7]  # Replace with actual model output parsing

import fitz  # PyMuPDF

def highlight_sentences_in_pdf(pdf_path, sentences, highlighted_indices, output_path):
    doc = fitz.open(pdf_path)
    for idx, page_num, _, sent in sentences:
        if idx in highlighted_indices:
            page = doc[page_num]
            # highlight each occurrence of the sentence string (could be optimized)
            areas = page.search_for(sent)
            for inst in areas:
                page.add_highlight_annot(inst)
    doc.save(output_path, deflate=True)
    doc.close()


# Example usage (commented out)
if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    if file_path:
        sentences = extract_sentences_with_indices(file_path)
        # For actual use, iterate over chunks:
        highlighted_indices = set()
        for chunk in chunk_sentences(sentences):
            indices = prompt_llm_for_indices(chunk)
            highlighted_indices.update(indices)

        # Example usage:
        highlight_sentences_in_pdf(
            file_path, 
            sentences, 
            highlighted_indices, 
            'highlighted_textbook.pdf'
        )
