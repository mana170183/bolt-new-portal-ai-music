import React, { useState, useEffect } from 'react'
import { Play, Sparkles, Zap, Music, Volume2, Headphones } from 'lucide-react'

const Hero = ({ onNavigate }) => {
  const [currentText, setCurrentText] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  
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

  const handlePlayDemo = () => {
    setIsPlaying(!isPlaying)
    // Add demo audio logic here
  }

  return (
    <section className="relative bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 py-20 overflow-hidden text-white">
      {/* Animated Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-15 animate-pulse" style={{ animationDelay: '4s' }}></div>
        
        {/* Floating Music Notes */}
        <div className="absolute top-1/4 left-1/4 animate-bounce" style={{ animationDelay: '1s', animationDuration: '3s' }}>
          <Music className="w-8 h-8 text-purple-300 opacity-60" />
        </div>
        <div className="absolute top-1/3 right-1/4 animate-bounce" style={{ animationDelay: '2s', animationDuration: '4s' }}>
          <Volume2 className="w-6 h-6 text-blue-300 opacity-60" />
        </div>
        <div className="absolute bottom-1/3 left-1/3 animate-bounce" style={{ animationDelay: '3s', animationDuration: '3.5s' }}>
          <Headphones className="w-7 h-7 text-indigo-300 opacity-60" />
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-sm rounded-full px-6 py-3 mb-8 shadow-lg border border-white/20">
            <Sparkles className="h-5 w-5 text-yellow-300 animate-pulse" />
            <span className="text-sm font-medium text-white">Next-Gen AI Music Studio</span>
          </div>

          {/* Main Heading with Dynamic Text */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6">
            Create{' '}
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent animate-pulse">
              {dynamicTexts[currentText]}
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-xl md:text-2xl text-purple-100 mb-8 max-w-3xl mx-auto leading-relaxed">
            Transform your creative vision into professional music with our advanced AI technology. 
            Perfect for content creators, filmmakers, and music enthusiasts.
          </p>

          {/* Enhanced CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-12">
            <button 
              onClick={handleStartCreating}
              className="group relative bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-4 px-8 rounded-full transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
            >
              <div className="flex items-center space-x-3">
                <Play className="h-6 w-6 group-hover:scale-110 transition-transform" />
                <span className="text-lg">Start Creating Music</span>
              </div>
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full blur-lg opacity-30 group-hover:opacity-50 transition-opacity -z-10"></div>
            </button>
            
            <button 
              onClick={handlePlayDemo}
              className="group bg-white/10 backdrop-blur-sm hover:bg-white/20 text-white font-semibold py-4 px-8 rounded-full transition-all duration-300 border border-white/30 hover:border-white/50"
            >
              <div className="flex items-center space-x-3">
                <Zap className={`h-6 w-6 transition-transform ${isPlaying ? 'animate-pulse text-yellow-300' : ''}`} />
                <span className="text-lg">{isPlaying ? 'Playing Demo...' : 'Watch Demo'}</span>
              </div>
            </button>
          </div>

          {/* Enhanced Stats with Animation */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            <div className="group text-center p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:bg-white/10 transition-all duration-300">
              <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform">
                500K+
              </div>
              <div className="text-purple-200">Tracks Generated</div>
            </div>
            <div className="group text-center p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:bg-white/10 transition-all duration-300">
              <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform">
                100+
              </div>
              <div className="text-purple-200">Music Styles</div>
            </div>
            <div className="group text-center p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:bg-white/10 transition-all duration-300">
              <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform">
                50K+
              </div>
              <div className="text-purple-200">Happy Creators</div>
            </div>
            <div className="group text-center p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:bg-white/10 transition-all duration-300">
              <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform">
                4.9★
              </div>
              <div className="text-purple-200">User Rating</div>
            </div>
          </div>

          {/* Featured Demo Section */}
          <div className="mt-16 max-w-4xl mx-auto">
            <p className="text-lg text-purple-200 mb-6">🎵 Listen to AI-generated samples:</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {['Epic Orchestral', 'Chill Lo-Fi', 'Energetic Rock'].map((style, index) => (
                <button
                  key={style}
                  className="group p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:bg-white/10 transition-all duration-300"
                  onClick={() => handlePlayDemo()}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-white font-medium">{style}</span>
                    <Play className="w-5 h-5 text-purple-300 group-hover:text-white transition-colors" />
                  </div>
                  <div className="mt-2 w-full bg-white/10 rounded-full h-2">
                    <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full" style={{ width: `${30 + index * 20}%` }}></div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Hero