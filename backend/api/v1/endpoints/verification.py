"""
News Verification Endpoints
Provides advanced verification and flagged news tracking
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
import logging

from services.advanced_verification_service import advanced_verifier

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/verify-article")
async def verify_single_article(article: Dict) -> Dict:
    """
    Verify a single news article using advanced verification
    
    Returns comprehensive verification report including:
    - Overall verification score (0-1)
    - Individual check results
    - Flag status and reasons
    """
    try:
        logger.info(f"Verifying article: {article.get('title', 'Unknown')}")
        
        verification_result = await advanced_verifier.verify_article(article)
        
        return {
            "success": True,
            "verification": verification_result
        }
    
    except Exception as e:
        logger.error(f"Article verification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )


@router.get("/flagged-news")
async def get_flagged_news(
    limit: int = Query(50, ge=1, le=100, description="Number of flagged articles to return")
) -> Dict:
    """
    Get list of flagged news articles
    
    Returns articles that failed verification checks with:
    - Article details (title, URL, source)
    - Verification score
    - Flag reasons
    - Check summaries
    """
    try:
        flagged_articles = advanced_verifier.get_flagged_news(limit=limit)
        stats = advanced_verifier.get_flagged_stats()
        
        return {
            "success": True,
            "total_flagged": len(flagged_articles),
            "statistics": stats,
            "flagged_articles": flagged_articles
        }
    
    except Exception as e:
        logger.error(f"Failed to get flagged news: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve flagged news: {str(e)}"
        )


@router.get("/flagged-stats")
async def get_flagged_statistics() -> Dict:
    """
    Get statistics about flagged news articles
    
    Returns:
    - Total number of flagged articles
    - Most common flag reasons
    - Average verification scores
    """
    try:
        stats = advanced_verifier.get_flagged_stats()
        
        return {
            "success": True,
            "statistics": stats
        }
    
    except Exception as e:
        logger.error(f"Failed to get flagged stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.post("/batch-verify")
async def verify_batch_articles(articles: List[Dict]) -> Dict:
    """
    Verify multiple news articles in batch
    
    Useful for verifying entire news feed at once
    """
    try:
        logger.info(f"Batch verifying {len(articles)} articles")
        
        results = []
        flagged_count = 0
        
        for article in articles:
            verification = await advanced_verifier.verify_article(article)
            results.append(verification)
            if verification['is_flagged']:
                flagged_count += 1
        
        return {
            "success": True,
            "total_verified": len(results),
            "flagged_count": flagged_count,
            "verified_count": len(results) - flagged_count,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Batch verification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch verification failed: {str(e)}"
        )
