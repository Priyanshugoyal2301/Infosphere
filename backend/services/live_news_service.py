"""
Live News Fetching Service with Multiple API Sources
Supports NewsAPI, GNews, and NewsData.io with automatic fallback
"""

import httpx
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import asyncio

load_dotenv()


class LiveNewsService:
    """Fetch live news from multiple sources with caching and fallback"""
    
    def __init__(self):
        # Try to load .env file (for local development)
        # In production (Render), environment variables come from platform settings
        try:
            import pathlib
            env_path = pathlib.Path(__file__).parent.parent.parent / '.env'
            if env_path.exists():
                load_dotenv(dotenv_path=env_path, override=True)
                print(f"[INIT] Loaded .env from: {env_path}")
            else:
                print(f"[INIT] No .env file at {env_path}, using system environment variables")
        except Exception as e:
            print(f"[INIT] Could not load .env: {e}, using system environment variables")
        
        # API Keys - will work from .env (local) or Render environment variables
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.gnews_key = os.getenv("GNEWS_API_KEY")
        self.newsdata_key = os.getenv("NEWSDATA_API_KEY")
        
        print(f"[INIT] .env path: {env_path}")
        print(f"[INIT] .env exists: {env_path.exists()}")
        print(f"[INIT] Loaded API Keys: NewsAPI={bool(self.newsapi_key)}, GNews={bool(self.gnews_key)}, NewsData={bool(self.newsdata_key)}")
        
        # Cache settings
        self.cache_file = "news_cache.json"
        cache_duration_minutes = int(os.getenv("NEWS_CACHE_DURATION", 120))
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        
        # API endpoints
        self.newsapi_url = "https://newsapi.org/v2/top-headlines"
        self.gnews_url = "https://gnews.io/api/v4/top-headlines"
        self.newsdata_url = "https://newsdata.io/api/1/news"
    
    async def fetch_live_news(self, category: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Fetch live news with automatic fallback between sources
        Priority: NewsAPI -> GNews -> NewsData -> Cache
        """
        
        print(f"\n[DEBUG] fetch_live_news called with category={category}, limit={limit}")
        print(f"[DEBUG] API Keys present: NewsAPI={bool(self.newsapi_key)}, GNews={bool(self.gnews_key)}, NewsData={bool(self.newsdata_key)}")
        
        # Check cache first
        cached_news = self._get_cached_news(category)
        if cached_news:
            print(f"📦 Returning cached news (age: {self._cache_age(category)} minutes)")
            return cached_news[:limit]
        
        print(f"[DEBUG] No valid cache found, trying APIs...")
        
        # Try fetching from APIs in order
        news_articles = None
        
        # Try NewsAPI first
        if self.newsapi_key:
            try:
                print("🔄 Fetching from NewsAPI...")
                news_articles = await self._fetch_from_newsapi(category, limit)
                if news_articles:
                    print(f"✅ NewsAPI: Fetched {len(news_articles)} articles")
            except Exception as e:
                print(f"⚠️ NewsAPI failed: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Fallback to GNews
        if not news_articles and self.gnews_key:
            try:
                print("🔄 Fetching from GNews...")
                news_articles = await self._fetch_from_gnews(category, limit)
                if news_articles:
                    print(f"✅ GNews: Fetched {len(news_articles)} articles")
            except Exception as e:
                print(f"⚠️ GNews failed: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Fallback to NewsData
        if not news_articles and self.newsdata_key:
            try:
                print("🔄 Fetching from NewsData.io...")
                news_articles = await self._fetch_from_newsdata(category, limit)
                if news_articles:
                    print(f"✅ NewsData: Fetched {len(news_articles)} articles")
            except Exception as e:
                print(f"⚠️ NewsData failed: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # If all APIs fail, return stale cache
        if not news_articles:
            print("⚠️ All APIs failed, returning stale cache")
            return self._get_stale_cache(category)[:limit]
        
        # Cache the results
        self._cache_news(news_articles, category)
        return news_articles[:limit]
    
    async def _fetch_from_newsapi(self, category: Optional[str], limit: int) -> List[Dict]:
        """Fetch from NewsAPI.org"""
        params = {
            "apiKey": self.newsapi_key,
            "country": "in",
            "pageSize": min(limit, 100)
        }
        
        if category and category != "all":
            # Map our categories to NewsAPI categories
            category_map = {
                "politics": "general",
                "business": "business",
                "technology": "technology",
                "sports": "sports",
                "entertainment": "entertainment",
                "health": "health",
                "science": "science"
            }
            params["category"] = category_map.get(category.lower(), "general")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.newsapi_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                # NewsAPI free tier might return 0 results, skip to next source
                if not articles or len(articles) == 0:
                    print("⚠️ NewsAPI returned 0 articles (free tier limitation)")
                    return []
                    
                return self._process_newsapi_articles(articles)
            elif response.status_code == 429:
                print("⚠️ NewsAPI rate limit exceeded")
                return []
            else:
                raise Exception(f"NewsAPI error: {response.status_code}")
    
    async def _fetch_from_gnews(self, category: Optional[str], limit: int) -> List[Dict]:
        """Fetch from GNews API"""
        params = {
            "apikey": self.gnews_key,
            "country": "in",
            "lang": "en",
            "max": min(limit, 100)
        }
        
        if category and category != "all":
            params["topic"] = category.lower()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.gnews_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_gnews_articles(data.get("articles", []))
            else:
                raise Exception(f"GNews error: {response.status_code}")
    
    async def _fetch_from_newsdata(self, category: Optional[str], limit: int) -> List[Dict]:
        """Fetch from NewsData.io"""
        params = {
            "apikey": self.newsdata_key,
            "country": "in",
            "language": "en"
        }
        
        if category and category != "all":
            params["category"] = category.lower()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.newsdata_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_newsdata_articles(data.get("results", []))
            else:
                raise Exception(f"NewsData error: {response.status_code}")
    
    def _process_newsapi_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process NewsAPI articles to standard format"""
        processed = []
        
        for article in articles:
            if not article.get("title") or article.get("title") == "[Removed]":
                continue
                
            processed.append({
                "id": hash(article["url"]),
                "title": article["title"],
                "description": article.get("description") or "",
                "content": article.get("content") or article.get("description") or "",
                "url": article["url"],
                "source": article["source"]["name"],
                "author": article.get("author") or "Unknown",
                "published_at": article["publishedAt"],
                "image_url": article.get("urlToImage"),
                "category": self._auto_categorize(article["title"], article.get("description", "")),
                "sentiment": "neutral",
                "confidence": 0.0,
                "api_source": "NewsAPI"
            })
        
        return processed
    
    def _process_gnews_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process GNews articles to standard format"""
        processed = []
        
        for article in articles:
            processed.append({
                "id": hash(article["url"]),
                "title": article["title"],
                "description": article.get("description") or "",
                "content": article.get("content") or article.get("description") or "",
                "url": article["url"],
                "source": article["source"]["name"],
                "author": "Unknown",
                "published_at": article["publishedAt"],
                "image_url": article.get("image"),
                "category": self._auto_categorize(article["title"], article.get("description", "")),
                "sentiment": "neutral",
                "confidence": 0.0,
                "api_source": "GNews"
            })
        
        return processed
    
    def _process_newsdata_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process NewsData articles to standard format"""
        processed = []
        
        for article in articles:
            processed.append({
                "id": hash(article.get("link", str(hash(article["title"])))),
                "title": article["title"],
                "description": article.get("description") or "",
                "content": article.get("content") or article.get("description") or "",
                "url": article.get("link", ""),
                "source": article.get("source_id", "Unknown"),
                "author": ", ".join(article.get("creator", [])) if article.get("creator") else "Unknown",
                "published_at": article.get("pubDate", datetime.now().isoformat()),
                "image_url": article.get("image_url"),
                "category": article.get("category", [None])[0] or self._auto_categorize(article["title"], article.get("description", "")),
                "sentiment": "neutral",
                "confidence": 0.0,
                "api_source": "NewsData"
            })
        
        return processed
    
    def _auto_categorize(self, title: str, description: str) -> str:
        """Auto-categorize article based on content"""
        text = f"{title} {description}".lower()
        
        # Keywords for each category
        categories = {
            "Politics": ["election", "government", "minister", "parliament", "pm modi", "congress", "bjp", "policy", "supreme court"],
            "Sports": ["cricket", "football", "sports", "player", "match", "ipl", "world cup", "olympics", "fifa"],
            "Technology": ["tech", "ai", "smartphone", "app", "google", "apple", "software", "ai/ml", "startup", "innovation"],
            "Entertainment": ["film", "actor", "bollywood", "celebrity", "music", "movie", "netflix", "series", "award"],
            "Business": ["economy", "market", "stock", "business", "company", "rupee", "gdp", "trade", "investment"],
            "Health": ["health", "hospital", "doctor", "disease", "covid", "vaccine", "medicine", "treatment"],
            "Crime": ["crime", "police", "arrest", "murder", "theft", "scam", "fraud", "investigation"],
            "Weather": ["rain", "weather", "cyclone", "temperature", "forecast", "flood", "storm"],
            "Accident": ["accident", "crash", "collision", "injured", "died", "fatal"],
            "International": ["g20", "russia", "china", "usa", "pakistan", "dubai", "international", "global"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "General"
    
    def _cache_news(self, articles: List[Dict], category: Optional[str] = None):
        """Cache fetched news"""
        cache_key = category or "all"
        cache_data = self._load_cache()
        
        cache_data[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "articles": articles
        }
        
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"💾 Cached {len(articles)} articles for category: {cache_key}")
        except Exception as e:
            print(f"⚠️ Cache write failed: {str(e)}")
    
    def _get_cached_news(self, category: Optional[str] = None) -> Optional[List[Dict]]:
        """Get cached news if still valid (within cache duration)"""
        cache_key = category or "all"
        cache_data = self._load_cache()
        
        if cache_key in cache_data:
            cached = cache_data[cache_key]
            timestamp = datetime.fromisoformat(cached["timestamp"])
            
            if datetime.now() - timestamp < self.cache_duration:
                return cached["articles"]
        
        return None
    
    def _get_stale_cache(self, category: Optional[str] = None) -> List[Dict]:
        """Get cached news even if expired (fallback when all APIs fail)"""
        cache_key = category or "all"
        cache_data = self._load_cache()
        
        if cache_key in cache_data:
            return cache_data[cache_key]["articles"]
        
        # Return any available cached data
        for key, data in cache_data.items():
            if data.get("articles"):
                return data["articles"]
        
        return []
    
    def _cache_age(self, category: Optional[str] = None) -> int:
        """Get age of cache in minutes"""
        cache_key = category or "all"
        cache_data = self._load_cache()
        
        if cache_key in cache_data:
            timestamp = datetime.fromisoformat(cache_data[cache_key]["timestamp"])
            age = datetime.now() - timestamp
            return int(age.total_seconds() / 60)
        
        return 0
    
    def _load_cache(self) -> Dict:
        """Load cache file"""
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print("⚠️ Cache file corrupted, creating new cache")
            return {}
    
    async def get_breaking_news(self, limit: int = 10) -> List[Dict]:
        """Get top breaking news"""
        all_news = await self.fetch_live_news(category=None, limit=limit * 2)
        
        # Sort by publish date (newest first)
        all_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        
        return all_news[:limit]
    
    async def search_news(self, query: str, limit: int = 20) -> List[Dict]:
        """Search news by keyword"""
        all_news = await self.fetch_live_news(limit=100)
        
        # Simple keyword search
        query_lower = query.lower()
        filtered = [
            article for article in all_news
            if query_lower in article["title"].lower() or query_lower in article["description"].lower()
        ]
        
        return filtered[:limit]


# Global instance
live_news_service = LiveNewsService()
