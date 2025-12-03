"""
Simple direct test of live news service
"""
import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    print("Importing service...")
    from backend.services.live_news_service import live_news_service
    
    print("Fetching news...")
    news = await live_news_service.fetch_live_news(limit=5)
    
    print(f"\nGot {len(news)} articles")
    
    if news:
        print("\nFirst article:")
        print(f"  Title: {news[0]['title']}")
        print(f"  Source: {news[0]['source']}")
        print(f"  API: {news[0]['api_source']}")
    else:
        print("No articles fetched!")

asyncio.run(test())
