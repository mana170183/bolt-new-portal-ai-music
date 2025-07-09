// This is a fallback implementation of the /api/user/quota endpoint
// to prevent 404 errors during initialization

import { NextResponse } from 'next/server';

export async function GET() {
  // Default user quota data
  const quota = {
    used: 0,
    total: 10,
    remaining: 10,
    plan: 'free',
    nextReset: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours from now
  };

  return NextResponse.json({ 
    success: true, 
    quota
  });
}
