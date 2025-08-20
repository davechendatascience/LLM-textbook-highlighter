# highlight_utils.py

from keybert import KeyBERT
import requests
from llm import send_prompt_to_perplexity

def extract_topics_from_textbook(text, num_topics=5):
    """Extracts topics from a textbook chunk using KeyBERT."""
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(
        text, keyphrase_ngram_range=(1,3), stop_words='english', top_n=num_topics)
    topics = [kw[0] for kw in keywords]
    return topics

def search_web_perplexity(query, api_key):
    results = send_prompt_to_perplexity(query, api_key, search_enabled=True)
    return results
