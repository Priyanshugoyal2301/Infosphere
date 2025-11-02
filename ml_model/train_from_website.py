"""
News Classification Model Training Pipeline

This module implements a complete ML pipeline for categorizing user-submitted news reports
into predefined classes: Crime, Accident, Event, and Weather.

Features:
- Simulated data fetching from database
- Text preprocessing (cleaning, stopword removal)
- TF-IDF vectorization
- Logistic Regression classification
- Model persistence for deployment
- Performance evaluation

Author: Infosphere ML Team
Date: October 2025
"""

import pandas as pd
import numpy as np
import pickle
import os
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


def fetch_user_data():
    """
    Fetches user-submitted news data from database via backend connector.
    
    This now connects to the actual database connector to fetch real user submissions
    with proper text cleaning and preprocessing. Falls back to simulated data if needed.
    
    Returns:
        pd.DataFrame: DataFrame with 'text' and 'label' columns
    """
    print("� Fetching user data from database...")
    
    try:
        # Import the database connector from backend
        import sys
        import os
        
        # Add backend directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_path = os.path.join(os.path.dirname(current_dir), 'backend')
        if backend_path not in sys.path:
            sys.path.append(backend_path)
        
        # Import and use the Infosphere database adapter
        from infosphere_db_adapter import fetch_user_data as fetch_from_infosphere_db
        return fetch_from_infosphere_db()
        
    except ImportError as e:
        print(f"⚠️  Could not import database connector: {e}")
        print("🔄 Using simulated data as fallback...")
        return _get_fallback_data()
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("🔄 Using simulated data as fallback...")
        return _get_fallback_data()


def _get_fallback_data():
    """
    Fallback function that provides simulated data if database connection fails.
    
    Returns:
        pd.DataFrame: Simulated user submission data
    """
    print("📊 Using fallback simulated data...")
    
    # Simulated user-submitted news data with realistic examples
    sample_data = [
        # Crime category
        ("Theft reported at MG Road shopping complex", "Crime"),
        ("Robbery incident near central bus station", "Crime"),
        ("Chain snatching case filed at local police station", "Crime"),
        ("Burglary attempt foiled by security guard", "Crime"),
        ("Fraud case registered against online seller", "Crime"),
        ("Assault case reported in residential area", "Crime"),
        ("Vandalism incident at public park", "Crime"),
        ("Drug peddling bust by police team", "Crime"),
        ("Cybercrime complaint filed by businessman", "Crime"),
        ("Eve teasing incident reported by student", "Crime"),
        
        # Accident category  
        ("Fire broke out near main road junction", "Accident"),
        ("Car collision reported on highway stretch", "Accident"),
        ("Gas cylinder explosion in residential building", "Accident"),
        ("Bike skidded on wet road during rush hour", "Accident"),
        ("Building collapse due to weak foundation", "Accident"),
        ("Electric shock incident at construction site", "Accident"),
        ("Tree fell on moving vehicle during storm", "Accident"),
        ("Chemical leak reported at industrial area", "Accident"),
        ("Water pipe burst causing road flooding", "Accident"),
        ("Elevator malfunction traps office workers", "Accident"),
        
        # Event category
        ("Free vaccination camp tomorrow at community center", "Event"),
        ("Cultural festival organized by local committee", "Event"),
        ("Blood donation drive scheduled this weekend", "Event"),
        ("Career guidance seminar for students announced", "Event"),
        ("Health checkup camp for senior citizens", "Event"),
        ("Tree plantation drive in city parks", "Event"),
        ("Cooking competition registration starts today", "Event"),
        ("Charity run for underprivileged children", "Event"),
        ("Technology workshop for entrepreneurs", "Event"),
        ("Art exhibition opens at gallery tomorrow", "Event"),
        
        # Weather category
        ("Heavy rainfall warning issued by meteorology department", "Weather"),
        ("Temperature expected to rise significantly today", "Weather"),
        ("Fog disrupts morning traffic on major roads", "Weather"),
        ("Thunderstorm alert for evening hours", "Weather"),
        ("Cyclone warning issued for coastal areas", "Weather"),
        ("Heatwave conditions likely to continue", "Weather"),
        ("Sudden weather change brings relief from heat", "Weather"),
        ("Monsoon season officially begins in region", "Weather"),
        ("Winter temperatures drop below normal range", "Weather"),
        ("Humidity levels cause discomfort across city", "Weather"),
        
        # Additional diverse examples
        ("Power outage affects residential neighborhoods", "Event"),
        ("Road construction creates traffic bottleneck", "Event"),
        ("School closure announced due to festival", "Event"),
        ("Emergency services respond to medical crisis", "Accident"),
        ("Pickpocketing incidents increase in market area", "Crime"),
        ("Strong winds damage outdoor advertising boards", "Weather"),
        ("Community kitchen serves free meals", "Event"),
        ("Vehicle breakdown causes traffic jam", "Accident"),
        ("Missing person case filed with authorities", "Crime"),
        ("Weather forecast predicts clear skies", "Weather"),
    ]
    
    # Create DataFrame
    df = pd.DataFrame(sample_data, columns=['text', 'label'])
    
    print(f"✅ Fetched {len(df)} user submissions")
    print(f"📈 Data distribution:")
    print(df['label'].value_counts().to_string())
    
    return df


