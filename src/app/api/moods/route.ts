import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const moods = [
      { id: '1', name: 'Happy', description: 'Upbeat and joyful' },
      { id: '2', name: 'Sad', description: 'Melancholic and emotional' },
      { id: '3', name: 'Energetic', description: 'High energy and exciting' },
      { id: '4', name: 'Calm', description: 'Peaceful and relaxing' },
      { id: '5', name: 'Mysterious', description: 'Dark and intriguing' },
      { id: '6', name: 'Romantic', description: 'Love and passion' },
      { id: '7', name: 'Epic', description: 'Grand and dramatic' },
      { id: '8', name: 'Nostalgic', description: 'Reminiscent and wistful' }
    ];

    return NextResponse.json({
      success: true,
      moods: moods
    });
  } catch (error) {
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch moods',
        details: error.message 
      }, 
      { status: 500 }
    );
  }
}
