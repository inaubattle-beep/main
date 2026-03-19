import openai
from ollama import Client

class LLMRouter:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.ollama_client = Client(host='http://localhost:11434')

    async def generate(self, prompt: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                api_key=self.openai_api_key
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback to Ollama
            response = self.ollama_client.generate(model="llama3", prompt=prompt)
            return response['response']