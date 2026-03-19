#!/usr/bin/env bash
set -euo pipefail
echo "[Docker] Setting up multi-service stack (backend + kernel + ollama) via Docker Compose"

cat > docker-compose.yml <<'YAML'
version: '3.9'
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET=changeme
      - OPENAI_API_KEY
    container_name: aios_backend
  kernel:
    build:
      context: .
      dockerfile: Dockerfile.kernel
    environment:
      - DATABASE_URL
    depends_on:
      - backend
    container_name: aios_kernel
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    container_name: aios_ollama
YAML

echo "[Docker] Created docker-compose.yml. Running docker-compose up --build --detach"
docker-compose up --build -d
