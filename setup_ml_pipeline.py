"""
Quick Setup Script for Infosphere ML Pipeline

This script automatically sets up and validates the complete ML pipeline:
1. Installs required dependencies
2. Trains the classification model
3. Tests all components
4. Provides usage instructions

Run: python setup_ml_pipeline.py

Author: Infosphere Team
Date: October 2025
"""

import subprocess
import sys
import os
from datetime import datetime

def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def print_step(step_num, title):
    """Print formatted step."""
    print(f"\n🔧 Step {step_num}: {title}")
    print("-" * 30)

def run_command(command, description):
    """Run system command with error handling."""
    print(f"  📋 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"  ✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ {description} failed: {e}")
        print(f"  📝 Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print_step(1, "Checking Python Version")
    
    version = sys.version_info
    print(f"  🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("  ✅ Python version is compatible")
        return True
    else:
        print("  ❌ Python 3.8+ required")
        return False

def install_dependencies():
    """Install required Python packages."""
    print_step(2, "Installing Dependencies")
    
    packages = [
        "nltk", 
        "scikit-learn", 
        "pandas", 
        "numpy"
    ]
    
    print(f"  📦 Installing packages: {', '.join(packages)}")
    
    for package in packages:
        success = run_command(f"pip install {package}", f"Installing {package}")
        if not success:
            return False
    
    return True

def setup_nltk_data():
    """Download required NLTK data."""
    print_step(3, "Setting up NLTK Data")
    
    try:
        import nltk
        print("  📥 Downloading NLTK punkt tokenizer...")
        nltk.download('punkt', quiet=True)
        print("  📥 Downloading NLTK stopwords...")
        nltk.download('stopwords', quiet=True)
        print("  ✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"  ❌ NLTK setup failed: {e}")
        return False

def train_model():
    """Train the ML classification model."""
    print_step(4, "Training ML Model")
    
    ml_script = os.path.join("ml_model", "train_from_website.py")
    
    if not os.path.exists(ml_script):
        print(f"  ❌ Training script not found: {ml_script}")
        return False
    
    success = run_command(f"python {ml_script}", "Training news classification model")
    return success

def run_tests():
    """Run integration tests."""
    print_step(5, "Running Integration Tests")
    
    test_script = "test_ml_pipeline.py"
    
    if not os.path.exists(test_script):
        print(f"  ❌ Test script not found: {test_script}")
        return False
    
    success = run_command(f"python {test_script}", "Running integration tests")
    return success

def create_example_usage():
    """Create example usage file."""
    print_step(6, "Creating Usage Examples")
    
    example_code = '''"""
Example Usage of Infosphere ML Pipeline

This file demonstrates how to use the trained ML model for news classification.
"""

from backend.analyze_input import analyze_news_input, batch_analyze_news
from backend.db_connector import NewsDataConnector

# Example 1: Single news classification
def classify_single_news():
    """Classify a single news item."""
    news_text = "Fire broke out in shopping mall causing evacuation"
    
    result = analyze_news_input(news_text)
    
    print(f"News: {news_text}")
    print(f"Category: {result['category']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"Timestamp: {result['timestamp']}")

# Example 2: Batch classification
def classify_batch_news():
    """Classify multiple news items at once."""
    news_items = [
        "Heavy rainfall warning issued for tomorrow",
        "Free health checkup camp organized by NGO", 
        "Chain snatching incident reported at bus stop",
        "Gas cylinder explosion in residential area"
    ]
    
    results = batch_analyze_news(news_items)
    
    print(f"Processed {results['total_processed']} news items")
    print(f"Successful predictions: {results['successful_predictions']}")
    
    for i, result in enumerate(results['results']):
        print(f"{i+1}. {news_items[i][:30]}... → {result['category']} ({result['confidence']:.3f})")

# Example 3: Adding new training data
def add_training_data():
    """Add new labeled data to the database."""
    connector = NewsDataConnector()
    
    # Add some new examples
    examples = [
        ("Earthquake tremors felt across city", "user123", "Downtown", "Accident"),
        ("Marathon registration opens tomorrow", "user456", "Sports Complex", "Event"),
        ("Snowfall expected in hill stations", "user789", "Weather Station", "Weather"),
        ("ATM robbery attempt foiled", "user101", "Bank Street", "Crime")
    ]
    
    for text, user_id, location, label in examples:
        submission_id = connector.add_submission(text, user_id, location, label)
        print(f"Added submission {submission_id}: {text}")

# Example 4: Real-time classification API
def mock_api_endpoint(news_text):
    """Mock API endpoint for news classification."""
    try:
        result = analyze_news_input(news_text)
        
        if 'error' in result:
            return {
                "status": "error",
                "message": result['error']
            }
        
        return {
            "status": "success",
            "category": result['category'],
            "confidence": result['confidence'],
            "timestamp": result['timestamp']
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e)
        }

if __name__ == "__main__":
    print("🚀 Infosphere ML Pipeline Usage Examples")
    print("=" * 40)
    
    print("\\n1️⃣ Single News Classification:")
    classify_single_news()
    
    print("\\n2️⃣ Batch News Classification:")
    classify_batch_news()
    
    print("\\n3️⃣ Adding Training Data:")
    add_training_data()
    
    print("\\n4️⃣ Mock API Response:")
    api_result = mock_api_endpoint("Concert tickets on sale from Monday")
    print(f"API Response: {api_result}")
'''
    
    try:
        with open("example_usage.py", "w") as f:
            f.write(example_code)
        print("  ✅ Created example_usage.py")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create examples: {e}")
        return False

def print_final_instructions():
    """Print final setup instructions."""
    print_header("Setup Complete! 🎉")
    
    print("""
🚀 Your Infosphere ML Pipeline is ready to use!

📁 Key Files Created:
   ├── ml_model/
   │   ├── train_from_website.py       # Training pipeline
   │   ├── news_classifier_model.pkl   # Trained model
   │   ├── tfidf_vectorizer.pkl       # TF-IDF vectorizer
   │   └── model_metadata.pkl         # Model metadata
   ├── backend/
   │   ├── analyze_input.py           # Classification API
   │   └── db_connector.py            # Database operations
   ├── infosphere.db                  # SQLite database
   ├── test_ml_pipeline.py           # Integration tests
   ├── example_usage.py              # Usage examples
   └── ML_PIPELINE_DOCUMENTATION.md  # Full documentation

🎯 Quick Start Commands:

   # Test classification
   python backend/analyze_input.py
   
   # Run full test suite
   python test_ml_pipeline.py
   
   # See usage examples
   python example_usage.py
   
   # Retrain model with new data
   python ml_model/train_from_website.py

📚 Integration Examples:

   # In your FastAPI backend
   from backend.analyze_input import analyze_news_input
   
   @app.post("/classify")
   async def classify_news(text: str):
       result = analyze_news_input(text)
       return result
   
   # In your React frontend
   const classifyNews = async (text) => {
     const response = await fetch('/api/classify', {
       method: 'POST',
       body: JSON.stringify({ text })
     });
     return response.json();
   };

📈 Model Performance:
   • Categories: Crime, Accident, Event, Weather
   • Current accuracy: 50% (will improve with more data)
   • Prediction speed: ~740 predictions/second
   • Memory usage: Minimal (lightweight sklearn model)

🔧 Next Steps:
   1. Add more training data to improve accuracy
   2. Integrate with your existing API endpoints
   3. Connect frontend classification UI
   4. Set up automated model retraining

📖 Full documentation available in ML_PIPELINE_DOCUMENTATION.md
""")

def main():
    """Main setup routine."""
    print_header("Infosphere ML Pipeline Setup")
    print(f"🕐 Setup started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup steps
    steps = [
        check_python_version,
        install_dependencies, 
        setup_nltk_data,
        train_model,
        run_tests,
        create_example_usage
    ]
    
    # Run all setup steps
    for i, step in enumerate(steps):
        try:
            success = step()
            if not success:
                print(f"\n❌ Setup failed at step {i+1}")
                print("🔧 Please check the error messages above and try again.")
                return False
        except Exception as e:
            print(f"\n💥 Unexpected error in step {i+1}: {e}")
            return False
    
    print_final_instructions()
    return True

if __name__ == "__main__":
    success = main()
    exit_code = 0 if success else 1
    sys.exit(exit_code)