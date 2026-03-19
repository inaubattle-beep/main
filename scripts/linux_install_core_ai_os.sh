#!/usr/bin/env bash
set -euo pipefail

echo "[Install] Core AI OS - Linux Installer"

REPO_ROOT=$(pwd)

echo "[Install] Updating package index..."
sudo apt-get update -y

echo "[Install] Installing required packages..."
sudo apt-get install -y python3 python3-venv python3-pip curl git npm
 
echo "[Install] Installing Docker and Docker Compose..."
sudo apt-get install -y docker.io docker-compose
sudo systemctl enable --now docker

echo "[Install] Creating Python virtual environment..."
if [ ! -d venv ]; then
  python3 -m venv venv
fi
source venv/bin/activate

echo "[Install] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[Install] Installing npm dependencies (if frontend present)..."
if [ -f package.json ]; then
  npm ci
elif [ -d frontend ] && [ -f frontend/package.json ]; then
  (cd frontend && npm ci)
fi

echo "[Install] Starting services via bootstrap script..."
bash bootstrap/start.sh &
echo "[Install] Bootstrap started."
