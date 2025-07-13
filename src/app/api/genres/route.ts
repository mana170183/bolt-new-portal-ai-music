import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const genres = [
      { id: '1', name: 'Electronic', description: 'Electronic music with synthesizers and digital sounds' },
      { id: '2', name: 'Rock', description: 'Rock music with guitars and drums' },
      { id: '3', name: 'Jazz', description: 'Jazz music with improvisation and swing' },
      { id: '4', name: 'Classical', description: 'Classical music with orchestral instruments' },
      { id: '5', name: 'Hip Hop', description: 'Hip hop music with beats and rap' },
      { id: '6', name: 'Pop', description: 'Popular music with catchy melodies' },
      { id: '7', name: 'Ambient', description: 'Atmospheric and ambient music' },
      { id: '8', name: 'Folk', description: 'Traditional folk music' }
    ];

    return NextResponse.json({
      success: true,
      genres: genres
    });
  } catch (error) {
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch genres',
        details: error.message 
      }, 
      { status: 500 }
    );
  }
}
