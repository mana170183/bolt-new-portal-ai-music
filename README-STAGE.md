# Portal AI Music - Free Deployment Branch (Stage)

> **Branch Purpose**: This `stage` branch contains a complete free deployment solution for rapid prototyping and testing before moving to Azure production.

## 🎯 Overview

This branch provides a **$0/month** deployment solution using free tiers of modern cloud platforms, allowing you to:

- ✅ Validate your AI music generation concept
- ✅ Test with real users (up to 50-100 users)
- ✅ Gather feedback and iterate quickly
- ✅ Prepare for production Azure deployment

## 🏗️ Architecture

```
Frontend (Vercel) → Backend (Railway) → Database (Supabase) → AI (Hugging Face)
```

| Component | Platform | Free Tier | Monthly Cost |
|-----------|----------|-----------|--------------|
| Frontend | Vercel | 100GB bandwidth | $0 |
| Backend API | Railway | $5 credit | $0 |
| Database | Supabase | 500MB + Auth | $0 |
| AI Services | Hugging Face | Rate-limited | $0 |
| File Storage | Supabase Storage | 1GB | $0 |
| **Total** | | | **$0** |

## 🚀 Quick Start

### 1. One-Command Setup
```bash
# Setup local development environment
./setup-local-dev.sh

# Deploy to free platforms (after configuring accounts)
./deploy-free.sh

# Test deployment
./test-free-deployment.sh https://your-app.railway.app
```

### 2. Manual Setup
```bash
# 1. Install dependencies
npm install
cd backend-free && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.local.example .env.local
cp backend-free/.env.example backend-free/.env
# Edit both files with your API keys

# 3. Test locally
./start-local-dev.sh

# 4. Deploy
vercel --prod  # Frontend
cd backend-free && railway up  # Backend
```

## 📋 Platform Setup Checklist

### Supabase (Database & Storage)
- [ ] Create project at https://supabase.com
- [ ] Run SQL schema from deployment guide
- [ ] Create `music-files` storage bucket
- [ ] Get URL and anon key

### Railway (Backend API)
- [ ] Create account at https://railway.app
- [ ] Install CLI: `npm install -g @railway/cli`
- [ ] Connect GitHub repository
- [ ] Set environment variables

### Vercel (Frontend)
- [ ] Create account at https://vercel.com
- [ ] Install CLI: `npm install -g vercel`
- [ ] Connect GitHub repository
- [ ] Configure environment variables

### Hugging Face (AI Services)
- [ ] Create account at https://huggingface.co
- [ ] Generate API token with "Read" permissions
- [ ] No additional setup required

## 📖 Documentation

- **[Complete Deployment Guide](docs/FREE-DEPLOYMENT-GUIDE.md)** - Step-by-step instructions
- **[API Documentation](docs/API.md)** - Backend API reference
- **[Azure Migration Path](docs/DEPLOYMENT.md)** - Moving to production

## 🛠️ Development Workflow

### Local Development
```bash
# Start both frontend and backend
./start-local-dev.sh

# Backend only (http://localhost:5000)
cd backend-free && source venv/bin/activate && python app.py

# Frontend only (http://localhost:3000)
npm start
```

### Testing
```bash
# Local API test
curl http://localhost:5000/health

# Production deployment test
./test-free-deployment.sh https://your-app.railway.app

# Load testing
npm install -g artillery
artillery quick --count 10 --num 3 https://your-app.railway.app
```

## 📊 Monitoring & Limits

### Free Tier Limits
- **Railway**: $5 credit (~500 hours runtime)
- **Vercel**: 100GB bandwidth (~100K page views)
- **Supabase**: 500MB database, 50K MAU
- **Hugging Face**: Rate-limited (varies by model)

### Monitoring Dashboards
- Railway: https://railway.app/dashboard
- Vercel: https://vercel.com/dashboard
- Supabase: https://app.supabase.com/

### Expected Capacity
- **Users**: 50-100 concurrent users
- **Generations**: ~1,000 per month
- **Storage**: ~500MB audio files
- **Runtime**: 24/7 with Railway credit

## 🔄 Migration to Azure

When ready for production scale:

```bash
# Switch to Azure deployment branch
git checkout dev

# Follow Azure deployment guide
terraform init
terraform plan -var-file="environments/dev-optimized.tfvars"
terraform apply
```

Migration includes:
- Data export from Supabase to Azure SQL
- Container deployment to Azure Container Apps
- DNS update to Azure Front Door
- SSL certificate provisioning

## 🆘 Troubleshooting

### Common Issues

1. **Railway App Sleeping**
   - Solution: Use UptimeRobot (free) to ping every 5 minutes

2. **Hugging Face Rate Limits**
   - Solution: Implement queue system with exponential backoff

3. **Storage Quota Exceeded**
   - Solution: Auto-cleanup old files or upgrade Supabase

### Debug Commands
```bash
# Check Railway logs
railway logs

# Check API health
curl https://your-app.railway.app/health

# Validate environment
cat backend-free/.env | grep -v "^#"
```

## 📈 Success Metrics

Track these KPIs:
- Response time: < 3s average
- Success rate: > 95%
- User retention: Weekly active users
- Cost efficiency: Stay within free tiers

## 🎯 Branch Strategy

- **`main`**: Production-ready code
- **`dev`**: Azure deployment & enterprise features  ← *Azure/Terraform*
- **`stage`**: Free deployment & prototyping ← *Current branch*
- **`production`**: Live production releases

## 🤝 Contributing

1. Make changes in `stage` branch for free deployment features
2. Test with `./test-free-deployment.sh`
3. Cherry-pick features to `dev` for Azure compatibility
4. Keep deployment strategies separate

---

**Ready to deploy for free? Start with `./setup-local-dev.sh`** 🚀
