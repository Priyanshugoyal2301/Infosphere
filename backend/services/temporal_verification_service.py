"""
Temporal Fact-Checking Service
Tracks claims across time and detects contradictions
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class TemporalFactChecker:
    """Track and verify claims across time"""
    
    def __init__(self):
        self.timeline_db_path = Path("data/fact_timeline.json")
        self.timeline_db_path.parent.mkdir(exist_ok=True)
        self.fact_timeline = self._load_timeline()
    
    def _load_timeline(self) -> Dict:
        """Load fact timeline database"""
        if self.timeline_db_path.exists():
            with open(self.timeline_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"claims": [], "sources": {}}
    
    def _save_timeline(self):
        """Save fact timeline database"""
        with open(self.timeline_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.fact_timeline, f, indent=2, ensure_ascii=False)
    
    def _generate_claim_hash(self, claim: str) -> str:
        """Generate unique hash for a claim"""
        return hashlib.sha256(claim.lower().strip().encode()).hexdigest()[:16]
    
    def add_claim(self, claim: str, source: str, article_url: str, verified: bool = False) -> str:
        """Add a new claim to the timeline"""
        claim_hash = self._generate_claim_hash(claim)
        
        claim_entry = {
            "claim_id": claim_hash,
            "claim_text": claim,
            "source": source,
            "article_url": article_url,
            "timestamp": datetime.now().isoformat(),
            "verified": verified,
            "contradictions": []
        }
        
        # Check for contradictions with existing claims
        contradictions = self._find_contradictions(claim, source)
        if contradictions:
            claim_entry["contradictions"] = contradictions
        
        self.fact_timeline["claims"].append(claim_entry)
        
        # Track source history
        if source not in self.fact_timeline["sources"]:
            self.fact_timeline["sources"][source] = []
        self.fact_timeline["sources"][source].append({
            "claim_id": claim_hash,
            "timestamp": claim_entry["timestamp"]
        })
        
        self._save_timeline()
        return claim_hash
    
    def _find_contradictions(self, claim: str, source: str) -> List[Dict]:
        """Find contradicting claims from the same source"""
        contradictions = []
        claim_lower = claim.lower()
        
        # Get all previous claims from this source
        if source in self.fact_timeline["sources"]:
            for claim_entry in self.fact_timeline["claims"]:
                if claim_entry["source"] == source:
                    # Simple contradiction detection (can be enhanced with NLP)
                    if self._detect_contradiction(claim_lower, claim_entry["claim_text"].lower()):
                        contradictions.append({
                            "claim_id": claim_entry["claim_id"],
                            "original_claim": claim_entry["claim_text"],
                            "timestamp": claim_entry["timestamp"],
                            "article_url": claim_entry["article_url"]
                        })
        
        return contradictions
    
    def _detect_contradiction(self, claim1: str, claim2: str) -> bool:
        """Detect if two claims contradict (basic implementation)"""
        # Contradiction patterns
        contradictory_pairs = [
            ("will", "will not"),
            ("confirmed", "denied"),
            ("true", "false"),
            ("increase", "decrease"),
            ("approve", "reject"),
            ("support", "oppose")
        ]
        
        for word1, word2 in contradictory_pairs:
            if (word1 in claim1 and word2 in claim2) or (word2 in claim1 and word1 in claim2):
                # Check if they're about the same topic (very basic)
                words1 = set(claim1.split())
                words2 = set(claim2.split())
                common_words = words1.intersection(words2)
                if len(common_words) > 3:  # At least 3 common words
                    return True
        
        return False
    
    def get_source_timeline(self, source: str) -> List[Dict]:
        """Get all claims from a source over time"""
        if source not in self.fact_timeline["sources"]:
            return []
        
        source_claims = []
        for claim_ref in self.fact_timeline["sources"][source]:
            claim = next((c for c in self.fact_timeline["claims"] 
                         if c["claim_id"] == claim_ref["claim_id"]), None)
            if claim:
                source_claims.append(claim)
        
        return sorted(source_claims, key=lambda x: x["timestamp"])
    
    def check_narrative_shift(self, source: str, days: int = 30) -> Dict:
        """Detect narrative shifts for a source"""
        from datetime import timedelta
        
        timeline = self.get_source_timeline(source)
        if not timeline:
            return {"shift_detected": False, "details": []}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_claims = [c for c in timeline 
                        if datetime.fromisoformat(c["timestamp"]) > cutoff_date]
        
        shifts = []
        for i, claim in enumerate(recent_claims):
            if claim["contradictions"]:
                shifts.append({
                    "current_claim": claim["claim_text"],
                    "timestamp": claim["timestamp"],
                    "contradicts": claim["contradictions"]
                })
        
        return {
            "shift_detected": len(shifts) > 0,
            "details": shifts,
            "total_claims": len(recent_claims),
            "contradictory_claims": len(shifts)
        }


# Global instance
temporal_checker = TemporalFactChecker()
