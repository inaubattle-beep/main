from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Core Application
    APP_NAME: str = "AI Operating System Layer"
    VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Database
    # Use SQLite for local development without PostgreSQL dependencies by default
    DATABASE_URL: str = "sqlite+aiosqlite:///./aios.db"
    
    # Authentication
    SECRET_KEY: str = "super_secret_jwt_key_ai_os"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # LLM Providers - Primary (Cloud)
    OPENAI_API_KEY: Optional[str] = "your-openai-api-key"
    
    # LLM Providers - Backup (Local - Ollama)
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_HOST: str = "http://127.0.0.1:11434" # For compatibility
    OLLAMA_API_KEY: Optional[str] = "0faf4fbf981c4e24a83d2d5832d5c794.6eqO-KItSxhgpa07RcWJpv_0"
    OLLAMA_MODEL: str = "llama3"
    
    # LLM Providers - Backup (Local - LM Studio)
    LM_STUDIO_BASE_URL: str = "http://127.0.0.1:1234/v1"
    LM_STUDIO_API_KEY: Optional[str] = "sk-lm-nrqVNjE0:clpfx2Y7n5bE1Rz2O52Z"
    
    # Automation (n8n Integration)
    N8N_WEBHOOK_SECRET: Optional[str] = None
    N8N_HOST: str = "http://127.0.0.1:5678"
    
    # Logging & Monitoring
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
