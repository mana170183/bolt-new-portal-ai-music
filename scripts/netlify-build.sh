#!/bin/bash

# This is a custom build script for Netlify that works around Prisma issues
echo "Starting Netlify build with workarounds..."

# Generate Prisma client first
echo "Generating Prisma client..."
npx prisma generate

# Set environment variable to disable database access during build
export SKIP_DB_OPERATIONS=true
export NEXT_TELEMETRY_DISABLED=1

# Build Next.js app as static site to avoid Prisma SSG issues
echo "Building Next.js app..."
next build
next export

echo "Build completed successfully!"
