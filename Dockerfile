FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y gcc postgresql-server-dev-all musl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y gcc musl-dev && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
