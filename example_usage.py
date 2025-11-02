"""
Example Usage of Infosphere ML Pipeline

This file demonstrates how to use the trained ML model for news classification.
Run this script to see practical examples of the ML pipeline in action.

Author: Infosphere Team
Date: October 2025
"""

import sys
import os

# Add backend path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

from backend.analyze_input import analyze_news_input, batch_analyze_news
from backend.db_connector import NewsDataConnector

def example_1_single_classification():
    """Example 1: Classify a single news item."""
    print("1️⃣ Single News Classification Example")
    print("-" * 35)
    
    news_text = "Fire broke out in shopping mall causing evacuation"
    
    result = analyze_news_input(news_text)
    
    print(f"📰 News: {news_text}")
    print(f"🏷️ Category: {result['category']}")
    print(f"📊 Confidence: {result['confidence']:.3f}")
    print(f"🕐 Timestamp: {result['timestamp']}")
    
    if 'all_probabilities' in result:
        print("📈 All Category Probabilities:")
        for category, prob in result['all_probabilities'].items():
            print(f"   {category}: {prob:.3f}")

def example_2_batch_classification():
    """Example 2: Classify multiple news items at once."""
    print("\n2️⃣ Batch News Classification Example")
    print("-" * 35)
    
    news_items = [
        "Heavy rainfall warning issued for tomorrow",
        "Free health checkup camp organized by NGO", 
        "Chain snatching incident reported at bus stop",
        "Gas cylinder explosion in residential area"
    ]
    
    results = batch_analyze_news(news_items)
    
    print(f"📊 Processed {results['total_processed']} news items")
    print(f"✅ Successful predictions: {results['successful_predictions']}")
    print(f"❌ Failed predictions: {results['failed_predictions']}")
    print("\n📋 Individual Results:")
    
    for i, result in enumerate(results['results']):
        if 'error' not in result:
            print(f"   {i+1}. {news_items[i][:40]}... → {result['category']} ({result['confidence']:.3f})")
        else:
            print(f"   {i+1}. {news_items[i][:40]}... → Error: {result['error']}")

def example_3_add_training_data():
    """Example 3: Add new labeled data to the database."""
    print("\n3️⃣ Adding New Training Data Example")
    print("-" * 35)
    
    try:
        connector = NewsDataConnector()
        
        # Add some new examples
        examples = [
            ("Earthquake tremors felt across city", "user123", "Downtown", "Accident"),
            ("Marathon registration opens tomorrow", "user456", "Sports Complex", "Event"),
            ("Snowfall expected in hill stations", "user789", "Weather Station", "Weather"),
            ("ATM robbery attempt foiled", "user101", "Bank Street", "Crime")
        ]
        
        print("📝 Adding new training examples:")
        for text, user_id, location, label in examples:
            submission_id = connector.add_submission(text, user_id, location, label)
            print(f"   ✅ Added submission {submission_id}: {text} → {label}")
        
        # Show updated distribution
        distribution = connector.get_label_distribution()
        print(f"\n📊 Updated label distribution: {distribution}")
        
    except Exception as e:
        print(f"❌ Error adding training data: {e}")

def example_4_database_operations():
    """Example 4: Database operations and analysis."""
    print("\n4️⃣ Database Operations Example")
    print("-" * 35)
    
    try:
        connector = NewsDataConnector()
        
        # Fetch all submissions
        all_data = connector.fetch_all_submissions()
        print(f"📊 Total submissions in database: {len(all_data)}")
        
        # Fetch recent submissions (last 7 days)
        recent_data = connector.fetch_recent_submissions(days=7)
        print(f"📅 Recent submissions (7 days): {len(recent_data)}")
        
        # Show label distribution
        distribution = connector.get_label_distribution()
        print("📈 Current label distribution:")
        for label, count in distribution.items():
            print(f"   {label}: {count} submissions")
        
        # Show sample data
        print("\n📋 Sample submissions:")
        sample_data = all_data.head(3)
        for _, row in sample_data.iterrows():
            print(f"   '{row['text'][:50]}...' → {row['label']}")
            
    except Exception as e:
        print(f"❌ Error with database operations: {e}")

def example_5_mock_api_endpoint():
    """Example 5: Mock API endpoint for news classification."""
    print("\n5️⃣ Mock API Endpoint Example")
    print("-" * 35)
    
    def mock_api_classify(news_text):
        """Mock API endpoint for news classification."""
        try:
            result = analyze_news_input(news_text)
            
            if 'error' in result:
                return {
                    "status": "error",
                    "message": result['error'],
                    "code": 400
                }
            
            return {
                "status": "success",
                "data": {
                    "category": result['category'],
                    "confidence": result['confidence'],
                    "timestamp": result['timestamp']
                },
                "code": 200
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e),
                "code": 500
            }
    
    # Test API with different inputs
    test_cases = [
        "Concert tickets on sale from Monday",
        "Road accident causes traffic jam",
        "Heavy fog disrupts flight operations", 
        ""  # Empty input to test error handling
    ]
    
    print("🌐 Testing mock API endpoints:")
    for i, test_input in enumerate(test_cases):
        api_result = mock_api_classify(test_input)
        
        print(f"\n   API Request {i+1}:")
        print(f"   Input: '{test_input}'" if test_input else "   Input: [empty]")
        print(f"   Response: {api_result}")

def example_6_model_performance():
    """Example 6: Check model performance and status."""
    print("\n6️⃣ Model Performance Analysis")
    print("-" * 35)
    
    try:
        from backend.analyze_input import get_model_status
        
        # Get model status
        status = get_model_status()
        
        print("🤖 Model Information:")
        print(f"   Status: {status['status']}")
        print(f"   Model Type: {status.get('model_type', 'N/A')}")
        print(f"   Categories: {status.get('categories', [])}")
        print(f"   Feature Count: {status.get('feature_count', 'N/A')}")
        print(f"   Training Date: {status.get('training_date', 'N/A')}")
        print(f"   Accuracy: {status.get('accuracy', 'N/A')}")
        
        # Test classification confidence across categories
        confidence_test = [
            ("Major fire incident at industrial complex", "Accident"),
            ("Blood donation camp organized at hospital", "Event"),
            ("Heavy monsoon rains expected next week", "Weather"),
            ("Chain snatching reported in market area", "Crime")
        ]
        
        print("\n📊 Confidence Score Analysis:")
        for text, expected in confidence_test:
            result = analyze_news_input(text)
            if 'error' not in result:
                correct = "✅" if result['category'] == expected else "⚠️"
                print(f"   {correct} {result['category']} (conf: {result['confidence']:.3f}) | Expected: {expected}")
                print(f"      Text: '{text[:60]}...'")
        
    except Exception as e:
        print(f"❌ Error analyzing model performance: {e}")

def main():
    """Run all examples."""
    print("🚀 Infosphere ML Pipeline Usage Examples")
    print("=" * 50)
    print("This script demonstrates practical usage of the ML pipeline")
    print()
    
    try:
        example_1_single_classification()
        example_2_batch_classification()
        example_3_add_training_data()
        example_4_database_operations()
        example_5_mock_api_endpoint()
        example_6_model_performance()
        
        print("\n" + "=" * 50)
        print("🎉 All examples completed successfully!")
        print("📚 Check ML_PIPELINE_DOCUMENTATION.md for more details")
        print("🔧 Run 'python test_ml_pipeline.py' for comprehensive tests")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("🔧 Make sure the ML model is trained: python ml_model/train_from_website.py")

if __name__ == "__main__":
    main()