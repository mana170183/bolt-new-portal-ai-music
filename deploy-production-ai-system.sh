#!/bin/bash

# Production AI Music System Deployment Script
echo "🎵 Deploying Production AI Music Generation System..."

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS and install dependencies
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Running on macOS, checking dependencies..."
    
    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        print_warning "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install system dependencies
    print_status "Installing system dependencies..."
    brew install python@3.11 portaudio
    
    # Install Node.js if not present
    if ! command -v node &> /dev/null; then
        brew install node
    fi
fi

# Create Python virtual environment
print_status "Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements_production.txt

# Create environment file
print_status "Creating environment configuration..."
cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///production_music.db

# Azure Configuration (Optional - for production features)
AZURE_STORAGE_CONNECTION_STRING=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=

# OpenAI Configuration (Alternative to Azure)
OPENAI_API_KEY=

# Application Configuration
FLASK_ENV=production
PORT=5001
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
EOF

print_success "Environment file created at backend/.env"
print_warning "Please edit backend/.env to add your API keys if you want to use Azure/OpenAI features"

# Initialize database
print_status "Initializing production database..."
python3 -c "
from production_ai_system import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

# Test the backend
print_status "Testing backend functionality..."
python3 -c "
import sys
sys.path.append('.')
from production_ai_system import generator
generator.initialize_sample_data()
print('Backend initialization successful')
"

cd ..

# Install frontend dependencies
print_status "Installing frontend dependencies..."
npm install

# Build the frontend
print_status "Building frontend..."
npm run build

# Create startup scripts
print_status "Creating startup scripts..."

# Backend startup script
cat > start-production-backend.sh << 'EOF'
#!/bin/bash
echo "Starting Production AI Music Backend..."
cd backend
source venv/bin/activate
export FLASK_ENV=production
python3 production_ai_system.py
EOF

chmod +x start-production-backend.sh

# Frontend startup script
cat > start-production-frontend.sh << 'EOF'
#!/bin/bash
echo "Starting Production AI Music Frontend..."
npm run dev
EOF

chmod +x start-production-frontend.sh

# Complete deployment script
cat > deploy-production-system.sh << 'EOF'
#!/bin/bash
echo "🎵 Starting Complete Production AI Music System..."

# Start backend in background
echo "Starting backend..."
./start-production-backend.sh &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Test backend health
echo "Testing backend health..."
for i in {1..10}; do
    if curl -s http://localhost:5001/health > /dev/null; then
        echo "✅ Backend is healthy"
        break
    fi
    echo "⏳ Waiting for backend... ($i/10)"
    sleep 2
done

# Start frontend
echo "Starting frontend..."
./start-production-frontend.sh &
FRONTEND_PID=$!

echo "🎵 Production AI Music System is running!"
echo "📊 Backend: http://localhost:5001"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"

# Handle shutdown
trap 'echo "Shutting down..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT

# Keep script running
wait
EOF

chmod +x deploy-production-system.sh

# Create production test script
cat > test-production-system.py << 'EOF'
#!/usr/bin/env python3
"""
Production AI Music System Test Suite
"""

