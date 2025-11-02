"""
News Classification Analyzer for Backend API

This module provides the main analysis function that loads the trained ML model
and vectorizer to classify news text into categories (Crime, Accident, Event, Weather).

It serves as the bridge between the trained ML pipeline and the backend API endpoints,
providing real-time news classification with confidence scores.

Author: Infosphere Backend Team
Date: October 2025
"""

import pickle
import os
import numpy as np
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsClassifier:
    """
    Wrapper class for the trained news classification model.
    
    Handles model loading, text preprocessing, and prediction with confidence scores.
    """
    
    def __init__(self, model_dir=None):
        """
        Initialize the news classifier.
        
        Args:
            model_dir (str, optional): Directory containing model files
        """
        if model_dir is None:
            # Default to ml_model directory in parent folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            self.model_dir = os.path.join(parent_dir, 'ml_model')
        else:
            self.model_dir = model_dir
            
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.is_loaded = False
        
        # Load model on initialization
        self._load_model_artifacts()
    
    def _load_model_artifacts(self):
        """
        Load the trained model, vectorizer, and other artifacts.
        """
        try:
            # Model file paths
            model_path = os.path.join(self.model_dir, 'news_classifier_model.pkl')
            vectorizer_path = os.path.join(self.model_dir, 'tfidf_vectorizer.pkl')
            metadata_path = os.path.join(self.model_dir, 'model_metadata.pkl')
            
            # Check if files exist
            if not all(os.path.exists(path) for path in [model_path, vectorizer_path, metadata_path]):
                logger.error("❌ Model files not found. Please train the model first.")
                logger.error("Run: python ml_model/train_from_website.py")
                self.is_loaded = False
                return
            
            # Load model artifacts
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
                
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
                
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            self.is_loaded = True
            logger.info("✅ Model artifacts loaded successfully")
            logger.info(f"📊 Model accuracy: {self.metadata.get('accuracy', 'N/A'):.3f}")
            
        except Exception as e:
            logger.error(f"❌ Error loading model artifacts: {e}")
            self.is_loaded = False
    
    def predict_single(self, text):
        """
        Predict category for a single text input.
        
        Args:
            text (str): News text to classify
            
        Returns:
            dict: Prediction results with category and confidence
        """
        if not self.is_loaded:
            return {
                'category': 'Error', 
                'confidence': 0.0,
                'error': 'Model not loaded'
            }
        
        if not text or not text.strip():
            return {
                'category': 'Error',
                'confidence': 0.0, 
                'error': 'Empty input text'
            }
        
        try:
            # Preprocess and vectorize text
            text_cleaned = text.strip().lower()
            text_vectorized = self.vectorizer.transform([text_cleaned])
            
            # Get prediction and probability
            prediction = self.model.predict(text_vectorized)[0]
            probabilities = self.model.predict_proba(text_vectorized)[0]
            confidence = np.max(probabilities)
            
            # Get all class probabilities for detailed analysis
            classes = self.model.classes_
            class_probs = dict(zip(classes, probabilities))
            
            return {
                'category': prediction,
                'confidence': float(confidence),
                'all_probabilities': class_probs,
                'timestamp': datetime.now().isoformat(),
                'model_version': self.metadata.get('version', '1.0')
            }
            
        except Exception as e:
            logger.error(f"❌ Error during prediction: {e}")
            return {
                'category': 'Error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def predict_batch(self, texts):
        """
        Predict categories for multiple text inputs.
        
        Args:
            texts (list): List of news texts to classify
            
        Returns:
            list: List of prediction results
        """
        if not self.is_loaded:
            return [{'category': 'Error', 'confidence': 0.0, 'error': 'Model not loaded'}] * len(texts)
        
        results = []
        for text in texts:
            result = self.predict_single(text)
            results.append(result)
        
        return results
    
    def get_model_info(self):
        """
        Get information about the loaded model.
        
        Returns:
            dict: Model metadata and performance information
        """
        if not self.is_loaded:
            return {'error': 'Model not loaded'}
        
        return {
            'model_type': 'Logistic Regression with TF-IDF',
            'categories': list(self.model.classes_),
            'feature_count': self.vectorizer.max_features,
            'ngram_range': self.vectorizer.ngram_range,
            'training_date': self.metadata.get('training_date', 'Unknown'),
            'accuracy': self.metadata.get('accuracy', 'Unknown'),
            'precision': self.metadata.get('precision', 'Unknown'),
            'recall': self.metadata.get('recall', 'Unknown'),
            'f1_score': self.metadata.get('f1_score', 'Unknown'),
            'model_version': self.metadata.get('version', '1.0')
        }


# Global classifier instance (singleton pattern)
_classifier_instance = None

def get_classifier():
    """
    Get or create the global classifier instance.
    
    Returns:
        NewsClassifier: Initialized classifier instance
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = NewsClassifier()
    return _classifier_instance


def analyze_news_input(user_text):
    """
    Main function to analyze news input and return predicted category with confidence.
    
    This is the primary function called by API endpoints.
    
    Args:
        user_text (str): User-submitted news text
        
    Returns:
        dict: Analysis results with category, confidence, and metadata
    """
    logger.info(f"🔍 Analyzing news input: '{user_text[:50]}...'")
    
    try:
        # Get classifier instance
        classifier = get_classifier()
        
        if not classifier.is_loaded:
            logger.error("❌ Classifier not properly loaded")
            return {
                'category': 'Error',
                'confidence': 0.0,
                'error': 'Model not available',
                'status': 'failed'
            }
        
        # Perform classification
        result = classifier.predict_single(user_text)
        
        # Add analysis metadata
        result.update({
            'input_length': len(user_text),
            'analysis_status': 'success' if 'error' not in result else 'failed',
            'processed_at': datetime.now().isoformat()
        })
        
        # Log successful analysis
        if 'error' not in result:
            logger.info(f"✅ Classification result: {result['category']} (confidence: {result['confidence']:.3f})")
        else:
            logger.error(f"❌ Classification failed: {result['error']}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in analyze_news_input: {e}")
        return {
            'category': 'Error',
            'confidence': 0.0,
            'error': 'Analysis service unavailable',
            'status': 'failed',
            'processed_at': datetime.now().isoformat()
        }


def batch_analyze_news(texts):
    """
    Analyze multiple news texts in batch.
    
    Args:
        texts (list): List of news texts to analyze
        
    Returns:
        dict: Batch analysis results
    """
    logger.info(f"🔍 Batch analyzing {len(texts)} news inputs")
    
    try:
        classifier = get_classifier()
        
        if not classifier.is_loaded:
            return {
                'results': [],
                'error': 'Model not available',
                'status': 'failed'
            }
        
        # Process all texts
        results = classifier.predict_batch(texts)
        
        # Add batch metadata
        successful_predictions = sum(1 for r in results if 'error' not in r)
        
        return {
            'results': results,
            'total_processed': len(texts),
            'successful_predictions': successful_predictions,
            'failed_predictions': len(texts) - successful_predictions,
            'status': 'success',
            'processed_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error in batch analysis: {e}")
        return {
            'results': [],
            'error': str(e),
            'status': 'failed'
        }


def get_model_status():
    """
    Get current status and information about the classification model.
    
    Returns:
        dict: Model status and metadata
    """
    try:
        classifier = get_classifier()
        
        status = {
            'model_loaded': classifier.is_loaded,
            'status': 'active' if classifier.is_loaded else 'inactive',
            'last_check': datetime.now().isoformat()
        }
        
        if classifier.is_loaded:
            status.update(classifier.get_model_info())
        
        return status
        
    except Exception as e:
        return {
            'model_loaded': False,
            'status': 'error',
            'error': str(e),
            'last_check': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test the analyzer
    print("🧪 Testing News Classification Analyzer")
    print("=" * 40)
    
    # Test single prediction
    test_texts = [
        "Fire broke out in commercial building",
        "Free health checkup camp organized", 
        "Heavy rainfall expected tomorrow",
        "Theft reported near metro station"
    ]
    
    print("\n📝 Testing individual predictions:")
    for text in test_texts:
        result = analyze_news_input(text)
        print(f"Text: '{text}'")
        print(f"Category: {result['category']} (Confidence: {result.get('confidence', 0):.3f})")
        print()
    
    # Test model status
    print("📊 Model Status:")
    status = get_model_status()
    for key, value in status.items():
        print(f"{key}: {value}")