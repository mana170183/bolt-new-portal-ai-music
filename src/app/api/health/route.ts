import { NextResponse } from 'next/server';

export async function GET() {
  try {
    return NextResponse.json({
      success: true,
      message: 'Health check passed',
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    });
  } catch (error) {
    return NextResponse.json(
      { 
        success: false, 
        error: 'Health check failed',
        details: error.message 
      }, 
      { status: 500 }
    );
  }
}
