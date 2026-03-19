class BaseAgent:
    def __init__(self, agent_id: str, role: str):
        self.agent_id = agent_id
        self.role = role
    
    async def process_task(self, task_description: str):
        """
        Base logic for extending agents logic
        """
        pass
