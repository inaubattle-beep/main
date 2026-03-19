import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from memory.models import Agent
from auth.security import get_password_hash

async def load_agents_from_config(db: AsyncSession, config_path: str = "agents_config.json"):
    if not os.path.exists(config_path):
        print("Agent config not found")
        return

    with open(config_path, "r") as f:
        data = json.load(f)
    
    for agent_data in data.get("agents", []):
        result = await db.execute(select(Agent).where(Agent.agent_id == agent_data["id"]))
        existing = result.scalars().first()
        if not existing:
            new_agent = Agent(
                agent_id=agent_data["id"],
                username=agent_data["username"],
                hashed_password=get_password_hash(agent_data["password"]),
                role=agent_data["role"],
                permissions=agent_data["permissions"]
            )
            db.add(new_agent)
    await db.commit()
