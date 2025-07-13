import { NextResponse } from 'next/server';

export async function GET() {
  // Simple 440Hz tone for 2 seconds
  const sampleRate = 22050; // Lower sample rate for smaller file
  const duration = 2; // 2 seconds
  const frequency = 440; // A4 note
  const samples = sampleRate * duration;
  
  // Create a simple sine wave
  const buffer = new ArrayBuffer(samples * 2);
  const view = new DataView(buffer);
  
  for (let i = 0; i < samples; i++) {
    // Generate sine wave with fade in/out to avoid clicks
    const t = i / sampleRate;
    const fadeIn = Math.min(t * 10, 1); // 0.1 second fade in
    const fadeOut = Math.min((duration - t) * 10, 1); // 0.1 second fade out
    const envelope = fadeIn * fadeOut;
    
    const amplitude = Math.sin(2 * Math.PI * frequency * t) * 0.3 * envelope;
    const sample = Math.round(amplitude * 32767);
    view.setInt16(i * 2, sample, true);
  }
  
  // Simple WAV header
  const header = new ArrayBuffer(44);
  const headerView = new DataView(header);
  
  // "RIFF" chunk
  headerView.setUint32(0, 0x52494646, false); // "RIFF"
  headerView.setUint32(4, 36 + buffer.byteLength, true); // File size - 8
  headerView.setUint32(8, 0x57415645, false); // "WAVE"
  
  // "fmt " sub-chunk
  headerView.setUint32(12, 0x666d7420, false); // "fmt "
  headerView.setUint32(16, 16, true); // Sub-chunk size
  headerView.setUint16(20, 1, true); // Audio format (PCM)
  headerView.setUint16(22, 1, true); // Number of channels
  headerView.setUint32(24, sampleRate, true); // Sample rate
  headerView.setUint32(28, sampleRate * 2, true); // Byte rate
  headerView.setUint16(32, 2, true); // Block align
  headerView.setUint16(34, 16, true); // Bits per sample
  
  // "data" sub-chunk
  headerView.setUint32(36, 0x64617461, false); // "data"
  headerView.setUint32(40, buffer.byteLength, true); // Data size
  
  // Combine header and audio data
  const wavFile = new Uint8Array(44 + buffer.byteLength);
  wavFile.set(new Uint8Array(header), 0);
  wavFile.set(new Uint8Array(buffer), 44);
  
  return new NextResponse(wavFile, {
    headers: {
      'Content-Type': 'audio/wav',
      'Content-Length': wavFile.length.toString(),
      'Cache-Control': 'public, max-age=3600',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Accept-Ranges': 'bytes',
      'Content-Disposition': 'inline; filename="demo-audio.wav"'
    }
  });
}
