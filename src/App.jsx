import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import Features from './components/Features'
import MusicGenerator from './components/MusicGenerator'
import AdvancedStudio from './components/AdvancedStudio'
import MusicLibrary from './components/MusicLibrary'
import Pricing from './components/Pricing'
import Footer from './components/Footer'
import LoadingScreen from './components/LoadingScreen'

function App() {
  const [activeTab, setActiveTab] = useState('simple')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate app initialization
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 2000)

    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <Header />
      <Hero />
      <Features />
      
      {/* Music Generation Tabs */}
      <div className="bg-gray-100 py-12" id="generator">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Tab Navigation */}
          <div className="flex justify-center mb-8">
            <nav className="flex space-x-1 bg-white rounded-lg p-1">
              <button
                onClick={() => setActiveTab('simple')}
                className={`px-6 py-3 rounded-md font-medium transition-all ${
                  activeTab === 'simple'
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Simple Mode
              </button>
              <button
                onClick={() => setActiveTab('advanced')}
                className={`px-6 py-3 rounded-md font-medium transition-all ${
                  activeTab === 'advanced'
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Advanced Studio
              </button>
              <button
                onClick={() => setActiveTab('library')}
                className={`px-6 py-3 rounded-md font-medium transition-all ${
                  activeTab === 'library'
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Music Library
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="min-h-[600px]">
            {activeTab === 'simple' && <MusicGenerator />}
            {activeTab === 'advanced' && <AdvancedStudio />}
            {activeTab === 'library' && <MusicLibrary />}
          </div>
        </div>
      </div>

      <Pricing />
      <Footer />
    </div>
  )
}

export default App