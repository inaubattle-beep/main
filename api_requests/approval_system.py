from sqlalchemy.ext.asyncio import AsyncSession
from memory.models import Task, TaskState

async def approve_task(task_id: int, db: AsyncSession, approved: bool = True):
    task = await db.get(Task, task_id)
    if not task:
        return False
    
    if task.state == TaskState.WAITING_FOR_USER:
        if approved:
            task.state = TaskState.RUNNING
            task.pending_approval_request = None
            db.add(task)
            await db.commit()
            return True
        else:
            task.state = TaskState.COMPLETED
            task.result = "Request rejected by human admin."
            db.add(task)
            await db.commit()
            return True
    return False
