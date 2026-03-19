"""LLM Router: primary OpenAI API with backup Ollama (local) fallback.
"""
import httpx
import asyncio
import os

PRIMARY_API = "https://api.openai.com/v1/completions"
MODEL = os.environ.get("OPENAI_MODEL", "text-davinci-003")
API_KEY = os.environ.get("OPENAI_API_KEY", "")
# Optional Ollama API key for local/private instances (bearer token if provided)
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
BACKUP_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/v1/generate")
LMSTUDIO_URL = os.environ.get("LMSTUDIO_URL", "")
LMSTUDIO_API_KEY = os.environ.get("LMSTUDIO_API_KEY", "")


class LLMRouter:
    def __init__(self):
        self.primary = True

    async def generate(self, prompt: str, max_tokens: int = 256) -> str:
        # Primary: OpenAI if API key provided
        text = await self._call_openai(prompt, max_tokens)
        if text is not None:
            return text
        # Secondary: LM Studio if configured
        if LMSTUDIO_URL:
            text = await self._call_lmstudio(prompt, max_tokens)
            if text:
                return text
        # Tertiary: Ollama
        text = await self._call_ollama(prompt, max_tokens)
        return text or ""

    async def _call_openai(self, prompt: str, max_tokens: int) -> str | None:
        if not API_KEY:
            return None
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "n": 1,
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    PRIMARY_API,
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json=payload,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    # OpenAI's response structure varies; handle common layouts
                    choices = data.get("choices") or []
                    if choices:
                        return choices[0].get("text", "").strip()
        except Exception:
            pass
        return None

    async def _call_ollama(self, prompt: str, max_tokens: int) -> str:
        payload = {"prompt": prompt, "model": "llama3", "max_tokens": max_tokens, "temperature": 0.7}
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                headers = {}
                if OLLAMA_API_KEY:
                    headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
                resp = await client.post(BACKUP_OLLAMA_URL, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("generated_text", "").strip()
        except Exception:
            pass
        return ""

    async def _call_lmstudio(self, prompt: str, max_tokens: int) -> str:
        payload = {"prompt": prompt, "max_tokens": max_tokens, "temperature": 0.7}
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                headers = {}
                if LMSTUDIO_API_KEY:
                    headers["Authorization"] = f"Bearer {LMSTUDIO_API_KEY}"
                resp = await client.post(LMSTUDIO_URL, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, dict):
                        if "choices" in data:
                            first = data["choices"][0]
                            if isinstance(first, dict):
                                t = first.get("text") or first.get("message", {}).get("content")
                                if t:
                                    return t.strip()
                        if "generated_text" in data:
                            return str(data["generated_text"]).strip()
                    if "text" in data:
                        return str(data["text"]).strip()
        except Exception:
            pass
        return ""


llm_router = LLMRouter()
