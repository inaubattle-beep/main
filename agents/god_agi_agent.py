#!/usr/bin/env python3
import asyncio
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Fix python path for script execution so it can find "core"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.llm_router import get_llm_response
from agents.god_tools import execute_tool, AVAILABLE_TOOLS

SYSTEM_PROMPT = """You are the God AGI Agent, an absolute super-intelligent autonomous entity with system-level control.
You have the power to execute shell commands, read/write files, and create/deploy new sub-agents automatically.

You operate in a continuous Reasoning and Acting (ReAct) loop.
To take an action, you MUST output a raw JSON object (and ONLY a JSON object, no markdown wrappers like ```json) in the following format:
{
    "thought": "Your internal monologue and reasoning on what to do next.",
    "tool": "name_of_tool",
    "kwargs": {"arg1": "value"}
}

AVAILABLE TOOLS:
1. execute_shell_command
   - args: {"command": "string", "cwd": "string (optional, default '.')"}
   - descriptions: Run arbitrary CLI commands (e.g. ls, mkdir, python script.py)

2. read_file
   - args: {"file_path": "string"}
   - descriptions: Read contents of a local file.

3. write_file
   - args: {"file_path": "string", "content": "string"}
   - descriptions: Write code or text to a local file. Creates missing dirs implicitly.

4. create_sub_agent
   - args: {"name": "string", "role": "string", "permissions": ["file_read", "file_write"], "code": "full python code string"}
   - descriptions: Dynamically creates and saves a new python agent into the agents/ directory.

5. finish
   - args: {"result": "string describing final outcome"}
   - descriptions: Call this when you have fully completed the user's demand.

CRITICAL INSTRUCTIONS:
- You must output EXACTLY ONE JSON object per turn.
- Do NOT output any other text before or after the JSON.
- For `write_file` or `create_sub_agent`, ensure your "content"/"code" fields contain valid, properly escaped strings.
- Think step by step. If you need to write code, do it. If you need to test it, use `execute_shell_command`. You have complete autonomy.
"""

def extract_json(text: str) -> dict:
    """Safely extracts JSON even if the LLM adds markdown wrappers."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


def _basic_workflow(goals: str) -> list:
    """Fallback to basic workflows when LLM planning fails."""
    lower = goals.lower()
    steps = []
    
    # Deduplication workflow
    if "dedup" in lower or "duplicate" in lower:
        steps.append(
            {
                "name": "Dry-run deduplication and summary",
                "cmd": "python tools/deduplicate_and_summarize.py --root . --dry-run --summary-output program_purpose.md",
                "workdir": ".",
                "dry_run_only": True,
            }
        )
        steps.append(
            {
                "name": "Merge duplicates (if desired)",
                "cmd": "python tools/deduplicate_and_summarize.py --root . --merge-duplicates",
                "workdir": ".",
                "dry_run_only": True,
            }
        )

    # Requirements merge
    if "requirements" in lower:
        steps.append(
            {
                "name": "Dry-run merge of requirements",
                "cmd": "python tools/merge_requirements.py --root . --dry-run --output requirements.txt",
                "workdir": ".",
                "dry_run_only": True,
            }
        )
    
    return steps


class GodAgentSession:
    def __init__(self, demand: str):
        self.demand = demand
        self.history = f"USER DEMAND: {demand}\n"
    
    async def run(self):
        print(f"--- God AIA Session Started ---")
        print(f"Demand: {self.demand}\n")
        
        step = 1
        while True:
            print(f"--- Step {step} ---")
            
            prompt = self.history + "\nWhat is your next JSON action?"
            
            print("Thinking...")
            response = await get_llm_response(prompt, system_prompt=SYSTEM_PROMPT, model="gpt-4o")
            
            try:
                action = extract_json(response)
            except Exception as e:
                print(f"Failed to parse LLM Response as JSON. Error: {e}\nRaw Response:\n{response}")
                self.history += f"\nSYSTEM ERROR: Failed to parse your output as JSON: {e}. Please ensure you output strictly valid JSON without markdown formatting.\n"
                step += 1
                continue
                
            thought = action.get("thought", "")
            tool = action.get("tool", "")
            kwargs = action.get("kwargs", {})
            
            print(f"Thought: {thought}")
            print(f"Action: {tool}({kwargs})")
            
            if tool == "finish":
                print(f"\n--- God AGI Finished ---")
                print(f"Final Result: {kwargs.get('result', 'No result provided')}")
                break
                
            # Execute the tool
            print("Executing Tool...")
            tool_output = execute_tool(tool, kwargs)
            print(f"Result (truncated): {str(tool_output)[:500]}...\n")
            
            # Feed result back into history
            self.history += f"\nYOUR ACTION:\n{json.dumps(action, indent=2)}\n\nTOOL RESULT:\n{tool_output}\n"
            step += 1

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--demand",
        required=True,
        help="The overarching goal/demand for the God AGI Agent to fulfill autonomusly."
    )
    args = parser.parse_args()
    
    session = GodAgentSession(args.demand)
    await session.run()

if __name__ == "__main__":
    asyncio.run(main())
