import requests
from google import genai
from google.genai.types import Tool, GenerateContentConfig

def send_prompt_to_gemini(prompt, api_key, model="gemini-2.0-flash-exp", search_enabled=False):
    """Send prompt to Gemini API with optional web search grounding (disabled by default for cost savings)"""
    try:
        client = genai.Client(api_key=api_key)
        
        # Configure tools for web search if enabled
        tools = []
        if search_enabled:
            tools = [Tool(google_search={})]
        
        config = GenerateContentConfig(tools=tools) if tools else None
            
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )
        
        return response.text
        
    except Exception as err:
        print("Gemini API Error:", str(err))
        raise err

def send_prompt_to_perplexity(prompt, api_key, model="llama-3.1-sonar-small-128k-online", search_enabled=False):
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
    return response.json()['choices'][0]['message']['content']