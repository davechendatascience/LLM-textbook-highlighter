import fitz  # PyMuPDF
import re
import unicodedata
from nltk.tokenize import sent_tokenize
from collections import defaultdict

def normalize_word(word):
    """
    Normalize a word for robust matching: lowercase, strip leading/trailing punctuation,
    remove diacritics (accents), and keep only alphanumeric + internal punctuation.
    """
    word_norm = unicodedata.normalize('NFKD', word)
    word_norm = word_norm.encode('ascii', 'ignore').decode("ascii")
    word_norm = re.sub(r"^\W+|\W+$", "", word_norm.lower())
    return word_norm

def extract_sentences_and_chunks(pdf_path, chunk_size=40):
    """
    Extract sentences and map them to grouped word bounding boxes from the PDF,
    returning sentence chunks for LLM and a page_word_map for annotation/highlighting.
    Robust to special characters and punctuation.
    """
    doc = fitz.open(pdf_path)
    page_word_map = {}
    sentences = []
    global_idx = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        words_raw = page.get_text("words")  # list of (x0, y0, x1, y1, word, block_no, line_no, word_no)
        words = []
        for w in words_raw:
            words.append({
                "text": w[4],
                "x0": w[0],
                "y0": w[1],
                "x1": w[2],
                "y1": w[3],
                "block_no": w[5],
                "line_no": w[6],
                "word_no": w[7],
            })
        page_word_map[page_num] = words
        if not words:
            continue
        page_text = " ".join(w["text"] for w in words)
        sents = sent_tokenize(page_text)
        word_pointer = 0

        for s in sents:
            s_words = s.split()
            indices = []
            idx_pointer = word_pointer
            for word in s_words:
                target = normalize_word(word)
                while idx_pointer < len(words):
                    source = normalize_word(words[idx_pointer]["text"])
                    if source == target:
                        indices.append(idx_pointer)
                        idx_pointer += 1
                        break
                    idx_pointer += 1
            if indices:
                sentences.append({
                    "global_idx": global_idx,
                    "page_num": page_num,
                    "sentence": s,
                    "word_indices": indices
                })
                global_idx += 1
                word_pointer = idx_pointer

    # Chunk sentences for LLM prompt
    chunks = []
    for start in range(0, len(sentences), chunk_size):
        chunks.append(sentences[start:start+chunk_size])
    return sentences, chunks, page_word_map

def get_sentence_bboxes(word_list, word_indices, line_tol=2, margin=1):
    # Use only valid indices to avoid IndexError
    sentence_words = [word_list[i] for i in word_indices if 0 <= i < len(word_list)]
    if not sentence_words:
        return []
    from collections import defaultdict
    line_groups = defaultdict(list)
    for w in sentence_words:
        line_key = round(w["y0"] / line_tol)
        line_groups[line_key].append(w)
    bboxes = []
    for group in line_groups.values():
        x0 = min(w["x0"] for w in group) - margin
        x1 = max(w["x1"] for w in group) + margin
        y0 = min(w["y0"] for w in group) - margin
        y1 = max(w["y1"] for w in group) + margin
        bboxes.append((x0, y0, x1, y1))
    return bboxes

def highlight_sentences_in_pdf(pdf_path, highlight_groups, page_word_map, output_path, color=(1, 1, 0)):
    doc = fitz.open(pdf_path)
    for group in highlight_groups:
        chunk = group["chunk"]
        explanation = group.get('explanation', '')
        indices = group["group_indices"]
        note_added = False
        for idx_n, idx in enumerate(indices):
            sentence = chunk[idx]
            page_num = sentence["page_num"]  # use per-sentence page number
            words = page_word_map.get(page_num, [])
            sent_word_indices = sentence['word_indices']
            bboxes = get_sentence_bboxes(words, sent_word_indices, line_tol=2, margin=1)
            page = doc[page_num]
            for bbox_i, bbox in enumerate(bboxes):
                x0, y0, x1, y1 = bbox
                rect = fitz.Rect(x0, y0, x1, y1)
                annot = page.add_rect_annot(rect)
                annot.set_colors(stroke=color, fill=color)
                annot.set_opacity(0.2)
                annot.update()
                if not note_added and idx_n == 0 and bbox_i == 0:
                    try:
                        note_annot = page.add_text_annot(rect.bl, explanation, icon="Comment")
                    except TypeError:
                        note_annot = page.add_text_annot(rect.bl, explanation)
                    note_annot.update()
                    note_added = True
    doc.save(output_path)
