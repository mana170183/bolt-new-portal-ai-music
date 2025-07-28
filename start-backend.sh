#!/bin/bash

# Portal AI Music Backend Startup Script (Updated for Node.js)
echo "🎵 Portal AI Music - Backend Server Startup (Node.js/Express)"
echo "============================================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Check if we have the Node.js test server
if [ ! -f "$PROJECT_ROOT/test-server.cjs" ]; then
    echo "❌ Error: Cannot find test-server.cjs"
    echo "   Script location: $SCRIPT_DIR"
    echo "   Looking for: $PROJECT_ROOT/test-server.cjs"
    echo "   Please ensure the Node.js server file exists"
    exit 1
fi

echo "🚀 Starting Node.js Express API server on port 7071..."

# Navigate to project root
cd "$PROJECT_ROOT" || {
    echo "❌ Error: Cannot navigate to project root directory"
    exit 1
}

echo "📁 Working directory: $(pwd)"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed or not in PATH"
    echo "   Please install Node.js 16+ and try again"
    exit 1
fi

echo "� Using Node.js: $(node --version)"

# Check if required packages are installed
if [ ! -d "node_modules" ]; then
    echo "� Installing Node.js dependencies..."
    npm install
fi

# Start the server
echo "🎵 Starting AI Music API server..."
echo "   Server will be available at: http://localhost:7071"
echo "   Health check: http://localhost:7071/health"
echo "   API Health check: http://localhost:7071/api/health"
echo ""

node test-server.cjs