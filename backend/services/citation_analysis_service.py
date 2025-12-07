"""
Source Citation Analysis Service
Verifies quotes and statistics against original sources
"""

import httpx
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import asyncio


class SourceCitationAnalyzer:
    """Verify claims against original sources"""
    
    def __init__(self):
        self.official_sources = {
            "pib": "https://pib.gov.in/",
            "pm_india": "https://www.pmindia.gov.in/",
            "rbi": "https://www.rbi.org.in/",
            "who": "https://www.who.int/",
            "indiankanoon": "https://indiankanoon.org/",
            "census": "https://censusindia.gov.in/",
            "parliament": "https://sansad.in/"
        }
    
    async def verify_quote(self, quote: str, attributed_to: str, topic: Optional[str] = None) -> Dict:
        """Verify if a quote exists in official sources"""
        results = {
            "quote": quote,
            "attributed_to": attributed_to,
            "verified": False,
            "confidence": 0.0,
            "sources_checked": [],
            "matches": []
        }
        
        # Search in relevant official sources
        search_queries = self._build_search_queries(quote, attributed_to, topic)
        
        for source_name, source_url in self.official_sources.items():
            try:
                matches = await self._search_source(source_url, search_queries, quote)
                if matches:
                    results["sources_checked"].append(source_name)
                    results["matches"].extend(matches)
                    results["verified"] = True
                    results["confidence"] = min(0.95, results["confidence"] + 0.3)
            except Exception as e:
                print(f"Error checking {source_name}: {e}")
                continue
        
        return results
    
    def _build_search_queries(self, quote: str, attributed_to: str, topic: Optional[str]) -> List[str]:
        """Build search queries for verification"""
        queries = [
            quote,
            f"{attributed_to} {quote[:50]}",
            f'"{quote[:100]}"'
        ]
        
        if topic:
            queries.append(f"{topic} {attributed_to}")
        
        return queries
    
    async def _search_source(self, source_url: str, queries: List[str], quote: str) -> List[Dict]:
        """Search a source for matching quotes"""
        matches = []
        
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                for query in queries[:2]:  # Limit to 2 queries per source
                    # Try searching the source
                    search_url = f"{source_url}search?q={query}"
                    response = await client.get(search_url)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for quote matches in page content
                        text_content = soup.get_text()
                        if self._find_quote_match(quote, text_content):
                            matches.append({
                                "source": source_url,
                                "match_type": "exact",
                                "url": str(response.url),
                                "confidence": 0.9
                            })
                            break
        except Exception as e:
            print(f"Error searching {source_url}: {e}")
        
        return matches
    
    def _find_quote_match(self, quote: str, text: str) -> bool:
        """Check if quote exists in text"""
        quote_clean = quote.lower().strip()
        text_clean = text.lower()
        
        # Exact match
        if quote_clean in text_clean:
            return True
        
        # Fuzzy match (80% of words present)
        quote_words = set(quote_clean.split())
        quote_words = {w for w in quote_words if len(w) > 3}  # Filter small words
        
        if not quote_words:
            return False
        
        matches = sum(1 for word in quote_words if word in text_clean)
        match_ratio = matches / len(quote_words)
        
        return match_ratio >= 0.8
    
    async def verify_statistics(self, statistic: str, category: str) -> Dict:
        """Verify statistics against official databases"""
        results = {
            "statistic": statistic,
            "category": category,
            "verified": False,
            "official_value": None,
            "source": None
        }
        
        # Extract numbers from statistic
        numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', statistic)
        
        if not numbers:
            return results
        
        # Check category-specific sources
        source_map = {
            "population": "census",
            "finance": "rbi",
            "health": "who",
            "economic": "rbi"
        }
        
        source_key = source_map.get(category.lower())
        if source_key and source_key in self.official_sources:
            # Try to verify (basic implementation)
            results["source"] = self.official_sources[source_key]
            results["verified"] = False  # Would need actual API integration
        
        return results
    
    async def verify_pm_statement(self, statement: str) -> Dict:
        """Verify PM statements from official website/Twitter"""
        results = {
            "statement": statement,
            "verified": False,
            "sources": []
        }
        
        try:
            # Check PM India official website
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.official_sources["pm_india"])
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for statement in recent speeches/press releases
                    if self._find_quote_match(statement, soup.get_text()):
                        results["verified"] = True
                        results["sources"].append({
                            "type": "official_website",
                            "url": self.official_sources["pm_india"],
                            "confidence": 0.95
                        })
        except Exception as e:
            print(f"Error verifying PM statement: {e}")
        
        return results


# Global instance
citation_analyzer = SourceCitationAnalyzer()
