from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "AI Operating System Layer"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # LLM
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_HOST: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # n8n
    N8N_WEBHOOK_SECRET: Optional[str] = None
    N8N_HOST: str = "http://n8n:5678"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
