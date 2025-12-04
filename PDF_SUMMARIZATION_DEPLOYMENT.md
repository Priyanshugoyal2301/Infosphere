# PDF Policy Summarization - Deployment Guide

## Overview
The Infosphere platform now includes AI-powered PDF policy summarization using the BART-large-cnn model. This feature allows users to upload PDF policy documents and receive:

- **AI-generated summaries** using hierarchical chunking
- **Key points extraction** with top 5 important sentences
- **Document metadata** (pages, word count, etc.)
- **Rate limiting** to prevent abuse (5 requests/minute)

## Architecture

### Backend Components
1. **PDF Processing Service** (`backend/services/pdf_policy_service.py`)
   - Text extraction with pdfplumber and PyPDF2
   - BART-large-cnn model for summarization
   - Chunking for long documents (900 tokens/chunk)
   - Hierarchical summarization (chunk → combine → final)
   - Key sentence extraction

2. **API Endpoint** (`backend/api/v1/endpoints/policy.py`)
   - POST `/api/v1/policy/summarize` - Quick PDF summarization
   - Rate limiting: 5 requests/minute per IP
   - File validation: PDF only, max 10MB
   - Error handling and detailed responses

3. **Main Application** (`backend/main.py`)
   - SlowAPI integration for rate limiting
   - CORS configuration
   - Exception handlers

### Frontend Components
1. **PolicyDashboard** (`frontend/src/components/Policy/PolicyDashboard.tsx`)
   - File upload UI
   - Loading states and progress indicators
   - Summary and key points display
   - Error handling

## Model Information

### facebook/bart-large-cnn
- **Size**: 1.6GB download
- **Parameters**: 406M
- **Input Limit**: 1024 tokens
- **Performance**: 30-60s for 10-page PDF on CPU
- **Quality**: High-quality abstractive summaries
- **Optimization**: CPU-only inference (device=-1)

### Processing Strategy
1. **Short Documents** (<900 tokens): Direct summarization
2. **Long Documents** (>900 tokens):
   - Split into 900-token chunks
   - Summarize each chunk independently
   - Combine chunk summaries
   - Generate final summary from combined text
3. **Fallback**: Extractive summarization if BART fails

## Deployment Requirements

### Minimum System Requirements
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 2.5GB for model + code
- **CPU**: Any modern CPU (GPU optional but not required)
- **Python**: 3.8+
- **Node.js**: 16+

### Environment Variables
```bash
# Backend (.env)
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
TRANSFORMERS_CACHE=/tmp/transformers_cache  # For deployment
MODEL_CACHE_DIR=/app/models  # Optional custom cache
```

### Python Dependencies
```txt
# Core dependencies
fastapi>=0.104.0
uvicorn>=0.24.0
pdfplumber>=0.9.0
PyPDF2>=3.0.0

# ML dependencies
transformers>=4.35.0
torch>=2.0.0
sentencepiece>=0.1.99
tokenizers>=0.14.0

# Rate limiting
slowapi>=0.1.9
redis>=5.0.0  # Optional for distributed rate limiting
```

## Deployment Options

### Option 1: Render.com (Recommended)

#### render.yaml
```yaml
services:
  # Backend
  - type: web
    name: infosphere-backend
    env: python
    region: oregon
    plan: starter  # $7/month, 512MB RAM
    buildCommand: |
      pip install -r requirements.txt
      python -c "from transformers import BartTokenizer, BartForConditionalGeneration; BartTokenizer.from_pretrained('facebook/bart-large-cnn'); BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')"
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: TRANSFORMERS_CACHE
        value: /opt/render/project/.cache
      - key: CORS_ORIGINS
        fromService:
          type: web
          name: infosphere-frontend
          envVarKey: RENDER_EXTERNAL_URL
    
  # Frontend
  - type: web
    name: infosphere-frontend
    env: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/build
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

**Deployment Steps:**
1. Push code to GitHub
2. Connect Render to your repository
3. Create Web Service from `render.yaml`
4. Wait for build (10-15 minutes for first build with model download)
5. Access via provided URL

**Cost:** $7/month (Starter plan)

### Option 2: Fly.io

#### fly.toml
```toml
app = "infosphere"
primary_region = "ord"

[build]
  dockerfile = "Dockerfile.backend"

[env]
  PORT = "8080"
  TRANSFORMERS_CACHE = "/data/transformers_cache"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  
