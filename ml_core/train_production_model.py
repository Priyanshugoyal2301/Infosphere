"""
Train ATIE with Real Dataset
===========================
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os
from datetime import datetime

def load_real_dataset():
    """Load the actual fake news dataset"""
    print("📥 Loading real dataset...")
    
    df = pd.read_csv('datasets/news_articles.csv')
    print(f"Dataset loaded: {len(df)} samples")
    print(f"Columns: {df.columns.tolist()}")
    
    # Clean data
    df = df.dropna(subset=['text', 'label'])
    
    # Check unique labels
    print(f"Unique labels: {df['label'].unique()}")
    print(f"Label distribution:")
    print(df['label'].value_counts())
    
    # Convert to binary (Real=0, Fake=1)
    df['binary_label'] = df['label'].apply(lambda x: 1 if 'fake' in str(x).lower() else 0)
    
    print(f"Binary label distribution:")
    print(df['binary_label'].value_counts())
    
    return df

def train_production_model(df, test_size=0.2):
    """Train production-ready model with the real dataset"""
    print("\n🚀 Training production model...")
    
    # Prepare data
    X = df['text'].astype(str)
    y = df['binary_label']
    
    print(f"Training on {len(df)} samples")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=42
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Create TF-IDF vectorizer
    print("🔤 Creating TF-IDF vectors...")
    vectorizer = TfidfVectorizer(
        max_features=20000,
        stop_words='english',
        ngram_range=(1, 3),
        min_df=2,
        max_df=0.95
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print(f"Feature matrix shape: {X_train_vec.shape}")
    
    # Train multiple models and choose best
    models = {
        'Naive Bayes': MultinomialNB(alpha=0.1),
        'Logistic Regression': LogisticRegression(max_iter=1000, C=1.0)
    }
    
    best_model = None
    best_accuracy = 0
    best_name = ""
    
    for name, model in models.items():
        print(f"\n📈 Training {name}...")
        model.fit(X_train_vec, y_train)
        
        # Predict and evaluate
        y_pred = model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"{name} Accuracy: {accuracy:.4f}")
        
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_name = name
    
    print(f"\n🏆 Best model: {best_name} (Accuracy: {best_accuracy:.4f})")
    
    # Detailed evaluation of best model
    y_pred_best = best_model.predict(X_test_vec)
    print("\n📊 Detailed Classification Report:")
    print(classification_report(y_test, y_pred_best, target_names=['Real', 'Fake']))
    
    print("\n🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred_best)
    print(cm)
    
    # Save models
    print("\n💾 Saving trained models...")
    os.makedirs('models', exist_ok=True)
    
    with open('models/production_classifier.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    
    with open('models/production_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    # Save model info
    model_info = {
        'model_name': best_name,
        'accuracy': best_accuracy,
        'training_date': datetime.now().isoformat(),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'feature_count': X_train_vec.shape[1]
    }
    
    with open('models/model_info.pkl', 'wb') as f:
        pickle.dump(model_info, f)
    
    return best_model, vectorizer, best_accuracy

def test_trained_model():
    """Test the trained model with sample texts"""
    print("\n🧪 Testing trained model...")
    
    # Load trained model
    with open('models/production_classifier.pkl', 'rb') as f:
        model = pickle.load(f)
    
    with open('models/production_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    
    # Test samples
    test_texts = [
        "BREAKING: Scientists discover that water is actually harmful to humans!",
        "The local weather forecast indicates partly cloudy skies with temperatures reaching 75 degrees.",
        "You won't believe this SHOCKING discovery that doctors don't want you to know!",
        "The city council announced new policies for public transportation improvements.",
        "EXCLUSIVE: Politicians use this one weird trick to steal your money!"
    ]
    
    for text in test_texts:
        # Vectorize
        text_vec = vectorizer.transform([text])
        
        # Predict
        prediction = model.predict(text_vec)[0]
        probability = model.predict_proba(text_vec)[0]
        
        label = "FAKE" if prediction == 1 else "REAL"
        confidence = max(probability)
        
        print(f"\\nText: {text[:60]}...")
        print(f"Prediction: {label} (confidence: {confidence:.3f})")
        print(f"Fake probability: {probability[1]:.3f}")

def main():
    """Main training function"""
    print("🎯 ATIE Production Model Training")
    print("="*50)
    
    try:
        # Load dataset
        df = load_real_dataset()
        
        if len(df) < 100:
            print("❌ Dataset too small. Need at least 100 samples.")
            return False
        
        # Train model
        model, vectorizer, accuracy = train_production_model(df)
        
        print(f"\\n✅ Training completed successfully!")
        print(f"📊 Final accuracy: {accuracy:.4f}")
        
        # Test the model
        test_trained_model()
        
        print(f"\\n🎉 Production model ready!")
        print(f"💾 Models saved in: ./models/")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\\n✅ ATIE production model trained successfully!")
    else:
        print("\\n❌ Training failed.")