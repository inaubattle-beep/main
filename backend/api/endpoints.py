from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from pydantic import BaseModel
from memory.database import get_db
from memory.models import Task, Agent, User, TaskState
from auth.security import verify_password, create_access_token

router = APIRouter()

class LoginData(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginData, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalars().first()
    if user and verify_password(data.password, user.hashed_password):
        token = create_access_token({"sub": user.username, "type": "human"})
        return {"access_token": token, "token_type": "bearer"}
    
    # Check agent accounts
    result = await db.execute(select(Agent).where(Agent.username == data.username))
    agent = result.scalars().first()
    if agent and verify_password(data.password, agent.hashed_password):
        token = create_access_token({"sub": agent.username, "type": "agent"})
        return {"access_token": token, "token_type": "bearer"}
        
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@router.get("/status")
async def system_status():
    return {"status": "AI OS is running", "version": "1.0.0"}

@router.get("/agents")
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent))
    agents = result.scalars().all()
    return [{"id": a.agent_id, "role": a.role, "username": a.username} for a in agents]

@router.get("/pending-approvals")
async def pending_approvals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.state == TaskState.WAITING_FOR_USER))
    tasks = result.scalars().all()
    return [{"task_id": t.id, "agent": t.agent_id, "request": t.pending_approval_request} for t in tasks]

class ApprovalData(BaseModel):
    task_id: int
    approved: bool

@router.post("/approve")
async def approve(data: ApprovalData, db: AsyncSession = Depends(get_db)):
    from api_requests.approval_system import approve_task
    success = await approve_task(data.task_id, db, data.approved)
    if not success:
        raise HTTPException(status_code=400, detail="Task not found or not waiting for approval")
    return {"message": "Approval processed"}

class TaskCreate(BaseModel):
    agent_id: str
    description: str

@router.post("/tasks")
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(agent_id=data.agent_id, description=data.description)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return {"message": "Task queued", "task_id": new_task.id}
