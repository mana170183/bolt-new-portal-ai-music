@echo off
REM Portal AI Music Backend Startup Script for Windows (Updated for Node.js)

echo 🎵 Portal AI Music - Backend Server Startup (Node.js/Express)
echo ============================================================

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"

REM Remove trailing backslash if present
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM Check if we have the Node.js test server
if not exist "%PROJECT_ROOT%\test-server.cjs" (
    echo ❌ Error: Cannot find test-server.cjs
    echo    Script location: %SCRIPT_DIR%
    echo    Looking for: %PROJECT_ROOT%\test-server.cjs
    echo    Please ensure the Node.js server file exists
    pause
    exit /b 1
)

REM Navigate to project root
cd /d "%PROJECT_ROOT%"
if errorlevel 1 (
    echo ❌ Error: Cannot navigate to project root directory
    pause
    exit /b 1
)

echo 📁 Working directory: %CD%

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js is not installed or not in PATH
    echo    Please install Node.js 16+ and try again
    pause
    exit /b 1
)

echo � Using Node.js: 
node --version

REM Check if required packages are installed
if not exist "node_modules" (
    echo � Installing Node.js dependencies...
    npm install
)