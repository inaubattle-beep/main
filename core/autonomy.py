"""Autonomy module: automatic task generation for self-improvement"""
import asyncio
from typing import List, Dict

from core.llm_router import llm_router
from memory.memory_store import MemoryStore
from core.task_manager import TaskQueue


class AutonomyEngine:
    def __init__(self, memory: MemoryStore, queue: TaskQueue):
        self.memory = memory
        self.queue = queue
        self.last_suggestion_ts = 0

    async def generate_improvement_tasks(self) -> List[Dict]:
        # Propose a small set of improvements for automation and reliability
        prompt = (
            "Propose 3 concrete improvements to an AI OS with multi-agent RBAC, LLM routing, "
            "and a task queue. For each improvement, provide an id, description, and suggested owner role."
        )
        plan = await llm_router.generate(prompt, max_tokens=512)
        tasks = []
        if not plan:
            return tasks
        # Try to parse as JSON first; fall back to line-based parsing
        try:
            import json
            parsed = json.loads(plan)
            for item in parsed:
                tasks.append({"id": item.get("id"), "description": item.get("description"), "agent_id": item.get("owner"), "status": "PENDING"})
            return tasks
        except Exception:
            pass
        # Fallback: simplistic parsing by lines
        for line in plan.splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                tid, desc = line.split(":", 1)
                tasks.append({"id": tid.strip(), "description": desc.strip(), "agent_id": None, "status": "PENDING"})
        return tasks

    async def run_once(self) -> None:
        # Do not override if there are pending approvals
        # This function is designed to be called from the kernel loop
        tasks = await self.generate_improvement_tasks()
        for t in tasks:
            await self.queue.add_task(t)
