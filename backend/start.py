#!/usr/bin/env python3
"""
Startup script for the Flask backend server.
This script ensures proper initialization and error handling.
"""

import sys
import os
import subprocess
import socket
import time
from pathlib import Path

def check_python_environment():
    """Check if Python environment is properly set up."""
    try:
        import _signal
        print("✓ Python core modules are available")
        return True
    except ImportError as e:
        print(f"✗ Python environment is corrupted: {e}")
        print("Please recreate your virtual environment:")
        print("1. Delete the 'venv' folder")
        print("2. Run the startup script again")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import flask_cors
        import dotenv
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment setup."""
    backend_dir = Path(__file__).parent
    env_example = backend_dir / '.env.example'
    env_file = backend_dir / '.env'
    
    if env_example.exists() and not env_file.exists():
        print("ℹ Creating .env file from .env.example...")
        try:
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✓ .env file created")
        except Exception as e:
            print(f"⚠ Could not create .env file: {e}")
    
    return True

def check_flask_app():
    """Check if Flask app can be imported."""
    try:
        from app import app
        print("✓ Flask app imported successfully")
        return app
    except ImportError as e:
        print(f"✗ Cannot import Flask app: {e}")
        print("Please ensure app.py exists and is properly configured")
        return None
    except Exception as e:
        print(f"✗ Error in Flask app: {e}")
        return None

def check_port_availability(port=5000):
    """Check if the specified port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            print(f"✓ Port {port} is available")
            return True
    except OSError:
        print(f"⚠ Port {port} is already in use")
        print(f"  Please stop the application using port {port} or change the PORT in .env")
        return False

def wait_for_server(port=5000, timeout=30):
    """Wait for the server to start responding."""
    print(f"⏳ Waiting for server to start on port {port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    print(f"✓ Server is responding on port {port}")
                    return True
        except:
            pass
        time.sleep(1)
    
    print(f"⚠ Server did not start within {timeout} seconds")
    return False

def start_server():
    """Start the Flask development server."""
    try:
        port = int(os.environ.get('PORT', 5000))
        
        # Check if port is available
        if not check_port_availability(port):
            print(f"\n💡 To fix this issue:")
            print(f"   1. Stop any application using port {port}")
            print(f"   2. Or change PORT in backend/.env to an available port")
            print(f"   3. Update vite.config.js proxy target to match the new port")
            return False
        
        print("🚀 Starting Flask backend server...")
        print(f"📍 Server will be available at: http://localhost:{port}")
        print(f"🔍 Health check: http://localhost:{port}/health")
        print(f"📡 API endpoints: http://localhost:{port}/api/")
        print("\n" + "="*50)
        
        # Import and run the Flask app
        app = check_flask_app()
        if app is None:
            return False
            
        app.run(host='0.0.0.0', port=port, debug=True)
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        print("\nTroubleshooting tips:")
        print(f"1. Ensure port {port} is not in use by another application")
        print("2. Check that all dependencies are installed")
        print("3. Verify the Flask app configuration")
        print("4. Check the terminal output above for specific error messages")
        return False

def main():
    """Main startup function."""
    print("🔧 Portal AI Music Backend Server")
    print("="*40)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check Python environment
    if not check_python_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    check_environment()
    
    # Start server
    success = start_server()
    if not success:
        print("\n❌ Server startup failed")
        sys.exit(1)

if __name__ == '__main__':
    main()