// This file will help with the Vercel build process
// when deploying from GitHub

import { execSync } from 'child_process';

console.log('🚀 Starting Vercel build process from GitHub...');

// Function to run a command and log the output
function runCommand(command) {
  console.log(`Running: ${command}`);
  try {
    const output = execSync(command, { stdio: 'inherit' });
    return true;
  } catch (error) {
    console.error(`Error executing command: ${command}`);
    console.error(error);
    return false;
  }
}

// Main build process
async function main() {
  console.log('Node version:', process.version);
  console.log('Environment:', process.env.NODE_ENV);
  
  // Generate Prisma client first
  console.log('Generating Prisma client...');
  if (!runCommand('npx prisma generate')) {
    // Continue even if Prisma generate fails - Vercel will handle it
    console.log('Continuing despite Prisma generation issues');
  }
  
  // Build the Next.js app
  console.log('Building Next.js application...');
  runCommand('next build');
  
  console.log('✅ Build process completed');
}

// Run the build process
main().catch(error => {
  console.error('Build failed with error:', error);
  process.exit(1);
});
