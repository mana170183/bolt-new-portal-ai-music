"use client"

import React, { useState, useEffect, useRef } from 'react';
import { 
  Music, Settings, Download, Play, Pause, Volume2, 
  Piano, Guitar, Drum, Waves, Mic, Headphones, Loader2,
  AlertCircle, CheckCircle, Zap
} from 'lucide-react';
import { musicAPI, metadataAPI, authAPI } from '../services/api';

// Helper function to get human-readable audio error messages
const getAudioErrorMessage = (error) => {
  if (!error) return 'Unknown audio error';
  
  switch (error.code) {
    case error.MEDIA_ERR_ABORTED:
      return 'Audio playback was aborted';
    case error.MEDIA_ERR_NETWORK:
      return 'Network error while loading audio';
    case error.MEDIA_ERR_DECODE:
      return 'Audio format not supported or corrupted';
    case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
      return 'Audio format not supported by browser';
    default:
      return `Audio error (code: ${error.code})`;
  }
};

const AdvancedMusicGenerator = () => {
  const [formData, setFormData] = useState({
    lyrics: '',
    mood: 'upbeat',
    genre: 'pop',
    instruments: ['piano', 'guitar'],
    tempo_bpm: 120,
    duration: 30,
    output_format: 'wav',
    export_stems: false,
    style_complexity: 'moderate',
    key: 'C',
    structure: [],
    template: ''
  });

  const [availableInstruments, setAvailableInstruments] = useState([]);
  const [templates, setTemplates] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedTrack, setGeneratedTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [availableGenres, setAvailableGenres] = useState([]);
  const [availableMoods, setAvailableMoods] = useState([]);
  const [userQuota, setUserQuota] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Instrument icons mapping
  const instrumentIcons = {
    piano: Piano,
    "acoustic-guitar": Guitar,
    "electric-guitar": Guitar,
    "bass-guitar": Guitar,
    guitar: Guitar,
    bass: Guitar,
    drums: Drum,
    percussion: Drum,
    violin: Waves,
    cello: Waves,
    strings: Waves,
    synthesizer: Mic,
    "steel-drums": Drum,
    tabla: Drum,
    xylophone: Drum,
    marimba: Drum,
    vibraphone: Drum,
    harp: Waves,
    banjo: Guitar,
    mandolin: Guitar,
    ukulele: Guitar,
    sitar: Guitar,
    koto: Guitar,
    flute: Mic,
    clarinet: Mic,
    saxophone: Mic,
    trumpet: Mic,
    trombone: Mic,
    harmonica: Mic,
    bagpipes: Mic,
    didgeridoo: Mic,
    accordion: Mic,
    organ: Piano
  };

  // Add complexity options
  const complexityOptions = [
    { value: 'simple', label: 'Simple', description: 'Basic chord progressions and arrangements' },
    { value: 'moderate', label: 'Moderate', description: 'Standard complexity with some variations' },
    { value: 'complex', label: 'Complex', description: 'Advanced harmonies and sophisticated arrangements' }
  ];

  // Add key options
  const keyOptions = [
    'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B',
    'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am', 'A#m', 'Bm'
  ];

  // Add structure options
  const structureOptions = [
    { value: 'intro', label: 'Intro' },
    { value: 'verse', label: 'Verse' },
    { value: 'chorus', label: 'Chorus' },
    { value: 'bridge', label: 'Bridge' },
    { value: 'outro', label: 'Outro' },
    { value: 'buildup', label: 'Buildup' },
    { value: 'drop', label: 'Drop' },
    { value: 'breakdown', label: 'Breakdown' }
  ];

  useEffect(() => {
    const initializeStudio = async () => {
      try {
        console.log("Initializing Advanced Studio...");
        if (!authAPI.isAuthenticated()) {
          console.log("Authenticating...");
          await authAPI.generateToken('demo_user', 'free');
        }
        setIsAuthenticated(true);
        console.log("Authentication successful.");

        // Try each API call individually, fallback to []/{} if any fail
        let instrumentsResponse = { instruments: [] };
        let templatesResponse = { templates: {} };
        let genresResponse = { genres: [] };
        let moodsResponse = { moods: [] };
        let quotaResponse = {};
        let errorMessages = [];
        try {
          instrumentsResponse = await metadataAPI.getInstruments();
        } catch (e) {
          errorMessages.push('Instruments: ' + (e?.message || e));
        }
        try {
          templatesResponse = await metadataAPI.getCompositionTemplates();
        } catch (e) {
          errorMessages.push('Templates: ' + (e?.message || e));
        }
        try {
          genresResponse = await metadataAPI.getGenres();
        } catch (e) {
          errorMessages.push('Genres: ' + (e?.message || e));
        }
        try {
          moodsResponse = await metadataAPI.getMoods();
        } catch (e) {
          errorMessages.push('Moods: ' + (e?.message || e));
        }
        try {
          quotaResponse = await musicAPI.getUserQuota();
        } catch (e) {
          errorMessages.push('Quota: ' + (e?.message || e));
        }

        setAvailableInstruments(instrumentsResponse?.instruments || []);
        setTemplates(templatesResponse?.templates || {});
        setAvailableGenres(genresResponse?.genres || []);
        setAvailableMoods(moodsResponse?.moods || []);
        if (quotaResponse?.quota) {
          setUserQuota(quotaResponse.quota);
        }
        setFormData(prev => ({
          ...prev,
          genre: genresResponse?.genres?.[0]?.id || 'pop',
          mood: moodsResponse?.moods?.[0]?.id || 'upbeat',
          instruments: instrumentsResponse?.instruments?.[0] ? [instrumentsResponse.instruments[0].id] : [],
          template: Object.keys(templatesResponse?.templates || {})[0] || 'pop_ballad'
        }));

        if (errorMessages.length > 0) {
          setError('Some data failed to load: ' + errorMessages.join(' | '));
        } else {
          setError('');
        }
      } catch (err) {
        console.error("Failed to initialize Advanced Studio:", err);
        setError("Failed to load studio data: " + (err?.message || err));
      }
    };
    initializeStudio();
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

  const applyTemplate = (templateKey) => {
    const template = templates[templateKey];
    if (template) {
      setFormData(prev => ({
        ...prev,
        genre: template.genre || prev.genre,
        mood: template.mood || prev.mood,
        instruments: template.instruments || [],
        tempo_bpm: template.tempo_range ? Math.floor((template.tempo_range[0] + template.tempo_range[1]) / 2) : prev.tempo_bpm
      }));
    }
  };

  const generateMusic = async () => {
    if (formData.instruments.length === 0) {
      setError('Please select at least one instrument');
      return;
    }
    
    if (userQuota && userQuota.remaining_today === 0) {
      setError('Daily quota exceeded. Please upgrade your plan or try again tomorrow.');
      return;
    }

    setIsGenerating(true);
    setError('');
    setSuccess('');

    try {
      const result = await musicAPI.generateEnhancedMusic(formData);

      if (result.status === 'success') {
        setGeneratedTrack({
          id: result.track_id,
          title: result.metadata?.title || 'Generated Composition',
          url: result.audio_url,
          download_url: result.download_url,
          metadata: result.metadata,
          stem_urls: result.stem_urls || {}
        });
        setSuccess('Composition generated successfully!');
        
        // Update quota
        const updatedQuota = await musicAPI.getUserQuota();
        if (updatedQuota.status === 'success') {
          setUserQuota(updatedQuota.quota);
        }
      } else {
        setError(result.message || 'Failed to generate music');
      }
    } catch (error) {
      console.error('Generation failed:', error);
      setError(error.message || 'Failed to connect to the music generation service');
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePlayback = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => {
        setIsPlaying(true);
      }).catch(err => {
        console.error("Playback error:", err);
        if (err.name === 'NotAllowedError') {
          setError('Audio autoplay is blocked. Please try clicking play again.');
        } else if (err.name === 'NotSupportedError') {
          setError('Audio format not supported by your browser.');
        } else {
          setError(`Could not play audio: ${err.message}`);
        }
      });
    }
  };

  useEffect(() => {
    if (generatedTrack?.url && audioRef.current) {
      const audio = audioRef.current;
      const audioUrl = generatedTrack.url.startsWith('http')
        ? generatedTrack.url
        : `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'}${generatedTrack.url}`;
      
      audio.src = audioUrl;
      audio.load();

      const handleEnded = () => setIsPlaying(false);
      audio.addEventListener('ended', handleEnded);

      return () => {
        audio.removeEventListener('ended', handleEnded);
      };
    }
  }, [generatedTrack]);


  const downloadTrack = () => {
    if (generatedTrack?.download_url) {
      const downloadUrl = generatedTrack.download_url.startsWith('http')
        ? generatedTrack.download_url
        : `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'}${generatedTrack.download_url}`;
      window.open(downloadUrl, '_blank');
    }
  };

  const handleStructureToggle = (section) => {
    setFormData(prev => ({
      ...prev,
      structure: prev.structure.includes(section)
        ? prev.structure.filter(s => s !== section)
        : [...prev.structure, section]
    }));
  };

  const downloadStem = (instrument, url) => {
    const downloadUrl = url.startsWith('http')
      ? url
      : `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'}${url}`;
    window.open(downloadUrl, '_blank');
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

      {/* User Quota Display */}
      {userQuota && (
        <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Zap className="h-5 w-5 text-blue-600" />
              <span className="font-semibold text-gray-900">
                Plan: {userQuota.plan.charAt(0).toUpperCase() + userQuota.plan.slice(1)}
              </span>
            </div>
            <div className="text-sm text-gray-600">
              {userQuota.daily_limit > 0 ? (
                <>Remaining today: {userQuota.remaining_today}/{userQuota.daily_limit}</>
              ) : (
                'Unlimited generations'
              )}
            </div>
          </div>
        </div>
      )}

      {/* Error/Success Messages */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
          <span className="text-red-700">{error}</span>
        </div>
      )}
      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2">
          <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
          <span className="text-green-700">{success}</span>
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left Column - Input Controls */}
        <div className="space-y-6">
          {/* Lyrics Input */}
          <div className="bg-white rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Mic className="w-5 h-5 mr-2" />
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
                  {availableGenres.map(genre => (
                    <option key={genre.id} value={genre.id}>
                      {genre.name}
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
                  {availableMoods.map(mood => (
                    <option key={mood.id} value={mood.id}>
                      {mood.name}
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
                    {template.description}
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
            
            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <label className="block text-sm font-medium mb-2">Key</label>
                <select
                  className="w-full p-2 border rounded-lg"
                  value={formData.key}
                  onChange={(e) => handleInputChange('key', e.target.value)}
                >
                  {keyOptions.map(key => (
                    <option key={key} value={key}>{key}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Complexity</label>
                <select
                  className="w-full p-2 border rounded-lg"
                  value={formData.style_complexity}
                  onChange={(e) => handleInputChange('style_complexity', e.target.value)}
                >
                  {complexityOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
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

          {/* Song Structure */}
          <div className="bg-white rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-4">Song Structure (Optional)</h3>
            <div className="grid grid-cols-2 gap-2">
              {structureOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => handleStructureToggle(option.value)}
                  className={`p-2 text-sm rounded-lg border transition-colors ${
                    formData.structure.includes(option.value)
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
            {formData.structure.length > 0 && (
              <div className="mt-3 p-2 bg-gray-50 rounded text-sm">
                Structure: {formData.structure.join(' → ')}
              </div>
            )}
          </div>

          {/* Style Complexity, Key, and Structure */}
          <div className="bg-white rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-4">Composition Settings</h3>
            <div className="grid grid-cols-2 gap-4">
              {/* Style Complexity */}
              <div>
                <label className="block text-sm font-medium mb-2">Style Complexity</label>
                <select
                  className="w-full p-2 border rounded-lg"
                  value={formData.style_complexity}
                  onChange={(e) => handleInputChange('style_complexity', e.target.value)}
                >
                  {complexityOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Key Selection */}
              <div>
                <label className="block text-sm font-medium mb-2">Key</label>
                <select
                  className="w-full p-2 border rounded-lg"
                  value={formData.key}
                  onChange={(e) => handleInputChange('key', e.target.value)}
                >
                  {keyOptions.map(key => (
                    <option key={key} value={key}>
                      {key}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Song Structure */}
            <div className="mt-4">
              <label className="block text-sm font-medium mb-2">Song Structure</label>
              <div className="flex flex-wrap gap-2">
                {structureOptions.map(section => (
                  <button
                    key={section.value}
                    onClick={() => handleStructureToggle(section.value)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center space-x-2 ${
                      formData.structure.includes(section.value)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={formData.structure.includes(section.value)}
                      readOnly
                      className="form-checkbox h-4 w-4 text-blue-600"
                    />
                    <span>{section.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Instruments & Output */}
        <div className="space-y-6">
          {/* Instrument Selection */}
          <div className="bg-white rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Piano className="w-5 h-5 mr-2" />
              Select Instruments
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {availableInstruments.map(instrument => {
                const Icon = instrumentIcons[instrument.id] || Music;
                return (
                  <button
                    key={instrument.id}
                    onClick={() => handleInstrumentToggle(instrument.id)}
                    className={`p-4 rounded-lg border-2 flex flex-col items-center justify-center space-y-2 transition-all ${
                      formData.instruments.includes(instrument.id)
                        ? 'border-blue-500 bg-blue-50 text-blue-700 shadow-md'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-8 h-8" />
                    <span className="text-sm font-medium">{instrument.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Generate Button */}
          <div className="bg-white rounded-lg p-6 shadow-md text-center">
            <button
              onClick={generateMusic}
              disabled={isGenerating || formData.instruments.length === 0}
              className="w-full px-6 py-4 text-lg font-bold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <span className="flex items-center justify-center">
                  <Loader2 className="w-6 h-6 mr-2 animate-spin" />
                  Generating Composition...
                </span>
              ) : (
                'Generate Composition'
              )}
            </button>
            {formData.instruments.length === 0 && (
              <p className="text-xs text-red-500 mt-2">
                Please select at least one instrument to generate music.
              </p>
            )}
          </div>

          {/* Output Section */}
          {generatedTrack && (
            <div className="bg-white rounded-lg p-6 shadow-md animate-fade-in">
              <h3 className="text-xl font-semibold mb-4">Your Composition</h3>
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="font-medium">{generatedTrack.title}</div>
                <div className="flex items-center space-x-2">
                  <button onClick={togglePlayback} className="p-2 rounded-full hover:bg-gray-200">
                    {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  </button>
                  <button onClick={downloadTrack} className="p-2 rounded-full hover:bg-gray-200">
                    <Download className="w-5 h-5" />
                  </button>
                </div>
              </div>
              <audio 
                ref={audioRef} 
                className="hidden"
                preload="metadata"
                onError={(e) => {
                  console.error('Audio element error:', e);
                  const errorCode = e.target.error?.code || 'unknown';
                  setError(`Audio playback error: ${getAudioErrorMessage(e.target.error)}`);
                }}
              />

              {/* Stems Download */}
              {generatedTrack.stem_urls && Object.keys(generatedTrack.stem_urls).length > 0 && (
                <div className="mt-4">
                  <h4 className="font-semibold mb-2">Download Stems</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(generatedTrack.stem_urls).map(([instrument, url]) => (
                      <button
                        key={instrument}
                        onClick={() => downloadStem(instrument, url)}
                        className="w-full text-left p-2 bg-gray-100 rounded-lg hover:bg-gray-200 text-sm flex items-center justify-between"
                      >
                        <span>{instrument}</span>
                        <Download className="w-4 h-4" />
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedMusicGenerator;
