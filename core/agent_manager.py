import json
import os
import yaml
from typing import List, Optional
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from memory.models import Agent as AgentModel
from auth.security import get_password_hash

@dataclass
class Agent:
    id: str
    username: str
    password: str
    role: str
    permissions: List[str]

    def to_dict(self):
        return asdict(self)

async def load_agents_from_config(db: AsyncSession, config_path: str = "agents_config.json"):
    """Loads agents from a JSON config file into the database."""
    if not os.path.exists(config_path):
        return

    with open(config_path, "r") as f:
        data = json.load(f)
    
    for agent_data in data.get("agents", []):
        result = await db.execute(select(AgentModel).where(AgentModel.agent_id == agent_data["id"]))
        existing = result.scalars().first()
        if not existing:
            new_agent = AgentModel(
                agent_id=agent_data["id"],
                username=agent_data["username"],
                hashed_password=get_password_hash(agent_data["password"]),
                role=agent_data["role"],
                permissions=agent_data["permissions"]
            )
            db.add(new_agent)
    await db.commit()

class AgentManager:
    """Manages system agents from various configuration sources."""
    def __init__(self):
        self.agents: List[Agent] = []

    def load_agents_from_yaml(self, path: str = "config/agents.yaml"):
        """Loads agents from a YAML file for in-memory management."""
        if not os.path.exists(path):
            # Default fall-back agent
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
