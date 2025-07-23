"use client"

import React, { useState, useEffect, useRef } from 'react';
import { 
  Music, Settings, Download, Play, Pause, Volume2, 
  Piano, Guitar, Drum, Waves, Mic, Headphones, Loader2,
  AlertCircle, CheckCircle, Zap, Plus, Minus
} from 'lucide-react';

const AdvancedMusicGenerator = () => {
  const [formData, setFormData] = useState({
    prompt: '',
    mood: 'upbeat',
    genre: 'pop',
    instruments: ['piano', 'guitar'],
    tempo_bpm: 120,
    duration: 30,
    style_complexity: 'moderate',
    key: 'C'
  });

  const [availableGenres, setAvailableGenres] = useState([]);
  const [availableMoods, setAvailableMoods] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedTrack, setGeneratedTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const audioRef = useRef(null);

  // Available instruments
  const availableInstruments = [
    { id: 'piano', name: 'Piano', icon: Piano },
    { id: 'guitar', name: 'Guitar', icon: Guitar },
    { id: 'electric_guitar', name: 'Electric Guitar', icon: Guitar },
    { id: 'bass', name: 'Bass', icon: Guitar },
    { id: 'drums', name: 'Drums', icon: Drum },
    { id: 'synth', name: 'Synthesizer', icon: Waves },
    { id: 'strings', name: 'Strings', icon: Waves },
    { id: 'vocals', name: 'Vocals', icon: Mic }
  ];

  // Complexity options
  const complexityOptions = [
    { value: 'simple', label: 'Simple', description: 'Basic progressions' },
    { value: 'moderate', label: 'Moderate', description: 'Standard complexity' },
    { value: 'complex', label: 'Complex', description: 'Advanced arrangements' }
  ];

  // Key options
  const keyOptions = [
    'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B',
    'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am', 'A#m', 'Bm'
  ];

  // Fetch genres and moods
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch genres
        const genresResponse = await fetch('/api/genres');
        if (genresResponse.ok) {
          const genresData = await genresResponse.json();
          if (genresData.success && genresData.genres) {
            setAvailableGenres(genresData.genres);
          }
        }

        // Fetch moods
        const moodsResponse = await fetch('/api/moods');
        if (moodsResponse.ok) {
          const moodsData = await moodsResponse.json();
          if (moodsData.success && moodsData.moods) {
            setAvailableMoods(moodsData.moods);
          }
        }
      } catch (err) {
        console.error('Failed to fetch metadata:', err);
        // Use fallback data
        setAvailableGenres([
          { id: 'pop', name: 'Pop', description: 'Catchy mainstream music' },
          { id: 'rock', name: 'Rock', description: 'Guitar-driven music' },
          { id: 'electronic', name: 'Electronic', description: 'Digital sounds' },
          { id: 'jazz', name: 'Jazz', description: 'Smooth jazz' },
          { id: 'classical', name: 'Classical', description: 'Orchestral music' }
        ]);
        setAvailableMoods([
          { id: 'upbeat', name: 'Upbeat', description: 'Energetic and positive' },
          { id: 'calm', name: 'Calm', description: 'Peaceful and relaxing' },
          { id: 'dramatic', name: 'Dramatic', description: 'Intense and emotional' },
          { id: 'mysterious', name: 'Mysterious', description: 'Dark and intriguing' }
        ]);
      }
    };

    fetchData();
  }, []);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleInstrumentToggle = (instrumentId) => {
    setFormData(prev => ({
      ...prev,
      instruments: prev.instruments.includes(instrumentId)
        ? prev.instruments.filter(id => id !== instrumentId)
        : [...prev.instruments, instrumentId]
    }));
  };

  const handleGenerate = async () => {
    if (isGenerating) return;

    setIsGenerating(true);
    setError('');
    setSuccess('');
    setGeneratedTrack(null);

    try {
      console.log('Generating advanced music with params:', formData);

      const response = await fetch('/api/advanced-generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: formData.prompt,
          genre: formData.genre,
          mood: formData.mood,
          instruments: formData.instruments,
          tempo: formData.tempo_bpm,
          duration: formData.duration,
          key: formData.key,
          style_complexity: formData.style_complexity
        }),
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedTrack(data);
        setSuccess('Advanced music generated successfully!');
      } else {
        setError(data.error || 'Failed to generate music');
      }
    } catch (err) {
      console.error('Advanced generation error:', err);
      setError('Failed to generate music: ' + (err.message || 'Unknown error'));
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePlay = () => {
    if (!generatedTrack) return;

    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        // Use the download URL for playback
        const audioUrl = `${window.location.origin}${generatedTrack.download_url}`;
        audioRef.current.src = audioUrl;
        audioRef.current.play().then(() => {
          setIsPlaying(true);
        }).catch(err => {
          console.error('Playback failed:', err);
          setError('Playback failed: ' + err.message);
        });
      }
    }
  };

  const handleDownload = () => {
    if (!generatedTrack) return;
    
    const downloadUrl = `${window.location.origin}${generatedTrack.download_url}`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = generatedTrack.filename || 'generated_music.wav';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-white rounded-xl shadow-xl p-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="p-3 bg-purple-100 rounded-lg">
          <Settings className="w-6 h-6 text-purple-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Advanced Studio</h2>
          <p className="text-gray-600">Professional music generation with full control</p>
        </div>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
          <p className="text-green-700">{success}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Controls */}
        <div className="space-y-6">
          {/* Prompt */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Music Description
            </label>
            <textarea
              value={formData.prompt}
              onChange={(e) => handleInputChange('prompt', e.target.value)}
              placeholder="Describe the music you want to create..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              rows={3}
            />
          </div>

          {/* Genre & Mood */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Genre
              </label>
              <select
                value={formData.genre}
                onChange={(e) => handleInputChange('genre', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {availableGenres.map((genre) => (
                  <option key={genre.id} value={genre.id}>
                    {genre.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mood
              </label>
              <select
                value={formData.mood}
                onChange={(e) => handleInputChange('mood', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {availableMoods.map((mood) => (
                  <option key={mood.id} value={mood.id}>
                    {mood.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Instruments */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Instruments
            </label>
            <div className="grid grid-cols-2 gap-2">
              {availableInstruments.map((instrument) => {
                const Icon = instrument.icon;
                const isSelected = formData.instruments.includes(instrument.id);
                return (
                  <button
                    key={instrument.id}
                    onClick={() => handleInstrumentToggle(instrument.id)}
                    className={`p-3 rounded-lg border transition-all ${
                      isSelected
                        ? 'border-purple-500 bg-purple-50 text-purple-700'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-purple-300'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Icon className="w-4 h-4" />
                      <span className="text-sm font-medium">{instrument.name}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Settings */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tempo (BPM)
              </label>
              <input
                type="number"
                min="60"
                max="200"
                value={formData.tempo_bpm}
                onChange={(e) => handleInputChange('tempo_bpm', parseInt(e.target.value))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (seconds)
              </label>
              <input
                type="number"
                min="10"
                max="300"
                value={formData.duration}
                onChange={(e) => handleInputChange('duration', parseInt(e.target.value))}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Key
              </label>
              <select
                value={formData.key}
                onChange={(e) => handleInputChange('key', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {keyOptions.map((key) => (
                  <option key={key} value={key}>
                    {key}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Complexity
              </label>
              <select
                value={formData.style_complexity}
                onChange={(e) => handleInputChange('style_complexity', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {complexityOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || formData.instruments.length === 0}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating Advanced Music...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Generate Advanced Music
              </>
            )}
          </button>
        </div>

        {/* Right Column - Results */}
        <div className="space-y-6">
          {generatedTrack && (
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Music className="w-5 h-5" />
                Generated Track
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <button
                    onClick={handlePlay}
                    className="bg-purple-600 hover:bg-purple-700 text-white p-3 rounded-full transition-colors"
                  >
                    {isPlaying ? (
                      <Pause className="w-5 h-5" />
                    ) : (
                      <Play className="w-5 h-5" />
                    )}
                  </button>
                  
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Advanced Composition</p>
                    <p className="text-sm text-gray-600">
                      {formData.genre} • {formData.mood} • {formData.duration}s
                    </p>
                  </div>
                  
                  <button
                    onClick={handleDownload}
                    className="bg-green-600 hover:bg-green-700 text-white p-2 rounded-lg transition-colors"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>

                {/* Track Details */}
                <div className="bg-white rounded-lg p-4 border">
                  <h4 className="font-medium text-gray-900 mb-2">Track Details</h4>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p><span className="font-medium">Instruments:</span> {formData.instruments.join(', ')}</p>
                    <p><span className="font-medium">Tempo:</span> {formData.tempo_bpm} BPM</p>
                    <p><span className="font-medium">Key:</span> {formData.key}</p>
                    <p><span className="font-medium">Complexity:</span> {formData.style_complexity}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {!generatedTrack && !isGenerating && (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <div className="text-gray-400 mb-4">
                <Music className="w-12 h-12 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Track Generated</h3>
              <p className="text-gray-600">Configure your settings and generate advanced music</p>
            </div>
          )}
        </div>
      </div>

      {/* Hidden Audio Element */}
      <audio
        ref={audioRef}
        onEnded={() => setIsPlaying(false)}
        onError={(e) => {
          console.error('Audio playback error:', e);
          setError('Audio playback failed');
          setIsPlaying(false);
        }}
      />
    </div>
  );
};

export default AdvancedMusicGenerator;
