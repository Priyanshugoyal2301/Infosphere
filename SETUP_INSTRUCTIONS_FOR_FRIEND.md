# Infosphere Setup Instructions

## 🚀 Quick Setup Guide for Your Device

This is a complete working setup of the Infosphere platform with AI-powered PDF Policy Summarization.

### Prerequisites

1. **Python 3.11+** (Download from: https://www.python.org/downloads/)
2. **Node.js 16+** and npm (Download from: https://nodejs.org/)
3. **Git** (Download from: https://git-scm.com/)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Priyanshugoyal2301/infosphere-unc.git
cd infosphere-unc
```

### Step 2: Backend Setup

```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows CMD:
.\venv\Scripts\activate.bat
# On Mac/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### Step 4: Environment Variables

The `.env` file is already included in this private repo with all necessary API keys:
- NewsAPI, GNews, NewsData API keys (for news features)
- CORS settings for localhost
- Database configuration

**⚠️ IMPORTANT:** This `.env` file contains API keys. Keep this repository private!

### Step 5: Initialize Database

```bash
# Make sure virtual environment is activated
python -c "from backend.database.database import init_db; init_db()"
```

### Step 6: Start the Application

You need **TWO separate terminal windows**:

#### Terminal 1 - Backend Server:
```bash
# Make sure you're in the project root directory
# Activate venv if not already active
.\venv\Scripts\Activate.ps1

# Start backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### Terminal 2 - Frontend Server:
```bash
cd frontend
npm start
```

Browser should automatically open at `http://localhost:3000`

### Step 7: Verify Everything Works

1. **Backend Health Check:** Open http://localhost:8000/health
   - Should return: `{"status":"healthy","message":"Infosphere API is running"}`

2. **Frontend:** Open http://localhost:3000
   - You should see the Infosphere landing page

3. **API Documentation:** http://localhost:8000/docs
   - Interactive API documentation (Swagger UI)

### Step 8: Test PDF Summarization

1. Navigate to **Policy Desk** → **Upload PDF Policy** tab
2. Upload a PDF file (max 10MB, policy documents work best)
3. Click **"Analyze with AI"**
4. Wait 30-180 seconds (first time is slower as it downloads the ML model ~1.6GB)
5. You should see:
   - Summary of the PDF
   - Key points extracted
   - Metadata (pages, word count, etc.)

---

## 📁 Project Structure

```
infosphere/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application entry
│   ├── services/        # Business logic
│   │   └── pdf_policy_service.py  # PDF AI summarization
│   └── api/v1/endpoints/
│       └── policy.py    # Policy API endpoints
├── frontend/            # React frontend
│   └── src/
│       └── components/
│           └── Policy/
│               └── PolicyDashboard.tsx
├── ml_model/            # ML models (BART for summarization)
├── .env                 # Environment variables (INCLUDED)
└── requirements.txt     # Python dependencies
```

---

## 🔧 Troubleshooting

### Backend won't start:
- **Port 8000 in use?** 
  ```bash
  # Windows: Kill process on port 8000
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```
- **Module not found errors?**
  ```bash
  pip install -r requirements.txt --force-reinstall
  ```

### Frontend won't start:
- **Port 3000 in use?**
  - Just use the port it suggests (usually 3001)
  - Update backend CORS in `.env`: `CORS_ORIGINS=http://localhost:3001,...`
- **npm errors?**
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

### PDF Summarization Issues:
- **First run is SLOW (~5-10 minutes)**: Model downloads automatically (~1.6GB)
- **"Failed to fetch" error**: Make sure backend is running on port 8000
- **Out of memory**: Use smaller PDF files (<50 pages) or upgrade RAM

### Model Download Location:
- Models download to: `~/.cache/huggingface/` (Linux/Mac) or `C:\Users\<username>\.cache\huggingface\` (Windows)
- First summarization downloads `facebook/bart-large-cnn` (~1.6GB)

---

## 🎯 Key Features

1. **AI-Powered PDF Policy Summarization** (NEW!)
   - Uses Facebook's BART-large-cnn model
   - Hierarchical summarization for long documents
   - Automatic key points extraction

2. **Live News Integration**
   - Real-time news from multiple sources
   - AI trust scoring with ATIE engine

3. **Citizen Issue Tracking**
   - Submit and track civic issues
   - Media integrity verification

4. **Policy Analysis**
   - Upload and analyze policy documents
   - AI-powered insights

---

## 📊 Technology Stack

### Backend:
- **FastAPI** - Modern Python web framework
- **Transformers** - Hugging Face ML library
- **PyTorch** - Deep learning framework
- **pdfplumber** - PDF text extraction
- **SQLite** - Database

### Frontend:
- **React** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling

### AI/ML:
- **facebook/bart-large-cnn** - Text summarization (1.6GB)
- CPU-optimized inference
- Automatic chunking for long documents

---

## 📝 API Endpoints

### PDF Summarization:
- **POST** `/api/v1/policy/summarize`
  - Upload PDF file
  - Returns: Summary, key points, metadata
  - Rate limited: 5 requests/minute

### Health Check:
- **GET** `/health` - Backend status
- **GET** `/api/v1/policy/health` - Policy service status

### Full API Docs:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

---

## ⚙️ Configuration

### `.env` File (Already Included):
```env
# News API Keys (Already configured)
NEWSAPI_KEY=b9332a9838474c4e9f42521e4b2bb197
GNEWS_API_KEY=fb291ff45240642d21bf86126a73e072
NEWSDATA_API_KEY=pub_6212126cd950424e9655636edc039ad9

# Database
DATABASE_URL=sqlite:///./infosphere.db

# CORS (Adjust if frontend runs on different port)
CORS_ORIGINS=http://localhost:3000,http://localhost:80,https://infosphere-five.vercel.app

# Cache Settings
NEWS_CACHE_DURATION=120

# Secret Key
SECRET_KEY=your-secret-key-change-in-production
```

---

## 🔐 Security Notes

- This is a **PRIVATE repository** - do not make it public (contains API keys!)
- API keys are for development only
- For production: Generate new SECRET_KEY and use environment-specific API keys
- Rate limiting is enabled (5 requests/minute for PDF summarization)

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed correctly
3. Make sure both backend and frontend terminals are running
4. Check terminal output for specific error messages

---

## 🎉 You're All Set!

Once both servers are running, navigate to http://localhost:3000 and start exploring!

The PDF summarization feature is in **Policy Desk → Upload PDF Policy** tab.

Happy coding! 🚀
