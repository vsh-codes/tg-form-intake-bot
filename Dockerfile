# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS base

# Don't write .pyc files, don't buffer stdout — better for container logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first so they get cached separately from app code
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Drop privileges
RUN useradd --create-home --shell /bin/bash botuser && \
    chown -R botuser:botuser /app
USER botuser

# Persistent volumes mount points
VOLUME ["/app/data", "/app/logs", "/app/credentials"]

CMD ["python", "-m", "main"]
