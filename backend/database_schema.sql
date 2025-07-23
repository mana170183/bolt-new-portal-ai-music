-- Full AI Music Platform Database Schema
-- This script creates all necessary tables for metadata, user management, and training data

-- Create database (run this separately if needed)
-- CREATE DATABASE AIMusePlatform;
-- USE AIMusePlatform;

-- Genres table with detailed metadata
CREATE TABLE IF NOT EXISTS genres (
    id INT IDENTITY(1,1) PRIMARY KEY,
    genre_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    bpm_range_min INT DEFAULT 80,
    bpm_range_max INT DEFAULT 160,
    key_signatures TEXT, -- JSON array of common keys
    chord_progressions TEXT, -- JSON array of common progressions
    instruments TEXT, -- JSON array of typical instruments
    production_style TEXT, -- JSON object with style characteristics
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Moods table with audio parameters
CREATE TABLE IF NOT EXISTS moods (
    id INT IDENTITY(1,1) PRIMARY KEY,
    mood_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    energy_level INT CHECK (energy_level BETWEEN 1 AND 10), -- 1=very calm, 10=very energetic
    valence INT CHECK (valence BETWEEN 1 AND 10), -- 1=very negative, 10=very positive
    arousal INT CHECK (arousal BETWEEN 1 AND 10), -- 1=very relaxed, 10=very intense
    audio_parameters TEXT, -- JSON with ADSR, brightness, filters, etc.
    color_code VARCHAR(7), -- Hex color for UI
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Training data metadata
CREATE TABLE IF NOT EXISTS training_tracks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    track_name VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255),
    genre_id INT FOREIGN KEY REFERENCES genres(id),
    mood_id INT FOREIGN KEY REFERENCES moods(id),
    duration_seconds INT,
    bpm INT,
    key_signature VARCHAR(10),
    time_signature VARCHAR(10),
    audio_features TEXT, -- JSON with detailed audio analysis
    file_path VARCHAR(500), -- Path in blob storage
    file_size_bytes BIGINT,
    audio_format VARCHAR(20),
    sample_rate INT DEFAULT 44100,
    channels INT DEFAULT 2,
    quality_score DECIMAL(3,2), -- AI-assessed quality 0.00-1.00
    copyright_status VARCHAR(50), -- 'public_domain', 'creative_commons', 'licensed'
    source_url VARCHAR(500),
    downloaded_at DATETIME2 DEFAULT GETDATE(),
    processed_at DATETIME2,
    is_processed BIT DEFAULT 0,
    embedding_vector VARBINARY(MAX), -- Store audio embeddings for similarity
    created_at DATETIME2 DEFAULT GETDATE()
);

-- User-generated music tracks
CREATE TABLE IF NOT EXISTS generated_tracks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    track_id VARCHAR(100) NOT NULL UNIQUE, -- UUID for public access
    user_prompt TEXT,
    genre_id INT FOREIGN KEY REFERENCES genres(id),
    mood_id INT FOREIGN KEY REFERENCES moods(id),
    duration_seconds INT,
    parameters TEXT, -- JSON with all generation parameters
    file_path VARCHAR(500), -- Path in blob storage
    file_size_bytes BIGINT,
    audio_format VARCHAR(20),
    sample_rate INT DEFAULT 44100,
    generation_model VARCHAR(100), -- Which AI model was used
    generation_time_seconds DECIMAL(5,2),
    quality_score DECIMAL(3,2),
    user_rating INT CHECK (user_rating BETWEEN 1 AND 5),
    play_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    is_public BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- AI model training sessions
CREATE TABLE IF NOT EXISTS training_sessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    session_name VARCHAR(200) NOT NULL,
    model_type VARCHAR(100), -- 'azure_openai', 'local_diffusion', 'rnn', etc.
    base_model VARCHAR(100),
    training_data_filter TEXT, -- JSON criteria for selecting training data
    hyperparameters TEXT, -- JSON with training configuration
    epochs_completed INT DEFAULT 0,
    loss_value DECIMAL(10,6),
    validation_score DECIMAL(5,4),
    model_path VARCHAR(500), -- Path to saved model
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'training', 'completed', 'failed'
    started_at DATETIME2,
    completed_at DATETIME2,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Composition templates for advanced mode
