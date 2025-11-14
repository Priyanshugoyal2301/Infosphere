"""
Offline ATIE Service - AI Trust and Integrity Engine
===================================================

This is a simplified, offline-ready version that works without downloading external models.
Perfect for development and testing environments.
"""

import os
import re
import time
import hashlib
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

# Basic imports that don't require model downloads
# Optional heavy libs (not required for offline mode). Avoid hard dependency for faster dev startup.
try:
    from transformers import pipeline  # type: ignore
    import torch  # type: ignore
except Exception:
    pipeline = None  # noqa: F401
    torch = None  # noqa: F401
    logger = logging.getLogger(__name__)
    logger.info("Running offline ATIE without transformers/torch (not needed in offline mode)")

logger = logging.getLogger(__name__)

class OfflineTextualIntegrityAnalyzer:
    """Simplified textual integrity analyzer that works offline"""
    
    def __init__(self):
        """Initialize with rule-based analysis only"""
        self.fake_news_keywords = [
            'breaking', 'shocking', 'exclusive', 'urgent', 'alert', 'unbelievable',
            'doctors hate', 'they don\'t want you to know', 'this one trick',
            'you won\'t believe', 'secret revealed', 'conspiracy', 'cover-up'
        ]
        
        self.bias_indicators = {
            'emotional': ['terrible', 'horrible', 'amazing', 'incredible', 'outrageous'],
            'absolute': ['always', 'never', 'all', 'none', 'every', 'completely'],
            'loaded': ['failed', 'disaster', 'crisis', 'scandal', 'controversy']
        }
        
        self.credible_patterns = [
            r'according to \w+',
            r'study shows',
            r'research indicates',
            r'data suggests',
            r'expert says'
        ]
        
        logger.info("✅ Offline textual integrity analyzer initialized")
    
    def analyze_fake_news_probability(self, text: str) -> Dict[str, float]:
        """Rule-based fake news detection"""
        text_lower = text.lower()
        
        # Count suspicious keywords
        keyword_score = 0
        for keyword in self.fake_news_keywords:
            if keyword in text_lower:
                keyword_score += 1
        
        # Check for excessive punctuation
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        
        # Calculate fake probability
        keyword_factor = min(keyword_score * 15, 50)  # Max 50% from keywords
        punctuation_factor = min(exclamation_count * 5, 25)  # Max 25% from punctuation
        caps_factor = min(caps_ratio * 100, 25)  # Max 25% from caps
        
        fake_probability = keyword_factor + punctuation_factor + caps_factor
        fake_probability = min(fake_probability, 95)  # Cap at 95%
        
        real_probability = 100 - fake_probability
        authenticity_score = real_probability
        
        return {
            'authenticity_score': authenticity_score,
            'fake_probability': fake_probability,
            'real_probability': real_probability,
            'confidence': max(60, abs(fake_probability - 50) + 50),
            'classification': 'authentic' if authenticity_score > 50 else 'suspicious'
        }
    
    def analyze_bias(self, text: str) -> Dict[str, Union[str, float, List[str]]]:
        """Detect bias in text"""
        text_lower = text.lower()
        
        emotional_score = 0
        absolute_score = 0
        loaded_score = 0
        detected_indicators = []
        
        # Check for emotional language
        for word in self.bias_indicators['emotional']:
            count = text_lower.count(word)
            if count > 0:
                emotional_score += count * 10
                detected_indicators.append(f"Emotional language: '{word}'")
        
        # Check for absolute statements
        for word in self.bias_indicators['absolute']:
            if word in text_lower:
                absolute_score += 15
                detected_indicators.append(f"Absolute statement: '{word}'")
        
        # Check for loaded language
        for word in self.bias_indicators['loaded']:
            if word in text_lower:
                loaded_score += 10
                detected_indicators.append(f"Loaded language: '{word}'")
        
        total_bias_score = min(emotional_score + absolute_score + loaded_score, 100)
        
        # Determine bias type
        if total_bias_score < 20:
            bias_type = "neutral"
        elif total_bias_score < 50:
            bias_type = "slight_bias"
        else:
            bias_type = "strong_bias"
        
        return {
            'bias_type': bias_type,
            'bias_score': total_bias_score,
            'bias_breakdown': {
                'emotional': emotional_score,
                'absolute': absolute_score,
                'loaded': loaded_score
            },
            'detected_indicators': detected_indicators
        }
    
    def analyze_sensationalism(self, text: str) -> Dict[str, Union[float, List[str], bool]]:
        """Detect sensationalist language"""
        sensational_patterns = [
            r'\b[A-Z]{2,}\b',  # ALL CAPS words
            r'!{2,}',          # Multiple exclamations
            r'\?{2,}',         # Multiple question marks
            r'\bBREAKING\b',   # Breaking news
            r'\bSHOCKING\b',   # Shocking
            r'\bEXCLUSIVE\b'   # Exclusive
        ]
        
        detected_patterns = []
        sensationalism_score = 0
        
        for pattern in sensational_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                sensationalism_score += len(matches) * 10
                detected_patterns.extend(matches)
        
        sensationalism_score = min(sensationalism_score, 100)
        is_sensational = sensationalism_score > 30
        
        return {
            'sensationalism_score': sensationalism_score,
            'detected_patterns': detected_patterns,
            'is_sensational': is_sensational
        }
    
    def analyze_source_credibility(self, text: str, source_url: str = None) -> Dict[str, Union[float, List[str]]]:
        """Analyze source credibility indicators"""
        credibility_score = 50  # Base score
        indicators = []
        
        # Check for credible patterns
        for pattern in self.credible_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                credibility_score += len(matches) * 5
                indicators.extend([f"Credible reference: {match}" for match in matches])
        
        # Check for specific details
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'
        dates_found = re.findall(date_pattern, text)
        if dates_found:
            credibility_score += len(dates_found) * 3
            indicators.append(f"Specific dates mentioned: {len(dates_found)}")
        
        # Check for numbers and statistics
        number_pattern = r'\b\d+%|\b\d+\.\d+%|\$\d+|\d+ people'
        numbers_found = re.findall(number_pattern, text)
        if numbers_found:
            credibility_score += min(len(numbers_found) * 2, 15)
            indicators.append(f"Statistics/numbers provided: {len(numbers_found)}")
        
        credibility_score = min(credibility_score, 100)
        
        return {
            'credibility_score': credibility_score,
            'indicators': indicators
        }

