@echo off
REM Portal AI Music Backend Startup Script for Windows

echo 🎵 Portal AI Music - Backend Server Startup
echo ==========================================

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"

REM Remove trailing backslash if present
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM Check if we're in the right directory
if not exist "%PROJECT_ROOT%\backend\app.py" (
    echo ❌ Error: Cannot find backend\app.py
    echo    Script location: %SCRIPT_DIR%
    echo    Looking for: %PROJECT_ROOT%\backend\app.py
    echo    Please ensure this script is in the project root directory
    pause
    exit /b 1
)

REM Navigate to backend directory
cd /d "%PROJECT_ROOT%\backend"
if errorlevel 1 (
    echo ❌ Error: Cannot navigate to backend directory
    pause
    exit /b 1
)

echo 📁 Working directory: %CD%

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

REM Check for corrupted virtual environment and clean it if necessary
if exist "venv" (
    echo 🔍 Checking existing virtual environment...
    REM Test if _signal module is available
    python -c "import _signal" >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Python environment is corrupted ^(missing _signal module^), removing virtual environment...
        rmdir /s /q venv
    ) else (
        echo ✅ Virtual environment is healthy
    )
)

REM Create virtual environment if it doesn't exist or was removed
if not exist "venv" (
    echo 📦 Creating fresh virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Error: Failed to create virtual environment
        echo    Please ensure Python venv module is available
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ❌ Error: Cannot find virtual environment activation script
    pause
    exit /b 1
)

REM Verify Python environment is working
echo 🧪 Testing Python environment...
python -c "import _signal; print('✅ Python environment is working')" >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python environment is still corrupted
    echo    Removing virtual environment and trying again...
    call deactivate 2>nul
    rmdir /s /q venv
    echo 📦 Creating new virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Upgrade pip to latest version
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error: Failed to install dependencies
    echo    Please check requirements.txt and try again
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        echo ⚙️  Creating .env file from .env.example...
        copy .env.example .env >nul
    )
)

REM Final health check
echo 🏥 Running final health check...
python -c "import flask, flask_cors, dotenv; print('✅ All dependencies imported successfully')" >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Dependencies are not properly installed
    pause
    exit /b 1
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