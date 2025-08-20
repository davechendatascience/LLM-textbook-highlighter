# highlight_utils.py

# from keybert import KeyBERT
import requests
from llm import send_prompt_to_perplexity

# def extract_topics_from_textbook(text, num_topics=5):
#     """Extracts topics from a textbook chunk using KeyBERT."""
#     kw_model = KeyBERT()
#     keywords = kw_model.extract_keywords(
#         text, keyphrase_ngram_range=(1,3), stop_words='english', top_n=num_topics)
#     topics = [kw[0] for kw in keywords]
#     return topics

def search_web_perplexity(query, api_key):
    results = send_prompt_to_perplexity(query, api_key, search_enabled=True)
    return results

def build_contextual_highlight_prompt(chunk):
    # chunk: list of sentence dicts
    segment_text = " ".join(s["sentence"] for s in chunk)
    prompt = (
        "Below is a segment from a scientific document. "
        "First I want you to identify the key concepts in this segment. "
        "Then I want you to identify the sentences that best explain these concepts. "
        "Return the ONLY indices of those sentences as a comma-separated list (e.g., 2, 5, 7).\n\n"
        f"Segment context:\n{segment_text.strip()}\n\n"
        "Numbered sentences:\n" +
        "\n".join([f"{i+1}: {s['sentence']}" for i, s in enumerate(chunk)])
    )
    return prompt

def parse_llm_highlight_indices(llm_output, chunk):
    import re
    indices = [int(i) - 1 for i in re.findall(r'\b\d+\b', llm_output)]
    return [chunk[i] for i in indices if i >= 0 and i < len(chunk)]