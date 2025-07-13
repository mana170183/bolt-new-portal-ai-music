# Portal AI Music - Azure Enterprise Deployment 🎵

## Overview

Portal AI Music is an enterprise-grade AI-powered music generation platform deployed on Microsoft Azure. This solution provides a comprehensive, scalable, and compliant infrastructure supporting 100+ concurrent users with SOC 2 Type II and GDPR compliance.

![Portal AI Music Architecture](https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=1200&h=400&fit=crop&crop=center)

## 🏗️ Architecture

### Azure Services
- **Azure Container Apps**: Scalable application hosting with auto-scaling
- **Azure Container Registry**: Private container image storage
- **Azure SQL Database**: Business Critical tier with geo-replication
- **Azure Storage**: Hot tier with lifecycle management and CDN
- **Azure Cache for Redis**: Premium tier with persistence
- **Azure OpenAI**: GPT-4, GPT-3.5-Turbo, and text embeddings
- **Azure Cognitive Services**: Speech synthesis and analysis
- **Azure Machine Learning**: Model training and deployment
- **Azure AD B2C**: Identity management with MFA and conditional access
- **Azure Monitor**: Comprehensive monitoring, alerting, and dashboards
- **Azure Key Vault**: Secure secrets and certificate management

### Security & Compliance
- **Network Isolation**: Private endpoints and VNet integration
- **Data Encryption**: End-to-end encryption at rest and in transit
- **Identity Security**: Multi-factor authentication and conditional access
- **Compliance**: SOC 2 Type II and GDPR ready with audit logging
- **Monitoring**: Real-time security monitoring and incident response

## 🚀 Quick Start

### Prerequisites
- Azure subscription with Owner permissions
- Azure CLI installed
- Terraform >= 1.0
- Docker
- Git

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/your-org/portal-ai-music.git
cd portal-ai-music

# Login to Azure
az login
az account set --subscription "your-subscription-id"

# Create service principal for GitHub Actions
az ad sp create-for-rbac --name "portal-ai-music-github" \
  --role "Owner" \
  --scopes "/subscriptions/your-subscription-id" \
  --sdk-auth
```

### 2. Configure GitHub Secrets

Add these secrets to your GitHub repository:

| Secret | Description |
|--------|-------------|
| `AZURE_CREDENTIALS` | Service principal JSON from step 1 |
| `AZURE_CLIENT_ID` | Service principal client ID |
| `AZURE_CLIENT_SECRET` | Service principal secret |
| `AZURE_SUBSCRIPTION_ID` | Your Azure subscription ID |
| `AZURE_TENANT_ID` | Your Azure tenant ID |
| `TF_STATE_STORAGE_ACCOUNT` | Terraform state storage account |

### 3. Deploy Infrastructure

```bash
# Initialize Terraform
cd infrastructure/terraform
terraform init -backend-config=environments/backend-dev.hcl

# Plan deployment
terraform plan -var-file=environments/dev.tfvars

# Deploy infrastructure
terraform apply -var-file=environments/dev.tfvars

# Get deployment outputs
terraform output
```

### 4. Deploy Application

```bash
# Build and push container image
docker build -t portal-ai-music .
docker tag portal-ai-music <acr-name>.azurecr.io/portal-ai-music:latest
docker push <acr-name>.azurecr.io/portal-ai-music:latest

# Or use GitHub Actions for automated deployment
git push origin main
```
   cd portal-ai-music
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Start the backend server** (in a new terminal)
   
   **Option A: Using the startup script (Recommended)**
   ```bash
   # Make sure you're in the project root directory first
   # (the directory containing backend/, src/, README.md, etc.)
   
   # On Linux/Mac
   chmod +x start-backend.sh
   ./start-backend.sh
   
   # On Windows
   start-backend.bat
   ```
   
   **Option B: Manual setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

4. **Start the frontend** (in another terminal)
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

### Troubleshooting

**Backend Connection Issues:**
- Ensure the Flask server is running on port 5000
- Check that no other service is using port 5000
- Verify the backend server starts without errors
- Test the health endpoint: `curl http://localhost:5000/health`
- Make sure you're running the startup script from the project root directory

