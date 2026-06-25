import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leadbot.db")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    PORT = int(os.getenv("PORT", 8000))

config = Config()