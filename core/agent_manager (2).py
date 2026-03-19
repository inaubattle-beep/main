"""Agent Manager: loads and manages system agents from config.
"""
from dataclasses import dataclass, asdict
from typing import List
import yaml
import os

from memory.memory_store import MemoryStore


AGENTS_CONFIG_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "config", "agents.yaml"))


@dataclass
class Agent:
    id: str
    username: str
    password: str
    role: str
    permissions: List[str]

    def to_dict(self):
        return asdict(self)


class AgentManager:
    def __init__(self):
        self.agents: List[Agent] = []
        self.memory = MemoryStore()

    def load_agents(self):
        path = AGENTS_CONFIG_PATH
        if not os.path.exists(path):
            # Fallback to a default in-code agent
            self.agents = [Agent(id="admin-1", username="admin", password="adminpass", role="admin", permissions=["*"])]
            return
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        self.agents = []
        for a in data.get("agents", []):
            self.agents.append(
                Agent(
                    id=a.get("id", a.get("username", "agent")),
                    username=a.get("username"),
                    password=a.get("password"),
                    role=a.get("role", "agent"),
                    permissions=a.get("permissions", []),
                )
            )

    def get_agents(self) -> List[Agent]:
        return self.agents
