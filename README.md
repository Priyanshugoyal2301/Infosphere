# 🌐 Infosphere - AI-Powered Civic Intelligence Platform

## 🎯 What is Infosphere?

**Infosphere** is an advanced civic intelligence platform that fights misinformation, verifies news authenticity, and empowers citizens to report civic issues. We combine **AI-powered news verification**, **real-time fact-checking**, and **automated issue tracking** to create a more informed and engaged community.

### Why Infosphere?

In an era of information overload and fake news, Infosphere helps you:
- ✅ **Verify news authenticity** using official government sources (PIB, RBI, WHO)
- 🚩 **Identify misleading content** automatically flagged by our AI system
- 📰 **Access real-time verified news** from trusted sources
- 📝 **Report civic issues** with AI-powered categorization and tracking
- 📊 **Analyze policy documents** with AI-generated summaries

---

## ✨ Key Features

### 🔍 **Advanced News Verification System** (UNIQUE)
Our standout feature that validates news against official sources:
- **Official Source Validation** - Automatically cross-references government press releases (PIB), RBI announcements, WHO statements
- **Fact-Checker Integration** - Validates against AltNews, BoomLive, FactChecker.in
- **Image Authenticity Check** - Detects stock photos and reused images
- **Source Credibility Scoring** - Rates news sources on trustworthiness (90-95% for verified news)
- **Temporal Consistency** - Flags future-dated or suspiciously old articles
- **Multi-layered Verification** - 5 parallel checks with weighted scoring

### 🚩 **Flagged News Dashboard**
Real-time monitoring of questionable content:
- Articles scoring below 65% verification automatically flagged
- Detailed flag reasons with verification breakdown
- Statistics on common misinformation patterns
- Color-coded trust scores for quick assessment

### 📡 **Live News Feed**
Curated news from trusted sources:
- Real-time updates from NewsAPI, GNews, NewsData.io
- Auto-categorized by topic (Politics, Health, Technology, etc.)
- Every article verified with 90-95% confidence scores
- Clean, newspaper-style interface

### 📝 **Citizen Issue Reporting**
Smart civic engagement platform:
- AI-powered issue categorization (Infrastructure, Safety, Environment, etc.)
- Automated urgency detection (Low, Medium, High)
- Real-time tracking with estimated resolution times
- Photo/video evidence upload support
- Offline submission capability

### 📋 **AI Policy Desk**
Simplify complex policy documents:
- **PDF Summarization** using BART-large-cnn model
- Extract key points automatically
- Supports documents up to 10MB
- 30-180 second processing time
- Downloadable summaries

### 🔍 **Fact Check & Media Verification**
Advanced deepfake and media integrity checking:
- Real-time deepfake detection
- Face authentication analysis
- Trust scoring system (0-100)
- Batch verification support

### 📊 **Analytics Dashboard**
Data-driven insights on civic engagement:
- Issue resolution trends
- Category-wise statistics
- Public sentiment analysis
- Real-time metrics

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** - High-performance async Python framework
- **SQLite/PostgreSQL** - Flexible database options
- **SQLModel** - Modern ORM with Pydantic integration
- **BeautifulSoup4** - Web scraping for source verification
- **httpx** - Async HTTP client for API calls

### AI/ML Models
- **BART-large-cnn** - Document summarization (Facebook AI)
- **Transformers** - Pre-trained language models (Hugging Face)
- **PyTorch** - Deep learning framework
- **scikit-learn** - ML utilities and preprocessing
- **NLTK** - Natural language processing

### News & Verification APIs
- **NewsAPI** - Global news aggregation
- **GNews API** - Real-time news updates
- **NewsData.io** - Multi-source news feed
- **PIB India** - Official government press releases
- **RBI** - Reserve Bank of India announcements
- **WHO** - World Health Organization statements

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** - Modern utility-first styling
- **Recharts** - Beautiful data visualizations
- **React Router** - Client-side routing
- **Axios** - HTTP client

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 16+**
- **npm or yarn**
- **Git**

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/Priyanshugoyal2301/Infosphere.git
cd infosphere
```

**2. Backend Setup:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**3. Frontend Setup:**
```bash
cd frontend
npm install
```

**4. Environment Configuration:**

Create `.env` file in root directory:
```env
# News API Keys (Get free keys from respective websites)
NEWSAPI_KEY=your_newsapi_key
GNEWS_API_KEY=your_gnews_key
NEWSDATA_API_KEY=your_newsdata_key

# Google OAuth (Optional - for admin login)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret

# Database
DATABASE_URL=sqlite:///./infosphere.db

# Cache Settings
NEWS_CACHE_DURATION=120
```

Create `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

**5. Run the Application:**

**Backend** (Terminal 1):
```bash
# From root directory
python -m uvicorn backend.main:app --reload --port 8000
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm start
```

**6. Access the Application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📱 Usage Guide

### For Citizens

**1. View Verified News**
- Navigate to **Live News** or **Newsroom**
- All articles show verification scores (92-97%)
- Click any article to read from original source

**2. Check Flagged News**
- Visit **Flagged News** section
- See articles that failed verification
- Understand why content was flagged

**3. Report Civic Issues**
- Click **Submit Story**
- Fill in issue details (title, description, location)
- Upload photos/videos (optional)
- AI categorizes and assigns urgency
- Track resolution status

**4. Verify Media**
- Go to **Fact Check**
- Upload image/video or paste URL
- Get trust score and authenticity report

**5. Analyze Policies**
- Visit **Policy Desk**
- Upload PDF policy document (max 10MB)
- Click "Analyze with AI"
- Get summary and key points in 30-180 seconds

