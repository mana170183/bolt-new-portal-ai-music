import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Mock user tracks data
    const tracks = [
      {
        id: 'track_1',
        title: 'Sample Track 1',
        url: '/api/tracks/track_1.mp3',
        created_at: new Date().toISOString(),
        genre: 'pop',
        mood: 'upbeat',
        duration: 30,
      },
      {
        id: 'track_2', 
        title: 'Sample Track 2',
        url: '/api/tracks/track_2.mp3',
        created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        genre: 'rock',
        mood: 'energetic',
        duration: 45,
      }
    ];

    return NextResponse.json({
      success: true,
      tracks,
      count: tracks.length,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error fetching tracks:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch tracks' },
      { status: 500 }
    );
  }
}
