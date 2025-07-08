#!/bin/bash

# Portal AI Music Backend Startup Script
echo "🎵 Portal AI Music - Backend Server Startup"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/backend/app.py" ]; then
    echo "❌ Error: Cannot find backend/app.py"
    echo "   Script location: $SCRIPT_DIR"
    echo "   Looking for: $PROJECT_ROOT/backend/app.py"
    echo "   Please ensure this script is in the project root directory"
    exit 1
fi

# Navigate to backend directory
cd "$PROJECT_ROOT/backend" || {
    echo "❌ Error: Cannot navigate to backend directory"
    exit 1
}

echo "📁 Working directory: $(pwd)"

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

# Check for corrupted virtual environment and clean it if necessary
if [ -d "venv" ]; then
    echo "🔍 Checking existing virtual environment..."
    # Test if the virtual environment is working
    if ! source venv/bin/activate 2>/dev/null && ! source venv/Scripts/activate 2>/dev/null; then
        echo "⚠️  Virtual environment appears corrupted, removing it..."
        rm -rf venv
    else
        # Test if _signal module is available
        if ! $PYTHON_CMD -c "import _signal" 2>/dev/null; then
            echo "⚠️  Python environment is corrupted (missing _signal module), removing virtual environment..."
            deactivate 2>/dev/null || true
            rm -rf venv
        else
            echo "✅ Virtual environment is healthy"
        fi
    fi
fi

# Create virtual environment if it doesn't exist or was removed
if [ ! -d "venv" ]; then
    echo "📦 Creating fresh virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment"
        echo "   Please ensure you have python3-venv installed:"
        echo "   sudo apt-get install python3-venv  # On Ubuntu/Debian"
        echo "   brew install python3               # On macOS"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "❌ Error: Cannot find virtual environment activation script"
    exit 1
fi

# Verify Python environment is working
echo "🧪 Testing Python environment..."
if ! python -c "import _signal; print('✅ Python environment is working')" 2>/dev/null; then
    echo "❌ Error: Python environment is still corrupted"
    echo "   Removing virtual environment and trying again..."
    deactivate
    rm -rf venv
    echo "📦 Creating new virtual environment..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate
fi

# Upgrade pip to latest version
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    echo "   Please check requirements.txt and try again"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "⚙️  Creating .env file from .env.example..."
    cp .env.example .env
fi

# Final health check
echo "🏥 Running final health check..."
if ! python -c "import flask, flask_cors, dotenv; print('✅ All dependencies imported successfully')" 2>/dev/null; then
    echo "❌ Error: Dependencies are not properly installed"
    exit 1
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
python start.py