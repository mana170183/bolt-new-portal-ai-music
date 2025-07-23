-- Portal AI Music Database Schema

-- Music Catalog Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='music_catalog' AND xtype='U')
CREATE TABLE music_catalog (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    artist NVARCHAR(200),
    genre NVARCHAR(100),
    duration_seconds INT,
    file_url NVARCHAR(500),
    blob_path NVARCHAR(500),
    metadata NVARCHAR(MAX), -- JSON metadata
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Generated Music Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='generated_music' AND xtype='U')
CREATE TABLE generated_music (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    prompt NVARCHAR(MAX),
    style NVARCHAR(100),
    genre NVARCHAR(100),
    duration_seconds INT,
    file_url NVARCHAR(500),
    blob_path NVARCHAR(500),
    model_used NVARCHAR(100),
    generation_params NVARCHAR(MAX), -- JSON parameters
    status NVARCHAR(50) DEFAULT 'pending', -- pending, generating, completed, failed
    created_at DATETIME2 DEFAULT GETDATE(),
    completed_at DATETIME2
);

-- User Sessions Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='user_sessions' AND xtype='U')
CREATE TABLE user_sessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    session_id NVARCHAR(100) UNIQUE NOT NULL,
    user_ip NVARCHAR(50),
    user_agent NVARCHAR(500),
    total_generations INT DEFAULT 0,
    last_activity DATETIME2 DEFAULT GETDATE(),
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Training Data Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='training_data' AND xtype='U')
CREATE TABLE training_data (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    file_type NVARCHAR(50), -- audio, midi, sheet
    blob_path NVARCHAR(500),
    file_size_bytes BIGINT,
    metadata NVARCHAR(MAX), -- JSON metadata
    processed BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Music Templates Table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='music_templates' AND xtype='U')
CREATE TABLE music_templates (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    category NVARCHAR(100), -- genre, style, instrument
    template_data NVARCHAR(MAX), -- JSON template configuration
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Insert sample data for testing
IF NOT EXISTS (SELECT * FROM music_catalog WHERE title = 'Sample Track 1')
INSERT INTO music_catalog (title, artist, genre, duration_seconds, metadata) VALUES
('Sample Track 1', 'AI Composer', 'Electronic', 180, '{"bpm": 120, "key": "C major"}'),
('Sample Track 2', 'AI Composer', 'Ambient', 240, '{"bpm": 90, "key": "A minor"}'),
('Sample Track 3', 'AI Composer', 'Classical', 300, '{"bpm": 140, "key": "D major"}');

IF NOT EXISTS (SELECT * FROM music_templates WHERE name = 'Electronic Beat')
INSERT INTO music_templates (name, category, template_data) VALUES
('Electronic Beat', 'Electronic', '{"instruments": ["synth", "drums"], "bpm": 128, "structure": "intro-verse-chorus-verse-chorus-outro"}'),
('Ambient Pad', 'Ambient', '{"instruments": ["pad", "reverb"], "bpm": 80, "structure": "free-form"}'),
('Classical Suite', 'Classical', '{"instruments": ["piano", "strings"], "bpm": 120, "structure": "allegro-andante-allegro"}');

PRINT 'Database schema created successfully!';
