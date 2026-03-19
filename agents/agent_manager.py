import yaml
import asyncio
from typing import Dict
from .agent import Agent

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.running = False

    def load_agents_from_config(self, config_path="config/agents.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        for agent_config in config['agents']:
            agent = Agent(**agent_config)
            self.agents[agent.id] = agent

    async def run_agents(self):
        self.running = True
        while self.running:
            for agent in self.agents.values():
                await agent.execute()
            await asyncio.sleep(1)  # Adjust as needed

    def stop(self):
        self.running = False