import { NextResponse } from 'next/server';
import { getPrisma } from '@/lib/prisma-dynamic';

// List of instruments available for music generation
const instruments = [
  "Acoustic Guitar",
  "Electric Guitar",
  "Piano",
  "Violin",
  "Cello",
  "Flute",
  "Clarinet",
  "Saxophone",
  "Trumpet",
  "Trombone",
  "Bass Guitar",
  "Synthesizer",
  "Drums",
  "Percussion",
  "Harp",
  "Accordion",
  "Banjo",
  "Mandolin",
  "Harmonica",
  "Organ",
  "Ukulele",
  "Xylophone",
  "Marimba",
  "Vibraphone",
  "Bagpipes",
  "Steel Drums",
  "Didgeridoo",
  "Sitar",
  "Tabla",
  "Koto",
  "Shamisen",
  "Balalaika",
  "Theremin",
  "Vocoder",
  "Kalimba",
  "Oboe",
  "Bassoon",
  "French Horn",
  "Tuba",
  "Erhu",
  "Guzheng",
  "Pipa",
  "Shakuhachi",
  "Gamelan",
  "Dulcimer",
  "Hurdy-Gurdy"
];

export async function GET() {
  try {
    // This is just a placeholder - in the future, you could store instruments in the database
    // For now, we'll return a static list
    return NextResponse.json({ 
      success: true,
      instruments
    });
  } catch (error) {
    console.error('Error retrieving instruments:', error);
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : String(error) 
    }, { status: 500 });
  }
}
