# Infosphere ML Pipeline Documentation

## Overview

The Infosphere ML Pipeline is a complete machine learning system for automated news classification. It categorizes user-submitted news into four main categories: **Crime**, **Accident**, **Event**, and **Weather**.

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │   ML Pipeline   │
│   (React)       │───▶│   (FastAPI)      │───▶│   (Training)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Classification  │    │   Database      │
                       │   Analyzer       │    │   Connector     │
                       └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Trained Model   │    │  SQLite DB      │
                       │  (.pkl files)    │    │  (User Data)    │
                       └──────────────────┘    └─────────────────┘
```

## Key Components

### 1. Database Connector (`backend/db_connector.py`)
- **Purpose**: Manages user submission data storage and retrieval
- **Features**:
  - SQLite database integration
  - Sample data population
  - CRUD operations for submissions
  - Label distribution analysis
- **Usage**:
  ```python
  from backend.db_connector import fetch_user_data
  df = fetch_user_data()  # Returns pandas DataFrame
  ```

### 2. ML Training Pipeline (`ml_model/train_from_website.py`)
- **Purpose**: Trains the news classification model
- **Features**:
  - Text preprocessing with NLTK
  - TF-IDF vectorization (1000 features, 1-2 ngrams)
  - Logistic Regression classification
  - Model persistence (pickle format)
  - Performance evaluation
- **Usage**:
  ```bash
  python ml_model/train_from_website.py
  ```

### 3. Classification Analyzer (`backend/analyze_input.py`)
- **Purpose**: Provides real-time news classification API
- **Features**:
  - Model loading and caching
  - Single and batch prediction
  - Confidence scoring
  - Error handling
- **Usage**:
  ```python
  from backend.analyze_input import analyze_news_input
  result = analyze_news_input("Fire at shopping mall")
  # Returns: {'category': 'Accident', 'confidence': 0.85, ...}
  ```

## Installation & Setup

### Prerequisites
```bash
pip install nltk scikit-learn pandas numpy sqlite3
```

### Quick Start
1. **Initialize Database & Train Model**:
   ```bash
   cd infosphere
   python ml_model/train_from_website.py
   ```

2. **Test Classification**:
   ```bash
   python backend/analyze_input.py
   ```

3. **Verify Database**:
   ```bash
   python backend/db_connector.py
   ```

## Model Performance

### Current Statistics
- **Model Type**: Logistic Regression + TF-IDF
- **Categories**: Crime, Accident, Event, Weather  
- **Feature Count**: 1000 TF-IDF features
- **Training Data**: 20 labeled submissions (5 per category)
- **Accuracy**: 50% (limited by small dataset)

### Performance Metrics
```
              precision    recall  f1-score   support
    Accident       0.33      1.00      0.50         1
       Crime       1.00      1.00      1.00         1
       Event       0.00      0.00      0.00         1
     Weather       0.00      0.00      0.00         1
```

*Note: Performance will improve significantly with more training data*

## API Integration

### Backend Integration Example
```python
# In your FastAPI endpoint
from backend.analyze_input import analyze_news_input

@app.post("/classify-news")
async def classify_news(text: str):
    result = analyze_news_input(text)
    return {
        "category": result['category'],
        "confidence": result['confidence'],
        "timestamp": result['timestamp']
    }
```

### Frontend Integration Example
```javascript
// In your React component
const classifyNews = async (newsText) => {
  const response = await fetch('/api/classify-news', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: newsText })
  });
  
  const result = await response.json();
  console.log(`Category: ${result.category}, Confidence: ${result.confidence}`);
};
```

## File Structure

```
infosphere/
├── backend/
│   ├── analyze_input.py      # 🎯 Classification API
│   └── db_connector.py       # 🗄️ Database operations
├── ml_model/
│   ├── train_from_website.py # 🚀 Training pipeline
│   ├── news_classifier_model.pkl    # 📦 Trained model
│   ├── tfidf_vectorizer.pkl         # 📦 TF-IDF vectorizer
│   └── model_metadata.pkl           # 📦 Model metadata
├── infosphere.db             # 🗃️ SQLite database
└── requirements.txt          # 📋 Dependencies
```

## Usage Examples

### 1. Train New Model
```bash
# Full training pipeline
python ml_model/train_from_website.py

