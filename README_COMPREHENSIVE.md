# 🎵 Portal AI Music - Comprehensive AI Music Generation Platform

A next-generation AI music creation platform that integrates multiple AI models, real-time collaboration, and professional-grade audio controls.

## 🚀 Features

### 🎼 Advanced AI Music Generation
- **Multiple AI Models**: OpenAI MuseNet, Google Magenta, custom enhanced generator
- **Lyric-to-Music**: Transform lyrics into full musical compositions
- **Multi-Style Output**: Generate same content in different musical styles
- **Smart Arrangement**: AI-powered instrument arrangement and mixing

### 🎛️ Professional Audio Controls
- **Track Isolation**: Individual instrument stem control
- **Real-time Mixing**: Adjust volume, effects, and balance live
- **Advanced Export**: MP3, WAV, FLAC, MIDI with custom quality settings
- **Stem Separation**: Export individual instrument tracks

### 👥 Collaboration Features
- **Real-time Editing**: Live collaborative music creation
- **Role Management**: Owner, editor, and viewer permissions
- **Sharing**: Secure composition sharing with custom links
- **Version Control**: Track changes and collaboration history

### 🧠 AI Learning System
- **Style Transfer**: Transform compositions between genres
- **User Feedback**: Continuous improvement through user ratings
- **Personalization**: AI learns your musical preferences
- **Smart Suggestions**: Context-aware generation recommendations

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes, Prisma ORM
- **Database**: Neon PostgreSQL
- **Authentication**: Clerk
- **Storage**: Vercel Blob Storage
- **Deployment**: Vercel

### AI Integrations
- **OpenAI MuseNet**: Complex classical and jazz compositions
- **Google Magenta**: Style transfer and creative AI
- **Custom Enhanced Generator**: Multi-instrumental synthesis
- **Replicate**: Various open-source music models

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL database (Neon recommended)
- Clerk account for authentication

### Installation

1. **Clone and Install**
```bash
git clone <repository-url>
cd portal-ai-music
npm install
```

2. **Environment Setup**
```bash
cp .env.example .env.local
# Edit .env.local with your API keys
```

3. **Database Setup**
```bash
npx prisma generate
npx prisma db push
```

4. **Development Server**
```bash
npm run dev
```

## 🔧 Configuration

### Required Environment Variables

```env
# Database
DATABASE_URL="postgresql://username:password@host:5432/database"
DIRECT_URL="postgresql://username:password@host:5432/database"

# Authentication
CLERK_PUBLISHABLE_KEY="pk_test_..."
CLERK_SECRET_KEY="sk_test_..."

# AI APIs
OPENAI_API_KEY="sk-..."
REPLICATE_API_TOKEN="r8_..."
GOOGLE_CLOUD_API_KEY="..."

# Storage
BLOB_READ_WRITE_TOKEN="vercel_blob_..."

# Cache
UPSTASH_REDIS_REST_URL="https://..."
UPSTASH_REDIS_REST_TOKEN="..."
```

### Database Schema

The platform uses Prisma with PostgreSQL for data management:

- **Users**: Authentication, preferences, credits
- **Compositions**: Music tracks, metadata, collaboration
- **Collaborations**: Real-time editing permissions
- **Exports**: Download history and formats
- **Feedback**: User ratings and AI learning data

## 📊 API Reference

### Music Generation
```typescript
POST /api/generate-music
{
  "prompt": "Upbeat pop song for commercial",
  "lyrics": "Optional lyrics here...",
  "genre": "pop",
  "mood": "energetic",
  "duration": 30,
  "tempo": 120,
  "instruments": ["piano", "guitar", "drums"]
}
```

### Export
```typescript
POST /api/export
{
  "compositionId": "comp_123",
  "options": {
    "format": "mp3",
    "quality": "high",
    "includeStems": true,
    "includeMidi": false
  }
}
```

### Collaboration
```typescript
POST /api/collaborate
{
  "compositionId": "comp_123",
  "action": "invite",
  "email": "user@example.com",
  "role": "editor"
}
```

## 🎯 Usage Examples

### Basic Music Generation
```javascript
const composition = await fetch('/api/generate-music', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "Relaxing ambient music for meditation",
    genre: "ambient",
    mood: "calm",
    duration: 60,
    instruments: ["piano", "synthesizer", "violin"]
  })
})
```

### Real-time Collaboration
```javascript
// Join collaboration session
const session = new CollaborationSession(compositionId)
session.on('userJoined', (user) => console.log(`${user.name} joined`))
session.on('trackUpdated', (update) => applyUpdate(update))
```

### Style Transfer
```javascript
const transferred = await fetch('/api/style-transfer', {
  method: 'POST',
  body: JSON.stringify({
    compositionId: "comp_123",
    targetStyle: "jazz",
    intensity: 0.7
  })
})
```

## 🚀 Deployment

### Vercel Deployment

1. **Connect Repository**
```bash
vercel --prod
```

2. **Set Environment Variables**
- Configure all required environment variables in Vercel dashboard
- Set up Neon database connection
- Configure Clerk authentication

3. **Database Migration**
```bash
npx prisma db push
```

### Manual Deployment

1. **Build Application**
```bash
npm run build
```

2. **Start Production Server**
```bash
npm start
```

## 🔒 Security & Performance

### Security Features
- **Authentication**: Clerk-based secure authentication
- **Authorization**: Role-based access control
- **Rate Limiting**: API request rate limiting
- **Input Validation**: Comprehensive input sanitization
- **CORS**: Strict cross-origin policies

### Performance Optimizations
- **Caching**: Redis-based caching for frequent requests
- **CDN**: Global content delivery for audio files
- **Lazy Loading**: Progressive audio loading
- **Edge Functions**: Vercel edge computing
- **Database Optimization**: Connection pooling and indexing

## 📈 Monitoring & Analytics

- **Real-time Metrics**: Generation speed, success rates
- **User Analytics**: Engagement, feature usage
- **Error Tracking**: Comprehensive error logging
- **Performance Monitoring**: API response times

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/portal-ai-music/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/portal-ai-music/issues)
- **Discord**: [Community Server](https://discord.gg/your-server)
- **Email**: support@portal-ai-music.com

## 🙏 Acknowledgments

- **OpenAI** for MuseNet model access
- **Google** for Magenta research and tools
- **Meta** for MusicGen and open-source contributions
- **Vercel** for hosting and edge computing
- **Neon** for PostgreSQL database services
- **Clerk** for authentication infrastructure

---

**Portal AI Music** - Empowering creativity through AI 🎵✨
