import os
import httpx
from openai import AsyncOpenAI
from config.settings import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def get_llm_response(prompt: str, system_prompt: str = "You are a helpful AI OS agent.", model="gpt-4"):
    try:
        # Try OpenAI First
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            timeout=10
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
                        "stream": False
                    },
                    timeout=20
                )
                res.raise_for_status()
                data = res.json()
                return data.get("response", "")
        except Exception as ollama_err:
            print(f"Ollama Failed: {ollama_err}")
            return "Error: All LLM generation routes failed."
