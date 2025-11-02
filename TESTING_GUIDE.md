# 🧪 ATIE Testing Guide - AI Trust and Integrity Engine

## 🎯 **Quick Start Testing**

### **Step 1: Access the Application**
1. Open your browser and go to: `http://localhost:3000`
2. Click on **"Media Verification"** in the navigation menu

### **Step 2: Test ATIE Features**

#### 🔤 **Text Analysis Testing**

**Test Case 1: Fake News Detection**
```
Sample Text (copy and paste):
"BREAKING: Scientists have discovered that drinking water is actually harmful to humans and recommend switching to soda immediately. This shocking revelation comes from a study that was never published but totally exists."

Expected Result: HIGH fake news probability, LOW trust score
```

**Test Case 2: Legitimate News**
```
Sample Text (copy and paste):
"The weather forecast for tomorrow indicates partly cloudy skies with temperatures reaching 75 degrees Fahrenheit. Local meteorologists recommend carrying an umbrella as there is a 30% chance of rain in the afternoon."

Expected Result: LOW fake news probability, HIGH trust score
```

**Test Case 3: Biased Content**
```
Sample Text (copy and paste):
"The terrible politician from the opposing party has once again made a completely ridiculous decision that will destroy our economy forever. Anyone with half a brain can see this is the worst thing that has ever happened."

Expected Result: HIGH bias detection, sensationalism flags
```

#### 🖼️ **Media Analysis Testing**

**Test Media Files:**
- Upload any image to test the Media Integrity Engine (MIE)
- The system will analyze for potential manipulation

#### 🔗 **Composite Analysis Testing**

**Test Both Together:**
1. Upload an image
2. Add text content
3. Select "Composite Analysis"
4. Get combined trust score

---

## 🔧 **API Testing (Advanced)**

### **Method 1: Using Browser (Interactive Docs)**
1. Go to: `http://localhost:8000/docs`
2. Test these endpoints:

#### **ATIE Text Analysis**
```
POST /api/v1/atie/analyze-text
Body:
{
  "text": "Your test text here",
  "enable_cross_verification": true
}
```

#### **Quick Check**
```
POST /api/v1/atie/quick-check
Body:
{
  "text": "Short text for fast analysis"
}
```

### **Method 2: Using Command Line**

Test the ATIE service with curl commands:

```bash
# Test 1: Basic Text Analysis
curl -X POST "http://localhost:8000/api/v1/atie/analyze-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test of the fake news detection system.",
    "enable_cross_verification": true
  }'

# Test 2: Quick Check
curl -X POST "http://localhost:8000/api/v1/atie/quick-check" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Breaking news: This is definitely fake!"
  }'

# Test 3: Composite Analysis  
curl -X POST "http://localhost:8000/api/v1/atie/analyze-composite" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Sample news text for analysis",
    "media_analysis": {
      "manipulation_score": 0.3,
      "confidence": 0.85,
      "detected_techniques": ["none"]
    }
  }'
```

---

## 📊 **Expected Results Format**

### **Text Analysis Response:**
```json
{
  "trust_score": 0.75,
  "fake_news_probability": 0.25,
  "analysis_details": {
    "fake_news_score": 0.25,
    "bias_score": 0.15,
    "sensationalism_score": 0.10
  },
  "cross_verification": {
    "verified_claims": 2,
    "contradicted_claims": 0,
    "similarity_scores": [0.85, 0.92]
  },
  "confidence": 0.87,
  "processing_time": "0.245s"
}
```

### **Frontend Interface Features:**
- 🎯 **Trust Score Bar**: Visual indicator (0-100%)
- 📊 **Analysis Breakdown**: Detailed scores for each category
- ⚡ **Real-time Results**: Instant feedback as you type
- 🔄 **Analysis Mode Toggle**: Switch between media/text/composite

---

## 🎪 **Demo Scenarios**

### **Scenario 1: Politician Speech Analysis**
```
Text: "My opponent's policies will absolutely destroy the economy and lead to complete chaos. Everyone knows this is true, and any expert who disagrees is clearly biased."

Expected: HIGH bias, HIGH sensationalism, MEDIUM fake news
```

### **Scenario 2: Scientific Article**
```
Text: "According to a peer-reviewed study published in Nature, researchers found a correlation between exercise and improved cognitive function in adults aged 65-75."

Expected: LOW bias, LOW sensationalism, LOW fake news
```

### **Scenario 3: Social Media Post**
```
Text: "OMG!!! You won't BELIEVE what happened next! Doctors HATE this one simple trick that will change your life FOREVER!!!"

Expected: HIGH sensationalism, potential fake news indicators
```

---

## 🚀 **Performance Testing**

### **Load Testing**
```bash
# Test multiple requests quickly
for i in {1..10}; do
  curl -X POST "http://localhost:8000/api/v1/atie/quick-check" \
    -H "Content-Type: application/json" \
    -d '{"text": "Test message '$i'"}' &
done
```

### **Caching Verification**
1. Send the same request twice
2. Second request should be faster (cached result)
3. Check console logs for cache hits

---

## 🔍 **Debugging & Logs**

### **Backend Logs**
- Watch the terminal where you started `main.py`
- Look for ATIE service initialization messages
- Check for any error messages or warnings

### **Frontend Console**
- Open browser DevTools (F12)
- Check Network tab for API calls
- Look for any JavaScript errors in Console

### **Common Issues & Solutions**

**Issue**: "ATIE endpoints not available"
```bash
# Solution: Check if sentence-transformers is installed
cd backend
../venv/Scripts/python.exe -c "import sentence_transformers; print('OK')"
```

**Issue**: Slow response times
```bash
# Check if models are loading properly
# First request is slower (model loading), subsequent are faster
```

**Issue**: Frontend not updating
```bash
# Clear browser cache and refresh
# Check if both frontend and backend are running
```

---

## ✅ **Success Criteria**

Your ATIE implementation is working correctly if:

1. ✅ **Text analysis returns trust scores between 0-1**
2. ✅ **Fake news detection identifies obviously false content**
3. ✅ **Bias detection flags partisan language**
4. ✅ **Sensationalism detection catches clickbait-style text**
5. ✅ **Cross-verification finds similar content in trusted sources**
6. ✅ **Composite analysis combines media and text scores**
7. ✅ **Response times are under 3 seconds for first request, under 1 second for cached**
8. ✅ **Frontend updates in real-time with analysis results**

---

## 🎯 **Next Steps After Testing**

1. **Fine-tune Models**: Adjust thresholds based on your testing results
2. **Add More Trusted Sources**: Expand the database for better cross-verification
3. **Implement User Feedback**: Allow users to rate analysis accuracy
4. **Set Up Redis**: For production-level caching performance
5. **Add Analytics**: Track usage patterns and accuracy metrics

---

*Happy Testing! 🧪✨*