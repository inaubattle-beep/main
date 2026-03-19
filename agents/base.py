from core.llm import llm_client
from core.logger import logger
import asyncio

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.llm = llm_client
        self.running = False

    async def run(self):
        logger.info(f"Agent {self.name} starting...")
        self.running = True
        while self.running:
            try:
                await self.process()
                await asyncio.sleep(5) # Poll interval
            except Exception as e:
                logger.error(f"Agent {self.name} error: {e}")
                await asyncio.sleep(5)

    async def process(self):
        raise NotImplementedError
