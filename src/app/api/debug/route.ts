import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    success: true,
    config: {
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      NODE_ENV: process.env.NODE_ENV,
    },
    timestamp: new Date().toISOString()
  });
}
