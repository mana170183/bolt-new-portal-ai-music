import React, { useState } from 'react'
import { 
  Play, 
  Pause, 
  Download, 
  Loader2, 
  Music, 
  Settings,
  Volume2,
  Clock
} from 'lucide-react'

const MusicGenerator = () => {
  const [prompt, setPrompt] = useState('')
  const [duration, setDuration] = useState(30)
  const [genre, setGenre] = useState('pop')
  const [mood, setMood] = useState('upbeat')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedTrack, setGeneratedTrack] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const genres = [
    'Pop', 'Rock', 'Electronic', 'Classical', 'Jazz', 'Hip Hop', 
    'Country', 'Folk', 'Ambient', 'Cinematic'
  ]

  const moods = [
    'Upbeat', 'Calm', 'Energetic', 'Melancholic', 'Mysterious', 
    'Romantic', 'Epic', 'Peaceful', 'Dramatic', 'Playful'
  ]

  const handleGenerate = async () => {
    setIsGenerating(true)
    
    // Simulate API call
    setTimeout(() => {
      setGeneratedTrack({
        id: Date.now(),
        title: `${mood} ${genre} Track`,
        duration: duration,
        url: '#', // This would be the actual audio URL
        downloadUrl: '#'
      })
      setIsGenerating(false)
    }, 3000)
  }

  const togglePlayback = () => {
    setIsPlaying(!isPlaying)
  }

  return (
    <section id="generator" className="py-20 bg-gradient-to-br from-gray-50 to-primary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            <span className="gradient-text">Music Generator</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Describe the music you want and let our AI create it for you. 
            It's that simple!
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="card p-8">
            {/* Main Input */}
            <div className="mb-8">
              <label className="block text-lg font-semibold text-gray-900 mb-3">
                Describe your music
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g., An upbeat pop song with electronic beats, perfect for a workout video..."
                className="input-field h-32 resize-none"
                maxLength={500}
              />
              <div className="text-right text-sm text-gray-500 mt-2">
                {prompt.length}/500 characters
              </div>
            </div>

            {/* Settings Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {/* Duration */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2 flex items-center">
                  <Clock className="h-4 w-4 mr-2" />
                  Duration
                </label>
                <select
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  className="input-field"
                >
                  <option value={15}>15 seconds</option>
                  <option value={30}>30 seconds</option>
                  <option value={60}>1 minute</option>
                  <option value={120}>2 minutes</option>
                  <option value={180}>3 minutes</option>
                </select>
              </div>

              {/* Genre */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2 flex items-center">
                  <Music className="h-4 w-4 mr-2" />
                  Genre
                </label>
                <select
                  value={genre}
                  onChange={(e) => setGenre(e.target.value)}
                  className="input-field"
                >
                  {genres.map(g => (
                    <option key={g} value={g.toLowerCase()}>{g}</option>
                  ))}
                </select>
              </div>

              {/* Mood */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2 flex items-center">
                  <Settings className="h-4 w-4 mr-2" />
                  Mood
                </label>
                <select
                  value={mood}
                  onChange={(e) => setMood(e.target.value)}
                  className="input-field"
                >
                  {moods.map(m => (
                    <option key={m} value={m.toLowerCase()}>{m}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Generate Button */}
            <div className="text-center mb-8">
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !prompt.trim()}
                className="btn-primary text-lg px-12 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Generating Music...
                  </>
                ) : (
                  <>
                    <Music className="h-5 w-5 mr-2" />
                    Generate Music
                  </>
                )}
              </button>
            </div>

            {/* Generated Track */}
            {generatedTrack && (
              <div className="bg-gradient-to-r from-primary-50 to-accent-50 rounded-xl p-6 animate-fade-in">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-1">
                      {generatedTrack.title}
                    </h3>
                    <p className="text-gray-600">
                      Duration: {generatedTrack.duration} seconds
                    </p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={togglePlayback}
                      className="bg-white hover:bg-gray-50 p-3 rounded-full shadow-lg transition-all duration-200 hover:scale-105"
                    >
                      {isPlaying ? (
                        <Pause className="h-6 w-6 text-primary-600" />
                      ) : (
                        <Play className="h-6 w-6 text-primary-600" />
                      )}
                    </button>
                    <button className="bg-white hover:bg-gray-50 p-3 rounded-full shadow-lg transition-all duration-200 hover:scale-105">
                      <Volume2 className="h-6 w-6 text-gray-600" />
                    </button>
                    <button className="btn-primary flex items-center space-x-2">
                      <Download className="h-4 w-4" />
                      <span>Download</span>
                    </button>
                  </div>
                </div>

                {/* Audio Waveform Placeholder */}
                <div className="bg-white rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-center h-16 bg-gradient-to-r from-primary-100 to-accent-100 rounded">
                    <div className="flex items-end space-x-1">
                      {[...Array(20)].map((_, i) => (
                        <div
                          key={i}
                          className={`bg-gradient-to-t from-primary-500 to-accent-500 rounded-sm transition-all duration-300 ${
                            isPlaying ? 'animate-pulse' : ''
                          }`}
                          style={{
                            width: '4px',
                            height: `${Math.random() * 40 + 10}px`
                          }}
                        />
                      ))}
                    </div>
                  </div>
                </div>

                <div className="text-center text-sm text-gray-600">
                  🎉 Your AI-generated music is ready! This track is 100% royalty-free.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

export default MusicGenerator