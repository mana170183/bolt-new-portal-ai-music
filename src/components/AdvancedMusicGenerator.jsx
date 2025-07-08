import React, { useState, useEffect } from 'react';
import { Music, Settings, Download, Play, Pause, Volume2, 
         Piano, Guitar, Drum, Waves, Microphone2, Headphones } from 'lucide-react';

const AdvancedMusicGenerator = () => {
  const [formData, setFormData] = useState({
    lyrics: '',
    mood: 'upbeat',
    genre: 'pop',
    instruments: ['piano', 'guitar'],
    tempo_bpm: 120,
    duration: 30,
    output_format: 'wav',
    export_stems: false
  });

  const [availableInstruments, setAvailableInstruments] = useState([]);
  const [templates, setTemplates] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedTrack, setGeneratedTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audio, setAudio] = useState(null);
  const [error, setError] = useState('');

  // Available moods and genres
  const moods = [
    { value: 'upbeat', label: 'Upbeat', emoji: '😊' },
    { value: 'energetic', label: 'Energetic', emoji: '⚡' },
    { value: 'calm', label: 'Calm', emoji: '😌' },
    { value: 'sad', label: 'Sad', emoji: '😢' },
    { value: 'romantic', label: 'Romantic', emoji: '💕' },
    { value: 'mysterious', label: 'Mysterious', emoji: '🔮' },
    { value: 'epic', label: 'Epic', emoji: '🚀' }
  ];

  const genres = [
    { value: 'pop', label: 'Pop' },
    { value: 'rock', label: 'Rock' },
    { value: 'jazz', label: 'Jazz' },
    { value: 'blues', label: 'Blues' },
    { value: 'folk', label: 'Folk' },
    { value: 'electronic', label: 'Electronic' },
    { value: 'classical', label: 'Classical' },
    { value: 'country', label: 'Country' }
  ];

  // Instrument icons mapping
  const instrumentIcons = {
    piano: Piano,
    guitar: Guitar,
    bass: Guitar,
    drums: Drum,
    strings: Waves,
    synthesizer: Microphone2
  };

  useEffect(() => {
    fetchInstruments();
    fetchTemplates();
  }, []);

  const fetchInstruments = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/instruments');
      const data = await response.json();
      if (data.success) {
        setAvailableInstruments(data.instruments);
      }
    } catch (error) {
      console.error('Failed to fetch instruments:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/composition-templates');
      const data = await response.json();
      if (data.success) {
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

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

  const applyTemplate = (templateKey) => {
    const template = templates[templateKey];
    if (template) {
      setFormData(prev => ({
        ...prev,
        genre: templateKey,
        instruments: template.instruments,
        tempo_bpm: Math.floor((template.tempo_range[0] + template.tempo_range[1]) / 2)
      }));
    }
  };

  const generateMusic = async () => {
    if (formData.instruments.length === 0) {
      setError('Please select at least one instrument');
      return;
    }

    setIsGenerating(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5001/api/generate-advanced-music', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedTrack(data.track);
        
        // Create audio object for playback
        const audioUrl = `http://localhost:5001${data.track.url}`;
        const newAudio = new Audio(audioUrl);
        setAudio(newAudio);
      } else {
        setError(data.error || 'Failed to generate music');
      }
    } catch (error) {
      console.error('Generation failed:', error);
      setError('Failed to connect to the music generation service');
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePlayback = () => {
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
    } else {
      audio.play();
      setIsPlaying(true);
      audio.onended = () => setIsPlaying(false);
    }
  };

  const downloadTrack = () => {
    if (generatedTrack) {
      const downloadUrl = `http://localhost:5001${generatedTrack.download_url}`;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${generatedTrack.title}.wav`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-3">
          <Music className="w-8 h-8 text-blue-600" />
          <h1 className="text-4xl font-bold text-gray-900">
            Advanced AI Music Studio
          </h1>
        </div>
        <p className="text-xl text-gray-600">
          Create sophisticated multi-instrumental compositions with AI
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left Column - Input Controls */}
        <div className="space-y-6">
          {/* Lyrics Input */}
          <div className="bg-white rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Microphone2 className="w-5 h-5 mr-2" />
              Lyrics (Optional)
            </h3>
            <textarea
              className="w-full p-3 border rounded-lg resize-none"
              rows="4"
              placeholder="Enter your lyrics here... (optional)"
              value={formData.lyrics}
              onChange={(e) => handleInputChange('lyrics', e.target.value)}
            />
          </div>

          {/* Genre and Mood */}
          <div className="bg-white rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-4">Style & Mood</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Genre</label>
                <select
                  className="w-full p-2 border rounded-lg"
                  value={formData.genre}
                  onChange={(e) => handleInputChange('genre', e.target.value)}
                >
                  {genres.map(genre => (
                    <option key={genre.value} value={genre.value}>
                      {genre.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Mood</label>
                <select
                  className="w-full p-2 border rounded-lg"
                  value={formData.mood}
                  onChange={(e) => handleInputChange('mood', e.target.value)}
                >
                  {moods.map(mood => (
                    <option key={mood.value} value={mood.value}>
                      {mood.emoji} {mood.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Quick Templates */}
          <div className="bg-white rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-4">Quick Templates</h3>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(templates).map(([key, template]) => (
                <button
                  key={key}
                  onClick={() => applyTemplate(key)}
                  className="p-3 text-left border rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
                >
                  <div className="font-medium">{template.name}</div>
                  <div className="text-sm text-gray-500">
                    {template.instruments.join(', ')}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Technical Settings */}
          <div className="bg-white rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              Technical Settings
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Tempo (BPM): {formData.tempo_bpm}
                </label>
                <input
                  type="range"
                  min="60"
                  max="200"
                  step="5"
                  value={formData.tempo_bpm}
                  onChange={(e) => handleInputChange('tempo_bpm', parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Duration: {formData.duration}s
                </label>
                <input
                  type="range"
                  min="10"
                  max="120"
                  step="5"
                  value={formData.duration}
                  onChange={(e) => handleInputChange('duration', parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.export_stems}
                  onChange={(e) => handleInputChange('export_stems', e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm">Export individual instrument stems</span>
              </label>
            </div>
          </div>
        </div>

        {/* Right Column - Instruments & Output */}
        <div className="space-y-6">
          {/* Instrument Selection */}
          <div className="bg-white rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-4">Select Instruments</h3>
            <div className="grid grid-cols-2 gap-3">
              {availableInstruments.map(instrument => {
                const IconComponent = instrumentIcons[instrument.id] || Music;
                const isSelected = formData.instruments.includes(instrument.id);
                
                return (
                  <button
                    key={instrument.id}
                    onClick={() => handleInstrumentToggle(instrument.id)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <IconComponent className="w-5 h-5" />
                      <span className="font-medium">{instrument.name}</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {instrument.description}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={generateMusic}
            disabled={isGenerating || formData.instruments.length === 0}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg font-semibold text-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
                <span>Generating Music...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-2">
                <Music className="w-5 h-5" />
                <span>Generate Composition</span>
              </div>
            )}
          </button>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Generated Track */}
          {generatedTrack && (
            <div className="bg-white rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Headphones className="w-5 h-5 mr-2" />
                Generated Composition
              </h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium">{generatedTrack.title}</h4>
                  <p className="text-sm text-gray-500">
                    {generatedTrack.genre} • {generatedTrack.mood} • {generatedTrack.tempo_bpm} BPM
                  </p>
                  <p className="text-sm text-gray-500">
                    Instruments: {generatedTrack.instruments.join(', ')}
                  </p>
                </div>

                {/* Waveform Visualization */}
                {generatedTrack.waveform_data && (
                  <div className="flex items-end space-x-1 h-16 bg-gray-50 rounded p-2">
                    {generatedTrack.waveform_data.map((height, index) => (
                      <div
                        key={index}
                        className="bg-blue-500 rounded-sm flex-1 transition-all"
                        style={{ height: `${height}%` }}
                      />
                    ))}
                  </div>
                )}

                {/* Playback Controls */}
                <div className="flex items-center space-x-4">
                  <button
                    onClick={togglePlayback}
                    className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    <span>{isPlaying ? 'Pause' : 'Play'}</span>
                  </button>

                  <button
                    onClick={downloadTrack}
                    className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </button>
                </div>

                {/* Metadata */}
                {generatedTrack.metadata && (
                  <details className="bg-gray-50 rounded-lg p-3">
                    <summary className="font-medium cursor-pointer">Technical Details</summary>
                    <pre className="text-xs mt-2 text-gray-600 overflow-auto">
                      {JSON.stringify(generatedTrack.metadata, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedMusicGenerator;
