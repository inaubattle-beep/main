from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIError
from config.settings import settings
from core.logger import logger
import httpx

class LLMClient:
    def __init__(self):
        # Primary Client (OpenAI)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        
        # Secondary Client (Ollama - OpenAI Compatible)
        self.ollama_client = AsyncOpenAI(
            base_url=f"{settings.OLLAMA_HOST}/v1",
            api_key="ollama" # api key required but ignored
        )

    async def generate_response(self, prompt: str, model: str = "gpt-4-turbo", system_prompt: str = "You are a helpful AI assistant.") -> str:
        """
        Generates a response using OpenAI with failover to Ollama.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # Try OpenAI first
        if self.openai_client:
            try:
                logger.info(f"Attempting to call OpenAI with model {model}")
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                return response.choices[0].message.content
            except (RateLimitError, APIConnectionError, APIError) as e:
                logger.warning(f"OpenAI call failed: {e}. Switching to Local LLM (Ollama).")
        else:
             logger.info("OpenAI API Key not provided. Using Local LLM (Ollama) as primary.")

        # Failover to Ollama
        try:
            local_model = settings.OLLAMA_MODEL
            logger.info(f"Calling Ollama with model {local_model}")
            response = await self.ollama_client.chat.completions.create(
                model=local_model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Both OpenAI and Local LLM failed. Error: {e}")
            raise e

llm_client = LLMClient()
