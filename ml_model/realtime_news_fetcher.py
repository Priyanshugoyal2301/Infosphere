"""
Real-time News Fetcher for Infosphere ML Pipeline

This module fetches live news from major Indian news sources (Times of India, 
Hindustan Times), classifies them using the trained ML model, and stores them
in the Infosphere database for further processing.

Features:
- Real-time RSS feed parsing
- Automatic news classification
- Duplicate detection and removal
- Database integration
- Scheduled automated fetching
- Content filtering and preprocessing

Author: Infosphere Team
Date: October 2025
"""

import feedparser
import pandas as pd
import os
import sys
import sqlite3
import requests
from datetime import datetime, timedelta
import time
import schedule
import logging
from typing import List, Dict, Optional
import hashlib
import re
from bs4 import BeautifulSoup
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_fetcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add backend to path for ML integration
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)


class RealTimeNewsFetcher:
    """
    Fetches real-time news from Indian news sources and integrates with ML pipeline.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the news fetcher.
        
        Args:
            db_path (str, optional): Path to the database
        """
        self.db_path = db_path or "infosphere.db"
        
        # Extended RSS feeds for comprehensive coverage
        self.feeds = {
            # Times of India
            "TOI - Top Stories": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
            "TOI - India": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
            "TOI - Delhi": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
            "TOI - Mumbai": "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms",
            "TOI - Business": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
            
            # Hindustan Times  
            "HT - Top News": "https://www.hindustantimes.com/rss/topnews/rssfeed.xml",
            "HT - India News": "https://www.hindustantimes.com/rss/india/rssfeed.xml",
            "HT - Delhi News": "https://www.hindustantimes.com/rss/delhi/rssfeed.xml",
            "HT - Mumbai News": "https://www.hindustantimes.com/rss/mumbai/rssfeed.xml",
            "HT - Business": "https://www.hindustantimes.com/rss/business/rssfeed.xml",
            
            # Additional sources for better coverage
            "Indian Express": "https://indianexpress.com/print/front-page/feed/",
            "NDTV News": "https://feeds.feedburner.com/NDTV-LatestNews",
        }
        
        # Category keywords for enhanced classification
        self.category_keywords = {
            'Crime': [
                'murder', 'robbery', 'theft', 'burglary', 'assault', 'fraud', 'scam',
                'kidnapping', 'arrest', 'police', 'investigation', 'crime', 'criminal',
                'violence', 'shooting', 'stabbing', 'harassment', 'cybercrime'
            ],
            'Accident': [
                'accident', 'crash', 'collision', 'fire', 'blast', 'explosion', 
                'derailment', 'mishap', 'tragedy', 'incident', 'emergency', 'rescue',
                'injured', 'killed', 'fatalities', 'casualties', 'disaster'
            ],
            'Event': [
                'festival', 'celebration', 'conference', 'meeting', 'launch', 'opening',
                'ceremony', 'exhibition', 'workshop', 'seminar', 'concert', 'rally',
                'protest', 'march', 'campaign', 'election', 'vote', 'announcement'
            ],
            'Weather': [
                'rain', 'rainfall', 'storm', 'cyclone', 'hurricane', 'flood', 'drought',
                'temperature', 'heat', 'cold', 'fog', 'mist', 'weather', 'climate',
                'monsoon', 'thunderstorm', 'hailstorm', 'snowfall', 'humidity'
            ]
        }
        
        self._initialize_database()
        self._load_ml_model()
    
    def _initialize_database(self):
        """Initialize database tables for news storage."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create news_articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT,
                    content TEXT,
                    link TEXT UNIQUE NOT NULL,
                    published_date DATETIME,
                    fetched_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ml_category TEXT,
                    ml_confidence REAL,
                    keyword_category TEXT,
                    content_hash TEXT UNIQUE,
                    is_processed BOOLEAN DEFAULT FALSE,
                    location TEXT,
                    tags TEXT
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_category ON news_articles(ml_category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_source ON news_articles(source)')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    
    def _load_ml_model(self):
        """Load the trained ML model for classification."""
        try:
            from analyze_input import analyze_news_input, get_model_status
            
            # Check if model is loaded
            status = get_model_status()
            if status['model_loaded']:
                self.ml_classifier = analyze_news_input
                logger.info("✅ ML model loaded successfully")
            else:
                self.ml_classifier = None
                logger.warning("⚠️  ML model not available")
                
        except Exception as e:
            logger.error(f"❌ ML model loading failed: {e}")
            self.ml_classifier = None
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text content."""
        if not text:
            return ""
        
        # Remove HTML tags
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove common RSS artifacts
        text = re.sub(r'<.*?>', '', text)  # Any remaining HTML
        text = re.sub(r'\n+', ' ', text)   # Multiple newlines
        
        return text
    
    def _generate_content_hash(self, title: str, content: str) -> str:
        """Generate unique hash for content deduplication."""
        combined = f"{title}{content}".lower().strip()
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _classify_by_keywords(self, title: str, content: str) -> str:
        """Classify news using keyword matching as backup."""
        text = f"{title} {content}".lower()
        
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            category_scores[category] = score
        
        # Return category with highest score, or 'Event' as default
        return max(category_scores.items(), key=lambda x: x[1])[0] if any(category_scores.values()) else 'Event'
    
    def _extract_location(self, title: str, content: str) -> Optional[str]:
        """Extract location information from news content."""
        text = f"{title} {content}".lower()
        
        # Common Indian cities and states
        locations = [
            'delhi', 'mumbai', 'bangalore', 'kolkata', 'chennai', 'hyderabad',
            'pune', 'ahmedabad', 'jaipur', 'lucknow', 'kanpur', 'nagpur',
            'indore', 'thane', 'bhopal', 'visakhapatnam', 'pimpri', 'patna',
            'vadodara', 'ghaziabad', 'ludhiana', 'agra', 'nashik', 'faridabad',
            'meerut', 'rajkot', 'kalyan', 'vasai', 'varanasi', 'srinagar',
            'aurangabad', 'dhanbad', 'amritsar', 'navi mumbai', 'allahabad',
            'ranchi', 'howrah', 'coimbatore', 'jabalpur', 'gwalior', 'vijayawada',
            'jodhpur', 'madurai', 'raipur', 'kota', 'guwahati', 'chandigarh',
            'solapur', 'hubli', 'bareilly', 'moradabad', 'mysore', 'gurgaon',
            'aligarh', 'jalandhar', 'tiruchirappalli', 'bhubaneswar', 'salem',
            'uttar pradesh', 'maharashtra', 'tamil nadu', 'west bengal', 'rajasthan',
            'karnataka', 'gujarat', 'andhra pradesh', 'odisha', 'telangana',
            'kerala', 'jharkhand', 'assam', 'punjab', 'chhattisgarh', 'haryana',
            'jammu and kashmir', 'uttarakhand', 'himachal pradesh', 'tripura',
            'meghalaya', 'manipur', 'nagaland', 'goa', 'arunachal pradesh',
            'mizoram', 'sikkim'
        ]
        
        for location in locations:
            if location in text:
                return location.title()
        
        return None
    
    def fetch_single_feed(self, source_name: str, feed_url: str) -> List[Dict]:
        """Fetch and parse a single RSS feed."""
        articles = []
        
        try:
            logger.info(f"📡 Fetching from {source_name}...")
            
            # Set user agent to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Fetch with timeout
            response = requests.get(feed_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"⚠️  Feed parsing issues for {source_name}: {feed.bozo_exception}")
            
            for entry in feed.entries:
                try:
                    # Extract and clean content
                    title = self._clean_text(entry.get('title', ''))
                    summary = self._clean_text(entry.get('summary', ''))
                    content = self._clean_text(entry.get('description', summary))
                    
                    # Skip if no meaningful content
                    if not title or len(title) < 10:
                        continue
                    
                    # Parse published date
                    published_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'published'):
                        try:
                            published_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                        except:
                            published_date = datetime.now()
                    else:
                        published_date = datetime.now()
                    
                    # Generate content hash for deduplication
                    content_hash = self._generate_content_hash(title, content)
                    
                    # Extract location
                    location = self._extract_location(title, content)
                    
                    article = {
                        'source': source_name,
                        'title': title,
                        'summary': summary,
                        'content': content,
                        'link': entry.get('link', ''),
                        'published_date': published_date,
                        'content_hash': content_hash,
                        'location': location
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing entry from {source_name}: {e}")
                    continue
            
            logger.info(f"✅ Fetched {len(articles)} articles from {source_name}")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching {source_name}: {e}")
            return []
    
    def fetch_all_news(self) -> List[Dict]:
        """Fetch news from all configured sources."""
        all_articles = []
        
        logger.info("🌐 Starting news fetch from all sources...")
        
        for source_name, feed_url in self.feeds.items():
            articles = self.fetch_single_feed(source_name, feed_url)
            all_articles.extend(articles)
            
            # Small delay between requests to be respectful
            time.sleep(1)
        
        logger.info(f"📰 Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def classify_articles(self, articles: List[Dict]) -> List[Dict]:
        """Classify articles using ML model and keyword matching."""
        classified_articles = []
        
        logger.info("🤖 Classifying articles...")
        
        for article in articles:
            try:
                # ML Classification
                if self.ml_classifier:
                    text_for_classification = f"{article['title']} {article['content']}"
                    ml_result = self.ml_classifier(text_for_classification)
                    
                    if 'error' not in ml_result:
                        article['ml_category'] = ml_result['category']
                        article['ml_confidence'] = ml_result['confidence']
                    else:
                        article['ml_category'] = None
                        article['ml_confidence'] = 0.0
                else:
                    article['ml_category'] = None
                    article['ml_confidence'] = 0.0
                
                # Keyword-based classification as backup
                article['keyword_category'] = self._classify_by_keywords(
                    article['title'], 
                    article['content']
                )
                
                classified_articles.append(article)
                
            except Exception as e:
                logger.error(f"❌ Classification error: {e}")
                # Add article with default classification
                article['ml_category'] = 'Event'
                article['ml_confidence'] = 0.0
                article['keyword_category'] = 'Event'
                classified_articles.append(article)
        
        logger.info(f"✅ Classified {len(classified_articles)} articles")
        return classified_articles
    
    def save_to_database(self, articles: List[Dict]) -> int:
        """Save articles to database, avoiding duplicates."""
        if not articles:
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            new_articles = 0
            
            for article in articles:
                try:
                    # Check for duplicate based on content hash or link
                    cursor.execute('''
                        SELECT id FROM news_articles 
                        WHERE content_hash = ? OR link = ?
                    ''', (article['content_hash'], article['link']))
                    
                    if cursor.fetchone():
                        continue  # Skip duplicate
                    
                    # Insert new article
                    cursor.execute('''
                        INSERT INTO news_articles 
                        (source, title, summary, content, link, published_date, 
                         ml_category, ml_confidence, keyword_category, content_hash, location)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        article['source'],
                        article['title'],
                        article['summary'], 
                        article['content'],
                        article['link'],
                        article['published_date'],
                        article['ml_category'],
                        article['ml_confidence'],
                        article['keyword_category'],
                        article['content_hash'],
                        article['location']
                    ))
                    
                    new_articles += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error saving article: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            logger.info(f"💾 Saved {new_articles} new articles to database")
            return new_articles
            
        except Exception as e:
            logger.error(f"❌ Database save error: {e}")
            return 0
    
    def get_latest_news(self, hours: int = 24, category: Optional[str] = None) -> pd.DataFrame:
        """Get latest news from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Build query
            where_conditions = ["fetched_date >= datetime('now', '-{} hours')".format(hours)]
            params = []
            
            if category:
                where_conditions.append("(ml_category = ? OR keyword_category = ?)")
                params.extend([category, category])
            
            query = f'''
                SELECT 
                    source, title, summary, ml_category, ml_confidence, 
                    keyword_category, published_date, location, link
                FROM news_articles 
                WHERE {' AND '.join(where_conditions)}
                ORDER BY published_date DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error retrieving news: {e}")
            return pd.DataFrame()
    
    def get_news_statistics(self) -> Dict:
        """Get statistics about stored news."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Total articles
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            stats['total_articles'] = cursor.fetchone()[0]
            
            # By ML category
            cursor.execute('''
                SELECT ml_category, COUNT(*) as count 
                FROM news_articles 
                WHERE ml_category IS NOT NULL
                GROUP BY ml_category
            ''')
            stats['ml_categories'] = dict(cursor.fetchall())
            
            # By keyword category
            cursor.execute('''
                SELECT keyword_category, COUNT(*) as count 
                FROM news_articles 
                GROUP BY keyword_category
            ''')
            stats['keyword_categories'] = dict(cursor.fetchall())
            
            # By source
            cursor.execute('''
                SELECT source, COUNT(*) as count 
                FROM news_articles 
                GROUP BY source 
                ORDER BY count DESC
            ''')
            stats['sources'] = dict(cursor.fetchall())
            
            # Recent articles (last 24 hours)
            cursor.execute('''
                SELECT COUNT(*) FROM news_articles 
                WHERE fetched_date >= datetime('now', '-24 hours')
            ''')
            stats['recent_24h'] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {e}")
            return {}
    
    def run_single_fetch(self) -> Dict:
        """Run a single news fetch cycle."""
        logger.info("🚀 Starting news fetch cycle...")
        
        start_time = time.time()
        
        # Fetch news
        articles = self.fetch_all_news()
        
        if not articles:
            logger.warning("⚠️  No articles fetched")
            return {"status": "no_articles", "count": 0}
        
        # Classify articles
        classified_articles = self.classify_articles(articles)
        
        # Save to database
        new_count = self.save_to_database(classified_articles)
        
        end_time = time.time()
        duration = end_time - start_time
        
        result = {
            "status": "success",
            "total_fetched": len(articles),
            "new_saved": new_count,
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Fetch cycle completed: {result}")
        return result
    
    def export_to_csv(self, filename: str = None, hours: int = 24) -> str:
        """Export recent news to CSV file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_export_{timestamp}.csv"
        
        try:
            df = self.get_latest_news(hours=hours)
            
            if len(df) == 0:
                logger.warning("⚠️  No data to export")
                return None
            
            df.to_csv(filename, index=False)
            logger.info(f"📄 Exported {len(df)} articles to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Export error: {e}")
            return None


def setup_scheduler(fetcher: RealTimeNewsFetcher):
    """Setup scheduled news fetching."""
    
    def scheduled_fetch():
        """Wrapper function for scheduled execution."""
        try:
            result = fetcher.run_single_fetch()
            logger.info(f"📅 Scheduled fetch completed: {result['new_saved']} new articles")
        except Exception as e:
            logger.error(f"❌ Scheduled fetch failed: {e}")
    
    # Schedule fetching every 2 hours
    schedule.every(2).hours.do(scheduled_fetch)
    
    # Schedule daily statistics
    schedule.every().day.at("09:00").do(
        lambda: logger.info(f"📊 Daily stats: {fetcher.get_news_statistics()}")
    )
    
    logger.info("⏰ Scheduler configured: Fetching every 2 hours")


def main():
    """Main function for testing and demonstration."""
    print("🌐 Real-time News Fetcher for Infosphere")
    print("=" * 45)
    
    # Initialize fetcher
    fetcher = RealTimeNewsFetcher()
    
    # Show current statistics
    stats = fetcher.get_news_statistics()
    print(f"\n📊 Current Database Stats:")
    print(f"   Total Articles: {stats.get('total_articles', 0)}")
    print(f"   Recent (24h): {stats.get('recent_24h', 0)}")
    
    if stats.get('ml_categories'):
        print(f"   ML Categories: {stats['ml_categories']}")
    
    # Run single fetch
    print("\n🚀 Running single fetch cycle...")
    result = fetcher.run_single_fetch()
    
    # Show updated statistics  
    print(f"\n✅ Fetch Result:")
    print(f"   Status: {result['status']}")
    print(f"   Total Fetched: {result['total_fetched']}")
    print(f"   New Saved: {result['new_saved']}")
    print(f"   Duration: {result['duration_seconds']}s")
    
    # Show sample of latest news
    print(f"\n📰 Latest News Sample:")
    latest_df = fetcher.get_latest_news(hours=2)
    if len(latest_df) > 0:
        for _, row in latest_df.head(3).iterrows():
            print(f"   • {row['title'][:60]}... → {row['ml_category']} ({row['source']})")
    
    print(f"\n💡 Integration Tips:")
    print(f"   • Access via: fetcher.get_latest_news()")
    print(f"   • Export CSV: fetcher.export_to_csv()")
    print(f"   • Auto-schedule: setup_scheduler(fetcher)")


if __name__ == "__main__":
    main()