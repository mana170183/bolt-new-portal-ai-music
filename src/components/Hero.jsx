import React, { useState, useEffect, useRef } from 'react'
import { Play, Sparkles, Zap, Music, Volume2, Headphones } from 'lucide-react'
import { musicAPI } from '../services/api'

const Hero = ({ onNavigate }) => {
  const [currentText, setCurrentText] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [demoTracks, setDemoTracks] = useState([])
  const [currentTrack, setCurrentTrack] = useState(null)
  const audioRef = useRef(null)
  
  const dynamicTexts = [
    "AI Music in Seconds",
    "Professional Soundtracks", 
    "Royalty-Free Beats",
    "Custom Compositions"
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentText((prev) => (prev + 1) % dynamicTexts.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  // Load demo tracks on component mount
  useEffect(() => {
    loadDemoTracks()
  }, [])

  const loadDemoTracks = async () => {
    try {
      const response = await musicAPI.getDemoTracks()
      if (response.success) {
        setDemoTracks(response.tracks.slice(0, 3)) // Show first 3 tracks
      }
    } catch (error) {
      console.error('Failed to load demo tracks:', error)
      // Fallback to mock data
      setDemoTracks([
        { id: 'demo_1', title: 'Epic Orchestral', genre: 'Classical' },
        { id: 'demo_2', title: 'Chill Lo-Fi', genre: 'Electronic' },
        { id: 'demo_3', title: 'Energetic Rock', genre: 'Rock' }
      ])
    }
  }

  const handleStartCreating = () => {
    if (onNavigate) {
      onNavigate('generator')
    } else {
      // Fallback to scroll to generator section
      const element = document.getElementById('generator')
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }

  const handlePlayDemo = async (track = null) => {
    if (track && track.url) {
      // Play specific track
      if (currentTrack && currentTrack.id === track.id && isPlaying) {
        // Pause current track
        audioRef.current?.pause()
        setIsPlaying(false)
        setCurrentTrack(null)
      } else {
        // Play new track
        if (audioRef.current) {
          // Add better error handling for audio
          audioRef.current.src = track.url
          audioRef.current.preload = 'metadata'
          
          // Set up error handling with fallback URL support
          const handleLoadError = () => {
            // Try fallback URL if available and not already tried
            if (track.fallback_url && !audioRef.current?.src?.includes(track.fallback_url)) {
              console.warn(`Primary URL failed for ${track.title}, trying fallback...`)
              audioRef.current.src = track.fallback_url
              audioRef.current.load() // Force reload with new URL
              return // Let it try again
            }
            
            console.warn(`Audio playback not available for: ${track.title}`)
            // Show visual feedback instead of audio
            setCurrentTrack(track)
            setIsPlaying(true)
            
            // Stop "playing" after the track duration to simulate playback
            setTimeout(() => {
              setIsPlaying(false)
              setCurrentTrack(null)
            }, (track.duration || 30) * 1000)
          }
          
          const handleCanPlay = async () => {
            try {
              await audioRef.current.play()
              setCurrentTrack(track)
              setIsPlaying(true)
              const isUsingFallback = track.fallback_url && audioRef.current?.src?.includes(track.fallback_url)
              const sourceUsed = isUsingFallback ? 'fallback' : 'primary'
              console.log(`✅ Playing demo track (${sourceUsed}):`, track.title)
            } catch (playError) {
              console.error('❌ Play error:', playError)
              handleLoadError()
            }
          }
          
          audioRef.current.onerror = handleLoadError
          audioRef.current.oncanplay = handleCanPlay
          audioRef.current.load() // Force reload
        }
      }
    } else {
      setIsPlaying(!isPlaying)
      // Add generic demo logic here
    }
  }

  return (
    <section className="relative bg-gradient-to-br from-blue-50 via-white to-blue-100 py-20 overflow-hidden text-gray-900">
      {/* Animated Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-cyan-200 rounded-full mix-blend-multiply filter blur-xl opacity-15 animate-pulse" style={{ animationDelay: '4s' }}></div>
        
        {/* Floating Music Notes */}
        <div className="absolute top-1/4 left-1/4 animate-bounce" style={{ animationDelay: '1s', animationDuration: '3s' }}>
          <Music className="w-8 h-8 text-blue-500 opacity-60" />
        </div>
        <div className="absolute top-1/3 right-1/4 animate-bounce" style={{ animationDelay: '2s', animationDuration: '4s' }}>
          <Volume2 className="w-6 h-6 text-indigo-500 opacity-60" />
        </div>
        <div className="absolute bottom-1/3 left-1/3 animate-bounce" style={{ animationDelay: '3s', animationDuration: '3.5s' }}>
          <Headphones className="w-7 h-7 text-cyan-500 opacity-60" />
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 bg-white/95 backdrop-blur-sm rounded-full px-6 py-3 mb-8 shadow-lg border border-blue-300">
            <Sparkles className="h-5 w-5 text-blue-600 animate-pulse" />
            <span className="text-sm font-semibold text-gray-800">Next-Gen AI Music Studio</span>
          </div>

          {/* Main Heading with Dynamic Text */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 text-gray-900">
            Create{' '}
            <span className="bg-gradient-to-r from-blue-700 via-indigo-700 to-cyan-700 bg-clip-text text-transparent animate-pulse font-extrabold">
              {dynamicTexts[currentText]}
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-xl md:text-2xl text-gray-700 mb-8 max-w-3xl mx-auto leading-relaxed font-medium">
            Transform your creative vision into professional music with our advanced AI technology. 
            Perfect for content creators, filmmakers, and music enthusiasts.
          </p>

          {/* Enhanced CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-12">
            <button 
              onClick={handleStartCreating}
              className="group relative bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 text-white font-semibold py-4 px-8 rounded-full transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
            >
              <div className="flex items-center space-x-3">
                <Play className="h-6 w-6 group-hover:scale-110 transition-transform" />
                <span className="text-lg">Start Creating Music</span>
              </div>
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full blur-lg opacity-30 group-hover:opacity-50 transition-opacity -z-10"></div>
            </button>
            
            <button 
              onClick={handlePlayDemo}
              className="group bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 text-white font-semibold py-4 px-8 rounded-full transition-all duration-300 border border-blue-300 hover:border-purple-300 shadow-md hover:shadow-lg transform hover:scale-105"
            >
              <div className="flex items-center space-x-3">
                <Zap className={`h-6 w-6 transition-transform ${isPlaying ? 'animate-pulse' : ''}`} />
                <span className="text-lg">{isPlaying ? 'Playing Demo...' : 'Watch Demo'}</span>
              </div>
            </button>
          </div>

          {/* Enhanced Stats with Animation */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            <div className="group text-center p-6 bg-white/80 backdrop-blur-sm rounded-2xl border border-blue-300 hover:bg-white/90 transition-all duration-300 shadow-md hover:shadow-lg">
              <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform">
                500K+
              </div>
              <div className="text-gray-700 font-medium">Tracks Generated</div>
            </div>
            <div className="group text-center p-6 bg-white/80 backdrop-blur-sm rounded-2xl border border-blue-300 hover:bg-white/90 transition-all duration-300 shadow-md hover:shadow-lg">
              <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-indigo-700 to-cyan-700 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform">
                100+
              </div>
              <div className="text-gray-700 font-medium">Music Styles</div>
            </div>
            <div className="group text-center p-6 bg-white/80 backdrop-blur-sm rounded-2xl border border-blue-300 hover:bg-white/90 transition-all duration-300 shadow-md hover:shadow-lg">
              <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-cyan-700 to-blue-700 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform">
                50K+
              </div>
              <div className="text-gray-700 font-medium">Happy Creators</div>
            </div>
            <div className="group text-center p-6 bg-white/80 backdrop-blur-sm rounded-2xl border border-blue-300 hover:bg-white/90 transition-all duration-300 shadow-md hover:shadow-lg">
              <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform">
                4.9★
              </div>
              <div className="text-gray-700 font-medium">User Rating</div>
            </div>
          </div>

          {/* Featured Demo Section */}
          <div className="mt-16 max-w-4xl mx-auto">
            <p className="text-lg text-gray-700 mb-2 font-medium">🎵 Listen to AI-generated samples:</p>
            <p className="text-sm text-gray-500 mb-6">Click the play buttons to experience our AI music generation capabilities</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {demoTracks.map((track, index) => {
                const isCurrentlyPlaying = currentTrack?.id === track.id && isPlaying
                return (
                  <button
                    key={track.id}
                    className="group p-4 bg-white/70 backdrop-blur-sm rounded-xl border border-blue-200 hover:bg-white/90 transition-all duration-300 shadow-md hover:shadow-lg"
                    onClick={() => handlePlayDemo(track)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-gray-800 font-medium">{track.title}</span>
                      <div className="flex items-center space-x-2">
                        <Play className={`w-5 h-5 transition-colors ${isCurrentlyPlaying ? 'text-green-600 animate-pulse' : 'text-blue-600 group-hover:text-blue-700'}`} />
                        {isCurrentlyPlaying && (
                          <span className="text-xs text-green-600 font-medium">Playing</span>
                        )}
                      </div>
                    </div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${isCurrentlyPlaying ? 'bg-gradient-to-r from-green-500 to-emerald-500' : 'bg-gradient-to-r from-blue-500 to-indigo-500'}`} 
                        style={{ width: `${30 + index * 20}%` }}
                      ></div>
                    </div>
                    {track.genre && (
                      <div className="mt-1 text-xs text-gray-500">{track.genre} • {track.duration || '45'}s</div>
                    )}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Hidden audio element for demo playback */}
      <audio 
        ref={audioRef} 
        preload="metadata"
        onEnded={() => {
          setIsPlaying(false)
          setCurrentTrack(null)
        }}
        onError={() => {
          setIsPlaying(false)
          setCurrentTrack(null)
          console.error('Audio playback failed')
        }}
      />
    </section>
  )
}

export default Hero