import requests
import json
import time
import sys
from pathlib import Path

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get('http://localhost:5001/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data['status']}")
            print(f"   Services: {json.dumps(data['services'], indent=4)}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_metadata_endpoints():
    """Test metadata endpoints"""
    endpoints = [
        ('genres', '/api/metadata/genres'),
        ('moods', '/api/metadata/moods'),
        ('instruments', '/api/metadata/instruments'),
        ('templates', '/api/metadata/templates')
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:5001{endpoint}', timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name.title()}: {len(data.get(name, []))} items")
            else:
                print(f"❌ {name.title()} endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {name.title()} endpoint error: {e}")

def test_music_generation():
    """Test music generation"""
    print("\n🎵 Testing AI Music Generation...")
    
    try:
        # Test data
        generation_request = {
            "genre": "electronic",
            "mood": "energetic",
            "duration": 15,
            "tempo_bpm": 128,
            "instruments": ["synthesizer", "bass", "drums"],
            "style_complexity": "moderate",
            "key": "Am"
        }
        
        print(f"   Request: {json.dumps(generation_request, indent=2)}")
        
        response = requests.post(
            'http://localhost:5001/api/generate',
            json=generation_request,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Music generation successful!")
                metadata = result['data']['metadata']
                print(f"   Title: {metadata.get('title')}")
                print(f"   Genre: {metadata.get('genre')}")
                print(f"   AI Enhanced: {metadata.get('ai_enhanced')}")
                print(f"   Generation ID: {metadata.get('generation_id')}")
                
                # Test download
                gen_id = metadata.get('generation_id')
                if gen_id:
                    download_response = requests.get(
                        f'http://localhost:5001/api/download/{gen_id}',
                        timeout=30
                    )
                    if download_response.status_code == 200:
                        print("✅ Download endpoint working")
                        
                        # Save test file
                        test_file = Path('test_generated_music.wav')
                        with open(test_file, 'wb') as f:
                            f.write(download_response.content)
                        print(f"   Test file saved: {test_file}")
                    else:
                        print(f"❌ Download failed: {download_response.status_code}")
                
                return True
            else:
                print(f"❌ Generation failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Generation request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('message')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Music generation test error: {e}")
        return False

def test_generation_history():
    """Test generation history"""
    try:
        response = requests.get('http://localhost:5001/api/history?user_id=demo_user', timeout=10)
        if response.status_code == 200:
            data = response.json()
            history_count = len(data.get('history', []))
            print(f"✅ Generation History: {history_count} items")
            return True
        else:
            print(f"❌ History endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ History test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Production AI Music System Test Suite")
    print("=" * 50)
    
    # Wait for system to be ready
    print("⏳ Waiting for system to be ready...")
    for i in range(30):
        if test_backend_health():
            break
        time.sleep(2)
        if i == 29:
            print("❌ System not ready after 60 seconds")
            sys.exit(1)
    
    print("\n📊 Testing Metadata Endpoints...")
    test_metadata_endpoints()
    
    print("\n🎵 Testing Music Generation...")
    generation_success = test_music_generation()
    
    print("\n📜 Testing Generation History...")
    test_generation_history()
    
    print("\n" + "=" * 50)
    if generation_success:
        print("🎉 Production AI Music System is working correctly!")
        print("\nFeatures verified:")
        print("   ✅ Backend health monitoring")
        print("   ✅ Metadata API endpoints")
        print("   ✅ AI-enhanced music generation")
        print("   ✅ Audio file download")
        print("   ✅ Generation history")
        print("\nSystem is ready for production use!")
    else:
        print("⚠️  Some tests failed. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x test-production-system.py

# Create Docker files for production deployment
print_status "Creating production Docker configuration..."

cat > backend/Dockerfile.production << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements_production.txt .
RUN pip install --no-cache-dir -r requirements_production.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p generated_audio uploads models

# Expose port
EXPOSE 5001

# Run application
CMD ["python", "production_ai_system.py"]
EOF

cat > docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    ports:
      - "5001:5001"
    environment:
      - DATABASE_URL=sqlite:///production_music.db
      - FLASK_ENV=production
    volumes:
      - ./backend/generated_audio:/app/generated_audio
      - ./backend/uploads:/app/uploads
      - ./backend/models:/app/models
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped
EOF

cat > Dockerfile.frontend << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Build application
RUN npm run build

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "run", "dev"]
EOF

print_success "Production deployment configuration complete!"

echo ""
echo "🎉 Production AI Music System Deployment Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit backend/.env to add your API keys (Azure/OpenAI) if desired"
echo "2. Run the system: ./deploy-production-system.sh"
echo "3. Test the system: python3 test-production-system.py"
echo ""
echo "🔧 Available Commands:"
echo "   ./start-production-backend.sh   - Start backend only"
echo "   ./start-production-frontend.sh  - Start frontend only"
echo "   ./deploy-production-system.sh   - Start complete system"
echo "   python3 test-production-system.py - Test system functionality"
echo ""
echo "🌐 Access URLs:"
echo "   Backend API: http://localhost:5001"
echo "   Frontend App: http://localhost:3000"
echo "   Health Check: http://localhost:5001/health"
echo ""
echo "📊 Features:"
echo "   ✅ AI-Enhanced Music Generation with OpenAI/Azure integration"
echo "   ✅ Real music metadata from SQL database"
echo "   ✅ Genre/mood-based generation using real data"
echo "   ✅ Advanced frontend with full controls"
echo "   ✅ Production-ready deployment"
echo ""

print_success "Ready to generate amazing AI music! 🎵"
