import React from 'react'
import { Play, Sparkles, Zap } from 'lucide-react'

const Hero = () => {
  return (
    <section className="relative bg-gradient-to-br from-primary-50 via-white to-accent-50 py-20 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse-slow"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-accent-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse-slow animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-primary-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse-slow animation-delay-4000"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 bg-white/80 backdrop-blur-sm rounded-full px-4 py-2 mb-8 shadow-lg">
            <Sparkles className="h-4 w-4 text-accent-600" />
            <span className="text-sm font-medium text-gray-700">AI-Powered Music Generation</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 animate-fade-in">
            Create <span className="gradient-text">AI Music</span>
            <br />
            in Seconds
          </h1>

          {/* Subheading */}
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto animate-slide-up">
            Generate royalty-free music for your videos, podcasts, and content using advanced AI technology. 
            No musical experience required.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12 animate-slide-up">
            <button className="btn-primary flex items-center space-x-2 text-lg px-8 py-4">
              <Play className="h-5 w-5" />
              <span>Start Creating Music</span>
            </button>
            <button className="btn-secondary flex items-center space-x-2 text-lg px-8 py-4">
              <Zap className="h-5 w-5" />
              <span>Watch Demo</span>
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center animate-fade-in">
              <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">100K+</div>
              <div className="text-gray-600">Tracks Generated</div>
            </div>
            <div className="text-center animate-fade-in">
              <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">50+</div>
              <div className="text-gray-600">Music Styles</div>
            </div>
            <div className="text-center animate-fade-in">
              <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">10K+</div>
              <div className="text-gray-600">Happy Creators</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Hero