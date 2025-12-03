# 🚀 Infosphere Deployment Guide

## Table of Contents
- [Quick Deploy with Docker](#quick-deploy-with-docker)
- [Deploy on Render](#deploy-on-render)
- [Deploy on Vercel + Railway](#deploy-on-vercel--railway)
- [Deploy on AWS](#deploy-on-aws)
- [Environment Variables](#environment-variables)

---

## 🐳 Quick Deploy with Docker (Recommended)

### Prerequisites
- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- Git installed

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/Priyanshugoyal2301/Infosphere.git
cd Infosphere
```

2. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

3. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stop the application
```bash
docker-compose down
```

---

## 🌐 Deploy on Render (Free Tier Available)

### Backend Deployment on Render

1. **Create account** at [render.com](https://render.com)

2. **Create New Web Service**
   - Connect your GitHub repository
   - Select `Infosphere` repository
   - Configure:
     - **Name**: infosphere-backend
     - **Environment**: Python 3
     - **Build Command**: 
       ```bash
       pip install fastapi uvicorn sqlmodel python-multipart httpx pydantic python-dotenv pandas numpy beautifulsoup4 feedparser nltk scikit-learn
       ```
     - **Start Command**: 
       ```bash
       uvicorn backend.main:app --host 0.0.0.0 --port $PORT
       ```
     - **Instance Type**: Free

3. **Environment Variables** (Add in Render dashboard):
   ```
   PYTHON_VERSION=3.10.0
   DATABASE_URL=sqlite:///./infosphere.db
   ```

4. **Deploy** - Render will automatically deploy

5. **Note your backend URL**: `https://infosphere-backend.onrender.com`

### Frontend Deployment on Render

1. **Create New Static Site**
   - Connect same GitHub repository
   - Configure:
     - **Name**: infosphere-frontend
     - **Build Command**: 
       ```bash
       cd frontend && npm install && npm run build
       ```
     - **Publish Directory**: `frontend/build`

2. **Environment Variables**:
   ```
   REACT_APP_API_URL=https://infosphere-backend.onrender.com
   ```

3. **Deploy**

---

## ⚡ Deploy on Vercel + Railway

### Frontend on Vercel

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Deploy from frontend directory**
```bash
cd frontend
vercel --prod
```

3. **Configure**
   - Framework: Create React App
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Environment Variable: `REACT_APP_API_URL=<your-backend-url>`

### Backend on Railway

1. **Create account** at [railway.app](https://railway.app)

2. **New Project from GitHub**
   - Select `Infosphere` repository
   - Railway auto-detects Python
   - Add Start Command in Settings:
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```

3. **Add Environment Variables**:
   ```
   PYTHONUNBUFFERED=1
   DATABASE_URL=sqlite:///./infosphere.db
   ```

4. **Deploy** - Railway auto-deploys on push

---

## ☁️ Deploy on AWS (Production)

### Backend on AWS EC2

1. **Launch EC2 Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t2.micro (free tier) or t2.small
   - Security Group: Allow ports 22 (SSH), 8000 (API)

2. **SSH into instance**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv git -y
```

4. **Clone and setup**
```bash
git clone https://github.com/Priyanshugoyal2301/Infosphere.git
cd Infosphere
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlmodel python-multipart httpx pydantic python-dotenv pandas numpy beautifulsoup4 feedparser nltk scikit-learn
```

5. **Run with systemd** (create `/etc/systemd/system/infosphere.service`):
```ini
[Unit]
Description=Infosphere Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Infosphere
ExecStart=/home/ubuntu/Infosphere/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

6. **Enable and start**
```bash
sudo systemctl enable infosphere
sudo systemctl start infosphere
```

### Frontend on AWS S3 + CloudFront

1. **Build frontend**
```bash
cd frontend
npm install
npm run build
```

2. **Create S3 bucket** (e.g., `infosphere-frontend`)
   - Enable static website hosting
   - Upload `build/` contents

3. **Create CloudFront distribution**
   - Origin: S3 bucket
   - Enable HTTPS

4. **Update API URL** in frontend environment to point to EC2 backend

---

## 🔐 Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./infosphere.db
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
SECRET_KEY=your-secret-key-here
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
# or production URL
REACT_APP_API_URL=https://your-backend-domain.com
```

---

## 📊 Monitoring & Logs

### Docker Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Render Logs
- Available in Render dashboard under "Logs" tab

### Railway Logs
- Real-time logs in Railway project dashboard

### AWS CloudWatch
- Configure CloudWatch agent for EC2 logs
- Monitor API Gateway and Lambda metrics

---

## 🔄 CI/CD Setup (Optional)

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Infosphere

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

Add `RENDER_DEPLOY_HOOK` in GitHub Secrets (get from Render dashboard).

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### CORS Errors
Ensure backend `main.py` has correct CORS origins:
```python
origins = [
    "http://localhost:3000",
    "https://your-frontend-domain.com"
]
```

### Module Not Found
```bash
pip install -r requirements.txt
```

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Verify environment variables
3. Ensure ports are open
4. Contact: [your-email@example.com]

---

**🎉 Your Infosphere application is now deployed!**

Access your live application and share the link with users.
