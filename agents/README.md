This directory contains agent plugins that implement the program's core purpose: repository hygiene and dynamic task execution. The God AGI Agent orchestrates these plugins to perform operations such as:

- Deduplication and summarization of code
- Merging and consolidating requirements
- Docker-compose configuration management

Each agent extends the base Agent class to handle specific workflows. The system loads agents from `config/agents.yaml` and dynamically creates new agents as needed to fulfill user requests.
