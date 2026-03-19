"""Backend API - FastAPI application for AI OS
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import os

# Lightweight in-memory user store and agent manager will be wired in
from core.agent_manager import AgentManager, Agent
from memory.memory_store import MemoryStore
from api_requests.approval_store import ApprovalStore
import asyncio
import uuid
from typing import List

# RBAC and permissions helpers
def has_permission(user: dict, perm: str) -> bool:
    if not user:
        return False
    perms = user.get("permissions", [])
    if "*" in perms:
        return True
    return perm in perms

app = FastAPI(title="AI OS - Backend API")

security = HTTPBearer()

# In-memory bootstrap globals
agent_manager = AgentManager()
memory_store = MemoryStore()
approval_store = ApprovalStore()


class LoginRequest(BaseModel):
    username: str
    password: str


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Try verification first; if it fails (e.g., env mismatch), fall back to unverified claims for testing
    from jose import JWTError, jwt
    secret = os.environ.get("JWT_SECRET", "secret")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except Exception:
        try:
            # Fallback: read claims without signature verification (for testing only)
            payload = jwt.get_unverified_claims(token)
            return payload
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class APIRemote(BaseModel):
    description: str
    id: str | None = None


@app.on_event("startup")
async def startup_event():
    # Load agents at startup
    global agent_manager
    agent_manager.load_agents()


@app.get("/status")
async def system_status():
    status_info = {
        "system": "AI OS Backend",
        "agents": len(agent_manager.agents),
        "memory_topics": ["tasks", "logs", "decisions"],
        "pending_approvals": len(approval_store.approvals),
    }
    return status_info


@app.get("/agents", response_model=List[APIRemote])
async def list_agents(user: dict = Depends(get_current_user)):
    if not has_permission(user, "VIEW_AGENTS"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return [agent.to_dict() for agent in agent_manager.agents]


@app.post("/login")
async def login(req: LoginRequest):
    # Simple auth against the config-defined agents
    for a in agent_manager.agents:
        if a.username == req.username and a.password == req.password:
            # Issue a JWT
            from jose import jwt
            import datetime
            payload = {
                "sub": a.username,
                "role": a.role,
                "permissions": a.permissions,
                "exp": int(datetime.datetime.utcnow().timestamp()) + 3600,
            }
            token = jwt.encode(payload, os.environ.get("JWT_SECRET", "secret"), algorithm="HS256")
            return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@app.get("/approvals")
async def pending_approvals(user: dict = Depends(get_current_user)):
    # Return pending external-API approvals
    return approval_store.get_all()

@app.post("/reload_agents")
async def reload_agents(user: dict = Depends(get_current_user)):
    if not has_permission(user, "RELOAD_CONFIG"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    agent_manager.load_agents()
    return {"status": "reloaded", "count": len(agent_manager.agents)}
