import requests
from llm import send_prompt_to_perplexity

def build_contextual_highlight_prompt(chunk):
    segment_text = " ".join(s["sentence"] for s in chunk)
    prompt = (
        "Below is a segment from a scientific document.\n"
        "For each key concept, identify a small group of sentences (at most 2 per concept) that together best explain it. "
        "Be selective and do not include sentences that are not strictly essential. "
        "For each group, return the indices of relevant sentences (comma-separated) and a concise explanation, as follows: indices: explanation\n"
        "Example:\n2,3: defines DNA\n5,6: details replication mechanism\n\n"
        f"Segment context:\n{segment_text.strip()}\n\n"
        "Numbered sentences:\n" +
        "\n".join([f"{i+1}: {s['sentence']}" for i, s in enumerate(chunk)])
    )
    return prompt

def parse_llm_highlight_groups(llm_output, chunk):
    import re
    results = []
    pattern = r'([0-9,\s]+):\s*([^\n]+)'
    for line in llm_output.splitlines():
        m = re.match(pattern, line.strip())
        if m:
            indices_str, expl = m.groups()
            indices = [int(x.strip())-1 for x in indices_str.split(",") if x.strip().isdigit()]
            if not indices:
                continue
            # Each group contains all sentence data and explanation
            word_indices = []
            for i in indices:
                if 0 <= i < len(chunk):
                    word_indices += chunk[i]['word_indices']
            results.append({
                "group_indices": indices,
                "page_num": chunk[indices[0]]['page_num'],
                "chunk": chunk,
                "word_indices_grouped": word_indices,
                "explanation": expl.strip()
            })
    return results

def search_web_perplexity(query, api_key):
    results = send_prompt_to_perplexity(query, api_key, search_enabled=True)
    return results
