# 🚀 Deploy Infosphere on Vercel + Render

## Quick Deployment Guide

### Prerequisites
✅ GitHub repository ready (https://github.com/Priyanshugoyal2301/Infosphere.git)
✅ Code already pushed to main branch

---

## Step 1️⃣: Deploy Backend on Render (5 minutes)

### Option A: One-Click Deploy (Easiest)
1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → Select **"Web Service"**
3. **Connect GitHub** → Select `Infosphere` repository
4. **Configure:**
   - **Name**: `infosphere-backend`
   - **Environment**: `Python 3`
   - **Branch**: `main`
   - **Build Command**: 
     ```bash
     pip install fastapi uvicorn[standard] sqlmodel python-multipart httpx pydantic python-dotenv pandas numpy beautifulsoup4 feedparser nltk scikit-learn requests python-jose passlib bcrypt
     ```
   - **Start Command**: 
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: **Free**

5. **Environment Variables** (Click "Advanced" → Add):
   ```
   PYTHON_VERSION = 3.10.0
   DATABASE_URL = sqlite:///./infosphere.db
   PYTHONUNBUFFERED = 1
   ```

6. **Click "Create Web Service"**
   - Render will automatically deploy
   - Wait 5-10 minutes for first deployment
   - **Copy your backend URL**: `https://infosphere-backend-xxxx.onrender.com`

### Option B: Using render.yaml (Auto-deploy on push)
Render will automatically detect `render.yaml` in your repo and deploy!

**Test Backend**: Visit `https://your-backend-url.onrender.com/docs` to see API documentation

---

## Step 2️⃣: Deploy Frontend on Vercel (3 minutes)

### Method 1: Vercel Dashboard (Recommended)

1. **Go to Vercel**: https://vercel.com/login
2. **Import Project** → **Import Git Repository**
3. **Select** `Infosphere` from GitHub
4. **Configure:**
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

5. **Environment Variables** (Important!):
   ```
   REACT_APP_API_URL = https://infosphere-backend-xxxx.onrender.com
   ```
   ⚠️ **Replace with YOUR actual Render backend URL from Step 1**

6. **Click "Deploy"**
   - Deployment takes 2-3 minutes
   - **Your live URL**: `https://infosphere-xxxx.vercel.app`

### Method 2: Vercel CLI (Alternative)

```powershell
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend
cd frontend

# Login to Vercel
vercel login

# Deploy (follow prompts)
vercel --prod

# Set environment variable
vercel env add REACT_APP_API_URL production
# Enter: https://your-render-backend-url.onrender.com
```

---

## Step 3️⃣: Update Backend CORS (Important!)

After deploying frontend, update your backend to allow frontend domain:

1. **Edit** `backend/main.py` locally
2. **Update CORS origins** with your Vercel URL:
   ```python
   origins = [
       "http://localhost:3000",
       "https://infosphere-xxxx.vercel.app",  # Add your Vercel URL
       "*"  # Remove this in production, specify exact domains
   ]
   ```

3. **Commit and push**:
   ```powershell
   git add backend/main.py
   git commit -m "Update CORS for production deployment"
   git push origin main
   ```

4. **Render auto-deploys** on git push (wait 2-3 minutes)

---

## Step 4️⃣: Verify Deployment ✅

### Test Backend
```powershell
# Check API health
curl https://your-backend-url.onrender.com/api/v1/news/channels/status
```

### Test Frontend
1. Open `https://your-frontend-url.vercel.app`
2. Navigate through features
3. Check browser console for any errors

---

## 🔄 Continuous Deployment (Auto-deploy on push)

### ✅ Already Configured!
- **Render**: Auto-deploys backend when you push to `main`
- **Vercel**: Auto-deploys frontend when you push to `main`

Just push changes to GitHub:
```powershell
git add .
git commit -m "Your changes"
git push origin main
```

---

## 📊 Monitoring & Logs

### Render Dashboard
- **Logs**: https://dashboard.render.com → Select service → "Logs" tab
- **Metrics**: CPU, Memory, Request count
- **Shell Access**: Click "Shell" for debugging

### Vercel Dashboard
- **Analytics**: https://vercel.com/dashboard → Select project → "Analytics"
- **Deployments**: View all deployments and rollback if needed
- **Logs**: Real-time function logs

---

## 💰 Pricing (Both Free!)

### Render Free Tier
- ✅ 750 hours/month (enough for 1 service 24/7)
- ✅ Automatic SSL
- ⚠️ Spins down after 15 min inactivity (cold starts ~30s)
- 💡 **Tip**: Upgrade to $7/mo for always-on service

### Vercel Free Tier
- ✅ 100GB bandwidth/month
- ✅ 100 deployments/day
- ✅ Automatic SSL
- ✅ Global CDN
- ✅ No cold starts

---

## 🐛 Troubleshooting

### Frontend Can't Connect to Backend
**Problem**: CORS errors in browser console

**Solution**:
1. Verify `REACT_APP_API_URL` in Vercel environment variables
2. Check backend CORS origins include your Vercel URL
3. Redeploy both services

### Backend Shows 503 Error
**Problem**: Render service sleeping (free tier)

**Solution**:
- First request takes 30-60 seconds to wake up
- Upgrade to paid plan for always-on service
- Or implement keep-alive ping every 10 minutes

### Build Fails on Render
**Problem**: Missing dependencies

**Solution**:
1. Check Render logs
2. Add missing packages to build command
3. Verify Python version is 3.10

### Frontend Build Fails on Vercel
**Problem**: Node modules or build errors

**Solution**:
1. Check Vercel deployment logs
2. Verify `frontend/package.json` is correct
3. Test build locally: `cd frontend && npm run build`

---

## 🎯 Custom Domain (Optional)

### Add Custom Domain to Vercel
1. **Vercel Dashboard** → Project → **Settings** → **Domains**
2. **Add domain**: `infosphere.yourdomain.com`
3. **Configure DNS** (in your domain registrar):
   ```
   Type: CNAME
   Name: infosphere
   Value: cname.vercel-dns.com
   ```

### Add Custom Domain to Render
1. **Render Dashboard** → Service → **Settings** → **Custom Domain**
2. **Add domain**: `api.yourdomain.com`
3. **Configure DNS**:
   ```
   Type: CNAME
   Name: api
   Value: your-service.onrender.com
   ```

---

## 📞 Support & Next Steps

### Your Deployed URLs
- **Frontend**: `https://infosphere-xxxx.vercel.app`
- **Backend**: `https://infosphere-backend-xxxx.onrender.com`
- **API Docs**: `https://infosphere-backend-xxxx.onrender.com/docs`

### Next Steps
1. ✅ Test all features thoroughly
2. ✅ Share links with competition judges
3. ✅ Monitor logs for errors
4. ✅ Set up analytics (Google Analytics, Mixpanel)
5. ✅ Add custom domain for professional look

---

## 🎉 Congratulations!

Your **Infosphere** application is now live on the internet!

**Share your project:**
- Frontend: `https://your-app.vercel.app`
- GitHub: `https://github.com/Priyanshugoyal2301/Infosphere`

Good luck with your national competition! 🏆
