from pydantic_settings import BaseSettings
from typing import List
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pstral - Pack Solutions AI Assistant"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"]
    
    # OLLAMA
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "ministral:latest"
    
    # Context Management (to avoid token overflow)
    MAX_HISTORY_MESSAGES: int = 10  # Maximum messages to send to LLM
    MAX_FILE_CONTENT_LENGTH: int = 3000  # Max characters for uploaded files
    
    # ORACLE
    ORACLE_DSN: str = "localhost/XEPDB1"
    ORACLE_USER: str = "system"
    ORACLE_PASSWORD: str = "oracle"
    
    # JWT Authentication
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    class Config:
        case_sensitive = True

settings = Settings()
