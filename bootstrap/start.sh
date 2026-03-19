#!/bin/bash

# AI OS Bootstrap Script
echo "Bootstrapping AI OS Layer..."

# Check dependencies
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null
then
    echo "[!] docker-compose could not be found, attempting to use docker compose instead."
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo "Spinning up infrastructure (PostgreSQL & others)..."
$DOCKER_COMPOSE_CMD up -d db

echo "Waiting for database to be ready..."
sleep 5

echo "Starting backend and agents..."
$DOCKER_COMPOSE_CMD up -d backend n8n

echo "======================================"
echo "    AI OS Layer is now running!       "
echo "======================================"
echo "API Endpoint: http://localhost:8000/docs"
echo "System Status: http://localhost:8000/api/status"
echo "Logs: $DOCKER_COMPOSE_CMD logs -f backend"
