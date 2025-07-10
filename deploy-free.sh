#!/bin/bash

# Portal AI Music - Free Platform Deployment Script
# Deploy to Railway (backend) + Vercel (frontend) for free testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -b, --backend-only     Deploy only backend to Railway"
    echo "  -f, --frontend-only    Deploy only frontend to Vercel"
    echo "  -s, --setup            Setup free accounts and dependencies"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Free Platform Stack:"
    echo "  Backend:  Railway (Free \$5/month credit)"
    echo "  Frontend: Vercel (Free tier)"
    echo "  Database: Supabase (Free 500MB)"
    echo "  AI:       Hugging Face (Free inference)"
    echo "  Storage:  Supabase Storage (Free 1GB)"
}

check_prerequisites() {
    print_status "Checking prerequisites for free deployment..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install it first."
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install it first."
        exit 1
    fi
    
    # Check Railway CLI
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
    
    # Check Vercel CLI
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not found. Installing..."
        npm install -g vercel
    fi
    
    print_success "All prerequisites met"
}

setup_free_accounts() {
    print_status "Setting up free platform accounts..."
    echo ""
    echo "Please create accounts on these free platforms:"
    echo ""
    echo "1. 🚂 Railway: https://railway.app/"
    echo "   - Sign up with GitHub"
    echo "   - Get \$5 free credit monthly"
    echo ""
    echo "2. ▲ Vercel: https://vercel.com/"
    echo "   - Sign up with GitHub"
    echo "   - Unlimited static deployments"
    echo ""
    echo "3. ⚡ Supabase: https://supabase.com/"
    echo "   - Sign up with GitHub"
    echo "   - Free PostgreSQL + Auth + Storage"
    echo ""
    echo "4. 🤗 Hugging Face: https://huggingface.co/"
    echo "   - Sign up and get API key"
    echo "   - Free AI model inference"
    echo ""
    echo "After creating accounts, run:"
    echo "  railway login"
    echo "  vercel login"
    echo ""
}

create_backend_config() {
    print_status "Creating backend configuration for Railway..."
    
    # Create railway.json
    cat > railway.json << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "healthcheckPath": "/health"
  }
}
EOF

    # Create requirements.txt if it doesn't exist
    if [[ ! -f "backend/requirements.txt" ]]; then
        cat > backend/requirements.txt << EOF
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
requests==2.31.0
supabase==1.0.4
gunicorn==21.2.0
psycopg2-binary==2.9.7
sqlalchemy==2.0.21
transformers==4.33.2
torch==2.0.1
librosa==0.10.1
numpy==1.24.3
scipy==1.11.2
EOF
    fi

    # Create simple Flask app for testing
    if [[ ! -f "backend/app.py" ]]; then
        mkdir -p backend
        cat > backend/app.py << EOF
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import requests
import tempfile
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

