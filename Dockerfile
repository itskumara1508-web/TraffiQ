# Multi-stage production Dockerfile for TraffiQ Intelligent Traffic Management System
FROM python:3.11-slim as base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    YOLO_CONFIG_DIR=/tmp/ultralytics \
    MPLCONFIGDIR=/tmp/matplotlib \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies for OpenCV headless, PyTorch, and networking tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency list and install Python wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and models
COPY . .

# Ensure storage directories exist with write permissions
RUN mkdir -p /app/evidence /tmp/ultralytics /tmp/matplotlib && \
    chmod -R 777 /app/evidence /tmp/ultralytics /tmp/matplotlib

# Expose web dashboard & REST API port
EXPOSE 5050

# Health check against production endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5050/healthz || exit 1

# Launch TraffiQ real-time engine and web service
CMD ["python", "main.py"]

