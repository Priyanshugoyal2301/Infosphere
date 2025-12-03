"""
Debug script to test live news APIs with detailed error output
"""

import asyncio
import sys
import os
import httpx

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


async def test_newsapi():
    """Test NewsAPI directly"""
    print("\n" + "="*80)
    print("🔍 TESTING NEWSAPI.ORG")
    print("="*80)
    
    api_key = os.getenv("NEWSAPI_KEY")
    print(f"API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'NOT FOUND'}")
    
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "country": "in",
        "pageSize": 5
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n📡 Requesting: {url}")
            print(f"📋 Params: country=in, pageSize=5")
            
            response = await client.get(url, params=params)
            
            print(f"\n📊 Response Status: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS!")
                print(f"Total Results: {data.get('totalResults', 0)}")
                print(f"Articles Received: {len(data.get('articles', []))}")
                
                if data.get('articles'):
                    print("\n📰 Sample Article:")
                    article = data['articles'][0]
                    print(f"  Title: {article.get('title', 'N/A')}")
                    print(f"  Source: {article.get('source', {}).get('name', 'N/A')}")
                    print(f"  Published: {article.get('publishedAt', 'N/A')}")
            else:
                print(f"\n❌ ERROR!")
                print(f"Response Body: {response.text}")
                
    except Exception as e:
        print(f"\n❌ EXCEPTION: {type(e).__name__}")
        print(f"Message: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_gnews():
    """Test GNews API directly"""
    print("\n" + "="*80)
    print("🔍 TESTING GNEWS API")
    print("="*80)
    
    api_key = os.getenv("GNEWS_API_KEY")
    print(f"API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'NOT FOUND'}")
    
    url = "https://gnews.io/api/v4/top-headlines"
    params = {
        "apikey": api_key,
        "country": "in",
        "lang": "en",
        "max": 5
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n📡 Requesting: {url}")
            print(f"📋 Params: country=in, lang=en, max=5")
            
            response = await client.get(url, params=params)
            
            print(f"\n📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS!")
                print(f"Total Results: {data.get('totalArticles', 0)}")
                print(f"Articles Received: {len(data.get('articles', []))}")
                
                if data.get('articles'):
                    print("\n📰 Sample Article:")
                    article = data['articles'][0]
                    print(f"  Title: {article.get('title', 'N/A')}")
                    print(f"  Source: {article.get('source', {}).get('name', 'N/A')}")
                    print(f"  Published: {article.get('publishedAt', 'N/A')}")
            else:
                print(f"\n❌ ERROR!")
                print(f"Response Body: {response.text}")
                
    except Exception as e:
        print(f"\n❌ EXCEPTION: {type(e).__name__}")
        print(f"Message: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_newsdata():
    """Test NewsData.io API directly"""
    print("\n" + "="*80)
    print("🔍 TESTING NEWSDATA.IO")
    print("="*80)
    
    api_key = os.getenv("NEWSDATA_API_KEY")
    print(f"API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'NOT FOUND'}")
    
    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": api_key,
        "country": "in",
        "language": "en"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n📡 Requesting: {url}")
            print(f"📋 Params: country=in, language=en")
            
            response = await client.get(url, params=params)
            
            print(f"\n📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS!")
                print(f"Total Results: {data.get('totalResults', 0)}")
                print(f"Articles Received: {len(data.get('results', []))}")
                
                if data.get('results'):
                    print("\n📰 Sample Article:")
                    article = data['results'][0]
                    print(f"  Title: {article.get('title', 'N/A')}")
                    print(f"  Source: {article.get('source_id', 'N/A')}")
                    print(f"  Published: {article.get('pubDate', 'N/A')}")
            else:
                print(f"\n❌ ERROR!")
                print(f"Response Body: {response.text}")
                
    except Exception as e:
        print(f"\n❌ EXCEPTION: {type(e).__name__}")
        print(f"Message: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 DEBUGGING LIVE NEWS APIs")
    print("="*80)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("❌ .env file NOT found!")
        return
    
    # Test each API
    await test_newsapi()
    await test_gnews()
    await test_newsdata()
    
    print("\n" + "="*80)
    print("✅ DEBUG TESTS COMPLETED")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
