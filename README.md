# AIOS OpenCode Repository Hygiene Toolkit

A collection of lightweight tooling to help keep a repo clean, deduplicate identical content, consolidate dependencies, and unify docker-compose configurations. Includes a minimal GOD AGI Agent to orchestrate tasks.

## Quick Start

- Prerequisites:
  - Python 3.8+ installed
  - Optional: Docker and Docker Compose (for container-based workflows)
- Per-project Node scaffolding (optional)
  - Node version pin: `.nvmrc` (e.g., 20.4.0)
  - Docker-based Node scaffolding: `Dockerfile.node`, `docker-compose.node.yml`
- GOD AGI Agent (optional): `agents/god_agi_agent.py` (skeleton)

## How to run the available workflows

Deduplicate files and summarize program purpose (dry-run)
```
python tools/deduplicate_and_summarize.py --root . --dry-run --summary-output program_purpose.md
```

Merge duplicates (destructive) — use with care
```
python tools/deduplicate_and_summarize.py --root . --merge-duplicates
```

Consolidate requirements into a single root file (dry-run)
```
python tools/merge_requirements.py --root . --dry-run --output requirements.txt
```

Merge all docker-compose files into a single merged file (dry-run)
```
python tools/merge_docker_compose.py --root . --dry-run --output docker-compose.all.yml
```

Node per-project isolation
- Version pin: create a root file `.nvmrc` with a version (e.g. 20.4.0)
- Install and switch versions with your preferred tool (nvm on UNIX, nvm-windows on Windows)
- Install dependencies with `npm ci`

Container-based isolation
- Dockerfile.node and docker-compose.node.yml provide a scaffold for a per-project Node app.
- Use `docker compose -f docker-compose.node.yml up --build` to start the containerized app.

GOD AGI Agent (skeleton)
- Path: `agents/god_agi_agent.py`
- Purpose: plan and execute repo-health tasks (dry-run by default)
- Run: `python agents/god_agi_agent.py --goals "deduplicate docker-compose" --execute` to perform actions

## Why this exists
- To provide a consistent baseline for hygiene tasks across the repository: deduplication, dependency consolidation, and configuration unification.
- To offer a simple, safe way to experiment with automation (via the GOD AGI Agent) without risking the live codebase.

## Contributing
- Open issues or submit PRs to extend tooling (new patterns, safer dedup rules, or additional merge strategies).
- Keep changes small, test with dry-run first.

## License
- Include license information here if applicable.
