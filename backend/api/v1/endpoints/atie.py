"""
ATIE (AI Trust and Integrity Engine) API Endpoints
================================================

Endpoints for textual integrity analysis, fake news classification,
and cross-verification against trusted sources.
"""

from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
import logging

# Import the offline ATIE service for reliability
from services.offline_atie_service import atie_service, get_textual_trust_score

router = APIRouter(prefix="/atie", tags=["atie"])
logger = logging.getLogger(__name__)


class TextAnalysisRequest(BaseModel):
    """Request model for textual integrity analysis"""
    text: str = Field(..., description="Text content to analyze", min_length=10)
    source_url: Optional[str] = Field(None, description="Optional source URL")
    enable_cross_verification: bool = Field(
        True, 
        description="Enable cross-verification against trusted sources (slower but more accurate)"
    )
    cache_result: bool = Field(True, description="Cache result for faster future lookups")

class CompositeAnalysisRequest(BaseModel):
    """Request model for composite media + text analysis"""
    text: str = Field(..., description="Text content to analyze")
    media_data: Optional[Dict] = Field(None, description="Optional media analysis result")
    source_url: Optional[str] = Field(None, description="Optional source URL")


@router.post("/analyze-text")
async def analyze_textual_integrity(request: TextAnalysisRequest):
    """
    Analyze textual content for integrity, fake news, bias, and sensationalism
    
    Returns comprehensive ATIE Trust Score with detailed breakdown.
    """
    try:
        result = await atie_service.analyze_textual_integrity(
            text=request.text,
            source_url=request.source_url,
            enable_cross_verification=request.enable_cross_verification,
            cache_result=request.cache_result
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Textual integrity analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in textual integrity analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/analyze-composite")
async def analyze_composite_integrity(request: CompositeAnalysisRequest):
    """
    Analyze both textual and media content for comprehensive Trust Score
    
    Combines ATIE textual analysis with MIE media analysis for unified score.
    """
    try:
        # Get textual analysis
        textual_result = await atie_service.analyze_textual_integrity(
            text=request.text,
            source_url=request.source_url
        )
        
        # If media analysis is provided, combine scores
        if request.media_data:
            media_trust_score = request.media_data.get('trust_score', {}).get('overall_score', 50)
            
            # Calculate composite score (weighted average)
            text_score = textual_result['atie_trust_score']['score']
            composite_score = (text_score * 0.6) + (media_trust_score * 0.4)  # Text weighted higher
            
            composite_result = {
                "composite_trust_score": {
                    "score": round(composite_score, 2),
                    "components": {
                        "textual_score": text_score,
                        "media_score": media_trust_score,
                        "weights": {"text": 0.6, "media": 0.4}
                    },
                    "trust_level": _get_trust_level(composite_score),
                    "recommendation": _get_composite_recommendation(composite_score, text_score, media_trust_score)
                },
                "textual_analysis": textual_result,
                "media_analysis": request.media_data
            }
        else:
            # Only textual analysis available
            composite_result = {
                "composite_trust_score": textual_result['atie_trust_score'],
                "textual_analysis": textual_result,
                "media_analysis": None
            }
        
        return {
            "success": True,
            "data": composite_result,
            "message": "Composite integrity analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in composite analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Composite analysis failed: {str(e)}"
        )


@router.get("/quick-check")
async def quick_text_check(
    text: str = Query(..., description="Text to analyze", min_length=10),
    source_url: Optional[str] = Query(None, description="Optional source URL")
):
    """
    Quick textual integrity check (fast, cached results)
    
    Optimized for speed with caching and minimal cross-verification.
    """
    try:
        # Quick analysis without extensive cross-verification
        result = await atie_service.analyze_textual_integrity(
            text=text,
            source_url=source_url,
            enable_cross_verification=False,  # Faster
            cache_result=True
        )
        
        # Return simplified response
        trust_score = result['atie_trust_score']
        return {
            "success": True,
            "data": {
                "trust_score": trust_score['score'],
                "trust_level": trust_score['trust_level'],
                "recommendation": trust_score['recommendation'],
                "analysis_time": result['metadata']['analysis_time'],
                "from_cache": result['metadata'].get('from_cache', False)
            },
            "message": "Quick integrity check completed"
        }
        
    except Exception as e:
        logger.error(f"Error in quick check: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quick check failed: {str(e)}"
        )


@router.get("/verify-claims")
async def verify_text_claims(
    text: str = Query(..., description="Text containing claims to verify"),
    max_claims: int = Query(5, description="Maximum number of claims to extract", ge=1, le=10)
):
    """
    Extract and verify key claims from text against trusted sources
    """
    try:
        # Extract claims
        claims = atie_service.cross_verifier.extract_key_claims(text)
        claims = claims[:max_claims]
        
        if not claims:
            return {
                "success": True,
                "data": {
                    "claims_found": 0,
                    "message": "No verifiable claims found in the text"
                }
            }
        
        # Verify claims
        verification_result = await atie_service.cross_verifier.verify_claims(claims)
        
        return {
            "success": True,
            "data": {
                "claims_found": len(claims),
                "verification_summary": {
                    "verified": verification_result['verified_claims'],
                    "total": verification_result['total_claims'],
                    "overall_score": verification_result['overall_verification_score']
                },
                "claim_details": verification_result['claim_details']
            },
            "message": f"Verified {len(claims)} claims against trusted sources"
        }
        
    except Exception as e:
        logger.error(f"Error in claim verification: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Claim verification failed: {str(e)}"
        )


@router.get("/trusted-sources")
async def get_trusted_sources():
    """
    Get list of trusted news sources used for cross-verification
    """
    try:
        sources = atie_service.trusted_db.trusted_sources
        
        # Format for API response
        formatted_sources = [
            {
                "domain": domain,
                "credibility_score": info["credibility"],
                "bias_rating": info["bias"],
                "factual_reporting": info["factual"]
            }
            for domain, info in sources.items()
        ]
        
        return {
            "success": True,
            "data": {
                "total_sources": len(formatted_sources),
                "sources": formatted_sources
            },
            "message": "Retrieved trusted sources database"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving trusted sources: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve trusted sources: {str(e)}"
        )


@router.get("/cache-stats")
async def get_cache_statistics():
    """
    Get ATIE cache performance statistics
    """
    try:
        stats = atie_service.get_cache_stats()
        
        return {
            "success": True,
            "data": stats,
            "message": "Retrieved cache statistics"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cache stats: {str(e)}"
        )


@router.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """
    Accept a document upload (PDF or text), extract text, and run ATIE analysis.
    """
    try:
        content_type = file.content_type or ''
        text_content = ''

        page_count = None
        if content_type == 'application/pdf' or file.filename.lower().endswith('.pdf'):
            try:
                import pdfplumber  # type: ignore
                import io
                raw = await file.read()
                with pdfplumber.open(io.BytesIO(raw)) as pdf:
                    pages_text = [p.extract_text() or '' for p in pdf.pages]
                    page_count = len(pdf.pages)
                text_content = "\n\n".join(pages_text).strip()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {e}")
        else:
            raw_bytes = await file.read()
            try:
                text_content = raw_bytes.decode('utf-8', errors='ignore')
            except Exception:
                text_content = raw_bytes.decode('latin-1', errors='ignore')

        if not text_content or len(text_content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Document does not contain readable text")

        result = await atie_service.analyze_textual_integrity(
            text=text_content,
            enable_cross_verification=True,
            cache_result=True
        )

        document_report = {
            "filename": file.filename,
            "content_type": content_type,
            "page_count": page_count,
            "character_count": len(text_content),
            "preview": text_content[:1200]
        }

        return {"success": True, "data": result, "document_report": document_report}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {e}")

@router.get("/health")
async def atie_health_check():
    """
    ATIE service health check
    """
    try:
        # Test basic functionality
        test_text = "This is a test article to verify ATIE functionality."
        test_result = await atie_service.analyze_textual_integrity(
            text=test_text,
            enable_cross_verification=False,
            cache_result=False
        )
        
        cache_stats = atie_service.get_cache_stats()
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "components": {
                    "textual_analyzer": "operational",
                    "cross_verifier": "operational",
                    "cache": "operational" if cache_stats.get("connected") else "degraded",
                    "trusted_sources_db": "operational"
                },
                "test_analysis_time": test_result['metadata']['analysis_time'],
                "cache_type": cache_stats.get("cache_type", "unknown")
            },
            "message": "ATIE service is healthy and operational"
        }
        
    except Exception as e:
        logger.error(f"ATIE health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            },
            "message": "ATIE service health check failed"
        }


# Helper functions
def _get_trust_level(score: float) -> str:
    """Convert numeric score to trust level"""
    if score >= 85:
        return "very_high"
    elif score >= 70:
        return "high"
    elif score >= 50:
        return "moderate"
    elif score >= 30:
        return "low"
    else:
        return "very_low"


def _get_composite_recommendation(composite_score: float, text_score: float, media_score: float) -> str:
    """Generate recommendation for composite analysis"""
    if composite_score >= 85:
        return "Both textual and media content show high integrity. Content appears trustworthy."
    elif composite_score >= 70:
        return "Generally reliable content with good integrity across text and media components."
    elif composite_score >= 50:
        if abs(text_score - media_score) > 20:
            return "Mixed integrity signals. Significant discrepancy between text and media analysis."
        else:
            return "Moderate integrity. Verify from additional sources before sharing."
    else:
        return "Low integrity detected in content. Exercise strong caution and verify independently."