**Common Errors:**
- `ECONNREFUSED 127.0.0.1:5000`: Backend server is not running
- `500 Internal Server Error`: Check backend terminal for error messages
- `Authentication failed`: Backend server may have crashed or restarted
- `cd: no such file or directory: backend`: Run the script from the project root directory
- `ModuleNotFoundError: No module named '_signal'`: Corrupted Python environment - delete the `backend/venv` folder and run the startup script again

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   Flask API     │    │  Azure Blob     │
│  (Frontend)     │◄──►│   (Backend)     │◄──►│   Storage       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Azure Static    │    │ Azure App       │    │ AI Models       │
│ Web Apps        │    │ Service         │    │ (MusicGen)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern UI framework
- **Tailwind CSS** - Utility-first styling
- **Vite** - Fast build tool
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client

### Backend
- **Flask** - Lightweight Python web framework
- **Azure Blob Storage** - File storage
- **Transformers** - AI model integration
- **Gunicorn** - WSGI server

### AI & ML
- **MusicGen** - Meta's music generation model
- **Hugging Face** - Model hosting and inference
- **PyTorch** - Deep learning framework

### Cloud & DevOps
- **Azure Static Web Apps** - Frontend hosting
- **Azure App Service** - Backend hosting
- **GitHub Actions** - CI/CD pipeline
- **Docker** - Containerization

## 📁 Project Structure

```
portal-ai-music/
├── src/                    # Frontend source code
│   ├── components/         # React components
│   ├── App.jsx            # Main app component
│   └── main.jsx           # Entry point
├── backend/               # Backend source code
│   ├── app.py            # Flask application
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Container configuration
├── deployment/           # Deployment configurations
│   ├── azure-deploy.yml  # Frontend deployment
│   └── backend-deploy.yml # Backend deployment
├── docs/                 # Documentation
│   ├── API.md           # API documentation
│   └── DEPLOYMENT.md    # Deployment guide
└── README.md            # This file
```

## 🎵 How It Works

1. **Input**: User describes the desired music in natural language
2. **Processing**: AI model (MusicGen) generates audio based on the description
3. **Enhancement**: Audio is processed and optimized for quality
4. **Storage**: Generated track is stored in Azure Blob Storage
5. **Delivery**: User receives download link for high-quality audio file

## 🔧 Configuration

### Environment Variables

**Frontend (.env)**
```env
VITE_API_URL=http://localhost:5000
```

**Backend (.env)**
```env
AZURE_CONNECTION_STRING=your_azure_storage_connection_string
CONTAINER_NAME=music-files
FLASK_ENV=development
PORT=5000
```

## 🚀 Deployment

### Azure Deployment

1. **Frontend (Azure Static Web Apps)**
   ```bash
   # Deploy using GitHub Actions (automatic)
   # Or manually using Azure CLI
   az staticwebapp create --name portal-ai-music --resource-group myRG
   ```

2. **Backend (Azure App Service)**
   ```bash
   # Deploy using Azure CLI
   az webapp up --name portal-ai-music-api --resource-group myRG
   ```

3. **Storage (Azure Blob Storage)**
   ```bash
   # Create storage account
   az storage account create --name portalaimusic --resource-group myRG
   ```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## 📊 API Reference

### Generate Music
```http
POST /api/generate-music
Content-Type: application/json

{
  "prompt": "Upbeat electronic dance music",
  "duration": 30,
  "genre": "electronic",
  "mood": "energetic"
}
```

### Response
```json
{
  "status": "success",
  "track": {
    "id": "uuid",
    "title": "Energetic Electronic Track",
    "duration": 30,
    "url": "https://storage.com/track.mp3",
    "download_url": "https://storage.com/track.wav"
  }
}
```

See [API.md](docs/API.md) for complete API documentation.

## 🎯 Roadmap

- [ ] **User Authentication** - Azure AD B2C integration
- [ ] **Advanced AI Models** - Support for more music generation models
- [ ] **Real-time Editing** - In-browser audio editing tools
- [ ] **Collaboration Features** - Share and collaborate on tracks
- [ ] **Mobile App** - Native iOS and Android apps
- [ ] **API Marketplace** - Public API for developers
- [ ] **Advanced Analytics** - Usage analytics and insights

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Meta AI** for the MusicGen model
- **Hugging Face** for model hosting and transformers library
- **Azure** for cloud infrastructure
- **Unsplash** for beautiful stock photos
- **Lucide** for the icon set

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/portal-ai-music/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/portal-ai-music/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/portal-ai-music/discussions)
- **Email**: support@portalaimusic.com

## 🌟 Show Your Support

If you like this project, please give it a ⭐ on GitHub!

---

**Portal AI Music** - Create amazing music with the power of AI 🎵✨