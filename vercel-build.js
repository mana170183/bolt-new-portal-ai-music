/**
 * Custom build script for Vercel to handle Prisma build issues
 * This helps ensure Prisma client generates properly during build
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

// Log helper with timestamp
const log = (message) => {
  console.log(`[${new Date().toISOString()}] ${message}`);
};

// Run command and return its output
const runCommand = (command) => {
  log(`Running: ${command}`);
  try {
    const output = execSync(command, { encoding: 'utf8' });
    return output;
  } catch (error) {
    log(`Command failed: ${command}`);
    log(error.message);
    return null;
  }
};

// Main build function
const main = () => {
  log('Starting custom build process...');
  
  // Ensure environment is properly loaded
  log('Checking environment variables...');
  const hasDbUrl = !!process.env.PRISMA_DATABASE_URL || !!process.env.DATABASE_URL;
  log(`Database URL is ${hasDbUrl ? 'set' : 'NOT SET'}`);
  
  // Generate Prisma client
  log('Generating Prisma client...');
  const prismaResult = runCommand('npx prisma generate');
  log(prismaResult || 'Failed to generate Prisma client');

  // Run Next.js build
  log('Running Next.js build...');
  runCommand('next build');
  
  log('Build process completed.');
};

// Run the build
main();
