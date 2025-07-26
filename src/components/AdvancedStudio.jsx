import React, { useState, useEffect } from 'react'
import { 
  Play, 
  Pause, 
  Download, 
  Loader2, 
  Settings,
  Volume2,
  Clock,
  Sliders,
  Music2,
  Layers,
  Mic,
  Piano,
  Radio
} from 'lucide-react'
import { musicAPI } from '../services/api'

const AdvancedStudio = () => {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedTrack, setGeneratedTrack] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [settings, setSettings] = useState({
    duration: 60,
    tempo: 120,
    key: 'C',
    genre: 'electronic',
    mood: 'energetic',
    instruments: ['synthesizer', 'drums', 'bass'],
    effects: ['reverb', 'delay'],
    structure: 'verse-chorus-verse-chorus-bridge-chorus'
  })

  const instruments = [
    { id: 'piano', name: 'Piano', icon: Piano },
    { id: 'guitar', name: 'Guitar', icon: Music2 },
    { id: 'drums', name: 'Drums', icon: Volume2 },
    { id: 'bass', name: 'Bass', icon: Music2 },
    { id: 'synthesizer', name: 'Synthesizer', icon: Radio },
    { id: 'vocals', name: 'Vocals', icon: Mic },
    { id: 'strings', name: 'Strings', icon: Music2 },
    { id: 'brass', name: 'Brass', icon: Music2 }
  ]

  const effects = [
    'reverb', 'delay', 'chorus', 'distortion', 'compressor', 'equalizer'
  ]

  const structures = [
    'verse-chorus-verse-chorus',
    'verse-chorus-verse-chorus-bridge-chorus',
    'intro-verse-chorus-verse-chorus-bridge-chorus-outro',
    'a-b-a-b-c-b',
    'custom'
  ]

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    setIsGenerating(true)
    try {
      const response = await musicAPI.generateAdvanced({
        prompt,
        ...settings
      })
      
      if (response.success) {
        setGeneratedTrack(response.track)
      }
    } catch (error) {
      console.error('Generation failed:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const toggleInstrument = (instrumentId) => {
    setSettings(prev => ({
      ...prev,
      instruments: prev.instruments.includes(instrumentId)
        ? prev.instruments.filter(id => id !== instrumentId)
        : [...prev.instruments, instrumentId]
    }))
  }

  const toggleEffect = (effectId) => {
    setSettings(prev => ({
      ...prev,
      effects: prev.effects.includes(effectId)
        ? prev.effects.filter(id => id !== effectId)
        : [...prev.effects, effectId]
    }))
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Advanced Music Studio</h2>
        <p className="text-gray-600">Professional-grade AI music generation with full control</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Input Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Prompt Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Musical Concept
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your musical vision in detail... (e.g., 'An epic orchestral piece with soaring strings, powerful brass, and dramatic crescendos, perfect for a movie trailer')"
              className="w-full p-4 border border-gray-300 rounded-lg resize-none h-32 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          {/* Duration and Tempo */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (seconds)
              </label>
              <input
                type="range"
                min="15"
                max="300"
                value={settings.duration}
                onChange={(e) => setSettings(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                className="w-full"
              />
              <div className="text-center text-sm text-gray-500 mt-1">{settings.duration}s</div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tempo (BPM)
              </label>
              <input
                type="range"
                min="60"
                max="200"
                value={settings.tempo}
                onChange={(e) => setSettings(prev => ({ ...prev, tempo: parseInt(e.target.value) }))}
                className="w-full"
              />
              <div className="text-center text-sm text-gray-500 mt-1">{settings.tempo} BPM</div>
            </div>
          </div>

          {/* Key and Structure */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Musical Key
              </label>
              <select
                value={settings.key}
                onChange={(e) => setSettings(prev => ({ ...prev, key: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'].map(key => (
                  <option key={key} value={key}>{key} Major</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Song Structure
              </label>
              <select
                value={settings.structure}
                onChange={(e) => setSettings(prev => ({ ...prev, structure: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {structures.map(structure => (
                  <option key={structure} value={structure}>
                    {structure.charAt(0).toUpperCase() + structure.slice(1).replace(/-/g, ' - ')}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Instruments */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-4">
              Instruments
            </label>
            <div className="grid grid-cols-4 gap-3">
              {instruments.map(instrument => {
                const IconComponent = instrument.icon
                const isSelected = settings.instruments.includes(instrument.id)
                return (
                  <button
                    key={instrument.id}
                    onClick={() => toggleInstrument(instrument.id)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      isSelected
                        ? 'border-purple-500 bg-purple-50 text-purple-700'
                        : 'border-gray-200 bg-white text-gray-600 hover:border-purple-300'
                    }`}
                  >
                    <IconComponent className="w-6 h-6 mx-auto mb-2" />
                    <div className="text-sm font-medium">{instrument.name}</div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Effects */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-4">
              Audio Effects
            </label>
            <div className="flex flex-wrap gap-2">
              {effects.map(effect => {
                const isSelected = settings.effects.includes(effect)
                return (
                  <button
                    key={effect}
                    onClick={() => toggleEffect(effect)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      isSelected
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {effect.charAt(0).toUpperCase() + effect.slice(1)}
                  </button>
                )
              })}
            </div>
          </div>
        </div>

        {/* Settings Panel */}
        <div className="space-y-6">
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              Generation Settings
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Genre
                </label>
                <select
                  value={settings.genre}
                  onChange={(e) => setSettings(prev => ({ ...prev, genre: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="electronic">Electronic</option>
                  <option value="orchestral">Orchestral</option>
                  <option value="rock">Rock</option>
                  <option value="jazz">Jazz</option>
                  <option value="ambient">Ambient</option>
                  <option value="hip-hop">Hip Hop</option>
                  <option value="classical">Classical</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mood
                </label>
                <select
                  value={settings.mood}
                  onChange={(e) => setSettings(prev => ({ ...prev, mood: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="energetic">Energetic</option>
                  <option value="calm">Calm</option>
                  <option value="dramatic">Dramatic</option>
                  <option value="uplifting">Uplifting</option>
                  <option value="mysterious">Mysterious</option>
                  <option value="romantic">Romantic</option>
                  <option value="epic">Epic</option>
                </select>
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !prompt.trim()}
            className={`w-full py-4 px-6 rounded-lg font-semibold text-white transition-all ${
              isGenerating || !prompt.trim()
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-purple-600 hover:bg-purple-700 transform hover:scale-105'
            }`}
          >
            {isGenerating ? (
              <div className="flex items-center justify-center">
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Generating...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <Layers className="w-5 h-5 mr-2" />
                Generate Advanced Track
              </div>
            )}
          </button>

          {/* Generated Track */}
          {generatedTrack && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-900 mb-4">Generated Track</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    <span>{isPlaying ? 'Pause' : 'Play'}</span>
                  </button>
                  
                  <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </button>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                </div>
                
                <div className="text-sm text-green-700">
                  Duration: {settings.duration}s | {settings.tempo} BPM | Key: {settings.key}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdvancedStudio
