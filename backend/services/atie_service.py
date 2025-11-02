"""
AI Trust and Integrity Engine (ATIE) Service
============================================

The ATIE provides comprehensive textual integrity analysis through:
1. BERT-based fake news classification
2. Cross-verification against trusted sources
3. Redis caching for performance optimization
4. Real-time Trust Score generation
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import redis
import requests
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
    BertTokenizer,
    BertForSequenceClassification
)
import torch

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrustedSourcesDB:
    """Database of trusted news sources for cross-verification"""
    
    def __init__(self):
        self.trusted_sources = {
            # Major news outlets with high credibility scores
            "reuters.com": {"credibility": 95, "bias": "center", "factual": "very_high"},
            "apnews.com": {"credibility": 94, "bias": "center", "factual": "very_high"},
            "bbc.com": {"credibility": 92, "bias": "center-left", "factual": "very_high"},
            "npr.org": {"credibility": 91, "bias": "center-left", "factual": "very_high"},
            "wsj.com": {"credibility": 90, "bias": "center-right", "factual": "very_high"},
            "economist.com": {"credibility": 90, "bias": "center", "factual": "very_high"},
            "nytimes.com": {"credibility": 88, "bias": "center-left", "factual": "high"},
            "washingtonpost.com": {"credibility": 87, "bias": "center-left", "factual": "high"},
            "cnn.com": {"credibility": 82, "bias": "left", "factual": "high"},
            "foxnews.com": {"credibility": 75, "bias": "right", "factual": "mixed"},
            # Government and institutional sources
            "who.int": {"credibility": 98, "bias": "center", "factual": "very_high"},
            "cdc.gov": {"credibility": 97, "bias": "center", "factual": "very_high"},
            "gov.uk": {"credibility": 96, "bias": "center", "factual": "very_high"},
            "europa.eu": {"credibility": 95, "bias": "center", "factual": "very_high"},
        }
        
        # News API endpoints for real-time verification
        self.news_apis = {
            "newsapi": "https://newsapi.org/v2/everything",
            "mediastack": "https://api.mediastack.com/v1/news",
            "guardian": "https://content.guardianapis.com/search"
        }
    
    async def search_trusted_sources(self, query: str, limit: int = 10) -> List[Dict]:
        """Search trusted sources for similar articles"""
        try:
            # Simulate API calls to trusted sources
            # In production, implement actual API calls
            articles = []
            
            # Mock trusted source articles for development
            mock_articles = [
                {
                    "source": "reuters.com",
                    "title": f"Verified article about {query}",
                    "content": f"This is a verified article discussing {query} from a trusted source.",
                    "url": f"https://reuters.com/article/{hashlib.md5(query.encode()).hexdigest()[:8]}",
                    "published_at": datetime.now().isoformat(),
                    "credibility_score": 95
                },
                {
                    "source": "bbc.com",
                    "title": f"BBC coverage of {query}",
                    "content": f"BBC's comprehensive coverage of {query} with factual reporting.",
                    "url": f"https://bbc.com/news/{hashlib.md5(query.encode()).hexdigest()[:8]}",
                    "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "credibility_score": 92
                }
            ]
            
            return mock_articles[:limit]
            
        except Exception as e:
            logger.error(f"Error searching trusted sources: {e}")
            return []


class TextualIntegrityAnalyzer:
    """BERT-based textual fake news classification and integrity analysis"""
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.sentiment_analyzer = None
        self.sentence_transformer = None
        self._load_models()
        
        # Sensationalism patterns
        self.sensational_patterns = [
            r'\b(BREAKING|URGENT|SHOCKING|EXCLUSIVE|BOMBSHELL)\b',
            r'[!]{2,}',  # Multiple exclamation marks
            r'\b(MUST READ|DON\'T MISS|UNBELIEVABLE)\b',
            r'\b(SCANDAL|OUTRAGE|DISASTER|CRISIS)\b',
        ]
        
        # Bias indicators
        self.bias_patterns = {
            'left_bias': [r'\b(progressive|liberal|woke|inclusive)\b'],
            'right_bias': [r'\b(conservative|traditional|patriotic|freedom)\b'],
            'emotional': [r'\b(outraged|furious|devastated|thrilled)\b']
        }
        
        # Production model integration
        self.use_production_model = False
    
    def _load_models(self):
        """Load BERT model and supporting models with robust fallback"""
        try:
            logger.info("🔄 Loading BERT model...")
            # Load BERT for fake news classification
            self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
            # In production, load fine-tuned model on fake news data
            self.model = BertForSequenceClassification.from_pretrained(
                self.model_name, 
                num_labels=2  # Real vs Fake
            )
            
            logger.info("🔄 Loading sentiment analyzer...")
            try:
                # Load sentiment analyzer
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
            except Exception as sentiment_error:
                logger.warning(f"⚠️ Failed to load RoBERTa sentiment model, using default: {sentiment_error}")
                self.sentiment_analyzer = pipeline("sentiment-analysis")
            
            logger.info("🔄 Loading sentence transformer...")
            try:
                # Load sentence transformer for similarity
                self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as st_error:
                logger.warning(f"⚠️ Failed to load sentence transformer: {st_error}")
                self.sentence_transformer = None
            
            logger.info("✅ Textual integrity models loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            logger.info("🔄 Using fallback mock analysis")
            # Fallback to mock analysis
            self._initialize_mock_models()
    
    def _initialize_mock_models(self):
        """Initialize mock models when real models fail to load"""
        self.model = None
        self.tokenizer = None
        self.sentiment_analyzer = None
        self.sentence_transformer = None
        logger.info("✅ Mock models initialized")
    
    def analyze_sensationalism(self, text: str) -> Dict[str, Union[float, List[str]]]:
        """Detect sensationalist language patterns"""
        sensational_score = 0
        detected_patterns = []
        
        for pattern in self.sensational_patterns:
            matches = re.findall(pattern, text.upper())
            if matches:
                sensational_score += len(matches) * 10
                detected_patterns.extend(matches)
        
        # Normalize score to 0-100
        sensational_score = min(sensational_score, 100)
        
        return {
            "sensationalism_score": sensational_score,
            "detected_patterns": detected_patterns,
            "is_sensational": sensational_score > 30
        }
    
    def analyze_bias(self, text: str) -> Dict[str, Union[str, float, List[str]]]:
        """Detect political and emotional bias"""
        bias_scores = {}
        detected_bias = []
        
        for bias_type, patterns in self.bias_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text.lower())
                score += len(matches) * 5
                if matches:
                    detected_bias.extend(matches)
            bias_scores[bias_type] = min(score, 100)
        
        # Determine dominant bias
        dominant_bias = max(bias_scores, key=bias_scores.get) if any(bias_scores.values()) else "neutral"
        overall_bias_score = max(bias_scores.values()) if bias_scores.values() else 0
        
        return {
            "bias_type": dominant_bias,
            "bias_score": overall_bias_score,
            "bias_breakdown": bias_scores,
            "detected_indicators": detected_bias
        }
    
    def analyze_source_credibility(self, text: str, source_url: str = None) -> Dict[str, Union[float, str]]:
        """Analyze source credibility indicators"""
        credibility_score = 50  # Base score
        indicators = []
        
        # Check for source citations
        citation_patterns = [
            r'according to [a-zA-Z\s]+',
            r'reported by [a-zA-Z\s]+',
            r'source: [a-zA-Z\s]+',
            r'\[citation needed\]'
        ]
        
        citations_found = 0
        for pattern in citation_patterns:
            citations_found += len(re.findall(pattern, text.lower()))
        
        if citations_found > 0:
            credibility_score += min(citations_found * 10, 30)
            indicators.append(f"Found {citations_found} source citations")
        
        # Check for first-person reporting
        if re.search(r'\b(I witnessed|I saw|I heard)\b', text):
            credibility_score += 10
            indicators.append("First-person reporting detected")
        
        # Check for dates and specific details
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b|\b\w+ \d{1,2}, \d{4}\b'
        if re.search(date_pattern, text):
            credibility_score += 5
            indicators.append("Specific dates provided")
        
        return {
            "credibility_score": min(credibility_score, 100),
            "indicators": indicators
        }
    
    def set_production_model(self, model, vectorizer):
        """Set the trained production model"""
        self.production_model = model
        self.production_vectorizer = vectorizer
        self.use_production_model = True
        logger.info("✅ Production model activated for fake news classification")
    
    def classify_with_production_model(self, text: str) -> Dict[str, Union[float, str]]:
        """Use trained production model for classification"""
        try:
            if not (self.production_model and self.production_vectorizer):
                return self._rule_based_classification(text)
            
            # Vectorize the text
            text_vector = self.production_vectorizer.transform([text])
            
            # Get prediction
            prediction = self.production_model.predict(text_vector)[0]
            probabilities = self.production_model.predict_proba(text_vector)[0]
            
            # Extract probabilities (0=Real, 1=Fake)
            real_prob = probabilities[0]
            fake_prob = probabilities[1]
            
            authenticity_score = real_prob * 100
            confidence = max(fake_prob, real_prob) * 100
            
            return {
                "authenticity_score": authenticity_score,
                "fake_probability": fake_prob * 100,
                "real_probability": real_prob * 100,
                "confidence": confidence,
                "classification": "authentic" if prediction == 0 else "suspicious",
                "model_used": "production_trained_model"
            }
            
        except Exception as e:
            logger.error(f"Error in production model classification: {e}")
            return self._rule_based_classification(text)
    
    async def classify_fake_news(self, text: str) -> Dict[str, Union[float, str]]:
        """Enhanced fake news classification with production model priority"""
        try:
            # Use production model if available
            if self.use_production_model and hasattr(self, 'production_model') and self.production_model:
                return self.classify_with_production_model(text)
            
            # Fallback to BERT model
            if self.model is None or self.tokenizer is None:
                return self._rule_based_classification(text)
            
            # Tokenize text
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Get model prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            # Extract probabilities
            fake_prob = predictions[0][1].item()  # Probability of being fake
            real_prob = predictions[0][0].item()  # Probability of being real
            
            authenticity_score = real_prob * 100
            confidence = max(fake_prob, real_prob)
            
            return {
                "authenticity_score": authenticity_score,
                "fake_probability": fake_prob * 100,
                "real_probability": real_prob * 100,
                "confidence": confidence * 100,
                "classification": "authentic" if authenticity_score > 50 else "suspicious",
                "model_used": "bert_base"
            }
            
        except Exception as e:
            logger.error(f"Error in classification: {e}")
            return self._rule_based_classification(text)
    
    def _rule_based_classification(self, text: str) -> Dict[str, Union[float, str]]:
        """Fallback rule-based classification when BERT is unavailable"""
        score = 50  # Base score
        
        # Check for red flags
        red_flags = [
            r'\b(fake news|hoax|conspiracy|cover-up)\b',
            r'\b(they don\'t want you to know|hidden truth|secret)\b',
            r'\b(shocking revelation|exposé|leaked)\b'
        ]
        
        for pattern in red_flags:
            if re.search(pattern, text.lower()):
                score -= 20
        
        # Check for credibility indicators
        credible_indicators = [
            r'\b(study shows|research indicates|data suggests)\b',
            r'\b(professor|dr\.|expert|scientist)\b',
            r'\b(university|institute|organization)\b'
        ]
        
        for pattern in credible_indicators:
            if re.search(pattern, text.lower()):
                score += 15
        
        score = max(0, min(100, score))
        
        return {
            "authenticity_score": score,
            "fake_probability": 100 - score,
            "real_probability": score,
            "confidence": 70,  # Moderate confidence for rule-based
            "classification": "authentic" if score > 50 else "suspicious"
        }
    
    async def analyze_text_integrity(self, text: str, source_url: str = None) -> Dict:
        """Comprehensive textual integrity analysis"""
        start_time = time.time()
        
        # Run all analyses
        fake_news_result = await self.classify_fake_news(text)
        sensationalism = self.analyze_sensationalism(text)
        bias_analysis = self.analyze_bias(text)
        source_credibility = self.analyze_source_credibility(text, source_url)
        
        # Calculate composite textual integrity score
        weights = {
            'authenticity': 0.4,    # 40% - Core fake news classification
            'credibility': 0.25,    # 25% - Source credibility
            'sensationalism': 0.2,  # 20% - Sensationalism (inverse)
            'bias': 0.15           # 15% - Bias (inverse)
        }
        
        authenticity_component = fake_news_result['authenticity_score'] * weights['authenticity']
        credibility_component = source_credibility['credibility_score'] * weights['credibility']
        sensationalism_component = (100 - sensationalism['sensationalism_score']) * weights['sensationalism']
        bias_component = (100 - bias_analysis['bias_score']) * weights['bias']
        
        textual_integrity_score = (
            authenticity_component + 
            credibility_component + 
            sensationalism_component + 
            bias_component
        )
        
        analysis_time = time.time() - start_time
        
        return {
            "textual_integrity_score": round(textual_integrity_score, 2),
            "components": {
                "fake_news_classification": fake_news_result,
                "sensationalism_analysis": sensationalism,
                "bias_analysis": bias_analysis,
                "source_credibility": source_credibility
            },
            "metadata": {
                "analysis_time": analysis_time,
                "model_used": self.model_name,
                "timestamp": datetime.now().isoformat()
            }
        }


class CrossVerificationSystem:
    """NLP-based cross-verification against trusted sources"""
    
    def __init__(self, trusted_db: TrustedSourcesDB, sentence_transformer):
        self.trusted_db = trusted_db
        self.sentence_transformer = sentence_transformer
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def extract_key_claims(self, text: str) -> List[str]:
        """Extract key factual claims from text"""
        sentences = re.split(r'[.!?]+', text)
        
        # Filter for factual-sounding sentences
        factual_patterns = [
            r'\b\d+%\b',  # Percentages
            r'\b\d+,?\d*\b',  # Numbers
            r'\b(said|reported|confirmed|denied|announced)\b',  # Attribution verbs
            r'\b(according to|sources say|officials)\b'  # Source indicators
        ]
        
        key_claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Minimum length
                for pattern in factual_patterns:
                    if re.search(pattern, sentence.lower()):
                        key_claims.append(sentence)
                        break
        
        return key_claims[:5]  # Return top 5 claims
    
    async def verify_claims(self, claims: List[str]) -> Dict:
        """Verify claims against trusted sources"""
        verification_results = []
        
        for claim in claims:
            # Search for similar content in trusted sources
            similar_articles = await self.trusted_db.search_trusted_sources(claim)
            
            if not similar_articles:
                verification_results.append({
                    "claim": claim,
                    "verification_status": "unverified",
                    "confidence": 0,
                    "supporting_sources": []
                })
                continue
            
            # Calculate semantic similarity
            claim_embedding = self.sentence_transformer.encode([claim])
            similarities = []
            
            for article in similar_articles:
                article_text = f"{article['title']} {article['content']}"
                article_embedding = self.sentence_transformer.encode([article_text])
                similarity = cosine_similarity(claim_embedding, article_embedding)[0][0]
                similarities.append(similarity)
            
            max_similarity = max(similarities) if similarities else 0
            
            # Determine verification status
            if max_similarity > 0.8:
                status = "verified"
                confidence = min(95, max_similarity * 100)
            elif max_similarity > 0.6:
                status = "partially_verified"
                confidence = min(75, max_similarity * 100)
            else:
                status = "contradicted"
                confidence = min(60, (1 - max_similarity) * 100)
            
            verification_results.append({
                "claim": claim,
                "verification_status": status,
                "confidence": round(confidence, 2),
                "similarity_score": round(max_similarity, 3),
                "supporting_sources": [
                    {
                        "source": article["source"],
                        "title": article["title"],
                        "url": article["url"],
                        "credibility": article["credibility_score"]
                    }
                    for article in similar_articles[:3]
                ]
            })
        
        return {
            "verified_claims": len([r for r in verification_results if r["verification_status"] == "verified"]),
            "total_claims": len(claims),
            "overall_verification_score": self._calculate_verification_score(verification_results),
            "claim_details": verification_results
        }
    
    def _calculate_verification_score(self, results: List[Dict]) -> float:
        """Calculate overall verification score"""
        if not results:
            return 0
        
        scores = []
        for result in results:
            if result["verification_status"] == "verified":
                scores.append(result["confidence"])
            elif result["verification_status"] == "partially_verified":
                scores.append(result["confidence"] * 0.7)
            else:  # contradicted or unverified
                scores.append(20)  # Low score for contradicted claims
        
        return sum(scores) / len(scores) if scores else 0


class ATIEService:
    """Main AI Trust and Integrity Engine service"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        # Initialize components
        self.trusted_db = TrustedSourcesDB()
        self.textual_analyzer = TextualIntegrityAnalyzer()
        self.cross_verifier = CrossVerificationSystem(
            self.trusted_db, 
            self.textual_analyzer.sentence_transformer
        )
        
        # Load trained production models
        self.load_production_models()
        
        # Connect production model to textual analyzer
        if hasattr(self, 'production_model') and self.production_model:
            self.textual_analyzer.set_production_model(self.production_model, self.production_vectorizer)
        
        # Initialize Redis cache
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                decode_responses=True
            )
            self.redis_client.ping()  # Test connection
            logger.info("✅ Redis cache connected")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available, using in-memory cache: {e}")
            self.redis_client = None
            self.memory_cache = {}
    
    def load_production_models(self):
        """Load the trained production models"""
        import pickle
        import os
        
        model_dir = "../../ml_core/models"  # Path to trained models
        self.production_model = None
        self.production_vectorizer = None
        
        try:
            # Load trained classifier
            classifier_path = os.path.join(model_dir, "production_classifier.pkl")
            vectorizer_path = os.path.join(model_dir, "production_vectorizer.pkl")
            
            if os.path.exists(classifier_path) and os.path.exists(vectorizer_path):
                with open(classifier_path, 'rb') as f:
                    self.production_model = pickle.load(f)
                
                with open(vectorizer_path, 'rb') as f:
                    self.production_vectorizer = pickle.load(f)
                
                logger.info("✅ Production models loaded successfully")
                
                # Load model info if available
                info_path = os.path.join(model_dir, "model_info.pkl")
                if os.path.exists(info_path):
                    with open(info_path, 'rb') as f:
                        model_info = pickle.load(f)
                        logger.info(f"📊 Model accuracy: {model_info.get('accuracy', 'N/A'):.4f}")
            else:
                logger.warning("⚠️ Production models not found, using fallback models")
        except Exception as e:
            logger.error(f"❌ Failed to load production models: {e}")
            self.production_model = None
            self.production_vectorizer = None
    
    def _get_cache_key(self, text: str, source_url: str = None) -> str:
        """Generate cache key for text analysis"""
        content = text + (source_url or "")
        return f"atie:{hashlib.md5(content.encode()).hexdigest()}"
    
    def _cache_get(self, key: str) -> Optional[Dict]:
        """Get from cache"""
        try:
            if self.redis_client:
                cached = self.redis_client.get(key)
                return json.loads(cached) if cached else None
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def _cache_set(self, key: str, value: Dict, expire: int = 3600):
        """Set cache with expiration"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, expire, json.dumps(value))
            else:
                self.memory_cache[key] = value
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def analyze_textual_integrity(
        self, 
        text: str, 
        source_url: str = None,
        enable_cross_verification: bool = True,
        cache_result: bool = True
    ) -> Dict:
        """
        Comprehensive textual integrity analysis with caching
        
        Args:
            text: Content to analyze
            source_url: Optional source URL
            enable_cross_verification: Enable cross-verification (slower)
            cache_result: Cache the result for faster future lookups
            
        Returns:
            Complete ATIE analysis result
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(text, source_url)
        if cache_result:
            cached_result = self._cache_get(cache_key)
            if cached_result:
                cached_result['metadata']['from_cache'] = True
                cached_result['metadata']['cache_hit_time'] = time.time() - start_time
                logger.info(f"⚡ Cache hit for textual analysis (key: {cache_key[:12]}...)")
                return cached_result
        
        # Perform textual integrity analysis
        textual_analysis = await self.textual_analyzer.analyze_text_integrity(text, source_url)
        
        # Perform cross-verification if enabled
        cross_verification_result = None
        if enable_cross_verification:
            key_claims = self.cross_verifier.extract_key_claims(text)
            if key_claims:
                cross_verification_result = await self.cross_verifier.verify_claims(key_claims)
        
        # Calculate final ATIE Trust Score
        trust_score = self._calculate_atie_trust_score(
            textual_analysis, 
            cross_verification_result
        )
        
        # Compile final result
        result = {
            "atie_trust_score": trust_score,
            "textual_integrity": textual_analysis,
            "cross_verification": cross_verification_result,
            "metadata": {
                "analysis_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat(),
                "cache_key": cache_key,
                "from_cache": False
            }
        }
        
        # Cache result
        if cache_result:
            self._cache_set(cache_key, result)
            logger.info(f"💾 Cached textual analysis result (key: {cache_key[:12]}...)")
        
        return result
    
    def _calculate_atie_trust_score(
        self, 
        textual_analysis: Dict, 
        cross_verification: Optional[Dict]
    ) -> Dict:
        """Calculate composite ATIE Trust Score"""
        
        # Base score from textual integrity
        base_score = textual_analysis['textual_integrity_score']
        
        # Cross-verification bonus/penalty
        if cross_verification:
            verification_score = cross_verification['overall_verification_score']
            verified_ratio = cross_verification['verified_claims'] / max(cross_verification['total_claims'], 1)
            
            # Apply verification adjustment
            if verified_ratio > 0.7:  # Most claims verified
                verification_adjustment = min(15, verification_score * 0.15)
            elif verified_ratio > 0.4:  # Some claims verified
                verification_adjustment = 0
            else:  # Few claims verified
                verification_adjustment = -min(10, (1 - verified_ratio) * 20)
            
            final_score = base_score + verification_adjustment
        else:
            verification_adjustment = 0
            final_score = base_score
        
        # Ensure score is within bounds
        final_score = max(0, min(100, final_score))
        
        # Determine trust level
        if final_score >= 85:
            trust_level = "very_high"
        elif final_score >= 70:
            trust_level = "high"
        elif final_score >= 50:
            trust_level = "moderate"
        elif final_score >= 30:
            trust_level = "low"
        else:
            trust_level = "very_low"
        
        return {
            "score": round(final_score, 2),
            "trust_level": trust_level,
            "components": {
                "textual_integrity_base": base_score,
                "cross_verification_adjustment": verification_adjustment if cross_verification else None
            },
            "recommendation": self._generate_recommendation(final_score, textual_analysis)
        }
    
    def _generate_recommendation(self, score: float, analysis: Dict) -> str:
        """Generate human-readable recommendation"""
        if score >= 85:
            return "Content appears highly trustworthy with strong integrity indicators."
        elif score >= 70:
            return "Content shows good integrity with minor concerns."
        elif score >= 50:
            return "Content integrity is questionable. Verify from additional sources."
        elif score >= 30:
            return "Content shows significant integrity issues. Exercise caution."
        else:
            return "Content appears unreliable. Strong evidence of misinformation."
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        if self.redis_client:
            try:
                info = self.redis_client.info()
                return {
                    "cache_type": "redis",
                    "connected": True,
                    "keyspace_hits": info.get('keyspace_hits', 0),
                    "keyspace_misses": info.get('keyspace_misses', 0),
                    "used_memory": info.get('used_memory_human', 'Unknown')
                }
            except Exception as e:
                return {"cache_type": "redis", "connected": False, "error": str(e)}
        else:
            return {
                "cache_type": "memory",
                "connected": True,
                "cached_items": len(self.memory_cache)
            }