[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 1024
```

#### Dockerfile.backend (Update)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download BART model
RUN python -c "from transformers import BartTokenizer, BartForConditionalGeneration; \
    print('Downloading BART model...'); \
    BartTokenizer.from_pretrained('facebook/bart-large-cnn'); \
    BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn'); \
    print('Model downloaded successfully')"

# Copy application
COPY backend/ /app/backend/
COPY .env* /app/

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Start application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Deployment Steps:**
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Deploy
flyctl deploy

# Check logs
flyctl logs
```

**Cost:** Free tier (256MB RAM) or $1.94/month (1GB RAM)

### Option 3: Docker Compose (Local/VPS)

Use existing `docker-compose.yml`:

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

## Testing

### Local Testing

1. **Start Backend:**
```bash
cd c:\project\infosphere
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python backend/main.py
```

2. **Start Frontend:**
```bash
cd frontend
npm install
npm start
```

3. **Run Tests:**
```bash
python test_pdf_summarization.py
```

### Manual Testing

1. Navigate to http://localhost:3000
2. Login as admin or user
3. Go to Policy Desk
4. Click "Upload PDF Policy" tab
5. Select a PDF file (max 10MB)
6. Click "Analyze with AI"
7. Wait for summarization (30-180s depending on size)
8. Review summary and key points

### API Testing

```bash
# Using curl
curl -X POST http://localhost:8001/api/v1/policy/summarize \
  -F "file=@sample_policy.pdf"

# Using Python
import requests

with open('sample_policy.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/v1/policy/summarize',
        files={'file': f}
    )
    print(response.json())
```

## Performance Optimization

### 1. Model Caching
The model is cached after first load. Subsequent requests are faster.

### 2. Rate Limiting
Currently 5 requests/minute per IP. Adjust in `policy.py`:
```python
@limiter.limit("10/minute")  # Increase to 10/min
```

### 3. Background Processing (Optional)
For production, consider using Celery for async processing:

```python
# Install: pip install celery redis

# tasks.py
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def summarize_pdf_async(file_path):
    result = pdf_policy_analyzer.analyze_policy_pdf(file_path)
    return result

# In endpoint:
@router.post("/summarize-async")
async def summarize_pdf_async(file: UploadFile):
    # Save file
    task = summarize_pdf_async.delay(file_path)
    return {"task_id": task.id}
```

### 4. Redis Caching (Optional)
Cache summaries for repeated documents:

```python
import hashlib
import redis

redis_client = redis.Redis(host='localhost', port=6379)

def get_cached_summary(pdf_hash):
    return redis_client.get(f"summary:{pdf_hash}")

def cache_summary(pdf_hash, summary):
    redis_client.setex(f"summary:{pdf_hash}", 3600, summary)  # 1 hour TTL
```

## Monitoring

### Health Checks
- **Backend**: http://localhost:8001/health
- **Model Status**: Check logs for "BART model initialized"

### Logs
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Metrics to Monitor
- Request latency (target: <60s for 10-page PDF)
- Error rate (target: <5%)
- Model memory usage (expect 1.5-2GB)
- Rate limit hits

## Troubleshooting

### Issue: Model download timeout
**Solution:** Pre-download model in build step or increase timeout

### Issue: Out of memory
**Solution:** 
- Use smaller model: `sshleifer/distilbart-cnn-12-6`
- Increase server RAM
- Reduce chunk size in pdf_policy_service.py

### Issue: Slow summarization
**Solution:**
- Check CPU resources
- Reduce max_length parameter
- Use extractive fallback for speed

### Issue: Rate limit errors
**Solution:** Increase rate limit or implement Redis-based distributed limiting

## Security Considerations

1. **File Upload Validation**
   - Only PDF files accepted
   - 10MB size limit
   - Content type checking

2. **Rate Limiting**
   - 5 requests/minute per IP
   - Prevents abuse

3. **CORS Configuration**
   - Whitelist specific origins
   - No credentials with wildcard

4. **Model Safety**
   - Use official Hugging Face models
   - Pin specific versions
   - Regular security updates

## Future Enhancements

1. **Multi-language Support**
   - Use mBART for multilingual policies
   - Language detection

2. **Enhanced Analysis**
   - Policy timeline extraction
   - Stakeholder identification
   - Sentiment analysis

3. **Comparison Features**
   - Compare multiple policies
   - Track policy changes over time

4. **Export Options**
   - Download summary as PDF
   - Email summaries
   - API webhooks

## Support

For issues or questions:
- GitHub: https://github.com/Priyanshugoyal2301/Infosphere
- Check logs: `backend/logs/` (if configured)
- Run test suite: `python test_pdf_summarization.py`

## License

This implementation uses:
- **BART**: Apache 2.0 License (Facebook AI)
- **Transformers**: Apache 2.0 License (Hugging Face)
- **FastAPI**: MIT License
