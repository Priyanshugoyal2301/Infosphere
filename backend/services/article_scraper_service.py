"""
Article Scraper Service
Scrapes full article content from URLs for Reader Mode
"""

import aiohttp
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ArticleScraperService:
    """Service for scraping full article content from URLs"""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def scrape_article(self, url: str) -> Dict[str, any]:
        """
        Scrape full article content from URL
        
        Args:
            url: Article URL to scrape
            
        Returns:
            Dictionary with title, content, author, published_date, and image_url
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch article: {url} (Status: {response.status})")
                        return {"error": f"Failed to fetch article (Status: {response.status})"}
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract article data
                    article_data = {
                        "url": url,
                        "title": self._extract_title(soup),
                        "content": self._extract_content(soup),
                        "author": self._extract_author(soup),
                        "published_date": self._extract_date(soup),
                        "image_url": self._extract_image(soup, url),
                        "source": self._extract_source(soup, url)
                    }
                    
                    logger.info(f"Successfully scraped article: {url}")
                    return article_data
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error scraping article {url}: {str(e)}")
            return {"error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error scraping article {url}: {str(e)}")
            return {"error": f"Scraping error: {str(e)}"}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try multiple common title locations
        title_selectors = [
            ('meta', {'property': 'og:title'}),
            ('meta', {'name': 'twitter:title'}),
            ('h1', {}),
            ('title', {})
        ]
        
        for tag_name, attrs in title_selectors:
            if attrs:
                tag = soup.find(tag_name, attrs)
                if tag:
                    return tag.get('content', '') if 'meta' in tag_name else tag.get_text(strip=True)
            else:
                tag = soup.find(tag_name)
                if tag:
                    return tag.get_text(strip=True)
        
        return "Untitled Article"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'form']):
            element.decompose()
        
        # Try to find article content using common selectors
        content_selectors = [
            ('article', {}),
            ('div', {'class': re.compile(r'article|content|post|story|entry', re.I)}),
            ('div', {'id': re.compile(r'article|content|post|story|entry', re.I)}),
            ('main', {}),
        ]
        
        content_parts = []
        
        for tag_name, attrs in content_selectors:
            if attrs:
                containers = soup.find_all(tag_name, attrs)
            else:
                containers = soup.find_all(tag_name)
            
            for container in containers:
                # Extract paragraphs from the container
                paragraphs = container.find_all(['p', 'h2', 'h3', 'blockquote'])
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 50:  # Only include substantial paragraphs
                        content_parts.append(text)
        
        # If we found content, join and return
        if content_parts:
            # Remove duplicates while preserving order
            seen = set()
            unique_parts = []
            for part in content_parts:
                if part not in seen:
                    seen.add(part)
                    unique_parts.append(part)
            
            return "\n\n".join(unique_parts)
        
        # Fallback: extract all paragraphs
        paragraphs = soup.find_all('p')
        fallback_content = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:
                fallback_content.append(text)
        
        return "\n\n".join(fallback_content) if fallback_content else "Content not available"
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author"""
        author_selectors = [
            ('meta', {'name': 'author'}),
            ('meta', {'property': 'article:author'}),
            ('span', {'class': re.compile(r'author', re.I)}),
            ('div', {'class': re.compile(r'author', re.I)}),
            ('a', {'rel': 'author'})
        ]
        
        for tag_name, attrs in author_selectors:
            tag = soup.find(tag_name, attrs)
            if tag:
                return tag.get('content', '') if 'meta' in tag_name else tag.get_text(strip=True)
        
        return None
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date"""
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'pubdate'}),
            ('meta', {'name': 'publishdate'}),
            ('meta', {'property': 'og:published_time'}),
            ('time', {'datetime': True}),
            ('span', {'class': re.compile(r'date|time', re.I)})
        ]
        
        for tag_name, attrs in date_selectors:
            tag = soup.find(tag_name, attrs)
            if tag:
                date = tag.get('content') or tag.get('datetime') or tag.get_text(strip=True)
                if date:
                    return date
        
        return None
    
    def _extract_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract main article image"""
        image_selectors = [
            ('meta', {'property': 'og:image'}),
            ('meta', {'name': 'twitter:image'}),
            ('img', {'class': re.compile(r'featured|hero|main', re.I)})
        ]
        
        for tag_name, attrs in image_selectors:
            tag = soup.find(tag_name, attrs)
            if tag:
                img_url = tag.get('content') or tag.get('src')
                if img_url:
                    # Make absolute URL if relative
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        parsed = urlparse(base_url)
                        img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
                    return img_url
        
        return None
    
    def _extract_source(self, soup: BeautifulSoup, url: str) -> str:
        """Extract source/publisher name"""
        source_selectors = [
            ('meta', {'property': 'og:site_name'}),
            ('meta', {'name': 'application-name'}),
        ]
        
        for tag_name, attrs in source_selectors:
            tag = soup.find(tag_name, attrs)
            if tag:
                source = tag.get('content', '')
                if source:
                    return source
        
        # Fallback to domain name
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain.split('.')[0].title()

# Global instance
_scraper_service = None

def get_article_scraper() -> ArticleScraperService:
    """Get or create the global article scraper service instance"""
    global _scraper_service
    if _scraper_service is None:
        _scraper_service = ArticleScraperService()
    return _scraper_service