# Global ATIE service instance
atie_service = ATIEService()


async def get_textual_trust_score(
    text: str, 
    source_url: str = None, 
    enable_cross_verification: bool = True
) -> Dict:
    """
    Main function to get textual trust score
    
    Usage:
        result = await get_textual_trust_score("Article content here...")
        trust_score = result['atie_trust_score']['score']
    """
    return await atie_service.analyze_textual_integrity(
        text=text,
        source_url=source_url,
        enable_cross_verification=enable_cross_verification
    )


if __name__ == "__main__":
    # Test the ATIE service
    async def test_atie():
        test_article = """
        BREAKING: New study from Harvard University shows that 85% of people 
        who exercise regularly report better mental health outcomes. Dr. Sarah Johnson, 
        lead researcher, confirmed that the data was collected over 3 years from 
        10,000 participants. The study was published in the Journal of Health Psychology 
        on March 15, 2024.
        """
        
        print("🔍 Testing ATIE Service...")
        result = await get_textual_trust_score(test_article)
        
        print(f"\n✅ ATIE Trust Score: {result['atie_trust_score']['score']}/100")
        print(f"📊 Trust Level: {result['atie_trust_score']['trust_level']}")
        print(f"💡 Recommendation: {result['atie_trust_score']['recommendation']}")
        print(f"⚡ Analysis Time: {result['metadata']['analysis_time']:.2f}s")
        
        return result
    
    # Run test
    asyncio.run(test_atie())