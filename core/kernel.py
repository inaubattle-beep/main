"""God AI Agent Kernel: orchestrates agents, tasks, approvals, and memory."""
import asyncio
import os
import subprocess
from typing import List, Optional
from core.autonomy import AutonomyEngine

from memory.models import Agent
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

    def execute_shell(self, command: str) -> str:
        try:
            # Security warning: This allows arbitrary code execution.
            print(f"God Agent Executing: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
            output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            return output
        except Exception as e:
            return f"Execution Error: {str(e)}"

    def write_file(self, path: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Write Error: {str(e)}"

    def read_file(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                return "Error: File not found."
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Read Error: {str(e)}"

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
        description = task.get("description")
        self.memory.add_log(f"Executing {task_id}: {description}")

        # Construct Prompt for God Agent
        system_prompt = (
            "You are the God AI Agent. You have full control over the system.\n"
            "You can execute shell commands, read/write files, and build programs.\n"
            "To execute a command, return: EXECUTE_SHELL: <command>\n"
            "To write a file, return: WRITE_FILE: <path>\\n<content>\\nEND_FILE\n"
            "To read a file, return: READ_FILE: <path>\n"
            "To plan or delegate, return: PLAN: <text>\n"
            "To complete the task, return: COMPLETED: <summary>\n"
            "Do not provide markdown formatting for the commands."
        )

        prompt = f"Task: {description}\nStatus: {task.get('status')}"
        
        # Call LLM
        response = await llm_router.generate(prompt, system_prompt=system_prompt)
        
        # Basic Parsing Logic
        execution_log = f"Agent Response: {response}\n"
        
        if "EXECUTE_SHELL:" in response:
            cmd = response.split("EXECUTE_SHELL:")[1].split("\n")[0].strip()
            out = self.execute_shell(cmd)
            execution_log += f"Command Output: {out}\n"
            # Feedback loop could be added here
        
        elif "WRITE_FILE:" in response:
            try:
                parts = response.split("WRITE_FILE:")[1].split("END_FILE")[0]
                lines = parts.strip().split("\n")
                path = lines[0].strip()
                content = "\n".join(lines[1:])
                out = self.write_file(path, content)
                execution_log += f"File Write: {out}\n"
            except Exception as e:
                execution_log += f"File Write Parse Error: {e}\n"

        elif "READ_FILE:" in response:
            path = response.split("READ_FILE:")[1].split("\n")[0].strip()
            content = self.read_file(path)
            execution_log += f"File Content: {content[:500]}...\n"

        self.memory.add_log(execution_log)
        
        # Persist decision/result
        self.memory.decisions.append({"task_id": task_id, "plan": response, "log": execution_log})
        task["status"] = COMPLETED
        task["result"] = execution_log

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