CREATE TABLE IF NOT EXISTS composition_templates (
    id INT IDENTITY(1,1) PRIMARY KEY,
    template_name VARCHAR(200) NOT NULL,
    genre_id INT FOREIGN KEY REFERENCES genres(id),
    structure TEXT NOT NULL, -- JSON array: [{"section": "intro", "duration": 8, "chords": "..."}, ...]
    description TEXT,
    difficulty_level INT CHECK (difficulty_level BETWEEN 1 AND 5),
    instruments TEXT, -- JSON array of required instruments
    is_premium BIT DEFAULT 0,
    usage_count INT DEFAULT 0,
    created_by VARCHAR(100), -- 'system' or user identifier
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- User preferences and history
CREATE TABLE IF NOT EXISTS user_preferences (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_session VARCHAR(100) NOT NULL, -- Session identifier
    favorite_genres TEXT, -- JSON array of genre IDs
    favorite_moods TEXT, -- JSON array of mood IDs
    preferred_duration INT DEFAULT 30,
    preferred_instruments TEXT, -- JSON array
    generation_history TEXT, -- JSON array of recent generation parameters
    last_active DATETIME2 DEFAULT GETDATE(),
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Insert comprehensive genre data
INSERT INTO genres (genre_code, name, description, bpm_range_min, bpm_range_max, key_signatures, chord_progressions, instruments, production_style) VALUES
('pop', 'Pop', 'Catchy mainstream music with broad appeal', 100, 130, '["C", "G", "F", "Am", "Dm"]', '[["C", "Am", "F", "G"], ["vi", "IV", "I", "V"], ["I", "V", "vi", "IV"]]', '["vocals", "electric_guitar", "bass", "drums", "piano", "synth"]', '{"reverb": "medium", "compression": "high", "brightness": 1.2, "punch": "strong"}'),
('rock', 'Rock', 'Guitar-driven energetic music with strong rhythms', 110, 140, '["E", "A", "D", "G", "B"]', '[["E", "A", "B", "E"], ["vi", "IV", "I", "V"], ["i", "bVII", "IV", "i"]]', '["electric_guitar", "bass", "drums", "vocals"]', '{"distortion": "medium", "reverb": "hall", "compression": "medium", "brightness": 1.3}'),
('jazz', 'Jazz', 'Sophisticated music with complex harmonies and improvisation', 80, 180, '["Bb", "F", "Eb", "C", "G"]', '[["ii7", "V7", "Imaj7"], ["Imaj7", "vi7", "ii7", "V7"], ["iii7", "vi7", "ii7", "V7"]]', '["piano", "upright_bass", "drums", "saxophone", "trumpet", "vocals"]', '{"reverb": "room", "compression": "light", "brightness": 1.0, "swing": true}'),
('electronic', 'Electronic', 'Digital and synthesized sounds with programmed beats', 110, 140, '["C", "G", "F", "Am", "Dm"]', '[["C", "Am", "F", "G"], ["vi", "IV", "I", "V"]]', '["synth", "drum_machine", "bass_synth", "lead_synth", "pad", "arp"]', '{"reverb": "digital", "compression": "heavy", "brightness": 1.4, "sidechain": true}'),
('hip-hop', 'Hip Hop', 'Urban beats with rhythmic vocals and strong bass', 70, 100, '["C", "G", "F", "Bb", "Dm"]', '[["i", "bVII", "bVI", "bVII"], ["i", "iv", "bVII", "i"]]', '["drums", "bass", "piano", "synth", "vocals", "strings"]', '{"reverb": "short", "compression": "punchy", "brightness": 1.1, "bass_heavy": true}'),
('classical', 'Classical', 'Traditional orchestral music with complex arrangements', 60, 120, '["C", "G", "D", "F", "Bb", "A", "E"]', '[["I", "V", "vi", "IV"], ["ii", "V", "I"], ["I", "IV", "V", "I"]]', '["violin", "viola", "cello", "contrabass", "flute", "oboe", "clarinet", "bassoon", "horn", "trumpet", "trombone", "timpani"]', '{"reverb": "cathedral", "compression": "minimal", "dynamics": "wide", "spatial": "orchestral"}'),
('ambient', 'Ambient', 'Atmospheric background music for relaxation', 60, 90, '["C", "Am", "F", "G", "Dm"]', '[["I", "V", "vi", "IV"], ["vi", "IV", "I", "V"]]', '["pad", "strings", "ambient_textures", "soft_piano", "field_recordings"]', '{"reverb": "long", "compression": "minimal", "brightness": 0.8, "spatial": "wide"}'),
('cinematic', 'Cinematic', 'Epic orchestral music for films and media', 70, 140, '["C", "Bb", "F", "G", "Dm", "Am"]', '[["i", "bVI", "bVII", "i"], ["I", "V", "vi", "IV"], ["vi", "IV", "I", "V"]]', '["orchestra", "choir", "epic_percussion", "brass", "strings", "woodwinds"]', '{"reverb": "hall", "compression": "cinematic", "dynamics": "epic", "spatial": "wide"}'),
('folk', 'Folk', 'Acoustic traditional music with storytelling', 90, 120, '["G", "D", "C", "A", "E"]', '[["G", "C", "D", "G"], ["Am", "F", "C", "G"], ["D", "G", "A", "D"]]', '["acoustic_guitar", "vocals", "fiddle", "banjo", "harmonica", "upright_bass"]', '{"reverb": "natural", "compression": "light", "brightness": 1.0, "warmth": "high"}'),
('country', 'Country', 'American country music with storytelling', 100, 130, '["G", "D", "C", "A", "E"]', '[["I", "V", "vi", "IV"], ["I", "IV", "V", "I"]]', '["acoustic_guitar", "electric_guitar", "pedal_steel", "fiddle", "bass", "drums", "vocals"]', '{"reverb": "room", "compression": "country", "brightness": 1.1, "twang": true}');

-- Insert comprehensive mood data
INSERT INTO moods (mood_code, name, description, energy_level, valence, arousal, audio_parameters, color_code) VALUES
('uplifting', 'Uplifting', 'Positive and inspiring energy', 7, 9, 6, '{"attack": 0.1, "decay": 0.3, "sustain": 0.7, "release": 0.4, "brightness": 1.2, "volume": 0.7, "reverb": "bright", "eq": {"low": 1.0, "mid": 1.1, "high": 1.2}}', '#FFD700'),
('calm', 'Calm', 'Peaceful and relaxing', 3, 7, 2, '{"attack": 0.2, "decay": 0.5, "sustain": 0.6, "release": 0.8, "brightness": 0.8, "volume": 0.4, "reverb": "soft", "eq": {"low": 1.1, "mid": 0.9, "high": 0.8}}', '#87CEEB'),
('energetic', 'Energetic', 'High energy and motivating', 9, 8, 9, '{"attack": 0.05, "decay": 0.2, "sustain": 0.8, "release": 0.3, "brightness": 1.3, "volume": 0.8, "reverb": "punchy", "eq": {"low": 1.2, "mid": 1.1, "high": 1.3}}', '#FF6B35'),
('dramatic', 'Dramatic', 'Intense and emotional', 8, 5, 8, '{"attack": 0.15, "decay": 0.4, "sustain": 0.9, "release": 0.6, "brightness": 1.1, "volume": 0.9, "reverb": "cathedral", "eq": {"low": 1.3, "mid": 1.0, "high": 1.1}}', '#8B0000'),
('mysterious', 'Mysterious', 'Dark and intriguing', 5, 3, 6, '{"attack": 0.3, "decay": 0.6, "sustain": 0.5, "release": 1.0, "brightness": 0.7, "volume": 0.6, "reverb": "dark", "eq": {"low": 1.2, "mid": 0.8, "high": 0.7}}', '#4B0082'),
('romantic', 'Romantic', 'Love and tender emotions', 4, 8, 5, '{"attack": 0.25, "decay": 0.4, "sustain": 0.8, "release": 0.7, "brightness": 0.9, "volume": 0.5, "reverb": "warm", "eq": {"low": 1.0, "mid": 1.1, "high": 0.9}}', '#FF69B4'),
('triumphant', 'Triumphant', 'Victory and achievement', 8, 9, 7, '{"attack": 0.1, "decay": 0.3, "sustain": 0.9, "release": 0.5, "brightness": 1.3, "volume": 0.85, "reverb": "grand", "eq": {"low": 1.2, "mid": 1.2, "high": 1.3}}', '#FFD700'),
('melancholic', 'Melancholic', 'Sad and reflective', 3, 2, 4, '{"attack": 0.4, "decay": 0.7, "sustain": 0.4, "release": 1.2, "brightness": 0.6, "volume": 0.4, "reverb": "distant", "eq": {"low": 0.9, "mid": 0.8, "high": 0.6}}', '#708090');

-- Insert sample composition templates
INSERT INTO composition_templates (template_name, genre_id, structure, description, difficulty_level, instruments) VALUES
('Pop Ballad', 1, '[{"section": "intro", "duration": 8, "chords": ["vi", "IV", "I", "V"], "dynamics": "soft"}, {"section": "verse", "duration": 16, "chords": ["I", "V", "vi", "IV"], "dynamics": "building"}, {"section": "chorus", "duration": 16, "chords": ["vi", "IV", "I", "V"], "dynamics": "full"}, {"section": "bridge", "duration": 8, "chords": ["ii", "V", "I"], "dynamics": "emotional"}, {"section": "outro", "duration": 8, "chords": ["vi", "IV", "I"], "dynamics": "fade"}]', 'Emotional pop ballad structure', 2, '["piano", "strings", "vocals", "light_drums"]'),
('Rock Anthem', 2, '[{"section": "intro", "duration": 8, "chords": ["E", "A", "B"], "dynamics": "building"}, {"section": "verse", "duration": 16, "chords": ["E", "A", "E", "B"], "dynamics": "medium"}, {"section": "chorus", "duration": 16, "chords": ["E", "A", "B", "E"], "dynamics": "full"}, {"section": "solo", "duration": 16, "chords": ["A", "B", "E"], "dynamics": "intense"}, {"section": "final_chorus", "duration": 16, "chords": ["E", "A", "B", "E"], "dynamics": "maximum"}]', 'High-energy rock song structure', 3, '["electric_guitar", "bass", "drums", "lead_guitar", "vocals"]');

-- Create indexes for performance
CREATE INDEX IX_genres_code ON genres(genre_code);
CREATE INDEX IX_moods_code ON moods(mood_code);
CREATE INDEX IX_training_tracks_genre ON training_tracks(genre_id);
CREATE INDEX IX_training_tracks_mood ON training_tracks(mood_id);
CREATE INDEX IX_generated_tracks_created ON generated_tracks(created_at);
CREATE INDEX IX_user_preferences_session ON user_preferences(user_session);
