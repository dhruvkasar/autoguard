# AutoGuard - AI-Powered Retail Theft & Violence Prevention System
# Dockerfile for Edge Detection + Backend Services

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 autoguard && \
    chown -R autoguard:autoguard /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=autoguard:autoguard . .

# Create necessary directories with proper ownership
RUN mkdir -p evidence logs config && \
    chown -R autoguard:autoguard evidence logs config

# Download YOLOv8 weights if not present
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" || echo "Weights will be downloaded on first run"

# Switch to non-root user
USER autoguard

# Expose Flask server port
EXPOSE 5000

# Environment variables (override via docker-compose)
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src.server

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Default command: run Flask server
# For detection, override with: docker-compose run detection python src/main.py --source 0
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
