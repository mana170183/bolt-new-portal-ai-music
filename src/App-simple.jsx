import React, { useState } from 'react'

// Simple fallback components to test loading
const SimpleHeader = () => (
  <header className="bg-white shadow-lg">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center py-6">
        <div className="flex items-center">
          <h1 className="text-2xl font-bold text-gray-900">🎵 Portal AI Music</h1>
        </div>
        <nav className="flex space-x-8">
          <a href="#features" className="text-gray-600 hover:text-blue-600">Features</a>
          <a href="#pricing" className="text-gray-600 hover:text-blue-600">Pricing</a>
        </nav>
      </div>
    </div>
  </header>
)

const SimpleHero = () => (
  <section className="bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 text-white py-20">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <h1 className="text-5xl md:text-6xl font-bold mb-6">
        Create AI Music <span className="text-yellow-300">Instantly</span>
      </h1>
      <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
        Generate custom, royalty-free music for your videos, podcasts, and projects using advanced AI technology
      </p>
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button className="bg-yellow-400 text-gray-900 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-yellow-300 transition-colors">
          Start Creating Music
        </button>
        <button className="border border-white text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white hover:text-gray-900 transition-colors">
          Watch Demo
        </button>
      </div>
    </div>
  </section>
)

const SimpleMusicGenerator = () => {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedTrack, setGeneratedTrack] = useState(null)

  const generateMusic = async () => {
    if (!prompt.trim()) return
    
    setIsGenerating(true)
    try {
      const response = await fetch('http://localhost:5001/api/generate-music', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          duration: 15,
          genre: 'pop',
          mood: 'upbeat'
        })
      })
      
      const data = await response.json()
      if (data.success) {
        setGeneratedTrack(data.track)
      }
    } catch (error) {
      console.error('Generation failed:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Generate Your Music
          </h2>
          <p className="text-xl text-gray-600">
            Describe the music you want and let AI create it for you
          </p>
        </div>
        
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Describe your music
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g., Upbeat pop song for a commercial with guitars and drums"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
              />
            </div>
            
            <button
              onClick={generateMusic}
              disabled={isGenerating || !prompt.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isGenerating ? (
                <span className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Generating Music...
                </span>
              ) : (
                '🎵 Generate Music'
              )}
            </button>
            
            {generatedTrack && (
              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">{generatedTrack.title}</h3>
                <audio controls className="w-full">
                  <source src={`http://localhost:5001${generatedTrack.url}`} type="audio/wav" />
                </audio>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

function App() {
  return (
    <div className="min-h-screen">
      <SimpleHeader />
      <SimpleHero />
      <SimpleMusicGenerator />
      
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">© 2025 Portal AI Music. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
