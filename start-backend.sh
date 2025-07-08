#!/bin/bash

# Portal AI Music Backend Startup Script
echo "🎵 Portal AI Music - Backend Server Startup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: backend/app.py"
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    echo "   Please install Python 3.7+ and try again"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🐍 Using Python: $($PYTHON_CMD --version)"

# Check if virtual environment should be created
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "⚙️  Creating .env file from .env.example..."
    cp .env.example .env
fi

# Start the server
echo ""
echo "🚀 Starting Flask backend server..."
echo "📍 Server will be available at: http://localhost:5000"
echo "🔍 Health check: http://localhost:5000/health"
echo "📡 API endpoints: http://localhost:5000/api/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Run the server using the startup script
$PYTHON_CMD start.py