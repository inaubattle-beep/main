import os
import httpx
from config.settings import settings

class LLMRouter:
    def __init__(self):
        # We use httpx directly to avoid openai/pydantic-core build dependencies on minimal environments
        pass

    async def _openai_compatible_call(self, base_url: str, api_key: str, model: str, messages: list, max_tokens: int):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=60)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]

    async def generate(self, prompt: str, system_prompt: str = "You are a helpful AI OS agent.", model="gpt-4", max_tokens=1024):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # 1. Try LM Studio First
        try:
            return await self._openai_compatible_call(
                base_url=settings.LM_STUDIO_BASE_URL,
                api_key=settings.LM_STUDIO_API_KEY,
                model="model-identifier",
                messages=messages,
                max_tokens=max_tokens
            )
        except Exception as e:
            print(f"LM Studio Failed: {e}. Trying Ollama.")

        # 2. Try Ollama (Using their specific API)
        try:
            headers = {}
            if settings.OLLAMA_API_KEY:
                headers["Authorization"] = f"Bearer {settings.OLLAMA_API_KEY}"
                
            async with httpx.AsyncClient() as http_client:
                res = await http_client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    headers=headers,
                    json={
                        "model": "llama3",
                        "prompt": f"{system_prompt}\n\n{prompt}",
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens
                        }
                    },
                    timeout=60
                )
                res.raise_for_status()
                data = res.json()
                return data.get("response", "")
        except Exception as ollama_err:
            print(f"Ollama Failed: {ollama_err}. Final retry with OpenAI.")

        # 3. Fallback to OpenAI
        try:
            return await self._openai_compatible_call(
                base_url="https://api.openai.com/v1",
                api_key=settings.OPENAI_API_KEY,
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
        except Exception as last_err:
            print(f"All LLM generation routes failed: {last_err}")
            return "Error: All LLM generation routes failed."

llm_router = LLMRouter()
get_llm_response = llm_router.generate