### For Administrators

**1. View Reports**
- Access **View Reports** dashboard
- See all submitted civic issues
- Filter by category, urgency, status

**2. Monitor Analytics**
- Check **Analytics** for trends
- Review resolution metrics
- Track public engagement

---

## 🌟 What Makes Infosphere Unique?

### 🏆 **Official Source Validation** (Our Competitive Advantage)

Unlike other fact-checking platforms that only use NLP/LLM analysis, Infosphere:

✅ **Scrapes and validates against official government sources**
- Press Information Bureau (PIB) for government announcements
- Reserve Bank of India (RBI) for financial news
- World Health Organization (WHO) for health updates
- Can be extended to court databases, police records, scientific journals

✅ **Real-time cross-referencing**
- Verifies quotes against official statements
- Validates statistics against government data
- Checks policy claims against actual releases

✅ **Multi-layered verification**
- Official sources (35% weight)
- Fact-checkers (25% weight)
- Source credibility (15% weight)
- Image authenticity (15% weight)
- Temporal consistency (10% weight)

**Example:**
```
Article: "PM announces ₹1000 crore scheme"
→ Infosphere scrapes PIB.gov.in
→ Finds official press release
→ Verifies amount, date, details
→ Score: 95% ✅

Article: "Minister said XYZ" (from unknown blog)
→ No PIB release found
→ Source not credible
→ Image is stock photo
→ Score: 38% 🚩 FLAGGED
```

---

## 📊 API Endpoints

### News & Verification
```
GET  /api/v1/news/live          - Fetch verified live news
GET  /api/v1/verification/flagged-news  - Get flagged articles
POST /api/v1/verification/verify-article - Verify single article
POST /api/v1/verification/batch-verify   - Batch verification
GET  /api/v1/verification/flagged-stats  - Get statistics
```

### Issue Reporting
```
POST /api/v1/issues/report      - Submit new issue
GET  /api/v1/issues/            - Get all issues
GET  /api/v1/issues/{id}        - Get specific issue
```

### Policy Analysis
```
POST /api/v1/policy/summarize   - Summarize PDF policy
POST /api/v1/policy/            - Analyze policy text
```

### Media Verification
```
POST /api/v1/media/verify       - Verify media authenticity
GET  /api/v1/media/verify/{id}  - Get verification result
```

### Authentication
```
POST /api/v1/auth/login         - User login
POST /api/v1/auth/register      - User registration
GET  /api/v1/auth/profile       - Get user profile
```

---

## 🔧 Configuration

### Backend Configuration

**Database:**
- Default: SQLite (`infosphere.db`)
- Production: PostgreSQL (update `DATABASE_URL`)

**News Cache:**
- Duration: 120 minutes (configurable via `NEWS_CACHE_DURATION`)
- Cache file: `news_cache_v2.json`

**Rate Limiting:**
- Optional (slowapi)
- PDF summarization: 5 requests/minute
- Gracefully disabled if slowapi not installed

### Frontend Configuration

**Environment Variables:**
- `REACT_APP_API_URL` - Backend API URL
- `REACT_APP_GOOGLE_CLIENT_ID` - Google OAuth (optional)

**Build for Production:**
```bash
cd frontend
npm run build
```

---

## 🚢 Deployment

### Render.com (Recommended)

**Backend:**
1. Connect GitHub repository
2. Select `backend` as root directory
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (API keys, DATABASE_URL)

**Frontend:**
1. Deploy to Vercel/Netlify
2. Build command: `npm run build`
3. Publish directory: `build`
4. Add environment variables

### Docker (Alternative)
```bash
# Backend
docker build -f Dockerfile.backend -t infosphere-backend .
docker run -p 8000:8000 infosphere-backend

# Frontend
docker build -f Dockerfile.frontend -t infosphere-frontend .
docker run -p 3000:3000 infosphere-frontend
```

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create feature branch:** `git checkout -b feature/amazing-feature`
3. **Commit changes:** `git commit -m 'Add amazing feature'`
4. **Push to branch:** `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend
- Write meaningful commit messages
- Add comments for complex logic
- Test before submitting PR

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Priyanshu Goyal** - Full Stack Developer & AI Enthusiast
- GitHub: [@Priyanshugoyal2301](https://github.com/Priyanshugoyal2301)

---

## 🙏 Acknowledgments

- **Hugging Face** - Transformers library and BART model
- **NewsAPI, GNews, NewsData** - News aggregation services
- **PIB India, RBI, WHO** - Official data sources
- **FastAPI** - Excellent Python framework
- **React Team** - Frontend library

---

## 📞 Support & Feedback

We'd love to hear from you!

**Have feedback on:**
- ✅ Feature usefulness and relevance
- ✅ User experience and interface
- ✅ Verification accuracy
- ✅ Performance and speed
- ✅ New feature suggestions

**Contact:**
- Open an issue on GitHub
- Create a discussion thread
- Email: priyanshugoyal2301@gmail.com

---

## 🗺️ Roadmap

**Upcoming Features:**
- [ ] Mobile app (React Native)
- [ ] Browser extension for real-time fact-checking
- [ ] WhatsApp bot for news verification
- [ ] Blockchain-based verification certificates
- [ ] Multi-language support (Hindi, regional languages)
- [ ] Voice-based issue reporting
- [ ] AI-powered news summary push notifications
- [ ] Court judgment database integration
- [ ] Police FIR verification system

---

**Built with ❤️ for a more informed society**
