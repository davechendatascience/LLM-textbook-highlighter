import requests

def send_prompt_to_perplexity(prompt, api_key, model="sonar-reasoning", search_enabled=False):
    """Send prompt to Perplexity API. Uses cheaper non-search models by default for cost savings.
    Available models: llama-3.1-sonar-small-128k-online, llama-3.1-sonar-large-128k-online, sonar-pro"""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "search": search_enabled
    }
    response = requests.post(url, headers=headers, json=data, verify=False)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("API Error:", response.text)
        raise err
    result = response.json()
    # Return the full response object to access citations
    return result