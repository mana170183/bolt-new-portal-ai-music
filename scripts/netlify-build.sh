#!/bin/bash

# This is a custom build script for Netlify that works around Prisma issues
echo "Starting Netlify build with workarounds..."

# Generate Prisma client first
echo "Generating Prisma client..."
npx prisma generate

# Set environment variable to disable database access during build
export SKIP_DB_OPERATIONS=true

# Build Next.js app with a flag to use mock data instead of DB during build
echo "Building Next.js app..."
next build

echo "Build completed successfully!"
