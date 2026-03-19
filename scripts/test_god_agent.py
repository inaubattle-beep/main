import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, patch, MagicMock

# Mock missing modules that require compilation
sys.modules["asyncpg"] = MagicMock()
sys.modules["psycopg2"] = MagicMock()

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.kernel import GodAIAgent, RUNNING, WAITING_FOR_USER, COMPLETED
from memory.memory_store import MemoryStore
from core.task_manager import TaskQueue
from api_requests.approval_store import ApprovalStore
from memory.models import Agent

class TestGodAgentFlows(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.memory = MemoryStore()
        self.queue = TaskQueue()
        self.approvals = ApprovalStore()
        self.agents = [Agent(agent_id="test_god", role="admin", permissions={"all": True})]
        self.agent = GodAIAgent(self.agents, self.memory, self.queue, self.approvals)

    @patch("core.llm_router.llm_router.generate", new_callable=AsyncMock)
    async def test_shell_execution_flow(self, mock_generate):
        # Scenario: Agent decides to run a shell command
        mock_generate.return_value = "EXECUTE_SHELL: echo 'Hello World'"
        
        # Add a task to the queue
        await self.queue.add_task({"id": "task-shell", "description": "Run a test command", "status": RUNNING})
        
        # Run one iteration
        await self.agent.run_once()
        
        # Verify
        last_log = self.memory.logs[-1]
        self.assertIn("Hello World", last_log)
        self.assertIn("Agent Response: EXECUTE_SHELL: echo 'Hello World'", last_log)

    @patch("core.llm_router.llm_router.generate", new_callable=AsyncMock)
    async def test_file_write_read_flow(self, mock_generate):
        test_file = "test_output.txt"
        test_content = "AIOS Validation Content"
        
        # 1. Write File
        mock_generate.return_value = f"WRITE_FILE: {test_file}\n{test_content}\nEND_FILE"
        await self.queue.add_task({"id": "task-write", "description": "Write a test file", "status": RUNNING})
        await self.agent.run_once()
        
        self.assertTrue(os.path.exists(test_file))
        with open(test_file, "r") as f:
            self.assertEqual(f.read(), test_content)
        
        # 2. Read File
        mock_generate.return_value = f"READ_FILE: {test_file}"
        await self.queue.add_task({"id": "task-read", "description": "Read the test file", "status": RUNNING})
        await self.agent.run_once()
        
        self.assertIn(test_content, self.memory.logs[-1])
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

    async def test_approval_pause_flow(self):
        # Scenario: Approval is pending, agent should not run tasks
        self.approvals.add_approval({"id": "app-1", "request": "Manual intervention needed"})
        await self.queue.add_task({"id": "task-queued", "description": "Should stay in queue", "status": RUNNING})
        
        # Run one iteration
        await self.agent.run_once()
        
        # Verify state changed to WAITING_FOR_USER
        self.assertEqual(self.agent.state, WAITING_FOR_USER)
        # Verify task is still in queue (or rather, wasn't processed)
        # In run_once, if approvals.get_all() returns something, it returns early.
        self.assertTrue(self.queue.has_tasks())

    @patch("core.llm_router.llm_router.generate", new_callable=AsyncMock)
    async def test_autonomy_task_generation(self, mock_generate):
        # Scenario: Autonomy engine generates new tasks
        mock_generate.return_value = "id-1: Improve memory logging\nid-2: Patch security hole"
        
        await self.agent.autonomy.run_once()
        
        # Verify tasks added to queue
        self.assertTrue(self.queue.has_tasks())
        task1 = await self.queue.get_next()
        self.assertEqual(task1["id"], "id-1")
        self.assertEqual(task1["description"], "Improve memory logging")

if __name__ == "__main__":
    unittest.main()
