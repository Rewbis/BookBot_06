import json
import re
import requests
from typing import Optional, Dict, Any

class OllamaClient:
    """Robust client for interacting with a local Ollama instance."""
    
    def __init__(self, model: str = "qwen3:14b", base_url: str = "http://127.0.0.1:11434"):
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
            from src.utils.logger import bot_logger
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            res_text = response.json().get("response", "")
            
            # Log the raw interaction
            bot_logger.log_interaction(self.model, f"System: {system}\nUser: {user}", res_text)
            
            # Clean and return
            return self._strip_thoughts(res_text)
        except Exception as e:
            from src.utils.logger import bot_logger
            bot_logger.log_error(f"Ollama Error: {str(e)}")
            return f"Error connecting to Ollama: {str(e)}"

    def _strip_thoughts(self, text: str) -> str:
        """Removes reasoning/thought blocks, handling potential truncation."""
        # 1. Strip complete <think> or <thinking> blocks
        text = re.sub(r'<(?:think|thinking)>.*?</(?:think|thinking)>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 2. Handle truncated blocks:
        # If we see an end tag but no start tag before it, strip everything from start to end tag
        if re.search(r'</(?:think|thinking)>', text, flags=re.IGNORECASE) and not re.search(r'<(?:think|thinking)>', text, flags=re.IGNORECASE):
             text = re.sub(r'^.*?</(?:think|thinking)>', '', text, flags=re.DOTALL | re.IGNORECASE)
             
        # If we see a start tag but no end tag after it, strip everything from start tag to end of string
        if re.search(r'<(?:think|thinking)>', text, flags=re.IGNORECASE) and not re.search(r'</(?:think|thinking)>', text, flags=re.IGNORECASE):
             text = re.sub(r'<(?:think|thinking)>.*$', '', text, flags=re.DOTALL | re.IGNORECASE)

        # 3. Final mop-up of any stray tags
        return re.sub(r'<(?:think|thinking)>|</(?:think|thinking)>', '', text, flags=re.IGNORECASE).strip()

    def _clean_json(self, text: str) -> Dict[str, Any]:
        """
        Deterministic cleaning of LLM output to extract JSON.
        Implements the 'Pythonic-First' strategy to avoid prompt escalation.
        """
        # 1. Strip thought blocks
        text = self._strip_thoughts(text)
        
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
