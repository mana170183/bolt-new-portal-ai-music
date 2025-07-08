#!/bin/bash

# AI Music Generation Backend Startup Script
# This script starts the Flask backend server for the AI Music Generator

echo "🎵 Starting AI Music Generation Backend Server..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found in current directory"
    echo "Please run this script from the backend directory:"
    echo "  cd /path/to/portal-ai-music/backend"
    echo "  ./start-backend.sh"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 to continue"
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python3 -c "import flask, flask_cors, numpy; print('✅ Core dependencies found')" 2>/dev/null || {
    echo "❌ Missing dependencies. Installing required packages..."
    pip3 install Flask Flask-CORS python-dotenv numpy scipy soundfile librosa gunicorn
}

# Kill any existing processes on port 5001
echo "🧹 Cleaning up any existing processes on port 5001..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Create generated_audio directory if it doesn't exist
mkdir -p generated_audio

echo ""
echo "🚀 Starting Flask server on port 5001..."
echo "📍 Health check: http://localhost:5001/health"
echo "📡 API base URL: http://localhost:5001/api/"
echo "🎼 Music generation: http://localhost:5001/api/generate-music"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="

# Start the server
python3 app.py
