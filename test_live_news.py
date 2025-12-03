"""
Test script for live news fetching service
Run this to verify that the APIs are working correctly
"""

import asyncio
import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.live_news_service import live_news_service


async def test_live_news():
    """Test live news fetching from all APIs"""
    
    print("=" * 80)
    print("TESTING LIVE NEWS SERVICE")
    print("=" * 80)
    
    # Test 1: Fetch all news
    print("\n📰 Test 1: Fetching latest news from all sources...")
    try:
        news = await live_news_service.fetch_live_news(limit=10)
        print(f"✅ Success! Fetched {len(news)} articles")
        
        if news:
            print("\n📋 Sample Article:")
            article = news[0]
            print(f"  Title: {article['title']}")
            print(f"  Source: {article['source']} (via {article['api_source']})")
            print(f"  Category: {article['category']}")
            print(f"  Published: {article['published_at']}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Fetch by category
    print("\n\n🏆 Test 2: Fetching sports news...")
    try:
        sports_news = await live_news_service.fetch_live_news(category="sports", limit=5)
        print(f"✅ Success! Fetched {len(sports_news)} sports articles")
        
        for i, article in enumerate(sports_news[:3], 1):
            print(f"\n  {i}. {article['title']}")
            print(f"     Source: {article['source']}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Breaking news
    print("\n\n🚨 Test 3: Fetching breaking news...")
    try:
        breaking = await live_news_service.get_breaking_news(limit=5)
        print(f"✅ Success! Fetched {len(breaking)} breaking news articles")
        
        for i, article in enumerate(breaking[:3], 1):
            print(f"\n  {i}. {article['title']}")
            print(f"     Published: {article['published_at']}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Search functionality
    print("\n\n🔍 Test 4: Searching for 'India' news...")
    try:
        search_results = await live_news_service.search_news(query="India", limit=5)
        print(f"✅ Success! Found {len(search_results)} matching articles")
        
        for i, article in enumerate(search_results[:3], 1):
            print(f"\n  {i}. {article['title']}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 80)
    print("\n💡 Tips:")
    print("  - News is cached for 2 hours to avoid API rate limits")
    print("  - The service automatically falls back between NewsAPI → GNews → NewsData")
    print("  - Check news_cache.json for cached articles")
    print("\n")


if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_live_news())
