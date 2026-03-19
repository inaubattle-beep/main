"""God AI Agent Kernel: orchestrates agents, tasks, approvals, and memory."""
import asyncio
from typing import List
from core.autonomy import AutonomyEngine

from core.agent_manager import Agent
from core.task_manager import TaskQueue
from core.llm_router import llm_router
from memory.memory_store import MemoryStore
from api_requests.approval_store import ApprovalStore


RUNNING = "RUNNING"
WAITING_FOR_USER = "WAITING_FOR_USER"
COMPLETED = "COMPLETED"


class GodAIAgent:
    def __init__(self, agents: List[Agent], memory: MemoryStore, queue: TaskQueue, approvals: ApprovalStore):
        self.agents = agents
        self.memory = memory
        self.queue = queue
        self.approvals = approvals
        self.state = RUNNING
        self.log = []
        self.autonomy = AutonomyEngine(memory, queue)

    async def bootstrap_seed_tasks(self):
        # Create a couple of seed tasks if the queue is empty
        if not self.queue.has_tasks():
            await self.queue.add_task({"id": "task-1", "description": "Summarize quarterly marketing metrics", "agent_id": self.agents[0].id, "status": RUNNING})
            await self.queue.add_task({"id": "task-2", "description": "Prepare sales forecast for next quarter", "agent_id": self.agents[0].id, "status": RUNNING})

    async def run_once(self):
        # Pause for approvals if needed
        if self.approvals.get_all():
            self.state = WAITING_FOR_USER
            return
        # If no tasks, seed some
        if not self.queue.has_tasks():
            await self.bootstrap_seed_tasks()
            return
        # Get next task
        task = await self.queue.get_next()
        if not task:
            return
        task_id = task.get("id")
        self.memory.add_log(f"Executing {task_id}: {task.get('description')}")
        # Use LLM to process task description into a planned response
        prompt = f"Task: {task.get('description')}. Produce a concise plan with steps and owner by agent."
        plan = await llm_router.generate(prompt)
        # Persist decision
        self.memory.decisions.append({"task_id": task_id, "plan": plan})
        task["status"] = COMPLETED
        self.memory.add_log(f"Task {task_id} completed. Plan: {plan[:200]}...")

    async def run_loop(self):
        while True:
            # check approvals state
            if self.approvals.get_all():
                self.state = WAITING_FOR_USER
                await asyncio.sleep(2)
                continue
            self.state = RUNNING
            await self.run_once()
            # Periodically run autonomy improvements to expand the queue
            try:
                await asyncio.wait_for(self.autonomy.run_once(), timeout=0)
            except Exception:
                pass
            await asyncio.sleep(1)
