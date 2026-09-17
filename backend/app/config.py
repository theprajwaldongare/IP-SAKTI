import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "IP Sakti - Ayurvedic IP & Regulatory AI Assistant"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

settings = Settings()
