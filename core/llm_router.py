import os
import httpx
from openai import AsyncOpenAI
from config.settings import settings

class LLMRouter:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate(self, prompt: str, system_prompt: str = "You are a helpful AI OS agent.", model="gpt-4", max_tokens=1024):
        try:
            # Try OpenAI First
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Failed: {e}. Falling back to Ollama.")
            # Fallback to local Ollama llama3
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
                print(f"Ollama Failed: {ollama_err}")
                return "Error: All LLM generation routes failed."

llm_router = LLMRouter()
get_llm_response = llm_router.generate  # Alias for backward compatibility if needed
