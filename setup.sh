#!/bin/bash

# 🎵 Portal AI Music - Quick Setup Script
# This script sets up the comprehensive AI music generation platform

set -e

echo "🎵 Portal AI Music - Comprehensive Platform Setup"
echo "================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version must be 18 or higher. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Generate Prisma client
echo "🗄️  Generating Prisma client..."
npx prisma generate

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "⚙️  Creating .env.local from template..."
    cp .env.example .env.local
    echo "📝 Please edit .env.local with your API keys and database URL"
fi

# Check if database URL is configured
if grep -q "postgresql://username:password@host:5432/database" .env.local; then
    echo "⚠️  WARNING: Please configure your database URL in .env.local"
    echo "   You can use Neon (neon.tech) for a free PostgreSQL database"
fi

# Check if Clerk keys are configured
if grep -q "pk_test_..." .env.local; then
    echo "⚠️  WARNING: Please configure your Clerk authentication keys in .env.local"
    echo "   Sign up at clerk.com to get your API keys"
fi

echo ""
echo "🚀 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Configure your environment variables in .env.local"
echo "2. Set up your database (recommended: Neon)"
echo "3. Configure authentication (Clerk)"
echo "4. Add AI API keys (OpenAI, Replicate)"
echo "5. Push database schema: npx prisma db push"
echo "6. Start development server: npm run dev"
echo ""
echo "📚 Documentation: README_COMPREHENSIVE.md"
echo "📋 Implementation Timeline: IMPLEMENTATION_TIMELINE.md"
echo "🌟 Live Demo: http://localhost:3000 (after npm run dev)"
echo ""
echo "Happy music creating! 🎵✨"
