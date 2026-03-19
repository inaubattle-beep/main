import asyncio
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from memory.models import Task, TaskState
from memory.database import AsyncSessionLocal
from core.llm_router import get_llm_response

class TaskManager:
    def __init__(self):
        self.is_running = False

    async def start_loop(self):
        self.is_running = True
        print("Task Manager Execution Loop Started.")
        while self.is_running:
            await self.process_pending_tasks()
            await asyncio.sleep(5)  # Continuous loop iteration

    async def process_pending_tasks(self):
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Task).where(Task.state == TaskState.RUNNING))
            tasks = result.scalars().all()
            
            for task in tasks:
                # Simulate task execution step
                if "API_REQUEST" in task.description and task.pending_approval_request is None:
                    task.state = TaskState.WAITING_FOR_USER
                    task.pending_approval_request = "Requires human to approve API request: " + task.description
                    db.add(task)
                    await db.commit()
                    continue
                
                # Else process via LLM Router
                response = await get_llm_response(prompt=task.description)
                task.result = response
                task.state = TaskState.COMPLETED
                db.add(task)
                await db.commit()

task_manager = TaskManager()

class TaskQueue:
    def __init__(self):
        self._queue = asyncio.Queue()

    async def add_task(self, task: Dict[str, Any]):
        await self._queue.put(task)

    async def get_next(self) -> Optional[Dict[str, Any]]:
        if self._queue.empty():
            return None
        return await self._queue.get()

    def has_tasks(self) -> bool:
        return not self._queue.empty()
