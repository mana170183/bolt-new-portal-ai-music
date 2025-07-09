import { NextResponse } from 'next/server';

const genres = [
  { id: 'pop', name: 'Pop', description: 'Popular music with catchy melodies' },
  { id: 'rock', name: 'Rock', description: 'Guitar-driven energetic music' },
  { id: 'jazz', name: 'Jazz', description: 'Smooth and sophisticated music' },
  { id: 'classical', name: 'Classical', description: 'Orchestral and timeless compositions' },
  { id: 'electronic', name: 'Electronic', description: 'Synthesized and digital sounds' },
  { id: 'blues', name: 'Blues', description: 'Soulful and emotional music' },
  { id: 'country', name: 'Country', description: 'Folk-inspired storytelling music' },
  { id: 'hip-hop', name: 'Hip-Hop', description: 'Rhythmic and lyrical music' },
  { id: 'reggae', name: 'Reggae', description: 'Caribbean-influenced relaxed beats' },
  { id: 'folk', name: 'Folk', description: 'Traditional and acoustic music' },
];

export async function GET() {
  try {
    return NextResponse.json({
      success: true,
      genres,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error fetching genres:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch genres' },
      { status: 500 }
    );
  }
}
