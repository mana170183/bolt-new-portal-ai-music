import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Mock user quota data
    const quota = {
      plan: 'free',
      total_monthly: 10,
      used_monthly: 2,
      remaining_monthly: 8,
      total_daily: 3,
      used_daily: 1,
      remaining_today: 2,
      reset_time: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    };

    return NextResponse.json({
      success: true,
      quota,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error fetching user quota:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch user quota' },
      { status: 500 }
    );
  }
}
