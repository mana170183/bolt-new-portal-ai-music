import { NextResponse } from 'next/server';
import { getPrisma } from '@/lib/prisma-dynamic';

// List of instruments available for music generation
const instruments = [
  { id: "acoustic-guitar", name: "Acoustic Guitar", category: "Strings" },
  { id: "electric-guitar", name: "Electric Guitar", category: "Strings" },
  { id: "piano", name: "Piano", category: "Keys" },
  { id: "violin", name: "Violin", category: "Strings" },
  { id: "cello", name: "Cello", category: "Strings" },
  { id: "flute", name: "Flute", category: "Wind" },
  { id: "clarinet", name: "Clarinet", category: "Wind" },
  { id: "saxophone", name: "Saxophone", category: "Wind" },
  { id: "trumpet", name: "Trumpet", category: "Brass" },
  { id: "trombone", name: "Trombone", category: "Brass" },
  { id: "bass-guitar", name: "Bass Guitar", category: "Strings" },
  { id: "synthesizer", name: "Synthesizer", category: "Electronic" },
  { id: "drums", name: "Drums", category: "Percussion" },
  { id: "percussion", name: "Percussion", category: "Percussion" },
  { id: "harp", name: "Harp", category: "Strings" },
  { id: "accordion", name: "Accordion", category: "Wind" },
  { id: "banjo", name: "Banjo", category: "Strings" },
  { id: "mandolin", name: "Mandolin", category: "Strings" },
  { id: "harmonica", name: "Harmonica", category: "Wind" },
  { id: "organ", name: "Organ", category: "Keys" },
  { id: "ukulele", name: "Ukulele", category: "Strings" },
  { id: "xylophone", name: "Xylophone", category: "Percussion" },
  { id: "marimba", name: "Marimba", category: "Percussion" },
  { id: "vibraphone", name: "Vibraphone", category: "Percussion" },
  { id: "bagpipes", name: "Bagpipes", category: "Wind" },
  { id: "steel-drums", name: "Steel Drums", category: "Percussion" },
  { id: "didgeridoo", name: "Didgeridoo", category: "Wind" },
  { id: "sitar", name: "Sitar", category: "Strings" },
  { id: "tabla", name: "Tabla", category: "Percussion" },
  { id: "koto", name: "Koto", category: "Strings" }
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
