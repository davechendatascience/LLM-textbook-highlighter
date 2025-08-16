import requests

def send_prompt_to_perplexity(prompt, api_key, model="sonar-pro"):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("API Error:", response.text)
        raise err
    return response.json()['choices'][0]['message']['content']