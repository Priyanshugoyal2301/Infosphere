"""
Enhanced Verification Endpoints
Integrates all advanced verification features
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path

# Add parent directory to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from backend.services.temporal_verification_service import temporal_checker
from backend.services.citation_analysis_service import citation_analyzer
from backend.services.image_verification_service import image_verifier
from backend.services.network_analysis_service import network_analyzer

router = APIRouter()


class VerifyArticleRequest(BaseModel):
    url: str
    title: str
    content: str
    source: str
    image_url: Optional[str] = None
    claims: Optional[List[str]] = []


class VerifyQuoteRequest(BaseModel):
    quote: str
    attributed_to: str
    topic: Optional[str] = None


class CitationRequest(BaseModel):
    citing_source: str
    cited_source: str
    article_url: str


@router.post("/enhanced-verify")
async def enhanced_verify_article(request: VerifyArticleRequest):
    """
    Comprehensive article verification using all advanced features
    """
    results = {
        "url": request.url,
        "title": request.title,
        "source": request.source,
        "overall_score": 0.0,
        "verifications": {
            "temporal": None,
            "citations": [],
            "image": None,
            "network": None
        },
        "warnings": [],
        "flags": []
    }
    
    try:
        # 1. Temporal Fact-Checking
        if request.claims:
            for claim in request.claims:
                claim_id = temporal_checker.add_claim(
                    claim=claim,
                    source=request.source,
                    article_url=request.url
                )
                
                # Check for contradictions
                timeline = temporal_checker.get_source_timeline(request.source)
                contradictions = [c for c in timeline if c.get("contradictions")]
                
                if contradictions:
                    results["warnings"].append(f"Source has {len(contradictions)} contradictory claims")
                    results["flags"].append("TEMPORAL_CONTRADICTION")
                    results["overall_score"] -= 0.2
        
        # Check narrative shift
        narrative_shift = temporal_checker.check_narrative_shift(request.source, days=30)
        if narrative_shift["shift_detected"]:
            results["warnings"].append(f"Narrative shift detected: {narrative_shift['contradictory_claims']} inconsistencies")
            results["flags"].append("NARRATIVE_SHIFT")
        
        results["verifications"]["temporal"] = narrative_shift
        
        # 2. Network Analysis
        circular = network_analyzer.detect_circular_reporting(request.source)
        if circular["circular"]:
            results["warnings"].append("Source part of circular citation network")
            results["flags"].append("CIRCULAR_REPORTING")
            results["overall_score"] -= 0.3
        
        trust_score = network_analyzer.calculate_trust_score(request.source)
        results["verifications"]["network"] = {
            "trust_score": trust_score,
            "circular_reporting": circular,
            "citation_network": network_analyzer.get_citation_network(request.source, depth=1)
        }
        
        results["overall_score"] += trust_score * 0.4
        
        # 3. Image Verification
        if request.image_url:
            image_verification = await image_verifier.verify_image(request.image_url)
            results["verifications"]["image"] = image_verification
            
            if image_verification["is_stock_photo"]:
                results["warnings"].append("Article uses stock photo")
                results["flags"].append("STOCK_PHOTO")
            
            if image_verification["warnings"]:
                results["flags"].append("IMAGE_SUSPICIOUS")
                results["overall_score"] -= 0.15
        
        # 4. Quote Verification (if PM/official mentioned)
        pm_keywords = ["pm", "prime minister", "modi", "minister"]
        if any(keyword in request.content.lower() for keyword in pm_keywords):
            # Extract potential quotes (simple regex)
            import re
            quotes = re.findall(r'"([^"]*)"', request.content)
            
            for quote in quotes[:3]:  # Check first 3 quotes
                if len(quote) > 20:  # Skip short quotes
                    verification = await citation_analyzer.verify_pm_statement(quote)
                    results["verifications"]["citations"].append({
                        "quote": quote,
                        "verification": verification
                    })
                    
                    if verification["verified"]:
                        results["overall_score"] += 0.2
                    else:
                        results["warnings"].append(f"Unverified quote: {quote[:50]}...")
                        results["flags"].append("UNVERIFIED_QUOTE")
        
        # Clamp overall score
        results["overall_score"] = max(0.0, min(1.0, 0.7 + results["overall_score"]))
        
        # Determine verdict
        if results["overall_score"] >= 0.8:
            results["verdict"] = "VERIFIED"
        elif results["overall_score"] >= 0.6:
            results["verdict"] = "NEEDS_REVIEW"
        else:
            results["verdict"] = "QUESTIONABLE"
        
        return {"success": True, "data": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post("/verify-quote")
async def verify_quote(request: VerifyQuoteRequest):
    """Verify a quote against official sources"""
    try:
        result = await citation_analyzer.verify_quote(
            quote=request.quote,
            attributed_to=request.attributed_to,
            topic=request.topic
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-citation")
async def add_citation(request: CitationRequest):
    """Add a citation to the network"""
    try:
        network_analyzer.add_citation(
            citing_source=request.citing_source,
            cited_source=request.cited_source,
            article_url=request.article_url
        )
        return {"success": True, "message": "Citation added to network"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network-analysis/{source}")
async def get_network_analysis(source: str):
    """Get complete network analysis for a source"""
    try:
        circular = network_analyzer.detect_circular_reporting(source)
        trust_score = network_analyzer.calculate_trust_score(source)
        network = network_analyzer.get_citation_network(source, depth=2)
        
        return {
            "success": True,
            "data": {
                "source": source,
                "trust_score": trust_score,
                "circular_reporting": circular,
                "network": network
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/echo-chambers")
async def get_echo_chambers():
    """Identify echo chambers in the citation network"""
    try:
        chambers = network_analyzer.identify_echo_chambers()
        return {
            "success": True,
            "data": {
                "count": len(chambers),
                "chambers": [list(chamber) for chamber in chambers]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/source-timeline/{source}")
async def get_source_timeline(source: str):
    """Get temporal timeline for a source"""
    try:
        timeline = temporal_checker.get_source_timeline(source)
        narrative_shift = temporal_checker.check_narrative_shift(source, days=60)
        
        return {
            "success": True,
            "data": {
                "source": source,
                "timeline": timeline,
                "narrative_analysis": narrative_shift
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
