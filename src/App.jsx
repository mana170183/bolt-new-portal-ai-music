import React, { useState } from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import Features from './components/Features'
import MusicGenerator from './components/MusicGenerator'
import AdvancedMusicGenerator from './components/AdvancedMusicGenerator'
import Pricing from './components/Pricing'
import Footer from './components/Footer'

function App() {
  const [activeMode, setActiveMode] = useState('simple')

  return (
    <div className="min-h-screen">
      <Header />
      <Hero />
      <Features />
      
      {/* Mode Selector */}
      <div className="bg-gray-100 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex justify-center space-x-4 mb-8">
            <button
              onClick={() => setActiveMode('simple')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeMode === 'simple'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Simple Mode
            </button>
            <button
              onClick={() => setActiveMode('advanced')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeMode === 'advanced'
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Advanced Studio
            </button>
          </div>
          
          {/* Render active component */}
          {activeMode === 'simple' ? <MusicGenerator /> : <AdvancedMusicGenerator />}
        </div>
      </div>
      
      <Pricing />
      <Footer />
    </div>
  )
}

export default App