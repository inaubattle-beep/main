"""Runtime wrapper to launch the God AI Kernel in a standalone process.
Parses a simple YAML config and starts the kernel loop in the foreground.
"""
import asyncio
import sys
import os
import yaml
import argparse

from core.agent_manager import AgentManager
from core.task_manager import TaskQueue
from memory.memory_store import MemoryStore
from api_requests.approval_store import ApprovalStore
from core.kernel import GodAIAgent


async def main(config_path: str):
    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    am = AgentManager()
    am.load_agents()
    queue = TaskQueue()
    mem = MemoryStore()
    approvals = ApprovalStore()
    kernel = GodAIAgent(am.get_agents(), mem, queue, approvals)
    await kernel.run_loop()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/god_ai_config.yaml", help="Path to God AI config file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.config))
