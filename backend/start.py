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
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_environment():
    """Check if Python environment is properly set up."""
    try:
        import _signal
        logger.info("✓ Python core modules are available")
        return True
    except ImportError as e:
        logger.error(f"✗ Python environment is corrupted: {e}")
        logger.info("Please recreate your virtual environment:")
        logger.info("1. Delete the 'venv' folder")
        logger.info("2. Run the startup script again")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import flask_cors
        import dotenv
        logger.info("✓ All dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        logger.info("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment setup."""
    backend_dir = Path(__file__).parent
    env_example = backend_dir / '.env.example'
    env_file = backend_dir / '.env'
    
    if env_example.exists() and not env_file.exists():
        logger.info("ℹ Creating .env file from .env.example...")
        try:
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            logger.info("✓ .env file created")
        except Exception as e:
            logger.warning(f"⚠ Could not create .env file: {e}")
    
    return True

def check_flask_app():
    """Check if Flask app can be imported."""
    try:
        from app import app
        logger.info("✓ Flask app imported successfully")
        return app
    except ImportError as e:
        logger.error(f"✗ Cannot import Flask app: {e}")
        logger.info("Please ensure app.py exists and is properly configured")
        return None
    except Exception as e:
        logger.error(f"✗ Error in Flask app: {e}")
        return None

def check_port_availability(port=5002):
    """Check if the specified port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            logger.info(f"✓ Port {port} is available")
            return True
    except OSError:
        logger.warning(f"⚠ Port {port} is already in use")
        logger.info(f"  Please stop the application using port {port} or change the PORT in .env")
        return False

def wait_for_server(port=5002, timeout=30):
    """Wait for the server to start responding."""
    logger.info(f"⏳ Waiting for server to start on port {port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    logger.info(f"✓ Server is responding on port {port}")
                    return True
        except:
            pass
        time.sleep(1)
    
    logger.warning(f"⚠ Server did not start within {timeout} seconds")
    return False

def start_server():
    """Start the Flask development server."""
    try:
        port = int(os.environ.get('PORT', 5002))
        
        # Check if port is available
        if not check_port_availability(port):
            logger.info(f"\n💡 To fix this issue:")
            logger.info(f"   1. Stop any application using port {port}")
            logger.info(f"   2. Or change PORT in backend/.env to an available port")
            logger.info(f"   3. Update vite.config.js proxy target to match the new port")
            return False
        
        logger.info("🚀 Starting Flask backend server...")
        logger.info(f"📍 Server will be available at: http://localhost:{port}")
        logger.info(f"🔍 Health check: http://localhost:{port}/health")
        logger.info(f"📡 API endpoints: http://localhost:{port}/api/")
        logger.info("\n" + "="*50)
        
        # Import and run the Flask app
        app = check_flask_app()
        if app is None:
            return False
            
        app.run(host='0.0.0.0', port=port, debug=False)
        return True
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        logger.info("\nTroubleshooting tips:")
        logger.info(f"1. Ensure port {port} is not in use by another application")
        logger.info("2. Check that all dependencies are installed")
        logger.info("3. Verify the Flask app configuration")
        logger.info("4. Check the terminal output above for specific error messages")
        return False

def main():
    """Main startup function."""
    logger.info("🔧 Portal AI Music Backend Server")
    logger.info("="*40)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    logger.info(f"📁 Working directory: {os.getcwd()}")
    
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
        logger.error("\n❌ Server startup failed")
        sys.exit(1)

if __name__ == '__main__':
    main()