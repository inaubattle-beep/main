from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from core.logger import logger
from typing import Dict, Any

router = APIRouter(prefix="/webhooks/n8n", tags=["n8n"])

class TaskUpdate(BaseModel):
    task_id: str
    status: str
    result: Dict[str, Any]

class ApprovalRequest(BaseModel):
    task_id: str
    agent_id: str
    action: str
    context: Dict[str, Any]

@router.post("/task_update")
async def receive_task_update(update: TaskUpdate):
    logger.info(f"Received task update from n8n: {update}")
    # Logic to update DB would go here
    return {"status": "received", "task_id": update.task_id}

@router.post("/approval")
async def receive_approval_request(request: ApprovalRequest):
    logger.info(f"Received approval request from Agent {request.agent_id} for Task {request.task_id}")
    # Logic to trigger n8n workflow for user approval
    # This might seem circular: Agent -> n8n -> User -> n8n -> Backend. 
    # But this endpoint is for n8n to notify backend about a process state, or for backend to receive a callback.
    
    return {"status": "processing", "message": "Approval workflow triggered"}
