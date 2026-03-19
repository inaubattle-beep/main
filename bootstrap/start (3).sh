#!/usr/bin/env bash
# Bootstrap script to start the AI OS stack: backend, kernel runtime, and services
# Note: This script is designed for POSIX environments. On Windows, use WSL or Git Bash.

set -e
export PYTHONUNBUFFERED=1

echo "[ bootstrap ] Starting services..."

# Ensure Python virtual env is activated if present
if [ -f "venv/bin/activate" ]; then
  echo "[ bootstrap ] Activating virtualenv..."
  source venv/bin/activate
fi

export OPENAI_API_KEY=${OPENAI_API_KEY:-""}
if [ -z "$OPENAI_API_KEY" ]; then
  echo "[ bootstrap ] Warning: OPENAI_API_KEY is not set. Primary LLM may fail until you set it."
fi

echo "[ bootstrap ] Launching backend (FastAPI) on port 8000..."
if command -v uvicorn >/dev/null 2>&1; then
  uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2 &
  PID_BACKEND=$!
else
  echo "[ bootstrap ] uvicorn not on PATH, trying python -m uvicorn"
  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2 &
  PID_BACKEND=$!
fi
PID_BACKEND=$!

echo "[ bootstrap ] Launching God AI Kernel runtime..."
python -m core.kernel_runtime --config config/god_ai_config.yaml &
PID_KERNEL=$!

echo "[ bootstrap ] All services started."
echo "Backend PID: $PID_BACKEND, Kernel PID: $PID_KERNEL"

wait -n $PID_BACKEND $PID_KERNEL
exit 0
