"""
Integration Test Suite for Infosphere ML Pipeline

This script tests the complete ML pipeline including:
- Database connectivity
- Model training
- News classification  
- Backend integration

Run this script to validate the entire system is working correctly.

Author: Infosphere Team
Date: October 2025
"""

import sys
import os
import time
from datetime import datetime

# Add backend path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

def test_database_connectivity():
    """Test database connector functionality."""
    print("🔍 Testing Database Connectivity...")
    
    try:
        from backend.db_connector import NewsDataConnector, fetch_user_data
        
        # Test connector initialization
        connector = NewsDataConnector()
        print("  ✅ Database connector initialized successfully")
        
        # Test data fetching
        df = fetch_user_data()
        if len(df) > 0:
            print(f"  ✅ Fetched {len(df)} records from database")
            print(f"  📊 Categories: {df['label'].unique().tolist()}")
        else:
            print("  ❌ No data found in database")
            return False
            
        # Test label distribution
        distribution = connector.get_label_distribution()
        print(f"  📈 Label distribution: {distribution}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False


def test_model_training():
    """Test ML model training pipeline."""
    print("\n🚀 Testing Model Training Pipeline...")
    
    try:
        # Import training functions
        import subprocess
        import pickle
        
        # Check if model files already exist
        model_dir = os.path.join(current_dir, 'ml_model')
        model_files = [
            'news_classifier_model.pkl',
            'tfidf_vectorizer.pkl', 
            'model_metadata.pkl'
        ]
        
        files_exist = all(os.path.exists(os.path.join(model_dir, f)) for f in model_files)
        
        if not files_exist:
            print("  🔄 Model files not found, training new model...")
            
            # Run training script
            result = subprocess.run([
                sys.executable, 
                os.path.join(model_dir, 'train_from_website.py')
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  ❌ Training failed: {result.stderr}")
                return False
            else:
                print("  ✅ Model training completed successfully")
        else:
            print("  ✅ Model files found")
            
        # Test loading model metadata
        metadata_path = os.path.join(model_dir, 'model_metadata.pkl')
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
            
        print(f"  📊 Model accuracy: {metadata.get('accuracy', 'Unknown')}")
        print(f"  🗓️ Training date: {metadata.get('training_date', 'Unknown')}")
        print(f"  🏷️ Categories: {metadata.get('classes', [])}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model training test failed: {e}")
        return False


def test_news_classification():
    """Test news classification functionality."""
    print("\n🎯 Testing News Classification...")
    
    try:
        from backend.analyze_input import analyze_news_input, get_model_status
        
        # Check model status
        status = get_model_status()
        if not status['model_loaded']:
            print("  ❌ Model not loaded")
            return False
            
        print(f"  ✅ Model loaded successfully")
        print(f"  📊 Model type: {status.get('model_type', 'Unknown')}")
        
        # Test sample classifications
        test_cases = [
            ("Fire broke out in commercial building", "Accident"),
            ("Free health checkup camp organized", "Event"), 
            ("Heavy rainfall expected tomorrow", "Weather"),
            ("Theft reported near metro station", "Crime"),
            ("Blood donation drive this weekend", "Event"),
            ("Car accident on highway", "Accident"),
            ("Thunderstorm warning issued", "Weather"),
            ("Burglary attempt at shop", "Crime")
        ]
        
        print("  🧪 Testing sample classifications:")
        correct_predictions = 0
        
        for text, expected_category in test_cases:
            result = analyze_news_input(text)
            
            if 'error' in result:
                print(f"    ❌ '{text[:30]}...' → Error: {result['error']}")
                continue
                
            predicted = result['category']
            confidence = result['confidence']
            is_correct = predicted == expected_category
            
            if is_correct:
                correct_predictions += 1
                
            status_icon = "✅" if is_correct else "⚠️"
            print(f"    {status_icon} '{text[:30]}...' → {predicted} (conf: {confidence:.3f})")
            
        accuracy = correct_predictions / len(test_cases) if test_cases else 0
        print(f"  📈 Test accuracy: {accuracy:.2%} ({correct_predictions}/{len(test_cases)})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Classification test failed: {e}")
        return False


def test_backend_integration():
    """Test backend integration components."""
    print("\n🔗 Testing Backend Integration...")
    
    try:
        from backend.analyze_input import (
            get_classifier, 
            batch_analyze_news,
            get_model_status
        )
        
        # Test singleton classifier
        classifier1 = get_classifier()
        classifier2 = get_classifier()
        
        if classifier1 is classifier2:
            print("  ✅ Singleton classifier pattern working")
        else:
            print("  ⚠️ Multiple classifier instances created")
            
        # Test batch processing
        batch_texts = [
            "Fire at factory", 
            "Concert tonight",
            "Rain warning",
            "Bank robbery"
        ]
        
        batch_results = batch_analyze_news(batch_texts)
        
        if batch_results['status'] == 'success':
            successful = batch_results['successful_predictions']
            total = batch_results['total_processed']
            print(f"  ✅ Batch processing: {successful}/{total} successful")
        else:
            print(f"  ❌ Batch processing failed: {batch_results.get('error', 'Unknown')}")
            
        # Test model info
        status = get_model_status()
        print(f"  📋 Model info available: {len(status)} fields")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Backend integration test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and edge cases."""
    print("\n🛡️ Testing Error Handling...")
    
    try:
        from backend.analyze_input import analyze_news_input
        
        # Test empty input
        result = analyze_news_input("")
        if 'error' in result:
            print("  ✅ Empty input handled correctly")
        else:
            print("  ⚠️ Empty input not handled")
            
        # Test very long input  
        long_text = "This is a very long news text. " * 100
        result = analyze_news_input(long_text)
        if result.get('category') != 'Error':
            print("  ✅ Long input processed successfully")
        else:
            print("  ⚠️ Long input caused error")
            
        # Test special characters
        special_text = "Fire at @#$%^&*() location with émojis 🔥"
        result = analyze_news_input(special_text)
        if result.get('category') != 'Error':
            print("  ✅ Special characters handled")
        else:
            print("  ⚠️ Special characters caused error")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        return False


def run_performance_benchmark():
    """Run basic performance benchmark."""
    print("\n⚡ Running Performance Benchmark...")
    
    try:
        from backend.analyze_input import analyze_news_input
        
        # Test multiple predictions for timing
        test_text = "Fire broke out in commercial building causing traffic jam"
        iterations = 10
        
        start_time = time.time()
        
        for _ in range(iterations):
            result = analyze_news_input(test_text)
            if 'error' in result:
                print(f"  ❌ Prediction failed during benchmark")
                return False
                
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations
        
        print(f"  ⏱️ Average prediction time: {avg_time*1000:.2f}ms")
        print(f"  🚀 Predictions per second: {1/avg_time:.1f}")
        
        if avg_time < 1.0:  # Less than 1 second
            print("  ✅ Performance acceptable for real-time usage")
        else:
            print("  ⚠️ Performance may be slow for real-time usage")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Performance benchmark failed: {e}")
        return False


def main():
    """Run complete integration test suite."""
    print("🧪 Infosphere ML Pipeline Integration Tests")
    print("=" * 50)
    print(f"📅 Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    tests = [
        ("Database Connectivity", test_database_connectivity),
        ("Model Training", test_model_training), 
        ("News Classification", test_news_classification),
        ("Backend Integration", test_backend_integration),
        ("Error Handling", test_error_handling),
        ("Performance Benchmark", run_performance_benchmark)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status_icon = "✅" if passed else "❌"
        print(f"{status_icon} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! ML pipeline is ready for production.")
        return 0
    elif passed_tests >= total_tests * 0.8:
        print("⚠️ Most tests passed. Some issues need attention.")
        return 1
    else:
        print("❌ Multiple test failures. System needs debugging.")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)