#!/bin/bash

echo "=== Portal AI Music - Azure Integration Setup ==="

# Set resource group and discovered resources
RESOURCE_GROUP="rg-portal-ai-music-dev"
SQL_SERVER="sql-portal-ai-music-dev"
SQL_DATABASE="portal-ai-music-db"
STORAGE_ACCOUNT="stportalaimusic439"
OPENAI_ACCOUNT="openai-portal-ai-music-dev"
KEY_VAULT="kv-portal-ai-music-dev"
ACR_NAME="acrportalaimusic508"

echo "Discovered Azure Resources:"
echo "- SQL Server: $SQL_SERVER"
echo "- SQL Database: $SQL_DATABASE"
echo "- Storage Account: $STORAGE_ACCOUNT"
echo "- OpenAI Account: $OPENAI_ACCOUNT"
echo "- Key Vault: $KEY_VAULT"
echo "- Container Registry: $ACR_NAME"

# Get connection details
echo -e "\n=== Getting Connection Details ==="
SQL_FQDN=$(az sql server show --name $SQL_SERVER --resource-group $RESOURCE_GROUP --query "fullyQualifiedDomainName" -o tsv 2>/dev/null || echo "sql-portal-ai-music-dev.database.windows.net")
STORAGE_ENDPOINT=$(az storage account show --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --query "primaryEndpoints.blob" -o tsv 2>/dev/null || echo "https://stportalaimusic439.blob.core.windows.net/")
OPENAI_ENDPOINT=$(az cognitiveservices account show --name $OPENAI_ACCOUNT --resource-group $RESOURCE_GROUP --query "properties.endpoint" -o tsv 2>/dev/null || echo "https://openai-portal-ai-music-dev.openai.azure.com/")
KV_URI=$(az keyvault show --name $KEY_VAULT --resource-group $RESOURCE_GROUP --query "properties.vaultUri" -o tsv 2>/dev/null || echo "https://kv-portal-ai-music-dev.vault.azure.net/")
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" -o tsv 2>/dev/null || echo "acrportalaimusic508.azurecr.io")

echo "Connection Details:"
echo "- SQL Server FQDN: $SQL_FQDN"
echo "- Storage Endpoint: $STORAGE_ENDPOINT"
echo "- OpenAI Endpoint: $OPENAI_ENDPOINT"
echo "- Key Vault URI: $KV_URI"
echo "- ACR Login Server: $ACR_LOGIN_SERVER"

# Create storage containers if they don't exist
echo -e "\n=== Creating Storage Containers ==="
az storage container create --name music-files --account-name $STORAGE_ACCOUNT --public-access off 2>/dev/null || echo "Container 'music-files' already exists or couldn't be created"
az storage container create --name generated-music --account-name $STORAGE_ACCOUNT --public-access off 2>/dev/null || echo "Container 'generated-music' already exists or couldn't be created"
az storage container create --name training-data --account-name $STORAGE_ACCOUNT --public-access off 2>/dev/null || echo "Container 'training-data' already exists or couldn't be created"

# Create SQL schema
echo -e "\n=== Creating SQL Database Schema ==="
cat > create_schema.sql << 'EOF'
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
EOF

echo "Executing SQL schema creation..."
# You may need to set SQL authentication details
# sqlcmd -S $SQL_FQDN -d $SQL_DATABASE -i create_schema.sql -U <username> -P <password>
echo "SQL schema file created at: $(pwd)/create_schema.sql"
echo "Please run this SQL script on your database manually or set up SQL authentication"

echo -e "\n=== Azure Integration Setup Complete ==="
echo "Next Steps:"
echo "1. Execute the SQL schema: create_schema.sql"
echo "2. Update backend environment variables"
echo "3. Deploy the updated backend"
echo "4. Test all endpoints"

# Export environment variables for backend
cat > .env.azure << EOF
# Azure Integration Environment Variables
AZURE_SQL_SERVER=$SQL_FQDN
AZURE_SQL_DATABASE=$SQL_DATABASE
AZURE_STORAGE_ACCOUNT=$STORAGE_ACCOUNT
AZURE_STORAGE_ENDPOINT=$STORAGE_ENDPOINT
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_KEY_VAULT_URI=$KV_URI
AZURE_CONTAINER_REGISTRY=$ACR_LOGIN_SERVER
RESOURCE_GROUP=$RESOURCE_GROUP

# Connection strings (update with actual credentials)
AZURE_SQL_CONNECTION_STRING="Driver={ODBC Driver 17 for SQL Server};Server=$SQL_FQDN;Database=$SQL_DATABASE;Uid=<username>;Pwd=<password>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=$STORAGE_ACCOUNT;AccountKey=<storage_key>;EndpointSuffix=core.windows.net"
AZURE_OPENAI_API_KEY="<openai_api_key>"
EOF

echo "Environment variables saved to: .env.azure"
