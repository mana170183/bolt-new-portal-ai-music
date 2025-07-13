import { NextResponse } from 'next/server';

export async function GET() {
  // Return a simple sine wave audio as base64 encoded MP3
  // This is a very short test tone for demo purposes
  const testAudioBase64 = `data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAABIADAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwP////////////////////////////////////////////////////////////////8AAAAATGF2YzU4LjEzAAAAAAAAAAAAAAAAJAAAAAAAAAAAASDs90hvAAAAAAAAAAAAAAAAAAAA`;
  
  try {
    // For now, just redirect to a known working audio file
    return NextResponse.redirect('https://www.soundjay.com/misc/sounds/bell-ringing-05.wav');
  } catch (error) {
    return NextResponse.json(
      { error: 'Audio not available' },
      { status: 404 }
    );
  }
}
