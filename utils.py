from tkinter import Tk, filedialog
import pdfplumber
from nltk.tokenize import sent_tokenize
import fitz  # PyMuPDF
import fasttext
import re
from collections import Counter

lang_detect_model = fasttext.load_model('models/lid.176.bin')

def chinese_sentence_tokenizer(text):
    # Split by Chinese full stop, exclamation, and question marks (and keep punctuation)
    fragments = re.split(r'(。|！|\!|？|\?)', text)
    sentences = []
    for i in range(0, len(fragments)-1, 2):
        sentence = fragments[i] + fragments[i+1]
        if sentence.strip():
            sentences.append(sentence.strip())
    # Handle last fragment
    if len(fragments) % 2 != 0 and fragments[-1].strip():
        sentences.append(fragments[-1].strip())
    return sentences

def majority_vote_language(text):
    lines = [line for line in text.split('\n') if line.strip()]
    langs = [lang_detect_model.predict(line)[0][0].replace('__label__','') for line in lines]
    most_common = Counter(langs).most_common(1)
    return most_common[0][0] if most_common else None

def auto_sentence_tokenize(text, lang_detect_model):
    # majority vote the
    lang = majority_vote_language(text)
    if lang == 'zh-cn' or lang == 'zh':
        return chinese_sentence_tokenizer(text)
    else:
        # Use English or other European language tokenizer
        from nltk.tokenize import sent_tokenize
        return sent_tokenize(text)


def extract_sentences_with_indices(pdf_path):
    sentences = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                page_sentences = auto_sentence_tokenize(text, lang_detect_model=lang_detect_model)
                for idx, sent in enumerate(page_sentences):
                    # (global_index, page_number, local_index, sentence)
                    sentences.append((len(sentences)+1, page_num, idx, sent))
    return sentences  # (global index, page number, in-page index, sentence)

def build_contextual_highlight_prompt(chunk_with_idx, external_contexts=None):
    """
    Builds a prompt for an LLM to highlight the most important sentences
    in the context of the full segment.
    chunk_with_idx: [(local_idx, global_idx, page_num, local_in_page, sentence), ...]
    """
    # Concatenate all sentences in the segment for context
    segment_text = " ".join([sentence for _, _, _, _, sentence in chunk_with_idx])

    prompt = (
        "Below is a segment from a scientific document. "
        "First I want you to identify the key concepts in this segment. "
        "Then I want you to identify the sentences that best explain these concepts. "
        "Return the top 10 indices of those sentences as a comma-separated list (e.g., 2, 5, 7).\n\n"
        f"Segment context:\n{segment_text.strip()}\n\n"
    )
    if external_contexts:
        prompt += "\nRelated context from web:\n"
        for topic, snippets in external_contexts.items():
            prompt += f"Topic: {topic}\n"
            for snippet in snippets:
                prompt += f"- {snippet}\n"
    prompt += (
        "Numbered sentences:\n" +
        "\n".join([f"{local_idx}: {sentence}" for local_idx, _, _, _, sentence in chunk_with_idx])
    )
    return prompt

def parse_llm_highlight_indices(llm_output, chunk_with_idx):
    # Extract local indices from LLM response
    indices = [int(i) for i in re.findall(r'\b\d+\b', llm_output)]
    # Map back to global indices and metadata
    highlighted_meta = [
        (global_idx, page_num, local_in_page, sentence)
        for local_chunk_idx, global_idx, page_num, local_in_page, sentence in chunk_with_idx
        if local_chunk_idx in indices
    ]
    return highlighted_meta

def chunk_sentences_with_mapping(sentences, chunk_size=40):
    # sentences: list of (global, page_num, local_in_page, sentence)
    for start in range(0, len(sentences), chunk_size):
        chunk = sentences[start:start+chunk_size]
        # produce chunk list of (local_chunk_idx, global_idx, page_num, local_in_page, sentence)
        chunk_with_idx = [
            (i+1, s[0], s[1], s[2], s[3])  # local index for LLM, plus all metadata
            for i, s in enumerate(chunk)
        ]
        yield chunk_with_idx

def is_chunk_meaningful(chunk_sentences, min_length=250, min_sentences=4, ignore_patterns=None):
    text = " ".join([s[4
    ] for s in chunk_sentences])  # s[1] is the sentence
    # Basic length check
    if len(text.strip()) < min_length or len(chunk_sentences) < min_sentences:
        return False
    # Pattern-based ignoring (e.g., “References”, “Table of Contents”)
    if ignore_patterns:
        for pat in ignore_patterns:
            if pat.lower() in text.lower():
                return False
    # Extra: Check for repeated punctuation, numbers, or list-like content
    non_boilerplate = sum(
        1 for _, _, _, _, sent in chunk_sentences
        if len(sent.split()) > 3 and not sent.strip().isdigit()
    )
    if non_boilerplate/min_sentences < 0.5:
        return False
    return True

def highlight_sentences_in_pdf(pdf_path, highlighted_meta, output_path):
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    for global_idx, page_num, local_in_page, sentence in highlighted_meta:
        page = doc[page_num]
        areas = page.search_for(sentence)
        for inst in areas:
            page.add_highlight_annot(inst)
    doc.save(output_path, deflate=True)
    doc.close()
