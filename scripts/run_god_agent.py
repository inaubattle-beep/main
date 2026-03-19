import asyncio
import os
import sys

# Add project root to path so imports work correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.kernel import GodAIAgent
from memory.memory_store import MemoryStore
from core.task_manager import TaskQueue
from api_requests.approval_store import ApprovalStore
from memory.models import Agent

async def main():
    print("Initializing God AI Agent...")
    
    # Init storage
    memory = MemoryStore()
    queue = TaskQueue()
    approvals = ApprovalStore()
    
    # Seed agents (mock for now or load from DB)
    # Using SQLAlchemy model directly
    agents = [Agent(agent_id="god_agent_1", role="admin", permissions={"all": True})]
    
    agent = GodAIAgent(agents, memory, queue, approvals)
    
    print("God AI Agent Started. Listening for tasks...")
    try:
        await agent.run_loop()
    except KeyboardInterrupt:
        print("God AI Agent Stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("God AI Agent Stopped.")
