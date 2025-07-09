'use client'

import { useState } from 'react'
import { Wand2, Music, Volume2 } from 'lucide-react'
import { MusicGenerationRequest, MusicGenre, MusicMood, Instrument } from '@/types/music'

interface GenerationPanelProps {
  onGenerate: (request: MusicGenerationRequest) => void
  isGenerating: boolean
  userId: string
}

const GENRES: MusicGenre[] = [
  'pop', 'rock', 'jazz', 'blues', 'classical', 'electronic',
  'hip-hop', 'country', 'folk', 'reggae', 'metal', 'punk',
  'indie', 'ambient', 'house', 'techno', 'dubstep', 'trap'
]

const MOODS: MusicMood[] = [
  'happy', 'sad', 'energetic', 'calm', 'mysterious', 'romantic',
  'aggressive', 'melancholic', 'uplifting', 'dark', 'nostalgic',
  'peaceful', 'intense', 'playful', 'dramatic', 'dreamy'
]

const INSTRUMENTS: Instrument[] = [
  'piano', 'guitar', 'bass', 'drums', 'violin', 'saxophone',
  'trumpet', 'cello', 'flute', 'synthesizer', 'organ', 'harp',
  'accordion', 'banjo', 'mandolin', 'harmonica', 'xylophone'
]

export default function GenerationPanel({ onGenerate, isGenerating, userId }: GenerationPanelProps) {
  const [prompt, setPrompt] = useState('')
  const [lyrics, setLyrics] = useState('')
  const [genre, setGenre] = useState<MusicGenre>('pop')
  const [mood, setMood] = useState<MusicMood>('happy')
  const [duration, setDuration] = useState(30)
  const [tempo, setTempo] = useState(120)
  const [keySignature, setKeySignature] = useState('C')
  const [timeSignature, setTimeSignature] = useState('4/4')
  const [selectedInstruments, setSelectedInstruments] = useState<Instrument[]>(['piano', 'guitar', 'bass', 'drums'])

  const handleInstrumentToggle = (instrument: Instrument) => {
    setSelectedInstruments(prev => 
      prev.includes(instrument)
        ? prev.filter(i => i !== instrument)
        : [...prev, instrument]
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!prompt.trim()) return

    const request: MusicGenerationRequest = {
      prompt: prompt.trim(),
      lyrics: lyrics.trim() || undefined,
      genre,
      mood,
      duration,
      tempo,
      keySignature,
      timeSignature,
      instruments: selectedInstruments,
      userId
    }

    onGenerate(request)
  }

  return (
    <div className="p-6 space-y-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Prompt */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Music Description
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the music you want to create... e.g., 'An upbeat pop song with electronic elements for a commercial'"
            className="form-input h-20 resize-none"
            required
          />
        </div>

        {/* Lyrics (Optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Lyrics (Optional)
          </label>
          <textarea
            value={lyrics}
            onChange={(e) => setLyrics(e.target.value)}
            placeholder="Enter lyrics to generate music that matches the mood and rhythm..."
            className="form-input h-24 resize-none"
          />
        </div>

        {/* Genre and Mood */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Genre
            </label>
            <select
              value={genre}
              onChange={(e) => setGenre(e.target.value as MusicGenre)}
              className="form-select"
            >
              {GENRES.map(g => (
                <option key={g} value={g}>
                  {g.charAt(0).toUpperCase() + g.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Mood
            </label>
            <select
              value={mood}
              onChange={(e) => setMood(e.target.value as MusicMood)}
              className="form-select"
            >
              {MOODS.map(m => (
                <option key={m} value={m}>
                  {m.charAt(0).toUpperCase() + m.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Duration and Tempo */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Duration (seconds)
            </label>
            <input
              type="range"
              min="15"
              max="180"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="text-center text-sm text-gray-400 mt-1">{duration}s</div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Tempo (BPM)
            </label>
            <input
              type="range"
              min="60"
              max="200"
              value={tempo}
              onChange={(e) => setTempo(Number(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="text-center text-sm text-gray-400 mt-1">{tempo} BPM</div>
          </div>
        </div>

        {/* Key and Time Signature */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Key Signature
            </label>
            <select
              value={keySignature}
              onChange={(e) => setKeySignature(e.target.value)}
              className="form-select"
            >
              {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'].map(key => (
                <option key={key} value={key}>{key}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Time Signature
            </label>
            <select
              value={timeSignature}
              onChange={(e) => setTimeSignature(e.target.value)}
              className="form-select"
            >
              <option value="4/4">4/4</option>
              <option value="3/4">3/4</option>
              <option value="2/4">2/4</option>
              <option value="6/8">6/8</option>
              <option value="12/8">12/8</option>
            </select>
          </div>
        </div>

        {/* Instruments */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Instruments ({selectedInstruments.length} selected)
          </label>
          <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
            {INSTRUMENTS.map(instrument => (
              <button
                key={instrument}
                type="button"
                onClick={() => handleInstrumentToggle(instrument)}
                className={`p-2 text-sm rounded-lg border transition-all ${
                  selectedInstruments.includes(instrument)
                    ? 'border-purple-500 bg-purple-500/20 text-purple-300'
                    : 'border-gray-700 bg-gray-800/50 text-gray-400 hover:border-gray-600'
                }`}
              >
                {instrument.charAt(0).toUpperCase() + instrument.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Generate Button */}
        <button
          type="submit"
          disabled={isGenerating || !prompt.trim()}
          className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Generating Music...
            </div>
          ) : (
            <div className="flex items-center justify-center">
              <Wand2 className="mr-2 h-5 w-5" />
              Generate Music
            </div>
          )}
        </button>
      </form>

      {/* Quick Presets */}
      <div className="border-t border-gray-800 pt-6">
        <h3 className="text-sm font-medium text-gray-300 mb-3">Quick Presets</h3>
        <div className="space-y-2">
          <button
            onClick={() => {
              setPrompt('Upbeat commercial pop music with electronic elements')
              setGenre('pop')
              setMood('energetic')
              setSelectedInstruments(['piano', 'guitar', 'bass', 'drums', 'synthesizer'])
            }}
            className="w-full p-3 text-left rounded-lg border border-gray-700 bg-gray-800/50 hover:border-gray-600 transition-colors"
          >
            <div className="font-medium text-sm">Commercial Pop</div>
            <div className="text-xs text-gray-400">Upbeat, energetic, perfect for ads</div>
          </button>
          
          <button
            onClick={() => {
              setPrompt('Relaxing ambient background music with soft piano')
              setGenre('ambient')
              setMood('calm')
              setSelectedInstruments(['piano', 'synthesizer', 'violin'])
            }}
            className="w-full p-3 text-left rounded-lg border border-gray-700 bg-gray-800/50 hover:border-gray-600 transition-colors"
          >
            <div className="font-medium text-sm">Ambient Background</div>
            <div className="text-xs text-gray-400">Calm, relaxing, perfect for focus</div>
          </button>
          
          <button
            onClick={() => {
              setPrompt('Epic cinematic orchestral music with dramatic build-up')
              setGenre('classical')
              setMood('dramatic')
              setSelectedInstruments(['violin', 'cello', 'trumpet', 'drums', 'organ'])
            }}
            className="w-full p-3 text-left rounded-lg border border-gray-700 bg-gray-800/50 hover:border-gray-600 transition-colors"
          >
            <div className="font-medium text-sm">Epic Cinematic</div>
            <div className="text-xs text-gray-400">Dramatic, powerful, orchestral</div>
          </button>
        </div>
      </div>
    </div>
  )
}