# Basic music generation endpoint
@app.route('/api/generate-music', methods=['POST'])
def generate_music():
    try:
        data = request.json
        prompt = data.get('prompt', 'happy music')
        
        # Simulate AI generation (replace with actual Hugging Face call)
        print(f"Generating music for prompt: {prompt}")
        
        # For now, return a success response
        return jsonify({
            "success": True,
            "prompt": prompt,
            "message": "Music generation simulated successfully",
            "audio_url": "/api/sample-audio"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Sample audio endpoint
@app.route('/api/sample-audio')
def sample_audio():
    return jsonify({"message": "Audio file would be served here"})

# Get music library
@app.route('/api/music-library')
def get_music_library():
    # Sample data for testing
    return jsonify({
        "tracks": [
            {"id": 1, "title": "Sample Track 1", "genre": "Electronic"},
            {"id": 2, "title": "Sample Track 2", "genre": "Classical"},
            {"id": 3, "title": "Sample Track 3", "genre": "Jazz"}
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
EOF
    fi

    print_success "Backend configuration created"
}

deploy_backend() {
    print_status "Deploying backend to Railway..."
    
    create_backend_config
    
    # Check if logged in to Railway
    if ! railway whoami &> /dev/null; then
        print_error "Please login to Railway first: railway login"
        exit 1
    fi
    
    # Initialize Railway project if needed
    if [[ ! -f "railway.toml" ]]; then
        print_status "Initializing Railway project..."
        railway init
    fi
    
    # Deploy to Railway
    print_status "Deploying to Railway..."
    railway up
    
    # Add PostgreSQL if needed
    print_status "Adding PostgreSQL database..."
    railway add postgresql
    
    print_success "Backend deployed to Railway!"
    
    # Get the deployment URL
    RAILWAY_URL=$(railway domain | grep -o 'https://[^[:space:]]*' | head -1)
    if [[ -n "$RAILWAY_URL" ]]; then
        echo ""
        print_success "🚂 Backend URL: $RAILWAY_URL"
        echo "   Health Check: $RAILWAY_URL/health"
        echo "   API Endpoint: $RAILWAY_URL/api/generate-music"
    fi
}

create_frontend_config() {
    print_status "Creating frontend configuration for Vercel..."
    
    # Create vercel.json
    cat > vercel.json << EOF
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_API_URL": "@api_url"
  }
}
EOF

    # Update package.json with build script if needed
    if [[ -f "package.json" ]] && ! grep -q "build" package.json; then
        print_status "Adding build script to package.json..."
        # This would need to be updated based on your actual build process
    fi

    print_success "Frontend configuration created"
}

deploy_frontend() {
    print_status "Deploying frontend to Vercel..."
    
    create_frontend_config
    
    # Check if we have a built frontend
    if [[ ! -d "dist" && ! -d "build" ]]; then
        print_status "Building frontend..."
        if [[ -f "package.json" ]]; then
            npm install
            npm run build
        else
            print_warning "No package.json found. Creating simple HTML for testing..."
            mkdir -p dist
            cat > dist/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Portal AI Music - Free Testing</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { text-align: center; }
        button { background: #0070f3; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0051cc; }
        .result { margin-top: 20px; padding: 20px; background: #f0f0f0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Portal AI Music</h1>
        <p>Free testing deployment</p>
        <button onclick="testAPI()">Test Music Generation</button>
        <div id="result" class="result" style="display: none;"></div>
    </div>

    <script>
        async function testAPI() {
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = 'Testing API...';
            
            try {
                const response = await fetch('/api/generate-music', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: 'happy electronic music' })
                });
                
                const data = await response.json();
                resultDiv.innerHTML = '<h3>✅ Success!</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                resultDiv.innerHTML = '<h3>❌ Error</h3><p>' + error.message + '</p>';
            }
        }
    </script>
</body>
</html>
EOF
        fi
    fi
    
    # Deploy to Vercel
    print_status "Deploying to Vercel..."
    vercel --prod
    
    print_success "Frontend deployed to Vercel!"
}

show_deployment_summary() {
    print_success "🎉 Free deployment completed!"
    echo ""
    echo "📋 Deployment Summary:"
    echo "  Frontend: Vercel (Free)"
    echo "  Backend:  Railway (Free \$5/month)"
    echo "  Database: Ready for Supabase"
    echo "  AI:       Ready for Hugging Face"
    echo ""
    echo "💡 Next Steps:"
    echo "1. Setup Supabase database and get connection string"
    echo "2. Get Hugging Face API key for music generation"
    echo "3. Add environment variables to Railway"
    echo "4. Download music datasets for training"
    echo "5. Test the full application flow"
    echo ""
    echo "📚 Documentation:"
    echo "  Free deployment guide: docs/FREE-DEPLOYMENT-GUIDE.md"
    echo "  Music datasets: Listed in the guide above"
    echo ""
    echo "💰 Monthly Cost: \$0 (Free tiers)"
}

# Parse command line arguments
BACKEND_ONLY=false
FRONTEND_ONLY=false
SETUP_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        -f|--frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        -s|--setup)
            SETUP_ONLY=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
echo "🎵 Portal AI Music - Free Platform Deployment"
echo "=============================================="
echo ""

if [[ "$SETUP_ONLY" == "true" ]]; then
    setup_free_accounts
    exit 0
fi

check_prerequisites

if [[ "$BACKEND_ONLY" == "true" ]]; then
    deploy_backend
elif [[ "$FRONTEND_ONLY" == "true" ]]; then
    deploy_frontend
else
    # Deploy both
    deploy_backend
    echo ""
    deploy_frontend
    echo ""
    show_deployment_summary
fi
