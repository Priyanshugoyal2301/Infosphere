"""
Enhanced ATIE Service with ML Model Training Capabilities
=======================================================

This module provides training capabilities for the BERT-based fake news classifier
using publicly available datasets.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import logging
import requests
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)

class FakeNewsDataset(Dataset):
    """Custom dataset for fake news classification"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class ATIEModelTrainer:
    """Enhanced ATIE Model Training System"""
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = None
        self.data_dir = Path("ml_core/datasets")
        self.model_dir = Path("ml_core/models")
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def download_liar_dataset(self) -> bool:
        """Download and prepare the LIAR dataset"""
        try:
            logger.info("📥 Downloading LIAR dataset...")
            
            # LIAR dataset URLs (simplified version)
            urls = {
                'train': 'https://raw.githubusercontent.com/thiagocastroferreira/fake_news_detection/master/data/liar/train.tsv',
                'test': 'https://raw.githubusercontent.com/thiagocastroferreira/fake_news_detection/master/data/liar/test.tsv',
                'valid': 'https://raw.githubusercontent.com/thiagocastroferreira/fake_news_detection/master/data/liar/valid.tsv'
            }
            
            for split, url in urls.items():
                file_path = self.data_dir / f"liar_{split}.tsv"
                if not file_path.exists():
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        logger.info(f"✅ Downloaded LIAR {split} set")
                    else:
                        logger.warning(f"⚠️ Could not download LIAR {split} set")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download LIAR dataset: {e}")
            return False
    
    def create_sample_dataset(self) -> Tuple[List[str], List[int]]:
        """Create a sample dataset for training if no external dataset is available"""
        
        fake_news_samples = [
            "BREAKING: Scientists discover that drinking water is actually harmful to humans and recommend switching to soda immediately",
            "SHOCKING: Local politician caught on camera eating pizza with a fork - impeachment proceedings to begin",
            "EXCLUSIVE: New study proves that looking at the sun directly improves eyesight by 300%",
            "URGENT: Government secretly replacing all birds with robot surveillance drones",
            "ALERT: Doctors hate this one weird trick that will make you immortal overnight",
            "BREAKING: Social media company admits to reading your thoughts through your phone screen",
            "SHOCKING: Eating ice cream for breakfast proven to be the healthiest meal of the day",
            "EXCLUSIVE: Local man discovers that gravity is just a government conspiracy",
            "URGENT: New law requires everyone to wear their clothes backwards starting next month",
            "ALERT: Scientists confirm that the earth is actually flat and shaped like a pizza slice"
        ]
        
        real_news_samples = [
            "The weather forecast for tomorrow indicates partly cloudy skies with temperatures reaching 75 degrees Fahrenheit",
            "Local city council approved the budget for the new public library construction project",
            "Stock market showed mixed results today with technology shares gaining 2.3 percent",
            "University researchers published a new study on renewable energy efficiency in solar panels",
            "Traffic delays are expected on Highway 101 due to scheduled maintenance work this weekend",
            "The annual charity fundraiser raised over $50,000 for local homeless shelters this year",
            "New restaurant opens downtown featuring locally sourced ingredients and seasonal menus",
            "School district announces extended summer learning programs for elementary students",
            "Public health officials recommend flu vaccinations as winter season approaches",
            "Local museum exhibits feature artwork from regional artists throughout the month"
        ]
        
        # Create balanced dataset
        texts = fake_news_samples + real_news_samples
        labels = [1] * len(fake_news_samples) + [0] * len(real_news_samples)  # 1=fake, 0=real
        
        # Shuffle the data
        combined = list(zip(texts, labels))
        np.random.shuffle(combined)
        texts, labels = zip(*combined)
        
        return list(texts), list(labels)
    
    def load_liar_dataset(self) -> Optional[Tuple[List[str], List[int]]]:
        """Load and process LIAR dataset"""
        try:
            train_file = self.data_dir / "liar_train.tsv"
            if not train_file.exists():
                logger.warning("LIAR dataset not found, using sample data")
                return None
            
            # Load LIAR dataset
            df = pd.read_csv(train_file, sep='\t', header=None)
            
            # LIAR format: [label, statement, subject, speaker, ...]
            # Labels: pants-fire, false, barely-true, half-true, mostly-true, true
            # We'll convert to binary: false-ish vs true-ish
            
            false_labels = ['pants-fire', 'false', 'barely-true']
            texts = df[1].astype(str).tolist()  # statement column
            labels = [1 if label in false_labels else 0 for label in df[0]]  # binary labels
            
            logger.info(f"✅ Loaded LIAR dataset: {len(texts)} samples")
            return texts, labels
            
        except Exception as e:
            logger.error(f"❌ Failed to load LIAR dataset: {e}")
            return None
    
    def prepare_training_data(self) -> Tuple[List[str], List[int]]:
        """Prepare training data from available sources"""
        
        # Try to load LIAR dataset first
        data = self.load_liar_dataset()
        if data is None:
            # Fall back to sample dataset
            logger.info("Using sample dataset for training")
            data = self.create_sample_dataset()
        
        return data
    
    def train_model(self, epochs: int = 3, batch_size: int = 8, learning_rate: float = 2e-5) -> bool:
        """Train the BERT model for fake news detection"""
        
        try:
            logger.info("🚀 Starting ATIE model training...")
            
            # Prepare data
            texts, labels = self.prepare_training_data()
            
            # Split data
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            logger.info(f"📊 Training samples: {len(train_texts)}, Validation: {len(val_texts)}")
            
            # Initialize model
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name, 
                num_labels=2
            )
            
            # Create datasets
            train_dataset = FakeNewsDataset(train_texts, train_labels, self.tokenizer)
            val_dataset = FakeNewsDataset(val_texts, val_labels, self.tokenizer)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=str(self.model_dir / "atie_checkpoints"),
                num_train_epochs=epochs,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                warmup_steps=100,
                weight_decay=0.01,
                learning_rate=learning_rate,
                logging_dir=str(self.model_dir / "logs"),
                logging_steps=10,
                eval_strategy="epoch",  # Updated parameter name
                save_strategy="epoch",
                load_best_model_at_end=True,
                metric_for_best_model="eval_accuracy",
                greater_is_better=True,
                save_total_limit=3,
            )
            
            # Trainer with evaluation metrics
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                compute_metrics=self.compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
            )
            
            # Train the model
            logger.info("🔥 Training in progress...")
            trainer.train()
            
            # Save the model
            model_path = self.model_dir / "atie_fine_tuned"
            trainer.save_model(str(model_path))
            self.tokenizer.save_pretrained(str(model_path))
            
            logger.info(f"✅ Model training completed and saved to {model_path}")
            
            # Evaluate final model
            eval_results = trainer.evaluate()
            logger.info(f"📊 Final evaluation results: {eval_results}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            return False
    
    def compute_metrics(self, eval_pred):
        """Compute evaluation metrics"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='binary')
        accuracy = accuracy_score(labels, predictions)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
        }
    
    def test_trained_model(self, test_texts: List[str]) -> List[Dict]:
        """Test the trained model on sample texts"""
        
        if self.model is None:
            # Try to load existing model
            model_path = self.model_dir / "atie_fine_tuned"
            if model_path.exists():
                self.model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
                self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            else:
                logger.error("No trained model found!")
                return []
        
        results = []
        self.model.eval()
        
        with torch.no_grad():
            for text in test_texts:
                inputs = self.tokenizer(
                    text, 
                    return_tensors='pt', 
                    truncation=True, 
                    padding='max_length',
                    max_length=512
                )
                
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
                
                fake_prob = probabilities[0][1].item()
                real_prob = probabilities[0][0].item()
                
                results.append({
                    'text': text,
                    'fake_probability': fake_prob,
                    'real_probability': real_prob,
                    'prediction': 'fake' if fake_prob > 0.5 else 'real',
                    'confidence': max(fake_prob, real_prob)
                })
        
        return results

# Training script function
def train_atie_model():
    """Main training function"""
    
    print("🎯 ATIE Model Training System")
    print("=" * 50)
    
    trainer = ATIEModelTrainer()
    
    # Option 1: Download LIAR dataset
    print("\n📥 Attempting to download LIAR dataset...")
    if trainer.download_liar_dataset():
        print("✅ LIAR dataset downloaded successfully!")
    else:
        print("⚠️ Using sample dataset for training")
    
    # Train the model
    print("\n🚀 Starting model training...")
    if trainer.train_model(epochs=2, batch_size=4):
        print("✅ Training completed successfully!")
        
        # Test the model
        test_texts = [
            "BREAKING: Scientists discover water is harmful!",
            "The weather will be sunny tomorrow with 75°F temperature.",
            "SHOCKING: Politicians hate this one weird trick!",
            "Local library announces new opening hours for the community."
        ]
        
        print("\n🧪 Testing trained model:")
        results = trainer.test_trained_model(test_texts)
        
        for result in results:
            print(f"\nText: {result['text'][:60]}...")
            print(f"Prediction: {result['prediction']} (confidence: {result['confidence']:.2f})")
            print(f"Fake probability: {result['fake_probability']:.3f}")
    else:
        print("❌ Training failed!")

if __name__ == "__main__":
    train_atie_model()