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
  const audioRef = useRef(null)
  const [genres, setGenres] = useState([
    {id: 'pop', name: 'Pop', description: 'Popular music with catchy melodies'},
    {id: 'rock', name: 'Rock', description: 'Guitar-driven energetic music'},
    {id: 'jazz', name: 'Jazz', description: 'Improvised, swing rhythms'},
    {id: 'classical', name: 'Classical', description: 'Orchestral, traditional'},
    {id: 'electronic', name: 'Electronic', description: 'Synthesized, digital sounds'},
    {id: 'orchestral', name: 'Orchestral', description: 'Full orchestra compositions'},
    {id: 'ambient', name: 'Ambient', description: 'Atmospheric, background music'},
    {id: 'hip-hop', name: 'Hip Hop', description: 'Rhythmic, beat-focused music'},
    {id: 'country', name: 'Country', description: 'Folk-inspired American music'},
    {id: 'blues', name: 'Blues', description: 'Soulful, guitar-based music'}
  ])
  const [moods, setMoods] = useState([
    {id: 'upbeat', name: 'Upbeat', description: 'Happy, energetic feeling'},
    {id: 'calm', name: 'Calm', description: 'Peaceful, relaxing'},
    {id: 'energetic', name: 'Energetic', description: 'High-energy, motivating'},
    {id: 'dramatic', name: 'Dramatic', description: 'Intense, emotional'},
    {id: 'uplifting', name: 'Uplifting', description: 'Inspiring, positive'},
    {id: 'mysterious', name: 'Mysterious', description: 'Dark, intriguing'},
    {id: 'romantic', name: 'Romantic', description: 'Love-themed, tender'},
    {id: 'melancholic', name: 'Melancholic', description: 'Sad, contemplative'}
  ])
  const [userQuota, setUserQuota] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(true) // Set to true by default

  useEffect(() => {
    initializeComponent()
  }, [])

  const initializeComponent = async () => {
    try {
      // Simple health check
      try {
        const healthResponse = await fetch('/health')
        if (healthResponse.ok) {
          const healthData = await healthResponse.json()
          console.log('Backend health check passed:', healthData)
        }
      } catch (healthError) {
        console.warn('Health check failed, but continuing:', healthError)
      }

      // Load basic data
      try {
        const [genresData, moodsData] = await Promise.all([
          musicAPI.getGenres(),
          musicAPI.getMoods()
        ])
        
        if (genresData.genres) {
          setGenres(genresData.genres)
        }
        if (moodsData.moods) {
          setMoods(moodsData.moods)
        }

        // Try to load quota data
        try {
          const quotaData = await musicAPI.getUserQuota()
          if (quotaData.quota) {
            setUserQuota(quotaData.quota)
          }
        } catch (quotaError) {
          console.warn('Failed to load quota:', quotaError)
          // Set default quota
          setUserQuota({
            daily_remaining: 50,
            daily_limit: 50,
            plan: 'free'
          })
        }
        
      } catch (error) {
        console.warn('Failed to load metadata, using defaults:', error)
      }
    } catch (error) {
      console.error('Initialization error:', error)
    }
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a music description')
      return
    }

    setIsGenerating(true)
    setError('')
    setSuccess('')
    
    try {
      const result = await musicAPI.generateMusic({
        prompt,
        duration,
        genre,
        mood
      })

      if (result.success) {
        setGeneratedTrack(result.track)
        setSuccess('Music generated successfully!')
        setError('') // Clear any previous errors
        console.log('Generated track:', result.track)
      } else {
        setError(result.message || 'Failed to generate music')
        setSuccess('')
      }
    } catch (error) {
      console.error('Generation error:', error)
      setError('Failed to generate music. Please try again.')
      setSuccess('')
    } finally {
      setIsGenerating(false)
    }
  }

  const togglePlayback = async () => {
    console.log('togglePlayback called', { 
      hasTrack: !!generatedTrack, 
      hasAudioUrl: !!generatedTrack?.audioUrl, 
      hasAudioRef: !!audioRef.current,
      audioUrl: generatedTrack?.audioUrl 
    });
    
    if (!generatedTrack?.audioUrl || !audioRef.current) {
      console.warn('No audio URL or audio element available');
      setError('Audio not available. Please generate music first.');
      return;
    }

    try {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
        console.log('Audio paused');
      } else {
        console.log('Attempting to play audio...');
        await audioRef.current.play();
        setIsPlaying(true);
        console.log('Audio playing');
      }
    } catch (error) {
      console.error('Audio playback error:', error);
      setError('Unable to play audio. Please try again.');
      setIsPlaying(false);
    }
  }

  // Handle audio events
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleEnded = () => setIsPlaying(false);
    const handleError = () => {
      setIsPlaying(false);
      setError('Audio failed to load. Using fallback audio.');
    };

    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    return () => {
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, [generatedTrack]);

  const handleDownload = () => {
    if (generatedTrack?.audioUrl) {
      const link = document.createElement('a');
      link.href = generatedTrack.audioUrl;
      link.download = `${generatedTrack.title || 'generated-music'}.wav`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }

  const canGenerate = () => {
    return prompt.trim() && !isGenerating
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
            {userQuota && userQuota.plan && (
              <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Zap className="h-5 w-5 text-blue-600" />
                    <span className="font-semibold text-gray-900">
                      Plan: {userQuota?.plan ? userQuota.plan.charAt(0).toUpperCase() + userQuota.plan.slice(1) : 'Free'}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {userQuota?.daily_limit && userQuota.daily_limit > 0 ? (
                      <>Remaining today: {userQuota.remaining_today || 0}/{userQuota.daily_limit}</>
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
            <div className="space-y-6 mb-8">
              {/* Duration */}
              <div>
                <label className="block text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Clock className="h-5 w-5 mr-2" />
                  Duration
                </label>
                <select
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  className="input-field max-w-xs"
                >
                  <option value={15}>15 seconds</option>
                  <option value={30}>30 seconds</option>
                  <option value={60}>1 minute</option>
                  <option value={120}>2 minutes</option>
                  <option value={180}>3 minutes</option>
                </select>
              </div>

              {/* Genre Selection */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Music className="h-5 w-5 mr-2" />
                    Genre
                  </label>
                  <select
                    value={genre}
                    onChange={(e) => setGenre(e.target.value)}
                    className="input-field w-full"
                  >
                    {genres.map(g => (
                      <option key={g.id} value={g.id}>
                        {g.name} - {g.description}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Mood Selection */}
                <div>
                  <label className="block text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Settings className="h-5 w-5 mr-2" />
                    Mood & Atmosphere
                  </label>
                  <select
                    value={mood}
                    onChange={(e) => setMood(e.target.value)}
                    className="input-field w-full"
                  >
                    {moods.map(m => (
                      <option key={m.id} value={m.id}>
                        {m.name} - {m.description}
                      </option>
                    ))}
                  </select>
                </div>
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
                      className="bg-white hover:bg-gray-50 p-3 rounded-full shadow-lg transition-all duration-200 hover:scale-105 relative"
                      title={isPlaying ? "Pause" : "Play"}
                    >
                      {isPlaying ? (
                        <Pause className="h-6 w-6 text-primary-600" />
                      ) : (
                        <Play className="h-6 w-6 text-primary-600" />
                      )}
                      {generatedTrack?.audioUrl && (
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"></div>
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

                {/* Hidden audio element for playback */}
                {generatedTrack?.audioUrl && (
                  <audio 
                    ref={audioRef} 
                    src={generatedTrack.audioUrl} 
                    preload="metadata"
                    onLoadedData={() => console.log('Audio loaded successfully')}
                    onError={(e) => console.error('Audio loading error:', e)}
                  />
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

export default MusicGenerator