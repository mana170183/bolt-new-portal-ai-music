import React, { useState, useEffect, useRef } from 'react'
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
  const audioRef = useRef(null)

  useEffect(() => {
    initializeComponent()
  }, [])

  const initializeComponent = async () => {
    try {
      // First check if backend is available
      try {
        console.log('Starting health check...')
        const healthResponse = await fetch('http://localhost:9000/health', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          // Add timeout to prevent hanging
          signal: AbortSignal.timeout(10000) // 10 second timeout
        })
        console.log('Health response status:', healthResponse.status)
        console.log('Health response headers:', Object.fromEntries(healthResponse.headers))
        
        if (!healthResponse.ok) {
          const errorText = await healthResponse.text()
          console.log('Health response error body:', errorText)
          throw new Error(`Health check failed: ${healthResponse.status} - ${errorText}`)
        }
        const healthData = await healthResponse.json()
        console.log('Backend health check passed:', healthData)
      } catch (healthError) {
        console.error('Backend health check failed:', healthError)
        if (healthError.name === 'TimeoutError') {
          setError('Backend server is taking too long to respond. Please check if the Flask server is running.')
        } else if (healthError.message.includes('Failed to fetch') || healthError.message.includes('ECONNREFUSED')) {
          setError('Cannot connect to backend server. Please start the Flask server by running the backend startup script in a separate terminal.')
        } else {
          setError(`Backend server error: ${healthError.message}. Please ensure the Flask server is running.`)
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

  const togglePlayback = async () => {
    if (audioRef.current && generatedTrack) {
      try {
        console.log('Toggle playback - Current state:', isPlaying)
        console.log('Audio URL:', generatedTrack.url)
        console.log('Audio element ready state:', audioRef.current.readyState)
        console.log('Audio element src:', audioRef.current.src)
        
        if (isPlaying) {
          audioRef.current.pause()
          setIsPlaying(false)
          console.log('Audio paused')
        } else {
          // Reset any previous errors
          setError('')
          
          // Ensure the audio src is set
          if (audioRef.current.src !== generatedTrack.url) {
            console.log('Setting audio src to:', generatedTrack.url)
            // Build full URL if the track URL is relative
            const audioUrl = generatedTrack.url.startsWith('http') 
              ? generatedTrack.url 
              : `http://localhost:9000${generatedTrack.url}`
            console.log('Full audio URL:', audioUrl)
            audioRef.current.src = audioUrl
            // Wait for the audio to load
            await new Promise((resolve, reject) => {
              const handleCanPlay = () => {
                audioRef.current.removeEventListener('canplay', handleCanPlay)
                audioRef.current.removeEventListener('error', handleError)
                resolve()
              }
              const handleError = (e) => {
                audioRef.current.removeEventListener('canplay', handleCanPlay)
                audioRef.current.removeEventListener('error', handleError)
                reject(e)
              }
              audioRef.current.addEventListener('canplay', handleCanPlay)
              audioRef.current.addEventListener('error', handleError)
            })
          }
          
          console.log('Attempting to play audio...')
          const playPromise = audioRef.current.play()
          
          if (playPromise !== undefined) {
            await playPromise
            setIsPlaying(true)
            console.log('Audio playing successfully')
          }
        }
      } catch (error) {
        console.error('Audio playback error:', error)
        setError(`Audio playback failed: ${error.message || 'Unknown error'}`)
        setIsPlaying(false)
        
        // Try to create a working audio URL as fallback
        if (generatedTrack?.url) {
          console.log('Trying fallback audio...')
          try {
            // Create a simple beep as fallback
            const audioContext = new (window.AudioContext || window.webkitAudioContext)()
            const oscillator = audioContext.createOscillator()
            const gainNode = audioContext.createGain()
            
            oscillator.connect(gainNode)
            gainNode.connect(audioContext.destination)
            
            oscillator.frequency.setValueAtTime(440, audioContext.currentTime) // A4 note
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 1)
            
            oscillator.start(audioContext.currentTime)
            oscillator.stop(audioContext.currentTime + 1)
            
            setSuccess('Playing fallback audio tone (generated music will be implemented)')
          } catch (fallbackError) {
            console.error('Fallback audio failed:', fallbackError)
          }
        }
      }
    } else {
      console.warn('No audio ref or generated track available')
      setError('No audio available to play')
    }
  }

  const handleDownload = () => {
    if (generatedTrack?.download_url) {
      // Build full URL if the download URL is relative
      const downloadUrl = generatedTrack.download_url.startsWith('http') 
        ? generatedTrack.download_url 
        : `http://localhost:9000${generatedTrack.download_url}`
      window.open(downloadUrl, '_blank')
    }
  }

  // Audio event handlers
  useEffect(() => {
    if (audioRef.current && generatedTrack) {
      const audio = audioRef.current
      
      const handleLoadedData = () => {
        console.log('Audio loaded successfully')
        console.log('Audio duration:', audio.duration)
        console.log('Audio ready state:', audio.readyState)
      }
      
      const handleCanPlay = () => {
        console.log('Audio can play')
      }
      
      const handleLoadStart = () => {
        console.log('Audio load started')
      }
      
      const handleEnded = () => {
        console.log('Audio playback ended')
        setIsPlaying(false)
      }
      
      const handleError = (e) => {
        console.error('Audio error event:', e)
        console.error('Audio error code:', audio.error?.code)
        console.error('Audio error message:', audio.error?.message)
        console.error('Audio src:', audio.src)
        setIsPlaying(false)
        
        // Provide specific error messages based on error code
        let errorMessage = 'Failed to load audio.'
        if (audio.error) {
          switch (audio.error.code) {
            case MediaError.MEDIA_ERR_ABORTED:
              errorMessage = 'Audio loading was aborted.'
              break
            case MediaError.MEDIA_ERR_NETWORK:
              errorMessage = 'Audio network error.'
              break
            case MediaError.MEDIA_ERR_DECODE:
              errorMessage = 'Audio decoding error - invalid format.'
              break
            case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
              errorMessage = 'Audio format not supported.'
              break
            default:
              errorMessage = 'Unknown audio error.'
          }
        }
        setError(errorMessage)
      }
      
      audio.addEventListener('loadeddata', handleLoadedData)
      audio.addEventListener('canplay', handleCanPlay)
      audio.addEventListener('loadstart', handleLoadStart)
      audio.addEventListener('ended', handleEnded)
      audio.addEventListener('error', handleError)
      
      // Set the audio source and preload
      if (generatedTrack.url) {
        console.log('Setting audio source:', generatedTrack.url.substring(0, 100) + '...')
        // Build full URL if the track URL is relative
        const audioUrl = generatedTrack.url.startsWith('http') 
          ? generatedTrack.url 
          : `http://localhost:9000${generatedTrack.url}`
        console.log('Full audio URL for useEffect:', audioUrl)
        audio.src = audioUrl
        audio.load() // Force reload
      }
      
      return () => {
        audio.removeEventListener('loadeddata', handleLoadedData)
        audio.removeEventListener('canplay', handleCanPlay)
        audio.removeEventListener('loadstart', handleLoadStart)
        audio.removeEventListener('ended', handleEnded)
        audio.removeEventListener('error', handleError)
      }
    }
  }, [generatedTrack])

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
                <label className="block text-sm font-semibold text-gray-900 mb-3 flex items-center">
                  <Clock className="h-4 w-4 mr-2" />
                  Duration
                </label>
                <select
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white"
                >
                  <option value={15}>15 seconds</option>
                  <option value={30}>30 seconds</option>
                  <option value={60}>1 minute</option>
                  <option value={120}>2 minutes</option>
                  <option value={180}>3 minutes</option>
                  <option value={300}>5 minutes</option>
                </select>
              </div>

              {/* Genre */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-3 flex items-center">
                  <Music className="h-4 w-4 mr-2" />
                  Genre
                </label>
                <select
                  value={genre}
                  onChange={(e) => setGenre(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white"
                >
                  {genres.map(g => (
                    <option key={g.id} value={g.id}>{g.name}</option>
                  ))}
                </select>
                {genres.find(g => g.id === genre) && (
                  <p className="text-xs text-gray-500 mt-1">
                    {genres.find(g => g.id === genre)?.description}
                  </p>
                )}
              </div>

              {/* Mood */}
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-3 flex items-center">
                  <Settings className="h-4 w-4 mr-2" />
                  Mood
                </label>
                <select
                  value={mood}
                  onChange={(e) => setMood(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white"
                >
                  {moods.map(m => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
                {moods.find(m => m.id === mood) && (
                  <p className="text-xs text-gray-500 mt-1">
                    {moods.find(m => m.id === mood)?.description}
                  </p>
                )}
              </div>
            </div>

            {/* Generate Button */}
            <div className="text-center mb-8">
              <button
                onClick={handleGenerate}
                disabled={!canGenerate()}
                className="btn-primary text-lg px-12 py-4 disabled:opacity-50 disabled:cursor-not-allowed transform transition-all duration-200 hover:scale-105"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Composing Your Track...
                  </>
                ) : (
                  <>
                    <Music className="h-5 w-5 mr-2" />
                    Compose Track
                  </>
                )}
              </button>
              
              {!isAuthenticated && (
                <p className="text-sm text-gray-500 mt-2">
                  Authentication required. Please refresh the page.
                </p>
              )}
              
              {isGenerating && (
                <div className="mt-4 text-sm text-gray-600">
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                  <p className="mt-2">Analyzing your prompt and generating {duration}s of {genre} music...</p>
                </div>
              )}
            </div>

            {/* Generated Track */}
            {generatedTrack && (
              <div className="bg-gradient-to-r from-primary-50 to-accent-50 rounded-xl p-6 animate-fade-in">
                {/* Audio element with better debugging */}
                <audio 
                  ref={audioRef} 
                  preload="metadata"
                  crossOrigin="anonymous"
                  onLoadStart={() => console.log('Audio load start')}
                  onCanPlay={() => console.log('Audio can play')}
                  onError={(e) => console.error('Audio element error:', e)}
                />
                
                {/* Debug info */}
                {process.env.NODE_ENV === 'development' && (
                  <div className="text-xs text-gray-500 mb-2 font-mono">
                    <div>Audio URL: {generatedTrack.url.substring(0, 50)}...</div>
                    <div>Ready State: {audioRef.current?.readyState || 'Not loaded'}</div>
                    <div>Duration: {audioRef.current?.duration || 'Unknown'}</div>
                  </div>
                )}
                
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-1">
                      {generatedTrack.title}
                    </h3>
                    <p className="text-gray-600">
                      Duration: {generatedTrack.duration}s • {generatedTrack.genre} • {generatedTrack.mood}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      License: 100% Royalty-Free • Track ID: {generatedTrack.id}
                    </p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={togglePlayback}
                      className="bg-white hover:bg-gray-50 p-3 rounded-full shadow-lg transition-all duration-200 hover:scale-105"
                      title={isPlaying ? 'Pause' : 'Play'}
                    >
                      {isPlaying ? (
                        <Pause className="h-6 w-6 text-primary-600" />
                      ) : (
                        <Play className="h-6 w-6 text-primary-600" />
                      )}
                    </button>
                    <button 
                      className="bg-white hover:bg-gray-50 p-3 rounded-full shadow-lg transition-all duration-200 hover:scale-105"
                      title="Volume"
                    >
                      <Volume2 className="h-6 w-6 text-gray-600" />
                    </button>
                    <button 
                      onClick={handleDownload}
                      className="btn-primary flex items-center space-x-2"
                      title="Download Track"
                    >
                      <Download className="h-4 w-4" />
                      <span>Download</span>
                    </button>
                  </div>
                </div>

                {/* Audio Waveform Visualization */}
                <div className="bg-white rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-center h-16 bg-gradient-to-r from-primary-100 to-accent-100 rounded">
                    <div className="flex items-end space-x-1">
                      {generatedTrack.waveform_data ? 
                        generatedTrack.waveform_data.map((height, i) => (
                          <div
                            key={i}
                            className={`bg-gradient-to-t from-primary-500 to-accent-500 rounded-sm transition-all duration-300 ${
                              isPlaying ? 'animate-pulse' : ''
                            }`}
                            style={{
                              width: '3px',
                              height: `${height}px`
                            }}
                          />
                        )) : 
                        [...Array(20)].map((_, i) => (
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
                        ))
                      }
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