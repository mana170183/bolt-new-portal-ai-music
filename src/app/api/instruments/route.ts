import { NextResponse } from 'next/server';
import { getPrisma } from '@/lib/prisma-dynamic';

// List of instruments available for music generation (fallback data)
const defaultInstruments = [
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
    // Try to get prisma client and check database connection
    const prisma = await getPrisma();
    
    // Just check if we can connect (no actual instruments table yet)
    await prisma.user.count();
    
    // Database connection succeeded, return instruments with DB status
    return NextResponse.json({ 
      success: true,
      instruments: defaultInstruments,
      source: "database-connection-verified", 
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error("Database connection error in instruments route:", error);
    
    // Return fallback data if database connection fails
    return NextResponse.json({ 
      success: true,
      instruments: defaultInstruments,
      source: "fallback-data",
      timestamp: new Date().toISOString()
    });
  }
}
