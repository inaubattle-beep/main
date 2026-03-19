import os
import subprocess
from typing import Dict, Any

def execute_shell_command(command: str, cwd: str = ".") -> str:
    """Executes a shell command on the host OS.
    
    Args:
        command: The CLI command to run.
        cwd: The working directory for the command.
    Returns:
        The combined stdout and stderr of the command.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output = f"Exit Code: {result.returncode}\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except Exception as e:
        return f"Error executing command: {str(e)}"

def read_file(file_path: str) -> str:
    """Reads a file from the host machine."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """Writes content to a file on the host machine. Creates directories if necessary."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file '{file_path}': {str(e)}"

def create_sub_agent(name: str, role: str, permissions: list, code: str) -> str:
    """Creates a new agent on demand by writing its python code to the agents/ directory.
    
    Args:
        name: Name of the agent class (e.g., DataAnalyzer)
        role: The role description
        permissions: List of permission string keys
        code: Full inner python code for the new agent.
    """
    try:
        file_name = f"agents/{name.lower()}_agent.py"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(code)
        return f"Agent {name} created successfully at {file_name}!"
    except Exception as e:
        return f"Error creating sub-agent: {str(e)}"

# Register the tools for the God Agent to use
AVAILABLE_TOOLS = {
    "execute_shell_command": execute_shell_command,
    "read_file": read_file,
    "write_file": write_file,
    "create_sub_agent": create_sub_agent
}

def execute_tool(tool_name: str, kwargs: Dict[str, Any]) -> str:
    """Dispatcher to run a dynamic tool by name."""
    if tool_name not in AVAILABLE_TOOLS:
        return f"Error: Tool '{tool_name}' not found."
    try:
        func = AVAILABLE_TOOLS[tool_name]
        return func(**kwargs)
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
