from fastapi import FastAPI
from backend.routers import webhooks
from config.settings import settings
from core.logger import logger
import uvicorn

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Operating System Layer with Failover LLM and n8n Integration",
    version="1.0.0",
    debug=settings.DEBUG
)

# Include Routers
app.include_router(webhooks.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "env": settings.APP_ENV}

@app.get("/")
async def root():
    return {
        "message": "AI OS Backend Operational",
        "docs": "/docs",
        "llm_primary": "OpenAI" if settings.OPENAI_API_KEY else "Ollama (Local)",
        "llm_secondary": "Ollama (Local)"
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
