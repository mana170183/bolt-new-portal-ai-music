# Portal AI Music - webappdev1701 Deployment Guide

## 🎯 Quick Setup for webappdev1701

**GitHub Account**: webappdev1701  
**Email**: restrovision@gmail.com  
**Repository**: https://github.com/webappdev1701/bolt-new-portal-ai-music  
**Branch**: stage (free deployment)  

## Step 1: Repository Setup

### Option A: Fork Repository (Easiest)
1. Login to GitHub as `webappdev1701`
2. Go to: https://github.com/mana170183/bolt-new-portal-ai-music
3. Click "Fork" → This creates your copy automatically
4. All branches will be copied to your account

### Option B: Transfer All Branches (Manual)
1. Login to GitHub as `webappdev1701`
2. Create new repository: `bolt-new-portal-ai-music`
3. Make it **Public** (required for Vercel free tier)
4. Run the transfer script:
   ```bash
   ./transfer-repository.sh
   ```

## Step 2: Platform Account Setup

### 2.1 Vercel Setup (Frontend)
- ✅ **Already created**: Account with restrovision@gmail.com
- Next: Connect GitHub repository

### 2.2 Railway Setup (Backend)
1. Go to: https://railway.app
2. Sign up with GitHub account (webappdev1701)
3. This will use: restrovision@gmail.com

### 2.3 Supabase Setup (Database)
1. Go to: https://supabase.com
2. Sign up with: restrovision@gmail.com
3. Create new project: "portal-ai-music"

### 2.4 Hugging Face Setup (AI)
1. Go to: https://huggingface.co
2. Sign up with: restrovision@gmail.com
3. Go to Settings → Access Tokens
4. Create new token with "Read" permissions

## Step 3: Deploy Backend to Railway

```bash
# Switch to your repository
cd portal-ai-music
git checkout stage

# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
# This will open browser - login with webappdev1701 GitHub account

# Navigate to backend directory
cd backend-free

# Initialize Railway project
railway init
# Choose: "Deploy from GitHub repo"
# Select: webappdev1701/bolt-new-portal-ai-music
# Directory: backend-free

# Set environment variables
railway variables set SUPABASE_URL=https://your-project-id.supabase.co
railway variables set SUPABASE_ANON_KEY=your-supabase-anon-key
railway variables set HUGGINGFACE_API_KEY=your-huggingface-token

# Deploy
railway up
```

## Step 4: Setup Supabase Database

1. **Create Project**:
   - Name: portal-ai-music
   - Region: Choose closest to your users
   - Database password: Save this securely

2. **Run SQL Schema**:
   ```sql
   -- In Supabase SQL Editor, run:
   CREATE TABLE users (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     email TEXT UNIQUE NOT NULL,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   CREATE TABLE music_generations (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     user_id UUID REFERENCES users(id),
     prompt TEXT NOT NULL,
     style TEXT,
     duration INTEGER,
     file_url TEXT,
     status TEXT DEFAULT 'pending',
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Enable Row Level Security
   ALTER TABLE users ENABLE ROW LEVEL SECURITY;
   ALTER TABLE music_generations ENABLE ROW LEVEL SECURITY;

   -- Create policies
   CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
   CREATE POLICY "Users can insert own data" ON users FOR INSERT WITH CHECK (auth.uid() = id);
   CREATE POLICY "Users can view own generations" ON music_generations FOR SELECT USING (auth.uid() = user_id);
   CREATE POLICY "Users can insert own generations" ON music_generations FOR INSERT WITH CHECK (auth.uid() = user_id);
   ```

3. **Create Storage Bucket**:
   - Go to Storage in Supabase dashboard
   - Create bucket: "music-files"
   - Set as public bucket

4. **Get API Keys**:
   - Go to Settings → API
   - Copy: Project URL and anon/public key

## Step 5: Deploy Frontend to Vercel

```bash
# Go back to root directory
cd ..

# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login
# Enter: restrovision@gmail.com
# Follow email verification

# Setup environment variables
cp .env.local.example .env.local
# Edit .env.local with your API keys:
# REACT_APP_API_URL=https://your-railway-app.railway.app
# REACT_APP_SUPABASE_URL=https://your-project-id.supabase.co
# REACT_APP_SUPABASE_ANON_KEY=your-supabase-anon-key

# Deploy to Vercel
vercel --prod

# Configure environment variables in Vercel dashboard
vercel env add REACT_APP_API_URL
vercel env add REACT_APP_SUPABASE_URL
vercel env add REACT_APP_SUPABASE_ANON_KEY
```

## Step 6: Environment Configuration

### Backend Environment (Railway)
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
HUGGINGFACE_API_KEY=hf_your-token-here
PORT=5000
FLASK_ENV=production
```

### Frontend Environment (Vercel)
```env
REACT_APP_API_URL=https://your-app-name.railway.app
REACT_APP_SUPABASE_URL=https://your-project-id.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Step 7: Test Deployment

```bash
# Test your deployment
./test-free-deployment.sh https://your-app-name.railway.app https://your-app-name.vercel.app
```

## Expected URLs

After deployment, you'll have:

- **Frontend**: `https://your-app-name.vercel.app`
- **Backend API**: `https://your-app-name.railway.app`
- **Database**: Supabase dashboard
- **Repository**: `https://github.com/webappdev1701/bolt-new-portal-ai-music`

## Troubleshooting

### Common Issues:

1. **Repository Access**: Make sure repository is public for Vercel free tier
2. **Environment Variables**: Double-check all API keys are correct
3. **CORS Issues**: Backend should allow requests from your Vercel domain
4. **Railway Sleeping**: Use UptimeRobot to ping every 5 minutes

### Debug Commands:
```bash
# Check Railway logs
railway logs

# Check Vercel deployment
vercel logs

# Test API health
curl https://your-app-name.railway.app/health
```

## Cost Summary

- **Railway**: $0 (Free $5 credit)
- **Vercel**: $0 (Free tier)
- **Supabase**: $0 (Free 500MB)
- **Hugging Face**: $0 (Free inference)
- **Total**: $0/month

## Next Steps

1. **Monitor Usage**: Check dashboards for resource consumption
2. **Add Custom Domain**: Configure your own domain in Vercel
3. **Setup Analytics**: Add Google Analytics or similar
4. **User Testing**: Share with friends for feedback
5. **Scale to Azure**: When ready, switch to `dev` branch

Ready to deploy? Start with the repository setup! 🚀
