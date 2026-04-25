import json
import re
import requests
import time
from typing import Optional, Dict, Any

class OllamaClient:
    """Robust client for interacting with a local Ollama instance."""
    
    def __init__(self, model: str = "qwen3:14b", base_url: str = "http://127.0.0.1:11434"):
        self.model = model
        self.base_url = base_url

    def prompt(self, system: str, user: str, temperature: float = 0.7, retries: int = 2, timeout: int = 120) -> str:
        """Sends a request to Ollama using the chat endpoint with retry logic."""
        url = f"{self.base_url}/api/chat"
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        attempt = 0
        while attempt <= retries:
            try:
                from src.utils.logger import bot_logger
                response = requests.post(url, json=payload, timeout=timeout)
                response.raise_for_status()
                res_text = response.json().get("message", {}).get("content", "")
                
                # Log the raw interaction
                bot_logger.log_interaction(self.model, f"System: {system}\nUser: {user}", res_text)
                
                # Clean and return
                return self._strip_thoughts(res_text)
            except Exception as e:
                attempt += 1
                from src.utils.logger import bot_logger
                if attempt <= retries:
                    wait_time = 2 ** attempt
                    bot_logger.log_error(f"Ollama Attempt {attempt} failed: {str(e)}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    bot_logger.log_error(f"Ollama Error after {retries} retries: {str(e)}")
                    return f"Error connecting to Ollama: {str(e)}"
        
        return "Critical Error: Reach unreachable state in prompt()"

    def _strip_thoughts(self, text: str) -> str:
        """Surgically removes reasoning/thought blocks without wiping other content."""
        # Remove any complete <think>...</think> or <thinking>...</thinking> blocks
        text = re.sub(r'(?si)<(think|thinking)>.*?</\1>', '', text)
        
        # Also handle any trailing/unclosed tags just in case
        text = re.sub(r'(?si)<(think|thinking)>.*$', '', text)
        
        return text.strip()

    def _clean_json(self, text: str) -> Dict[str, Any]:
        """Extracts and cleans JSON from LLM output."""
        text = self._strip_thoughts(text)
        
        # Look for markdown blocks first
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                json_str = re.sub(r',\s*([\]}])', r'\1', match.group(1))
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

        # Fallback to brute-force find
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            json_str = text[start:end+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Remove trailing commas
                json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    from src.utils.logger import bot_logger
                    bot_logger.log_error(f"JSON Parse Error: {str(e)}")
        
        return {"error": "Failed to parse JSON", "raw_content": text}
