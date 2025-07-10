#!/bin/bash

# Portal AI Music - Local Development Setup for Free Deployment
# Sets up the development environment for testing before deploying to free platforms

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

echo "🎵 Portal AI Music - Local Development Setup"
echo "==========================================="

setup_backend() {
    print_status "Setting up backend for local development..."
    
    cd backend-free
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please edit backend-free/.env with your actual API keys"
    fi
    
    cd ..
}

setup_frontend() {
    print_status "Setting up frontend for local development..."
    
    # Install frontend dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
        print_success "Dependencies installed"
    fi
    
    # Create .env.local file if it doesn't exist
    if [ ! -f ".env.local" ]; then
        print_status "Creating .env.local file from template..."
        cp .env.local.example .env.local
        print_warning "Please edit .env.local with your actual API keys"
    fi
}

create_start_script() {
    print_status "Creating local development start script..."
    
    cat > start-local-dev.sh << 'EOF'
#!/bin/bash

# Start Portal AI Music locally for development

echo "🚀 Starting Portal AI Music locally..."

# Check if .env files exist
if [ ! -f "backend-free/.env" ]; then
    echo "❌ backend-free/.env not found. Please copy from .env.example and configure."
    exit 1
fi

if [ ! -f ".env.local" ]; then
    echo "❌ .env.local not found. Please copy from .env.local.example and configure."
    exit 1
fi

# Start backend
echo "Starting backend..."
cd backend-free
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting frontend..."
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Portal AI Music is running locally:"
echo "   Backend:  http://localhost:5000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to clean up background processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Wait for interrupt
wait
EOF

    chmod +x start-local-dev.sh
    print_success "Created start-local-dev.sh script"
}

show_next_steps() {
    echo ""
    print_success "Local development setup completed!"
    echo ""
    echo "📋 Next steps:"
    echo "=============="
    echo "1. Create accounts on free platforms:"
    echo "   - Railway: https://railway.app"
    echo "   - Vercel: https://vercel.com"
    echo "   - Supabase: https://supabase.com"
    echo "   - Hugging Face: https://huggingface.co"
    echo ""
    echo "2. Configure environment variables:"
    echo "   - Edit backend-free/.env with your API keys"
    echo "   - Edit .env.local with your frontend settings"
    echo ""
    echo "3. Test locally:"
    echo "   ./start-local-dev.sh"
    echo ""
    echo "4. Deploy to free platforms:"
    echo "   ./deploy-free.sh"
    echo ""
    echo "5. Test deployment:"
    echo "   ./test-free-deployment.sh <your-api-url>"
    echo ""
    echo "📖 See docs/FREE-DEPLOYMENT-GUIDE.md for detailed instructions"
}

main() {
    setup_backend
    echo ""
    
    setup_frontend
    echo ""
    
    create_start_script
    echo ""
    
    show_next_steps
}

# Run setup
main "$@"
