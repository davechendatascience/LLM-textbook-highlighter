import fitz  # PyMuPDF
from nltk.tokenize import sent_tokenize
from collections import defaultdict

def extract_sentences_and_chunks(pdf_path, chunk_size=40):
    """
    Extract sentences and map them to grouped word bounding boxes from the PDF,
    returning sentence chunks for LLM and a page_word_map for annotation/highlighting.
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
            print(w)
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
                while idx_pointer < len(words):
                    if words[idx_pointer]["text"] == word:
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
    # Assumes word_list is a list of dicts as produced above
    sentence_words = [word_list[i] for i in word_indices]
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

def highlight_sentences_in_pdf(pdf_path, highlighted_sents, page_word_map, output_path, color=(1, 1, 0)):
    """
    Add rectangle highlights for the specified sentences using PyMuPDF.
    color: tuple of (r, g, b) with floats 0-1 (e.g. (1,1,0)=yellow), opacity 0.2 for highlight effect.
    """
    doc = fitz.open(pdf_path)
    for sent in highlighted_sents:
        page_num = sent['page_num']
        indices = sent['word_indices']
        words = page_word_map.get(page_num, [])
        bboxes = get_sentence_bboxes(words, indices, line_tol=2, margin=1)
        page = doc[page_num]
        for bbox in bboxes:
            x0, y0, x1, y1 = bbox
            rect = fitz.Rect(x0, y0, x1, y1)
            annot = page.add_rect_annot(rect)
            annot.set_colors(stroke=color, fill=color)
            annot.set_opacity(0.2)
            annot.update()
    doc.save(output_path)
