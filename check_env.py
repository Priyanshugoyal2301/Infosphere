"""Check if API keys are loaded"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Checking .env file...")
print(f"File exists: {os.path.exists('.env')}")

print("\nAPI Keys loaded:")
print(f"NEWSAPI_KEY: {os.getenv('NEWSAPI_KEY', 'NOT FOUND')[:20]}...")
print(f"GNEWS_API_KEY: {os.getenv('GNEWS_API_KEY', 'NOT FOUND')[:20]}...")
print(f"NEWSDATA_API_KEY: {os.getenv('NEWSDATA_API_KEY', 'NOT FOUND')[:20]}...")
