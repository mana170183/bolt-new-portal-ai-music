import React, { useState, useEffect } from 'react'
import { 
  Play, 
  Pause, 
  Download, 
  Loader2, 
  Music, 
  Settings,
  Volume2,
  Clock,
  AlertCircle,
  CheckCircle,
  Zap
} from 'lucide-react'
import { musicAPI, metadataAPI, authAPI } from '../services/api'
import { healthAPI } from '../services/api'

const MusicGenerator = () => {
  const [prompt, setPrompt] = useState('')
  const [duration, setDuration] = useState(30)
  const [genre, setGenre] = useState('pop')
  const [mood, setMood] = useState('upbeat')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedTrack, setGeneratedTrack] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [genres, setGenres] = useState([])
  const [moods, setMoods] = useState([])
  const [userQuota, setUserQuota] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    initializeComponent()
  }, [])

  const initializeComponent = async () => {
    try {
      // First check if backend is available
      try {
        const healthData = await healthAPI.checkHealth()
        console.log('Backend health check passed:', healthData)
        setSuccess('Connected to backend server successfully!')
      } catch (healthError) {
        console.error('Backend health check failed:', healthError)
        if (healthError.name === 'TimeoutError') {
          setError('Backend server timeout. Please ensure the Flask server is running on port 5000 and try refreshing the page.')
        } else if (healthError.message.includes('Failed to fetch') || healthError.message.includes('ECONNREFUSED')) {
          setError('Cannot connect to backend server. Please start the Flask server by running "./start-backend.sh" (Linux/Mac) or "start-backend.bat" (Windows) in a separate terminal, then refresh this page.')
        } else {
          setError(`Backend server error: ${healthError.message}. Please ensure the Flask server is running on port 5000 and try refreshing the page.`)
        }
        return
      }

      // Check authentication
      try {
        if (!authAPI.isAuthenticated()) {
          await authAPI.generateToken('demo_user', 'free')
        }
        setIsAuthenticated(true)
      } catch (authError) {
        console.error('Authentication failed:', authError)
        setError(`Authentication failed: ${authError.message || 'Unknown error'}. Please check the backend server logs.`)
        return
      }

      // Load metadata
      try {
        const [genresData, moodsData, quotaData] = await Promise.all([
          metadataAPI.getGenres(),
          metadataAPI.getMoods(),
          musicAPI.getUserQuota()
        ])

        if (genresData.status === 'success') {
          setGenres(genresData.genres)
        }
        if (moodsData.status === 'success') {
          setMoods(moodsData.moods)
        }
        if (quotaData.status === 'success') {
          setUserQuota(quotaData.quota)
        }
      } catch (metadataError) {
        console.error('Failed to load metadata:', metadataError)
        // Set default values if API fails
        setGenres([
          {id: 'pop', name: 'Pop', description: 'Catchy, mainstream melodies'},
          {id: 'rock', name: 'Rock', description: 'Guitar-driven, energetic'},
          {id: 'electronic', name: 'Electronic', description: 'Synthesized, digital sounds'}
        ])
        setMoods([
          {id: 'upbeat', name: 'Upbeat', description: 'Happy, energetic feeling'},
          {id: 'calm', name: 'Calm', description: 'Peaceful, relaxing'},
          {id: 'energetic', name: 'Energetic', description: 'High-energy, motivating'}
        ])
        // Don't show error for metadata loading failure if auth worked
        console.warn('Using default metadata due to API error')
      }
    } catch (error) {
      console.error('Initialization error:', error)
      setError(`Failed to initialize: ${error.message || 'Unknown error'}. Please ensure the backend server is running and refresh the page.`)
    }
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a music description')
      return
    }

    if (userQuota && userQuota.remaining_today === 0) {
      setError('Daily quota exceeded. Please upgrade your plan or try again tomorrow.')
      return
    }

    setIsGenerating(true)
    setError('')
    setSuccess('')
    
    try {
      const result = await musicAPI.generateMusic(prompt, {
        duration,
        genre,
        mood
      })

      if (result.status === 'success') {
        setGeneratedTrack(result.track)
        setSuccess('Music generated successfully!')
        
        // Update quota
        const updatedQuota = await musicAPI.getUserQuota()
        if (updatedQuota.status === 'success') {
          setUserQuota(updatedQuota.quota)
        }
      } else {
        setError(result.message || 'Failed to generate music')
      }
    } catch (error) {
      console.error('Generation error:', error)
      if (error.response?.status === 429) {
        setError('Rate limit exceeded. Please try again later.')
      } else if (error.response?.status === 401) {
        setError('Authentication failed. Please refresh the page.')
        setIsAuthenticated(false)
      } else {
        setError(error.message || 'Failed to generate music. Please try again.')
      }
    } finally {
      setIsGenerating(false)
    }
  }

  const togglePlayback = () => {
    setIsPlaying(!isPlaying)
  }

  const handleDownload = () => {
    if (generatedTrack?.download_url) {
      window.open(generatedTrack.download_url, '_blank')
    }
  }

  const canGenerate = () => {
    return prompt.trim() && 
           !isGenerating && 
           isAuthenticated && 
           (userQuota?.remaining_today !== 0)
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
            Professional quality, royalty-free music in seconds.
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="card p-8">
            {/* User Quota Display */}
            {userQuota && (
              <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Zap className="h-5 w-5 text-blue-600" />
                    <span className="font-semibold text-gray-900">
                      Plan: {userQuota.plan.charAt(0).toUpperCase() + userQuota.plan.slice(1)}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {userQuota.daily_limit > 0 ? (
                      <>Remaining today: {userQuota.remaining_today}/{userQuota.daily_limit}</>
                    ) : (
                      'Unlimited generations'
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Error/Success Messages */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
                <span className="text-red-700">{error}</span>
              </div>
            )}

            {success && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                <span className="text-green-700">{success}</span>
              </div>
            )}

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
              <div className="flex justify-between text-sm text-gray-500 mt-2">
                <span>{prompt.length}/500 characters</span>
                <span className="text-xs">💡 Be specific for better results</span>
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
                    <option key={g.id} value={g.id}>{g.name}</option>
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
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Generate Button */}
            <div className="text-center mb-8">
              <button
                onClick={handleGenerate}
                disabled={!canGenerate()}
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
              
              {!isAuthenticated && (
                <p className="text-sm text-gray-500 mt-2">
                  Authentication required. Please refresh the page.
                </p>
              )}
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
                      Duration: {generatedTrack.duration} seconds • {generatedTrack.genre} • {generatedTrack.mood}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      License: 100% Royalty-Free
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
                    <button 
                      onClick={handleDownload}
                      className="btn-primary flex items-center space-x-2"
                    >
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
                  🎉 Your AI-generated music is ready! This track is 100% royalty-free and ready for commercial use.
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