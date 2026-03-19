#!/bin/bash
echo "Starting AI Operating System Layer..."

if [ ! -f .env ]; then
    echo ".env file not found. Creating from .env.example..."
    cp .env.example .env
fi

echo "Building and starting containers..."
docker-compose up --build -d

echo "Services started. Tailing logs..."
docker-compose logs -f