def preprocess_text(text):
    """
    Clean and preprocess text data for ML model training.
    
    Args:
        text (str): Raw text input
        
    Returns:
        str: Cleaned and preprocessed text
    """
    if pd.isna(text):
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove special characters and digits, keep only alphabets and spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Tokenize and remove stopwords
    try:
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)
        filtered_text = [word for word in word_tokens if word not in stop_words]
        return ' '.join(filtered_text)
    except:
        # Fallback if NLTK fails
        return text


def train_classification_model(df):
    """
    Train a TF-IDF + Logistic Regression model for news classification.
    
    Args:
        df (pd.DataFrame): Training data with 'text' and 'label' columns
        
    Returns:
        tuple: (trained_model, vectorizer, test_accuracy)
    """
    print("\n🔧 Starting model training pipeline...")
    
    # Preprocess all text data
    print("🧹 Preprocessing text data...")
    df['cleaned_text'] = df['text'].apply(preprocess_text)
    
    # Remove any empty texts after preprocessing
    df = df[df['cleaned_text'].str.strip() != '']
    
    # Prepare features and labels
    X = df['cleaned_text']
    y = df['label']
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📊 Training set size: {len(X_train)}")
    print(f"📊 Testing set size: {len(X_test)}")
    
    # Create TF-IDF vectorizer with optimized parameters for small datasets
    vectorizer = TfidfVectorizer(
        max_features=1000,          # Reduce vocabulary size for small dataset
        min_df=1,                   # Include terms appearing in at least 1 document
        max_df=0.95,               # Ignore terms appearing in more than 95% of documents
        ngram_range=(1, 2),        # Use unigrams and bigrams
        stop_words='english'       # Additional stopword filtering
    )
    
    # Vectorize training data
    print("🔤 Converting text to TF-IDF vectors...")
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)
    
    # Train Logistic Regression classifier
    print("🎯 Training Logistic Regression classifier...")
    classifier = LogisticRegression(
        random_state=42,
        max_iter=1000,            # Increase iterations for convergence
        C=1.0,                    # Regularization parameter
        class_weight='balanced'   # Handle class imbalance
    )
    
    classifier.fit(X_train_vectorized, y_train)
    
    # Make predictions on test set
    y_pred = classifier.predict(X_test_vectorized)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    
    # Print detailed evaluation
    print(f"\n📈 Model Performance:")
    print(f"✅ Test Accuracy: {accuracy:.3f}")
    print(f"\n📊 Detailed Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Print feature importance (top words for each class)
    print(f"\n🔍 Top predictive features for each class:")
    feature_names = vectorizer.get_feature_names_out()
    
    for i, class_name in enumerate(classifier.classes_):
        # Get top 5 features for this class
        top_features_idx = classifier.coef_[i].argsort()[-5:][::-1]
        top_features = [feature_names[idx] for idx in top_features_idx]
        print(f"  {class_name}: {', '.join(top_features)}")
    
    return classifier, vectorizer, accuracy


def save_model_artifacts(classifier, vectorizer, accuracy):
    """
    Save trained model and vectorizer to disk for deployment.
    
    Args:
        classifier: Trained classification model
        vectorizer: Fitted TF-IDF vectorizer  
        accuracy (float): Model test accuracy
    """
    print(f"\n💾 Saving model artifacts...")
    
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save classifier
    classifier_path = os.path.join(current_dir, 'news_classifier_model.pkl')
    with open(classifier_path, 'wb') as f:
        pickle.dump(classifier, f)
    print(f"✅ Classifier saved to: {classifier_path}")
    
    # Save vectorizer  
    vectorizer_path = os.path.join(current_dir, 'tfidf_vectorizer.pkl')
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"✅ Vectorizer saved to: {vectorizer_path}")
    
    # Save metadata
    metadata = {
        'model_type': 'Logistic Regression + TF-IDF',
        'accuracy': accuracy,
        'classes': list(classifier.classes_),
        'training_date': datetime.now().isoformat(),
        'feature_count': len(vectorizer.get_feature_names_out())
    }
    
    metadata_path = os.path.join(current_dir, 'model_metadata.pkl')
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✅ Metadata saved to: {metadata_path}")


def main():
    """
    Main training pipeline execution.
    """
    print("🚀 Starting News Classification Model Training")
    print("=" * 50)
    
    try:
        # Step 1: Fetch training data
        df = fetch_user_data()
        
        # Step 2: Train model
        classifier, vectorizer, accuracy = train_classification_model(df)
        
        # Step 3: Save model artifacts
        save_model_artifacts(classifier, vectorizer, accuracy)
        
        print(f"\n🎉 Training completed successfully!")
        print(f"📊 Final model accuracy: {accuracy:.3f}")
        print(f"🔧 Model ready for deployment in backend")
        
        # Quick test of the trained model
        print(f"\n🧪 Quick model test:")
        test_texts = [
            "Fire broke out in shopping mall",
            "Heavy rain expected tomorrow", 
            "Robbery reported at bank",
            "Free health checkup camp announced"
        ]
        
        for text in test_texts:
            processed_text = preprocess_text(text)
            vectorized_text = vectorizer.transform([processed_text])
            prediction = classifier.predict(vectorized_text)[0]
            confidence = max(classifier.predict_proba(vectorized_text)[0])
            print(f"  '{text}' → {prediction} (confidence: {confidence:.3f})")
            
    except Exception as e:
        print(f"❌ Error during training: {str(e)}")
        raise


if __name__ == "__main__":
    main()