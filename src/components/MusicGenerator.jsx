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
import { musicAPI, metadataAPI, authAPI, healthAPI } from '../services/api'

// Helper function to get human-readable audio error messages
const getAudioErrorMessage = (error) => {
  if (!error) return 'Unknown audio error';
  
  switch (error.code) {
    case error.MEDIA_ERR_ABORTED:
      return 'Audio playback was aborted';
    case error.MEDIA_ERR_NETWORK:
      return 'Network error while loading audio';
    case error.MEDIA_ERR_DECODE:
      return 'Audio format not supported or corrupted';
    case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
      return 'Audio format not supported by browser';
    default:
      return `Audio error (code: ${error.code})`;
  }
};

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
      // Check backend health first
      console.log('Starting health check...')
      const healthData = await healthAPI.checkHealth()
      console.log('Health check successful:', healthData)

      // Authenticate
      if (!authAPI.isAuthenticated()) {
        console.log('Generating authentication token...')
        await authAPI.generateToken('demo_user', 'free')
      }
      setIsAuthenticated(true)

      // Load metadata with individual error handling
      let genresData = { genres: [] };
      let moodsData = { moods: [] };
      let quotaData = { quota: null };

      try {
        console.log('Fetching genres...')
        genresData = await metadataAPI.getGenres()
        console.log('Genres loaded:', genresData.genres?.length || 0)
      } catch (genresError) {
        console.error('Failed to fetch genres:', genresError)
      }

      try {
        console.log('Fetching moods...')
        moodsData = await metadataAPI.getMoods()
        console.log('Moods loaded:', moodsData.moods?.length || 0)
      } catch (moodsError) {
        console.error('Failed to fetch moods:', moodsError)
      }

      try {
        console.log('Fetching user quota...')
        quotaData = await musicAPI.getUserQuota()
        console.log('Quota loaded:', quotaData.quota)
      } catch (quotaError) {
        console.error('Failed to fetch quota:', quotaError)
      }

      // Set genres, with fallback
      if (genresData?.genres && genresData.genres.length > 0) {
        setGenres(genresData.genres);
        setGenre(genresData.genres[0].id);
      } else {
        console.warn('Using default genres list.');
        const defaultGenres = [
          {id: 'pop', name: 'Pop', description: 'Catchy, mainstream melodies'},
          {id: 'rock', name: 'Rock', description: 'Guitar-driven, energetic'},
          {id: 'electronic', name: 'Electronic', description: 'Synthesized, digital sounds'}
        ];
        setGenres(defaultGenres);
        setGenre(defaultGenres[0].id);
      }

      // Set moods, with fallback
      if (moodsData?.moods && moodsData.moods.length > 0) {
        setMoods(moodsData.moods);
        setMood(moodsData.moods[0].id);
      } else {
        console.warn('Using default moods list.');
        const defaultMoods = [
          {id: 'upbeat', name: 'Upbeat', description: 'Happy, energetic feeling'},
          {id: 'calm', name: 'Calm', description: 'Peaceful, relaxing'},
          {id: 'energetic', name: 'Energetic', description: 'High-energy, motivating'}
        ];
        setMoods(defaultMoods);
        setMood(defaultMoods[0].id);
      }

      // Set user quota
      if (quotaData?.quota) {
        setUserQuota(quotaData.quota);
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
      const result = await musicAPI.generateSimpleMusic({
        prompt,
        duration,
        genre,
        mood
      })

      console.log('Music generation result:', result)

      if (result.success === true) {
        // Create track object from backend response
        const track = {
          id: result.metadata?.filename || `track_${Date.now()}`,
          url: result.audio_file ? `/api/download/${result.audio_file}` : result.download_url,
          download_url: result.download_url,
          title: result.metadata?.title || prompt,
          duration: result.metadata?.duration || duration,
          genre: result.metadata?.genre || genre,
          mood: result.metadata?.mood || mood,
          filename: result.metadata?.filename || result.audio_file
        }
        
        console.log('Created track object:', track)
        setGeneratedTrack(track)
        setSuccess(result.message || 'Music generated successfully!')
        
        // Update quota
        try {
          const updatedQuota = await musicAPI.getUserQuota()
          if (updatedQuota.success === true) {
            setUserQuota(updatedQuota.quota)
          }
        } catch (quotaError) {
          console.warn('Failed to update quota:', quotaError)
        }
      } else {
        console.error('Music generation failed:', result)
        setError(result.message || result.error || 'Failed to generate music')
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
    if (!audioRef.current || !generatedTrack) return;
    
    try {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        // Use relative URL for proxy
        const audioUrl = generatedTrack.url.startsWith('http') 
          ? generatedTrack.url 
          : generatedTrack.url;
        
        // Set the audio source if it's different
        if (audioRef.current.src !== audioUrl) {
          audioRef.current.src = audioUrl;
          audioRef.current.load();
        }
        
        // Attempt to play
        const playPromise = audioRef.current.play();
        if (playPromise !== undefined) {
          playPromise.then(() => {
            setIsPlaying(true);
          }).catch(error => {
            console.error('Audio playback error:', error);
            if (error.name === 'NotAllowedError') {
              setError('Audio autoplay is blocked. Please click the play button after user interaction.');
            } else if (error.name === 'NotSupportedError') {
              setError('Audio format not supported by your browser.');
            } else {
              setError(`Audio format not supported or failed to load: ${error.message}`);
            }
          });
        }
      }
    } catch (error) {
      console.error('Playback error:', error);
      setError(`Audio playback failed: ${error.message}`);
    }
  }

  const handleDownload = () => {
    if (generatedTrack?.download_url) {
      // Use relative URL for proxy
      const downloadUrl = generatedTrack.download_url.startsWith('http') 
        ? generatedTrack.download_url 
        : generatedTrack.download_url;
      window.open(downloadUrl, '_blank');
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
          : generatedTrack.url; // Use relative URL for proxy
        console.log('Full audio URL for useEffect:', audioUrl);
        audio.src = audioUrl;
        audio.load(); // Force reload
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
                  onError={(e) => {
                    console.error('Audio element error:', e);
                    const errorMessage = getAudioErrorMessage(e.target.error);
                    setError(`Audio error: ${errorMessage}`);
                  }}
                />
                
                {/* Debug info */}
                {process.env.NODE_ENV === 'development' && (
                  <div className="text-xs text-gray-500 mb-2 font-mono bg-gray-100 p-2 rounded">
                    <div>🔗 Audio URL: {generatedTrack.url || 'No URL'}</div>
                    <div>📊 Ready State: {audioRef.current?.readyState || 'Not loaded'} (0=nothing, 1=metadata, 2=current, 3=future, 4=enough)</div>
                    <div>⏱️ Duration: {audioRef.current?.duration || 'Unknown'}</div>
                    <div>🎵 Can Play: {audioRef.current?.readyState >= 3 ? '✅' : '❌'}</div>
                    <div>📱 User Agent: {navigator.userAgent.includes('Safari') ? '🦎 Safari' : navigator.userAgent.includes('Chrome') ? '🟢 Chrome' : '🌐 Other'}</div>
                    <button 
                      onClick={() => {
                        console.log('Manual audio test...');
                        if (audioRef.current) {
                          console.log('Audio element exists');
                          console.log('Current src:', audioRef.current.src);
                          console.log('Ready state:', audioRef.current.readyState);
                          audioRef.current.load();
                          audioRef.current.play().then(() => {
                            console.log('Manual play successful');
                          }).catch(err => {
                            console.error('Manual play failed:', err);
                            alert(`Manual play failed: ${err.message}`);
                          });
                        }
                      }}
                      className="bg-blue-500 text-white px-2 py-1 rounded text-xs ml-2"
                    >
                      🧪 Test Audio
                    </button>
                  </div>
                )}
                
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-1">
                      {generatedTrack.title || 'Generated Track'}
                    </h3>
                    <p className="text-gray-600">
                      Duration: {generatedTrack.duration || 30}s • {generatedTrack.genre || 'Unknown'} • {generatedTrack.mood || 'Unknown'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      License: 100% Royalty-Free • Track ID: {generatedTrack.id || 'unknown'}
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