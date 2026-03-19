"""Simple asynchronous Task Queue for the AI OS core."""
import asyncio
from typing import Any, Dict, Optional


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
