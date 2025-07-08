@echo off
REM Portal AI Music Backend Startup Script for Windows

echo 🎵 Portal AI Music - Backend Server Startup
echo ==========================================

REM Check if we're in the right directory
if not exist "backend\app.py" (
    echo ❌ Error: Please run this script from the project root directory
    echo    Current directory: %CD%
    echo    Expected files: backend\app.py
    pause
    exit /b 1
)

REM Navigate to backend directory
cd backend

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo    Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo 🐍 Using Python: 
python --version

REM Check if virtual environment should be created
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        echo ⚙️  Creating .env file from .env.example...
        copy .env.example .env
    )
)

REM Start the server
echo.
echo 🚀 Starting Flask backend server...
echo 📍 Server will be available at: http://localhost:5000
echo 🔍 Health check: http://localhost:5000/health
echo 📡 API endpoints: http://localhost:5000/api/
echo.
echo Press Ctrl+C to stop the server
echo ==========================================

REM Run the server using the startup script
python start.py

pause