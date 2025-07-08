#!/usr/bin/env python3
"""
Startup script for the Flask backend server.
This script ensures proper initialization and error handling.
"""

import sys
import os
import subprocess
from pathlib import Path

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

def start_server():
    """Start the Flask development server."""
    try:
        print("🚀 Starting Flask backend server...")
        print("📍 Server will be available at: http://localhost:5000")
        print("🔍 Health check: http://localhost:5000/health")
        print("📡 API endpoints: http://localhost:5000/api/")
        print("\n" + "="*50)
        
        # Import and run the Flask app
        from app import app
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        sys.exit(1)

def main():
    """Main startup function."""
    print("🔧 Portal AI Music Backend Server")
    print("="*40)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    check_environment()
    
    # Start server
    start_server()

if __name__ == '__main__':
    main()