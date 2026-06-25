import requests
from config import config  # Changed from 'app.config' to 'config'

class LeadBotAgent:
    def __init__(self):
        self.model = config.OLLAMA_MODEL
        self.ollama_url = f"{config.OLLAMA_HOST}/api/generate"
        print(f"🤖 Agent ready with model: {self.model}")
    
    def ask_ollama(self, prompt):
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()["response"]
            return "I'm here to help!"
        except:
            return "Hello! Tell me about your needs."
    
    def process_message(self, message):
        response = self.ask_ollama(f"Respond briefly as a helpful assistant: {message}")
        return {"response": response}

agent = LeadBotAgent()