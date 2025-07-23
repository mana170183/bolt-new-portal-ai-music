#!/bin/bash

# Advanced AI Music Generation System - Complete Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Configuration
PROJECT_NAME="ai-music-generator"
BACKEND_IMAGE="ai-music-backend"
BACKEND_PORT=5000

log "Starting AI Music Generation System Deployment"

# Check Docker
if ! command -v docker &> /dev/null; then
    error "Docker is not installed"
fi

# Build backend
log "Building AI Music Backend..."
cd backend

# Create Dockerfile if it doesn't exist
if [ ! -f "Dockerfile.ai" ]; then
    log "Creating AI Dockerfile..."
    cat > Dockerfile.ai << 'DOCKER_EOF'
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1-dev \
    ffmpeg \
    sox \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements_full_ai.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ai_music_system.py app.py
COPY download_training_data.py .
COPY train_models.py .

RUN mkdir -p uploads generated_audio models training_data

EXPOSE 5000

CMD ["python", "app.py"]
DOCKER_EOF
fi

# Build image
docker build -f Dockerfile.ai -t "$BACKEND_IMAGE:latest" .

# Run container
log "Starting AI Music Backend..."
docker stop "$PROJECT_NAME-backend" 2>/dev/null || true
docker rm "$PROJECT_NAME-backend" 2>/dev/null || true

docker run -d \
    --name "$PROJECT_NAME-backend" \
    -p "$BACKEND_PORT:5000" \
    -v "$(pwd)/generated_audio:/app/generated_audio" \
    -v "$(pwd)/models:/app/models" \
    --restart unless-stopped \
    "$BACKEND_IMAGE:latest"

# Health check
log "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null; then
        success "Backend is healthy"
        break
    fi
    sleep 2
done

success "AI Music Generation System deployed!"
echo ""
echo "🎵 System is running:"
echo "   Backend: http://localhost:$BACKEND_PORT"
echo "   Health: http://localhost:$BACKEND_PORT/health"
echo "   API: http://localhost:$BACKEND_PORT/api/generate"
echo ""
echo "Test generation:"
echo "curl -X POST http://localhost:$BACKEND_PORT/api/generate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"style\": \"classical\", \"duration\": 10}'"
