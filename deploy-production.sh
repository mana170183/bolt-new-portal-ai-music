#!/bin/bash

# 🚀 Production Deployment Script for AI Music Generation System
# Supports multiple deployment platforms: Vercel, Railway, Render, Heroku

set -e

echo "🎵 AI Music Generation System - Production Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if required tools are installed
check_dependencies() {
    print_info "Checking deployment dependencies..."
    
    # Check for Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    # Check for npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    # Check for git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_status "All dependencies are available"
}

# Build the frontend
build_frontend() {
    print_info "Building frontend for production..."
    
    # Install dependencies
    npm ci
    
    # Build the Next.js application
    NODE_ENV=production npm run build
    
    print_status "Frontend build completed"
}

# Prepare backend for deployment
prepare_backend() {
    print_info "Preparing backend for production deployment..."
    
    # Create production requirements.txt if not exists
    if [ ! -f "backend/requirements_production.txt" ]; then
        cp backend/requirements_enhanced.txt backend/requirements_production.txt
    fi
    
    # Create Dockerfile for backend if not exists
    if [ ! -f "backend/Dockerfile" ]; then
        print_info "Creating production Dockerfile for backend..."
        cat > backend/Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_production.txt .
RUN pip install --no-cache-dir -r requirements_production.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p generated_audio/stems

# Expose port
EXPOSE 5001

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "app.py"]
EOF
    fi
    
    print_status "Backend prepared for deployment"
}

# Deploy to Railway
deploy_railway() {
    print_info "Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
    
    # Create railway.json if not exists
    cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm start",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
    
    # Create separate service for backend
    cat > backend/railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python app.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
    
    print_status "Railway configuration created"
    print_info "Run 'railway login' and 'railway up' to deploy"
}

# Deploy to Vercel
deploy_vercel() {
    print_info "Deploying to Vercel..."
    
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not found. Installing..."
        npm install -g vercel
    fi
    
    # Update vercel.json for production
    cat > vercel.json << 'EOF'
{
  "version": 2,
  "framework": "nextjs",
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/proxy/(.*)",
      "dest": "${BACKEND_URL}/api/$1",
      "status": 307
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "${BACKEND_URL}",
    "NODE_ENV": "production"
  },
  "functions": {
    "app/**": {
      "maxDuration": 30
    }
  }
}
EOF
    
    print_status "Vercel configuration updated"
    print_info "Run 'vercel --prod' to deploy"
}

# Deploy to Render
deploy_render() {
    print_info "Creating Render configuration..."
    
    # Create render.yaml
    cat > render.yaml << 'EOF'
services:
  - type: web
    name: ai-music-frontend
    env: node
    plan: starter
    buildCommand: npm ci && npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: NEXT_PUBLIC_API_URL
        fromService:
          type: web
          name: ai-music-backend
          property: host

  - type: web
    name: ai-music-backend
    env: python
    plan: starter
    rootDir: ./backend
    buildCommand: pip install -r requirements_production.txt
    startCommand: python app.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 5001
EOF
    
    print_status "Render configuration created"
    print_info "Connect your GitHub repo to Render dashboard to deploy"
}

# Create Docker Compose for local production testing
create_docker_compose() {
    print_info "Creating Docker Compose for production testing..."
    
    cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://backend:5001
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
      - CORS_ORIGINS=http://localhost:3000
    volumes:
      - ./backend/generated_audio:/app/generated_audio

networks:
  default:
    driver: bridge
EOF
    
    # Create frontend Dockerfile
    cat > Dockerfile.frontend << 'EOF'
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
EOF
    
    print_status "Docker Compose configuration created"
}

# Main deployment menu
main() {
    echo ""
    echo "Select deployment platform:"
    echo "1. Railway (Recommended - Easy full-stack deployment)"
    echo "2. Vercel (Frontend only - requires separate backend hosting)"
    echo "3. Render (Full-stack deployment)"
    echo "4. Docker Compose (Local production testing)"
    echo "5. All configurations (Create all config files)"
    echo ""
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            check_dependencies
            build_frontend
            prepare_backend
            deploy_railway
            ;;
        2)
            check_dependencies
            build_frontend
            deploy_vercel
            ;;
        3)
            check_dependencies
            build_frontend
            prepare_backend
            deploy_render
            ;;
        4)
            check_dependencies
            prepare_backend
            create_docker_compose
            ;;
        5)
            check_dependencies
            build_frontend
            prepare_backend
            deploy_railway
            deploy_vercel
            deploy_render
            create_docker_compose
            ;;
        *)
            print_error "Invalid choice. Please select 1-5."
            exit 1
            ;;
    esac
    
    echo ""
    print_status "Deployment configuration completed!"
    echo ""
    echo "📋 Next Steps:"
    echo "=============="
    
    case $choice in
        1)
            echo "🚂 Railway Deployment:"
            echo "   1. Install Railway CLI: npm install -g @railway/cli"
            echo "   2. Login: railway login"
            echo "   3. Create new project: railway new"
            echo "   4. Deploy frontend: railway up"
            echo "   5. Deploy backend: cd backend && railway up"
            ;;
        2)
            echo "▲ Vercel Deployment:"
            echo "   1. Install Vercel CLI: npm install -g vercel"
            echo "   2. Login: vercel login"
            echo "   3. Deploy: vercel --prod"
            echo "   ⚠️  Note: You'll need to deploy the backend separately"
            ;;
        3)
            echo "🎨 Render Deployment:"
            echo "   1. Connect your GitHub repository to Render"
            echo "   2. Create a new Blueprint service"
            echo "   3. Use the render.yaml configuration"
            ;;
        4)
            echo "🐳 Docker Compose Testing:"
            echo "   1. Run: docker-compose -f docker-compose.prod.yml up --build"
            echo "   2. Access frontend: http://localhost:3000"
            echo "   3. Access backend: http://localhost:5001"
            ;;
    esac
    
    echo ""
    print_info "🌐 Your AI Music Generation System is ready for production!"
}

# Run the script
main
