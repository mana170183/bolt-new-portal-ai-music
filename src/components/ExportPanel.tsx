'use client'

import { useState } from 'react'
import { Download, FileAudio, Disc, Music, Layers } from 'lucide-react'
import { CompositionResult, ExportOptions } from '@/types/music'

interface ExportPanelProps {
  composition: CompositionResult | null
}

export default function ExportPanel({ composition }: ExportPanelProps) {
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'mp3',
    quality: 'high',
    includeStems: false,
    includeMidi: false,
    sampleRate: 44100,
    bitrate: 320
  })
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async () => {
    if (!composition) return

    setIsExporting(true)
    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          compositionId: composition.id,
          options: exportOptions
        }),
      })

      if (!response.ok) {
        throw new Error('Export failed')
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${composition.title}.${exportOptions.format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
    }
  }

  if (!composition) {
    return (
      <div className="p-6 text-center">
        <Download className="h-12 w-12 text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-400 mb-2">No Composition Selected</h3>
        <p className="text-gray-500 text-sm">
          Select a composition to export
        </p>
      </div>
    )
  }

  const getEstimatedSize = () => {
    const duration = composition.metadata.duration
    const { format, quality, includeStems } = exportOptions
    
    let baseSizeMB = 0
    
    switch (format) {
      case 'mp3':
        baseSizeMB = quality === 'high' ? duration * 0.4 : duration * 0.2
        break
      case 'wav':
        baseSizeMB = duration * 1.4
        break
      case 'flac':
        baseSizeMB = duration * 0.8
        break
      case 'midi':
        baseSizeMB = 0.1
        break
    }
    
    if (includeStems && format !== 'midi') {
      baseSizeMB *= (composition.metadata.instruments.length + 1)
    }
    
    return Math.round(baseSizeMB * 10) / 10
  }

  return (
    <div className="p-6 space-y-6">
      {/* Format Selection */}
      <div>
        <h3 className="text-lg font-medium mb-4">Export Format</h3>
        <div className="grid grid-cols-2 gap-3">
          {[
            { value: 'mp3', label: 'MP3', icon: FileAudio, desc: 'Compressed, widely compatible' },
            { value: 'wav', label: 'WAV', icon: Music, desc: 'Uncompressed, high quality' },
            { value: 'flac', label: 'FLAC', icon: Disc, desc: 'Lossless compression' },
            { value: 'midi', label: 'MIDI', icon: Music, desc: 'Musical notation data' }
          ].map(({ value, label, icon: Icon, desc }) => (
            <button
              key={value}
              onClick={() => setExportOptions(prev => ({ ...prev, format: value as any }))}
              className={`p-3 text-left rounded-lg border transition-all ${
                exportOptions.format === value
                  ? 'border-purple-500 bg-purple-500/20'
                  : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
              }`}
            >
              <div className="flex items-center space-x-2 mb-1">
                <Icon className="h-4 w-4" />
                <span className="font-medium text-sm">{label}</span>
              </div>
              <p className="text-xs text-gray-400">{desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Quality Settings */}
      {exportOptions.format !== 'midi' && (
        <div>
          <h3 className="text-lg font-medium mb-4">Quality Settings</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Quality
              </label>
              <select
                value={exportOptions.quality}
                onChange={(e) => setExportOptions(prev => ({ 
                  ...prev, 
                  quality: e.target.value as any 
                }))}
                className="form-select"
              >
                <option value="low">Low (128 kbps)</option>
                <option value="medium">Medium (192 kbps)</option>
                <option value="high">High (320 kbps)</option>
                {exportOptions.format !== 'mp3' && (
                  <option value="lossless">Lossless</option>
                )}
              </select>
            </div>

            {exportOptions.format === 'wav' && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Sample Rate
                </label>
                <select
                  value={exportOptions.sampleRate}
                  onChange={(e) => setExportOptions(prev => ({ 
                    ...prev, 
                    sampleRate: Number(e.target.value) 
                  }))}
                  className="form-select"
                >
                  <option value={44100}>44.1 kHz (CD Quality)</option>
                  <option value={48000}>48 kHz (Studio Standard)</option>
                  <option value={96000}>96 kHz (High Resolution)</option>
                </select>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Advanced Options */}
      <div>
        <h3 className="text-lg font-medium mb-4">Advanced Options</h3>
        
        <div className="space-y-3">
          <label className="flex items-center space-x-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700 cursor-pointer hover:border-gray-600 transition-colors">
            <input
              type="checkbox"
              checked={exportOptions.includeStems}
              onChange={(e) => setExportOptions(prev => ({ 
                ...prev, 
                includeStems: e.target.checked 
              }))}
              className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
            />
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <Layers className="h-4 w-4" />
                <span className="font-medium text-sm">Include Individual Stems</span>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                Export each instrument as a separate track
              </p>
            </div>
          </label>

          <label className="flex items-center space-x-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700 cursor-pointer hover:border-gray-600 transition-colors">
            <input
              type="checkbox"
              checked={exportOptions.includeMidi}
              onChange={(e) => setExportOptions(prev => ({ 
                ...prev, 
                includeMidi: e.target.checked 
              }))}
              className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
            />
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <Music className="h-4 w-4" />
                <span className="font-medium text-sm">Include MIDI File</span>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                Add MIDI data for further editing
              </p>
            </div>
          </label>
        </div>
      </div>

      {/* Export Summary */}
      <div className="border-t border-gray-700 pt-6">
        <h3 className="text-lg font-medium mb-4">Export Summary</h3>
        
        <div className="bg-gray-800/50 rounded-lg p-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Composition:</span>
            <span>{composition.title}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Format:</span>
            <span className="uppercase">{exportOptions.format}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Quality:</span>
            <span className="capitalize">{exportOptions.quality}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Duration:</span>
            <span>{Math.round(composition.metadata.duration)}s</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Estimated Size:</span>
            <span>{getEstimatedSize()} MB</span>
          </div>
          {exportOptions.includeStems && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Stems:</span>
              <span>{composition.metadata.instruments.length} tracks</span>
            </div>
          )}
        </div>
      </div>

      {/* Export Button */}
      <button
        onClick={handleExport}
        disabled={isExporting}
        className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isExporting ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
            Exporting...
          </div>
        ) : (
          <div className="flex items-center justify-center">
            <Download className="mr-2 h-5 w-5" />
            Export {exportOptions.format.toUpperCase()}
          </div>
        )}
      </button>

      {/* Quick Export Presets */}
      <div className="border-t border-gray-700 pt-6">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Quick Presets</h3>
        <div className="space-y-2">
          <button
            onClick={() => setExportOptions({
              format: 'mp3',
              quality: 'high',
              includeStems: false,
              includeMidi: false,
              sampleRate: 44100,
              bitrate: 320
            })}
            className="w-full p-3 text-left rounded-lg border border-gray-700 bg-gray-800/50 hover:border-gray-600 transition-colors"
          >
            <div className="font-medium text-sm">Standard MP3</div>
            <div className="text-xs text-gray-400">High quality, small size</div>
          </button>
          
          <button
            onClick={() => setExportOptions({
              format: 'wav',
              quality: 'lossless',
              includeStems: true,
              includeMidi: true,
              sampleRate: 48000,
              bitrate: 1411
            })}
            className="w-full p-3 text-left rounded-lg border border-gray-700 bg-gray-800/50 hover:border-gray-600 transition-colors"
          >
            <div className="font-medium text-sm">Professional Package</div>
            <div className="text-xs text-gray-400">WAV + stems + MIDI</div>
          </button>
        </div>
      </div>
    </div>
  )
}
