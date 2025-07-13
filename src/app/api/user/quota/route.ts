import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Mock user quota data
    const quota = {
      plan: 'free',
      total_daily: 5,
      remaining_today: 3,
      total_monthly: 50,
      remaining_monthly: 25,
      reset_time: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    };

    return NextResponse.json({
      success: true,
      quota: quota
    });
  } catch (error) {
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch user quota',
        details: error.message 
      }, 
      { status: 500 }
    );
  }
}
