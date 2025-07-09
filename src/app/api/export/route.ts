import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs'
import { prisma } from '@/lib/prisma'

export async function POST(request: NextRequest) {
  try {
    const { userId } = auth()
    
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { compositionId, options } = await request.json()

    // Get composition
    const composition = await prisma.composition.findUnique({
      where: { id: compositionId },
      include: { user: true }
    })

    if (!composition) {
      return NextResponse.json({ error: 'Composition not found' }, { status: 404 })
    }

    // Check permissions
    if (composition.user.clerkId !== userId) {
      return NextResponse.json({ error: 'Access denied' }, { status: 403 })
    }

    // Create export record
    const exportRecord = await prisma.export.create({
      data: {
        compositionId,
        format: options.format,
        quality: options.quality,
        fileUrl: '', // Will be populated after processing
        fileSize: 0,
        isProcessing: true
      }
    })

    // Process export (this would be async in production)
    const exportedFile = await processExport(composition, options)

    // Update export record
    await prisma.export.update({
      where: { id: exportRecord.id },
      data: {
        fileUrl: exportedFile.url,
        fileSize: exportedFile.size,
        isProcessing: false
      }
    })

    // Return file for download
    const response = await fetch(exportedFile.url)
    const buffer = await response.arrayBuffer()

    return new NextResponse(buffer, {
      headers: {
        'Content-Type': getContentType(options.format),
        'Content-Disposition': `attachment; filename="${composition.title}.${options.format}"`
      }
    })

  } catch (error) {
    console.error('Export error:', error)
    return NextResponse.json(
      { error: 'Export failed' },
      { status: 500 }
    )
  }
}

async function processExport(composition: any, options: any) {
  // This would integrate with audio processing services
  // For now, return the original audio URL
  return {
    url: composition.audioUrl,
    size: Math.floor(Math.random() * 10000000) + 1000000 // Mock size
  }
}

function getContentType(format: string): string {
  const contentTypes: Record<string, string> = {
    mp3: 'audio/mpeg',
    wav: 'audio/wav',
    flac: 'audio/flac',
    midi: 'audio/midi'
  }
  return contentTypes[format] || 'application/octet-stream'
}
