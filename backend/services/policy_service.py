"""
AI Policy Sensemaking Service

This service handles:
1. Multilingual sentiment analysis for public comments using XLM-R
2. Automated policy document summarization using BART
3. Real-time public sentiment monitoring
4. Three-point policy summaries for easy consumption
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

logger = logging.getLogger(__name__)

class PolicyService:
    """
    Policy Sensemaking Service for sentiment analysis and summarization.
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sentiment_analyzer = None
        self.summarizer = None
        self.multilingual_analyzer = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize multilingual sentiment analyzer and summarization model."""
        try:
            # Initialize sentiment analysis (multilingual)
            try:
                # Use XLM-RoBERTa for multilingual sentiment (fallback to English model)
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
                    device=0 if torch.cuda.is_available() else -1
                )
            except:
                # Fallback to English sentiment analysis
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=0 if torch.cuda.is_available() else -1
                )
            
            # Initialize summarization (BART)
            try:
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    device=0 if torch.cuda.is_available() else -1,
                    max_length=150,
                    min_length=50,
                    do_sample=False
                )
            except Exception as e:
                logger.warning(f"Could not load BART model: {e}, using fallback")
                # Fallback to smaller model
                self.summarizer = pipeline(
                    "summarization",
                    model="sshleifer/distilbart-cnn-12-6",
                    device=0 if torch.cuda.is_available() else -1,
                    max_length=100,
                    min_length=30,
                    do_sample=False
                )
            
            logger.info("Policy Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Policy Service: {e}")
            # Set to None for rule-based fallback
            self.sentiment_analyzer = None
            self.summarizer = None
    
    async def analyze_sentiment(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Analyze sentiment of public comment text.
        
        Args:
            text: Comment text to analyze
            language: Language code (en, es, fr, etc.)
            
        Returns:
            Sentiment scores (positive, negative, neutral)
        """
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            if self.sentiment_analyzer and cleaned_text:
                # Use AI model for sentiment analysis
                result = self.sentiment_analyzer(cleaned_text)
                
                # Convert model output to standardized format
                sentiment_scores = self._normalize_sentiment_scores(result)
                
                return {
                    "positive": sentiment_scores["positive"],
                    "negative": sentiment_scores["negative"],
                    "neutral": sentiment_scores["neutral"],
                    "dominant_sentiment": max(sentiment_scores, key=sentiment_scores.get),
                    "confidence": sentiment_scores.get("confidence", 0.5),
                    "language": language,
                    "method": "ai_model"
                }
            else:
                # Fallback to rule-based sentiment analysis
                return await self._rule_based_sentiment(cleaned_text, language)
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "positive": 0.33,
                "negative": 0.33,
                "neutral": 0.34,
                "dominant_sentiment": "neutral",
                "confidence": 0.3,
                "error": str(e),
                "method": "error_fallback"
            }
    
    async def generate_summary(self, policy_text: str, max_points: int = 3) -> Dict[str, Any]:
        """
        Generate AI-powered summary of policy document.
        
        Args:
            policy_text: Full policy document text
            max_points: Maximum number of summary points (default: 3)
            
        Returns:
            Summary with key points and metadata
        """
        try:
            # Preprocess policy text
            cleaned_text = self._preprocess_policy_text(policy_text)
            
            if self.summarizer and len(cleaned_text) > 100:
                # Use AI model for summarization
                
                # Split long documents into chunks for better processing
                chunks = self._split_into_chunks(cleaned_text, max_chunk_size=1024)
                
                summaries = []
                for chunk in chunks:
                    try:
                        result = self.summarizer(chunk)
                        if result and len(result) > 0:
                            summaries.append(result[0]['summary_text'])
                    except Exception as e:
                        logger.warning(f"Error summarizing chunk: {e}")
                        continue
                
                if summaries:
                    # Combine and refine summaries
                    combined_summary = " ".join(summaries)
                    
                    # Extract key points
                    key_points = self._extract_key_points(combined_summary, max_points)
                    
                    return {
                        "summary": combined_summary,
                        "key_points": key_points,
                        "method": "ai_model",
                        "chunks_processed": len(chunks),
                        "original_length": len(policy_text),
                        "summary_length": len(combined_summary),
                        "compression_ratio": len(combined_summary) / len(policy_text)
                    }
                else:
                    # Fallback if AI summarization fails
                    return await self._rule_based_summary(cleaned_text, max_points)
            else:
                # Fallback to rule-based summarization
                return await self._rule_based_summary(cleaned_text, max_points)
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "summary": "Error generating summary",
                "key_points": ["Summary generation failed"],
                "error": str(e),
                "method": "error_fallback"
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Limit length for model processing
        return text[:500]  # Most models have token limits
    
    def _preprocess_policy_text(self, text: str) -> str:
        """Preprocess policy document text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common policy document artifacts
        text = re.sub(r'\[Page \d+\]', '', text)
        text = re.sub(r'Section \d+\.?\d*', '', text)
        text = re.sub(r'Article \d+\.?\d*', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        
        return text
    
    def _split_into_chunks(self, text: str, max_chunk_size: int = 1024) -> List[str]:
        """Split long text into chunks for processing."""
        if len(text) <= max_chunk_size:
            return [text]
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence would exceed limit, start new chunk
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _normalize_sentiment_scores(self, model_result: List[Dict]) -> Dict[str, float]:
        """Convert model output to normalized sentiment scores."""
        if not model_result:
            return {"positive": 0.33, "negative": 0.33, "neutral": 0.34}
        
        result = model_result[0] if isinstance(model_result, list) else model_result
        label = result.get('label', '').lower()
        score = result.get('score', 0.5)
        
        # Map different model outputs to standard format
        if 'positive' in label or 'pos' in label:
            return {
                "positive": score,
                "negative": (1 - score) / 2,
                "neutral": (1 - score) / 2,
                "confidence": score
            }
        elif 'negative' in label or 'neg' in label:
            return {
                "positive": (1 - score) / 2,
                "negative": score,
                "neutral": (1 - score) / 2,
                "confidence": score
            }
        else:  # neutral
            return {
                "positive": (1 - score) / 2,
                "negative": (1 - score) / 2,
                "neutral": score,
                "confidence": score
            }
    
    async def _rule_based_sentiment(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Fallback rule-based sentiment analysis."""
        if not text:
            return {"positive": 0.33, "negative": 0.33, "neutral": 0.34, "method": "rule_based_empty"}
        
        # Simple keyword-based sentiment
        positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "like", "appreciate", "support", "agree", "positive",
            "happy", "pleased", "satisfied", "approve"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "horrible", "hate", "dislike",
            "disagree", "oppose", "angry", "frustrated", "disappointed",
            "wrong", "unfair", "poor", "against", "negative"
        ]
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return {
                "positive": 0.33,
                "negative": 0.33,
                "neutral": 0.34,
                "dominant_sentiment": "neutral",
                "confidence": 0.3,
                "method": "rule_based"
            }
        
        positive_ratio = positive_count / total_sentiment_words
        negative_ratio = negative_count / total_sentiment_words
        neutral_ratio = max(0, 1 - positive_ratio - negative_ratio)
        
        # Normalize to ensure they sum to 1
        total = positive_ratio + negative_ratio + neutral_ratio
        if total > 0:
            positive_ratio /= total
            negative_ratio /= total
            neutral_ratio /= total
        
        dominant = "positive" if positive_ratio > max(negative_ratio, neutral_ratio) else \
                  "negative" if negative_ratio > neutral_ratio else "neutral"
        
        return {
            "positive": positive_ratio,
            "negative": negative_ratio,
            "neutral": neutral_ratio,
            "dominant_sentiment": dominant,
            "confidence": 0.6,
            "method": "rule_based"
        }
    
    async def _rule_based_summary(self, text: str, max_points: int = 3) -> Dict[str, Any]:
        """Fallback rule-based summarization."""
        if not text:
            return {
                "summary": "No content to summarize",
                "key_points": ["Document appears to be empty"],
                "method": "rule_based_empty"
            }
        
        # Extract sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) == 0:
            return {
                "summary": "Could not extract meaningful content",
                "key_points": ["Document format not supported for summarization"],
                "method": "rule_based_error"
            }
        
        # Simple extractive summarization - take first few sentences and some middle ones
        key_sentences = []
        
        if len(sentences) <= max_points:
            key_sentences = sentences
        else:
            # Take first sentence, last sentence, and some from middle
            key_sentences.append(sentences[0])
            
            if max_points > 2:
                mid_indices = np.linspace(1, len(sentences)-2, max_points-2, dtype=int)
                for idx in mid_indices:
                    if idx < len(sentences):
                        key_sentences.append(sentences[idx])
            
            if len(sentences) > 1:
                key_sentences.append(sentences[-1])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_sentences = []
        for sentence in key_sentences:
            if sentence not in seen and len(sentence.strip()) > 10:
                seen.add(sentence)
                unique_sentences.append(sentence.strip())
        
        summary = " ".join(unique_sentences)
        
        return {
            "summary": summary,
            "key_points": unique_sentences[:max_points],
            "method": "rule_based",
            "original_sentences": len(sentences),
            "summary_sentences": len(unique_sentences)
        }
    
    def _extract_key_points(self, summary_text: str, max_points: int = 3) -> List[str]:
        """Extract key points from summary text."""
        # Split by sentences and clean
        sentences = re.split(r'[.!?]+', summary_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        
        # Return up to max_points sentences
        return sentences[:max_points]
    
    async def get_sentiment_trends(self, policy_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get sentiment trends for a policy over time.
        
        Placeholder implementation - would query database in production.
        """
        # Placeholder data
        return {
            "policy_id": policy_id,
            "period_days": days,
            "trend_data": [],
            "overall_sentiment": {
                "positive": 0.4,
                "negative": 0.3,
                "neutral": 0.3
            },
            "sentiment_change": {
                "direction": "stable",
                "magnitude": 0.02
            }
        }