# Output:
# ✅ Fetched 20 labeled submissions from database  
# 📊 Training set size: 16, Testing set size: 4
# ✅ Test Accuracy: 0.500
# 💾 Model saved successfully
```

### 2. Classify Single News Item
```python
from backend.analyze_input import analyze_news_input

# Example classifications
result1 = analyze_news_input("Fire broke out in shopping mall")
# {'category': 'Accident', 'confidence': 0.309}

result2 = analyze_news_input("Free health checkup camp tomorrow") 
# {'category': 'Event', 'confidence': 0.358}

result3 = analyze_news_input("Heavy rainfall expected")
# {'category': 'Weather', 'confidence': 0.278}

result4 = analyze_news_input("Theft reported near metro")
# {'category': 'Crime', 'confidence': 0.402}
```

### 3. Add New Training Data
```python
from backend.db_connector import NewsDataConnector

connector = NewsDataConnector()
connector.add_submission(
    text="Earthquake tremors felt across city", 
    user_id="user123",
    location="City Center",
    label="Accident"
)

# Retrain model with new data
# python ml_model/train_from_website.py
```

### 4. Batch Classification
```python
from backend.analyze_input import batch_analyze_news

texts = [
    "Fire at factory",
    "Concert tonight", 
    "Rain warning",
    "Bank robbery"
]

results = batch_analyze_news(texts)
# Returns batch results with individual classifications
```

## Model Improvement Strategies

### 1. **Increase Training Data**
- Add more labeled examples (target: 100+ per category)
- Collect real user submissions
- Use data augmentation techniques

### 2. **Feature Engineering**
- Experiment with different TF-IDF parameters
- Add custom features (time, location, keywords)
- Try different text preprocessing approaches

### 3. **Model Optimization**
- Test other algorithms (Random Forest, SVM, Neural Networks)
- Hyperparameter tuning
- Cross-validation for better evaluation

### 4. **Production Enhancements**
- Model versioning and A/B testing
- Real-time performance monitoring
- Automated retraining pipeline

## Troubleshooting

### Common Issues

1. **"Model files not found"**
   ```bash
   # Solution: Run training pipeline
   python ml_model/train_from_website.py
   ```

2. **"ModuleNotFoundError: nltk"**
   ```bash
   # Solution: Install dependencies
   pip install nltk scikit-learn pandas numpy
   ```

3. **"After pruning, no terms remain"**
   - Issue: TF-IDF parameters too restrictive for small dataset
   - Solution: Adjust `min_df=1` in TfidfVectorizer

4. **Low model accuracy**
   - Issue: Insufficient training data
   - Solution: Add more labeled examples to database

### Performance Monitoring

```python
# Check model status
from backend.analyze_input import get_model_status
status = get_model_status()
print(f"Model loaded: {status['model_loaded']}")
print(f"Accuracy: {status['accuracy']}")
```

## Next Steps

### Immediate Improvements
1. **Data Collection**: Implement user feedback mechanism
2. **Model Enhancement**: Add more training examples  
3. **API Integration**: Connect with existing endpoints
4. **UI Integration**: Add classification results to frontend

### Long-term Roadmap
1. **Advanced ML**: Deep learning models (BERT, transformers)
2. **Real-time Processing**: Stream processing for live news
3. **Multi-language**: Support regional languages
4. **Sentiment Analysis**: Add emotion/sentiment detection
5. **Image Classification**: Extend to multimedia content

## Support

For issues or questions:
1. Check model files exist in `ml_model/` directory
2. Verify database has training data
3. Review logs in terminal output
4. Test individual components separately

---

**Built with ❤️ for the Infosphere Platform**  
*Automated News Classification System v1.0*