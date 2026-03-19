# AIOS - Artificial Intelligence Operating System

A powerful, autonomous multi-agent framework designed to orchestrate complex tasks, build programs, and manage system resources. At its core is the **God AGI Agent**, a super-privileged entity capable of full system interaction and autonomous problem-solving.

## Core Features

### 1. God AGI Agent
The **God AGI Agent** is the central orchestrator of the system. It possesses "superpowers" to:
- **Execute Shell Commands:** Run any terminal command across the system.
- **File System Control:** Read, write, and modify files to build and deploy programs.
- **Autonomous Planning:** Use advanced LLM reasoning to decompose high-level goals into executable steps.
- **Dynamic Agent Creation:** Spawn and manage specialized sub-agents based on task requirements.

### 2. Multi-Agent Orchestration
- **Agent Manager:** Handles registration, roles, and permissions (RBAC) for all agents.
- **Task Queue:** A robust asynchronous queue for managing and prioritizing system tasks.
- **Autonomy Engine:** Periodically generates self-improvement tasks to enhance system reliability and performance.

### 3. Repository Hygiene & Tooling
- **Deduplication:** Identify and merge duplicate content across the codebase.
- **Dependency Consolidation:** Merge multiple `requirements.txt` into a single root file.
- **Docker Unification:** Consolidate fragmented `docker-compose` files into a unified configuration.

## Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API Key or Local Ollama (llama3)
- Docker (optional, for containerized workflows)

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your environment in `.env`.

### Running the God AGI Agent
To launch the autonomous God Agent:
```bash
python scripts/run_god_agent.py
```

### Running Hygiene Tools
**Deduplicate and summarize (dry-run):**
```bash
python tools/deduplicate_and_summarize.py --root . --dry-run
```

**Consolidate requirements:**
```bash
python tools/merge_requirements.py --root . --output requirements.txt
```

## Architecture
- **`core/`**: The heart of the OS, containing the Kernel, God Agent logic, and Task Manager.
- **`agents/`**: Definitions for specialized task agents and base classes.
- **`memory/`**: Persistent and ephemeral storage for logs, decisions, and system state.
- **`backend/`**: FastAPI-based interface for external interaction and monitoring.

## Why AIOS?
AIOS provides a bridge between raw LLM intelligence and actionable system-level execution. It is designed for developers who need more than just a chatbot—it's a platform for building autonomous software engineering pipelines and self-managing systems.

## License
MIT License.
