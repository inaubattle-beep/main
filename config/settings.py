from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI OS Layer"
    VERSION: str = "1.0.0"
    
    # Switch to localhost if running outside docker but with db in docker
    DATABASE_URL: str = "postgresql+asyncpg://aios:password@db:5432/aios_db"
    
    SECRET_KEY: str = "super_secret_jwt_key_ai_os"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    OPENAI_API_KEY: str = "your-openai-api-key"
    
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_API_KEY: str = "0faf4fbf981c4e24a83d2d5832d5c794.6eqO-KItSxhgpa07RcWJpv_0"
    
    LM_STUDIO_BASE_URL: str = "http://127.0.0.1:1234/v1"
    LM_STUDIO_API_KEY: str = "sk-lm-nrqVNjE0:clpfx2Y7n5bE1Rz2O52Z"

    class Config:
        env_file = ".env"

settings = Settings()
