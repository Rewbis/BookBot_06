import json
import re
import requests
from typing import Optional, Dict, Any

class OllamaClient:
    """Robust client for interacting with a local Ollama instance."""
    
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def prompt(self, system: str, user: str, temperature: float = 0.7) -> str:
        """Sends a request to Ollama and returns the raw response text."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"System: {system}\n\nUser: {user}",
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def _clean_json(self, text: str) -> Dict[str, Any]:
        """
        Deterministic cleaning of LLM output to extract JSON.
        Implements the 'Pythonic-First' strategy to avoid prompt escalation.
        """
        # 1. Strip <think> blocks (DeepSeek/Reasoning models)
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # 2. Find the first '{' and last '}'
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            json_str = text[start:end+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Attempt to clean common JSON errors (trailing commas, etc.)
                # This is a simple version; can be expanded if needed.
                try:
                    # Remove trailing commas before closing braces/brackets
                    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
                    return json.loads(json_str)
                except:
                    pass
        
        # 3. Fallback: Look for markdown code blocks
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
                
        return {"error": "Failed to parse JSON", "raw_content": text}