class OfflineATIEService:
    """Offline AI Trust and Integrity Engine Service"""
    
    def __init__(self):
        """Initialize offline ATIE service"""
        self.textual_analyzer = OfflineTextualIntegrityAnalyzer()
        self.trusted_sources = self._load_trusted_sources()
        self.cache = {}  # Simple in-memory cache
        
        logger.info("✅ Offline ATIE service initialized successfully")
    
    def _load_trusted_sources(self) -> List[str]:
        """Load trusted news sources"""
        return [
            "reuters.com", "ap.org", "bbc.com", "npr.org",
            "cnn.com", "foxnews.com", "abcnews.go.com",
            "cbsnews.com", "nbcnews.com", "pbs.org"
        ]
    
    def _generate_cache_key(self, text: str, options: Dict = None) -> str:
        """Generate cache key for analysis results"""
        content = text + str(options or {})
        return f"atie:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def analyze_textual_integrity(
        self,
        text: str,
        source_url: Optional[str] = None,
        enable_cross_verification: bool = True,
        cache_result: bool = True
    ) -> Dict[str, Any]:
        """Complete textual integrity analysis"""
        
        # Check cache first
        cache_key = self._generate_cache_key(text, {
            'source_url': source_url,
            'cross_verification': enable_cross_verification
        })
        
        if cache_result and cache_key in self.cache:
            cached_result = self.cache[cache_key].copy()
            cached_result['metadata']['from_cache'] = True
            cached_result['metadata']['cache_hit_time'] = 0.001
            return cached_result
        
        start_time = time.time()
        
        # Run all analyses
        fake_news_result = self.textual_analyzer.analyze_fake_news_probability(text)
        bias_analysis = self.textual_analyzer.analyze_bias(text)
        sensationalism = self.textual_analyzer.analyze_sensationalism(text)
        source_credibility = self.textual_analyzer.analyze_source_credibility(text, source_url)
        
        # Calculate composite textual integrity score
        weights = {
            'authenticity': 0.4,
            'credibility': 0.25,
            'sensationalism': 0.2,
            'bias': 0.15
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
        
        # Prepare result
        result = {
            'atie_trust_score': {
                'score': round(textual_integrity_score, 2),
                'trust_level': self._get_trust_level(textual_integrity_score),
                'components': {
                    'textual_integrity_base': round(textual_integrity_score, 2),
                    'cross_verification_adjustment': None
                },
                'recommendation': self._get_recommendation(textual_integrity_score)
            },
            'textual_integrity': {
                'textual_integrity_score': round(textual_integrity_score, 2),
                'components': {
                    'fake_news_classification': fake_news_result,
                    'bias_analysis': bias_analysis,
                    'sensationalism_analysis': sensationalism,
                    'source_credibility': source_credibility
                },
                'metadata': {
                    'analysis_time': analysis_time,
                    'model_used': 'offline-rule-based',
                    'timestamp': datetime.now().isoformat()
                }
            },
            'cross_verification': None,  # Not implemented in offline mode
            'metadata': {
                'analysis_time': analysis_time,
                'timestamp': datetime.now().isoformat(),
                'cache_key': cache_key,
                'from_cache': False,
                'cache_hit_time': 0.0
            }
        }
        
        # Cache result
        if cache_result:
            self.cache[cache_key] = result.copy()
        
        return result
    
    def _get_trust_level(self, score: float) -> str:
        """Convert numeric score to trust level"""
        if score >= 80:
            return "high"
        elif score >= 60:
            return "moderate"
        elif score >= 40:
            return "low"
        else:
            return "very_low"
    
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on trust score"""
        if score >= 80:
            return "Content appears highly trustworthy and credible."
        elif score >= 60:
            return "Content integrity is questionable. Verify from additional sources."
        elif score >= 40:
            return "Content shows signs of bias or sensationalism. Use caution."
        else:
            return "Content appears unreliable. Seek verification from trusted sources."
    
    async def quick_check(self, text: str) -> Dict[str, Any]:
        """Quick integrity check for short texts"""
        return await self.analyze_textual_integrity(text, cache_result=True)
    
    async def analyze_composite(
        self,
        text: str,
        media_analysis: Optional[Dict] = None,
        source_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Composite analysis combining text and media integrity"""
        
        # Get text analysis
        text_result = await self.analyze_textual_integrity(text, source_url)
        
        if media_analysis:
            # Combine text and media scores
            text_score = text_result['atie_trust_score']['score']
            media_score = (1 - media_analysis.get('manipulation_score', 0)) * 100
            
            # Weighted composite score (60% text, 40% media)
            composite_score = (text_score * 0.6) + (media_score * 0.4)
            
            # Update the result with composite information
            text_result['atie_trust_score']['score'] = round(composite_score, 2)
            text_result['atie_trust_score']['components']['media_integrity'] = media_score
            text_result['media_analysis'] = media_analysis
        
        return text_result

# Create service instance
offline_atie_service = OfflineATIEService()

# Compatibility functions for existing code
async def get_textual_trust_score(text: str, source_url: str = None) -> Dict:
    """Get textual trust score - compatibility function"""
    result = await offline_atie_service.analyze_textual_integrity(text, source_url)
    return result['atie_trust_score']

# Export the service
atie_service = offline_atie_service