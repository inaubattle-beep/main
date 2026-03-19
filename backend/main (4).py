from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
from .database import get_db
from .auth import get_current_user, create_access_token, verify_password
from .models import Agent, Task, User
from .agent_manager import AgentManager
from core.llm_router import LLMRouter
from memory.memory import MemoryStore
from api_requests.approval import ApprovalSystem

app = FastAPI()

# Initialize components
agent_manager = AgentManager()
llm_router = LLMRouter(openai_api_key="0faf4fbf981c4e24a83d2d5832d5c794.6eqO-KItSxhgpa07RcWJpv_0")
memory = MemoryStore()
approval_system = ApprovalSystem()

@app.on_event("startup")
async def startup_event():
    await init_db()
    agent_manager.load_agents_from_config()
    # Start agent execution loop
    asyncio.create_task(agent_manager.run_agents())

@app.get("/status")
async def system_status():
    return {
        "status": "running",
        "agents": len(agent_manager.agents),
        "pending_approvals": len(approval_system.pending_requests)
    }

@app.post("/login")
async def login(username: str, password: str):
    # In a real system, validate against database
    if username == "admin" and verify_password(password, "$2b$12$..."):
        return {"token": create_access_token({"sub": username})}
    raise HTTPException(401, "Invalid credentials")

@app.get("/agents")
async def list_agents(current_user: dict = Depends(get_current_user)):
    return [{"id": a.id, "role": a.role} for a in agent_manager.agents.values()]

# Additional endpoints for tasks, approvals, etc.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)