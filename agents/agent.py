from abc import ABC, abstractmethod
from typing import Any, Dict

class Agent(ABC):
    def __init__(self, id: str, role: str, permissions: Dict[str, bool]):
        self.id = id
        self.role = role
        self.permissions = permissions

    @abstractmethod
    async def execute(self):
        pass

# Example concrete agent
class MarketingAgent(Agent):
    async def execute(self):
        # Example task
        print(f"MarketingAgent {self.id} executing...")