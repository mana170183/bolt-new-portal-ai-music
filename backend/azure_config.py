# Azure Configuration for AI Music Portal
# This file contains all Azure service configurations and credentials

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure Service Principal Credentials (from user requirements)
AZURE_CREDENTIALS = {
    'SP_APP_ID': '6a069624-67ed-4bfe-b4e6-301f6e02a853',
    'SP_PASSWORD': 'Q9a8Q~XRiQ3hKIHKUCFn6ka.jZ3udfNwyI.s2aC5',
    'SP_TENANT': 'bca013b2-c163-4a0d-ad43-e6f1d3cda34b',
    'RESOURCE_GROUP': 'rg-portal-ai-music'
}

# Azure SQL Database Configuration
AZURE_SQL_CONFIG = {
    'server': f"{AZURE_CREDENTIALS['RESOURCE_GROUP']}-sql.database.windows.net",
    'database': 'ai-music-portal-db',
    'username': 'sqladmin',
    'password': os.getenv('AZURE_SQL_PASSWORD', 'DefaultPassword123!'),
    'driver': '{ODBC Driver 18 for SQL Server}',
    'connection_string': None  # Will be constructed dynamically
}

# Azure Blob Storage Configuration
AZURE_STORAGE_CONFIG = {
    'account_name': f"{AZURE_CREDENTIALS['RESOURCE_GROUP'].replace('-', '')}storage",
    'account_key': os.getenv('AZURE_STORAGE_KEY'),
    'container_name': 'ai-music-tracks',
    'container_name_uploads': 'user-uploads',
    'container_name_demos': 'demo-tracks',
    'connection_string': None  # Will be constructed dynamically
}

# Azure OpenAI Configuration
AZURE_OPENAI_CONFIG = {
    'endpoint': f"https://{AZURE_CREDENTIALS['RESOURCE_GROUP']}-openai.openai.azure.com/",
    'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
    'api_version': '2024-02-15-preview',
    'deployment_name': 'gpt-4',
    'model': 'gpt-4',
    'max_tokens': 4000,
    'temperature': 0.7
}

# Azure Key Vault Configuration
AZURE_KEYVAULT_CONFIG = {
    'vault_name': f"{AZURE_CREDENTIALS['RESOURCE_GROUP']}-keyvault",
    'vault_url': f"https://{AZURE_CREDENTIALS['RESOURCE_GROUP']}-keyvault.vault.azure.net/"
}

# Construct connection strings
def get_azure_sql_connection_string():
    """Construct Azure SQL connection string"""
    return (
        f"Driver={AZURE_SQL_CONFIG['driver']};"
        f"Server=tcp:{AZURE_SQL_CONFIG['server']},1433;"
        f"Database={AZURE_SQL_CONFIG['database']};"
        f"Uid={AZURE_SQL_CONFIG['username']};"
        f"Pwd={AZURE_SQL_CONFIG['password']};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )

def get_azure_storage_connection_string():
    """Construct Azure Storage connection string"""
    if AZURE_STORAGE_CONFIG['account_key']:
        return (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={AZURE_STORAGE_CONFIG['account_name']};"
            f"AccountKey={AZURE_STORAGE_CONFIG['account_key']};"
            f"EndpointSuffix=core.windows.net"
        )
    return None

# Update configs with connection strings
AZURE_SQL_CONFIG['connection_string'] = get_azure_sql_connection_string()
AZURE_STORAGE_CONFIG['connection_string'] = get_azure_storage_connection_string()

# Environment variables for Azure authentication
AZURE_ENV_VARS = {
    'AZURE_CLIENT_ID': AZURE_CREDENTIALS['SP_APP_ID'],
    'AZURE_CLIENT_SECRET': AZURE_CREDENTIALS['SP_PASSWORD'],
    'AZURE_TENANT_ID': AZURE_CREDENTIALS['SP_TENANT']
}

# Set environment variables for Azure SDK
for key, value in AZURE_ENV_VARS.items():
    os.environ[key] = value

# API Configuration for Music Generation Services
MUSIC_API_CONFIG = {
    'suno': {
        'base_url': 'https://api.suno.ai/v1',
        'api_key': os.getenv('SUNO_API_KEY'),
        'enabled': bool(os.getenv('SUNO_API_KEY'))
    },
    'musicgen': {
        'base_url': 'https://api.replicate.com/v1',
        'api_key': os.getenv('REPLICATE_API_KEY'),
        'model': 'meta/musicgen',
        'enabled': bool(os.getenv('REPLICATE_API_KEY'))
    },
    'mubert': {
        'base_url': 'https://api-b2b.mubert.com/v2',
        'api_key': os.getenv('MUBERT_API_KEY'),
        'enabled': bool(os.getenv('MUBERT_API_KEY'))
    }
}

# Free Music Data APIs for Testing
FREE_MUSIC_APIS = {
    'freemusicarchive': {
        'base_url': 'https://freemusicarchive.org/api/v1',
        'enabled': True,
        'auth_required': False
    },
    'jamendo': {
        'base_url': 'https://api.jamendo.com/v3.0',
        'client_id': os.getenv('JAMENDO_CLIENT_ID'),
        'enabled': bool(os.getenv('JAMENDO_CLIENT_ID'))
    },
    'deezer': {
        'base_url': 'https://api.deezer.com',
        'enabled': True,
        'auth_required': False
    },
    'pixabay': {
        'base_url': 'https://pixabay.com/api',
        'api_key': os.getenv('PIXABAY_API_KEY'),
        'enabled': bool(os.getenv('PIXABAY_API_KEY'))
    }
}

# Database Tables Schema
DB_SCHEMA = {
    'users': '''
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(50) PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            plan VARCHAR(50) DEFAULT 'free',
            quota_daily_limit INT DEFAULT 50,
            quota_daily_used INT DEFAULT 0,
            quota_reset_date DATE,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
    ''',
    'tracks': '''
        CREATE TABLE IF NOT EXISTS tracks (
            id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50),
            title VARCHAR(255),
            prompt TEXT,
            genre VARCHAR(100),
            mood VARCHAR(100),
            duration INT,
            file_url VARCHAR(500),
            blob_name VARCHAR(255),
            metadata TEXT,
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''',
    'demo_tracks': '''
        CREATE TABLE IF NOT EXISTS demo_tracks (
            id VARCHAR(50) PRIMARY KEY,
            title VARCHAR(255),
            genre VARCHAR(100),
            duration INT,
            file_url VARCHAR(500),
            blob_name VARCHAR(255),
            featured BOOLEAN DEFAULT 0,
            play_count INT DEFAULT 0,
            created_at DATETIME DEFAULT GETDATE()
        )
    ''',
    'user_library': '''
        CREATE TABLE IF NOT EXISTS user_library (
            id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50),
            track_id VARCHAR(50),
            is_favorite BOOLEAN DEFAULT 0,
            play_count INT DEFAULT 0,
            last_played DATETIME,
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        )
    '''
}

print("✅ Azure configuration loaded successfully")
print(f"📊 Resource Group: {AZURE_CREDENTIALS['RESOURCE_GROUP']}")
print(f"🗄️ SQL Server: {AZURE_SQL_CONFIG['server']}")
print(f"💾 Storage Account: {AZURE_STORAGE_CONFIG['account_name']}")
print(f"🤖 OpenAI Endpoint: {AZURE_OPENAI_CONFIG['endpoint']}")
