from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from sqlmodel import Session
from typing import List, Optional, Dict, Any
import logging

# Try to import rate limiting (optional)
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False

from database.database import get_session
from database.models import Policy, PolicyCreate, PolicyResponse, SentimentScore
from services.policy_service import PolicyService
from services.pdf_policy_service import get_pdf_policy_analyzer

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize rate limiter (if available)
if RATE_LIMITING_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
else:
    limiter = None

@router.post("/", response_model=PolicyResponse)
async def create_policy(
    policy_data: PolicyCreate,
    session: Session = Depends(get_session)
):
    """
    Create a new policy document and generate AI summary.
    
    This endpoint:
    1. Stores the policy document
    2. Generates AI summary using BART
    3. Initializes sentiment tracking
    """
    try:
        policy_service = PolicyService()
        
        # Generate AI summary
        summary_result = await policy_service.generate_summary(policy_data.content)
        
        # Create policy record
        policy = Policy(
            title=policy_data.title,
            content=policy_data.content,
            ai_summary=summary_result["summary"],
            category=policy_data.category,
            status="active"
        )
        
        session.add(policy)
        session.commit()
        session.refresh(policy)
        
        # Initialize sentiment tracking
        initial_sentiment = SentimentScore(
            policy_id=policy.id,
            positive_score=0.0,
            negative_score=0.0,
            neutral_score=1.0,
            total_comments=0
        )
        session.add(initial_sentiment)
        session.commit()
        
        return PolicyResponse(
            id=policy.id,
            title=policy.title,
            ai_summary=policy.ai_summary,
            category=policy.category,
            status=policy.status,
            created_at=policy.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating policy: {str(e)}")

@router.get("/{policy_id}")
async def get_policy(
    policy_id: int,
    session: Session = Depends(get_session)
):
    """
    Get policy details with AI summary and current sentiment.
    """
    try:
        # Get policy
        policy = session.get(Policy, policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Get latest sentiment scores
        sentiment = session.query(SentimentScore).filter(
            SentimentScore.policy_id == policy_id
        ).order_by(SentimentScore.updated_at.desc()).first()
        
        return {
            "policy": {
                "id": policy.id,
                "title": policy.title,
                "ai_summary": policy.ai_summary,
                "category": policy.category,
                "status": policy.status,
                "created_at": policy.created_at
            },
            "sentiment": {
                "positive_score": sentiment.positive_score if sentiment else 0.0,
                "negative_score": sentiment.negative_score if sentiment else 0.0,
                "neutral_score": sentiment.neutral_score if sentiment else 1.0,
                "total_comments": sentiment.total_comments if sentiment else 0,
                "last_updated": sentiment.updated_at if sentiment else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving policy: {str(e)}")

@router.post("/{policy_id}/comment")
async def add_policy_comment(
    policy_id: int,
    comment: dict,
    session: Session = Depends(get_session)
):
    """
    Add a public comment to a policy and update sentiment analysis.
    
    Args:
        policy_id: ID of the policy
        comment: {"text": "comment text", "author": "optional author"}
    """
    try:
        # Verify policy exists
        policy = session.get(Policy, policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Analyze comment sentiment
        policy_service = PolicyService()
        sentiment_result = await policy_service.analyze_sentiment(comment["text"])
        
        # Update sentiment scores
        sentiment_record = session.query(SentimentScore).filter(
            SentimentScore.policy_id == policy_id
        ).order_by(SentimentScore.updated_at.desc()).first()
        
        if sentiment_record:
            # Update existing sentiment (running average)
            total = sentiment_record.total_comments
            sentiment_record.positive_score = (
                (sentiment_record.positive_score * total + sentiment_result["positive"]) / (total + 1)
            )
            sentiment_record.negative_score = (
                (sentiment_record.negative_score * total + sentiment_result["negative"]) / (total + 1)
            )
            sentiment_record.neutral_score = (
                (sentiment_record.neutral_score * total + sentiment_result["neutral"]) / (total + 1)
            )
            sentiment_record.total_comments += 1
        else:
            # Create new sentiment record
            sentiment_record = SentimentScore(
                policy_id=policy_id,
                positive_score=sentiment_result["positive"],
                negative_score=sentiment_result["negative"],
                neutral_score=sentiment_result["neutral"],
                total_comments=1
            )
            session.add(sentiment_record)
        
        session.commit()
        
        return {
            "message": "Comment processed successfully",
            "sentiment_analysis": sentiment_result,
            "updated_scores": {
                "positive": sentiment_record.positive_score,
                "negative": sentiment_record.negative_score,
                "neutral": sentiment_record.neutral_score,
                "total_comments": sentiment_record.total_comments
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing comment: {str(e)}")

@router.get("/")
async def list_policies(
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """
    List policies with optional filtering.
    """
    try:
        query = session.query(Policy)
        
        if category:
            query = query.filter(Policy.category == category)
        if status:
            query = query.filter(Policy.status == status)
            
        policies = query.offset(offset).limit(limit).all()
        
        return {
            "policies": [
                {
                    "id": policy.id,
                    "title": policy.title,
                    "category": policy.category,
                    "status": policy.status,
                    "created_at": policy.created_at,
                    "summary_preview": policy.ai_summary[:200] + "..." if len(policy.ai_summary) > 200 else policy.ai_summary
                }
                for policy in policies
            ],
            "total": query.count()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing policies: {str(e)}")

@router.get("/sentiment/dashboard")
async def get_sentiment_dashboard(session: Session = Depends(get_session)):
    """
    Get overall sentiment dashboard data across all active policies.
    """
    try:
        # Get all active policies with their sentiment scores
        active_policies = session.query(Policy).filter(Policy.status == "active").all()
        
        dashboard_data = []
        for policy in active_policies:
            sentiment = session.query(SentimentScore).filter(
                SentimentScore.policy_id == policy.id
            ).order_by(SentimentScore.updated_at.desc()).first()
            
            if sentiment:
                dashboard_data.append({
                    "policy_id": policy.id,
                    "policy_title": policy.title,
                    "category": policy.category,
                    "positive_score": sentiment.positive_score,
                    "negative_score": sentiment.negative_score,
                    "neutral_score": sentiment.neutral_score,
                    "total_comments": sentiment.total_comments
                })
        
        return {"policies": dashboard_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")

@router.post("/upload-pdf", response_model=Dict[str, Any])
async def upload_policy_pdf(
    file: UploadFile = File(..., description="PDF policy document to analyze"),
    save_to_database: bool = Form(default=False, description="Save analysis to database"),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Upload and analyze a PDF policy document.
    
    This endpoint:
    1. Extracts text from the uploaded PDF
    2. Analyzes policy structure and content
    3. Generates AI summary and key insights
    4. Optionally saves to database
    
    Returns comprehensive analysis including:
    - Document structure (title, sections, key points)
    - AI-generated summary
    - Sentiment analysis
    - Stakeholder identification
    - Timeline extraction
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Check file size (limit to 10MB)
        max_file_size = 10 * 1024 * 1024  # 10MB
        contents = await file.read()
        if len(contents) > max_file_size:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
        
        # Reset file pointer for processing
        await file.seek(0)
        
        logger.info(f"📄 Processing PDF upload: {file.filename}")
        
        # Analyze PDF using the PDF policy analyzer
        analysis_result = get_pdf_policy_analyzer().analyze_policy_pdf(file.file, file.filename)
        
        if not analysis_result['success']:
            raise HTTPException(status_code=400, detail=f"PDF analysis failed: {analysis_result['error']}")
        
        # If requested, save to database
        if save_to_database:
            try:
                policy = Policy(
                    title=analysis_result['policy_structure']['title'],
                    content=analysis_result['full_text'],
                    ai_summary=analysis_result['summary']['summary'],
                    category="uploaded_pdf",
                    status="active"
                )
                
                session.add(policy)
                session.commit()
                session.refresh(policy)
                
                analysis_result['database_id'] = policy.id
                logger.info(f"💾 Policy saved to database with ID: {policy.id}")
                
            except Exception as db_error:
                logger.error(f"Database save failed: {db_error}")
                analysis_result['database_warning'] = f"Analysis successful but database save failed: {str(db_error)}"
        
        # Format response for frontend
        response = {
            "success": True,
            "message": "PDF analysis completed successfully",
            "analysis": analysis_result,
            "quick_insights": {
                "document_pages": analysis_result['extraction_metadata']['total_pages'],
                "word_count": analysis_result['extraction_metadata']['word_count'],
                "key_sections": len(analysis_result['policy_structure']['sections']),
                "main_stakeholders": analysis_result['policy_structure']['stakeholders'][:5],
                "sentiment": analysis_result['sentiment_analysis']['sentiment'],
                "summary_confidence": analysis_result['summary']['confidence']
            }
        }
        
        logger.info(f"✅ PDF analysis completed: {file.filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

@router.post("/analyze-text", response_model=Dict[str, Any])
async def analyze_policy_text(
    text: str = Form(..., description="Policy text to analyze"),
    title: str = Form(default="Policy Document", description="Document title")
) -> Dict[str, Any]:
    """
    Analyze policy text without PDF upload.
    
    Useful for:
    - Analyzing copied policy text
    - Quick policy analysis
    - Testing policy analysis features
    """
    try:
        logger.info(f"📝 Analyzing policy text: {title}")
        
        # Create a structure similar to PDF analysis
        structure = pdf_policy_analyzer.extract_policy_structure(text)
        structure['title'] = title
        
        # Generate summary
        summary_result = pdf_policy_analyzer.generate_summary(text)
        
        # Analyze sentiment
        sentiment_result = pdf_policy_analyzer.analyze_sentiment(text)
        
        response = {
            "success": True,
            "message": "Policy text analysis completed",
            "analysis": {
                "policy_structure": structure,
                "summary": summary_result,
                "sentiment_analysis": sentiment_result,
                "analysis_timestamp": "2025-10-31T00:00:00",
                "full_text": text[:2000] + "..." if len(text) > 2000 else text
            },
            "quick_insights": {
                "word_count": len(text.split()),
                "key_sections": len(structure['sections']),
                "main_stakeholders": structure['stakeholders'][:5],
                "sentiment": sentiment_result['sentiment'],
                "summary_confidence": summary_result['confidence']
            }
        }
        
        logger.info(f"✅ Policy text analysis completed: {title}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Policy text analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Policy analysis failed: {str(e)}")

# Conditional rate limiting decorator
if RATE_LIMITING_AVAILABLE and limiter:
    @router.post("/summarize", response_model=Dict[str, Any])
    @limiter.limit("5/minute")
    async def summarize_pdf(
        request: Request,
        file: UploadFile = File(..., description="PDF policy document to summarize"),
    ) -> Dict[str, Any]:
        return await _summarize_pdf_impl(file)
else:
    @router.post("/summarize", response_model=Dict[str, Any])
    async def summarize_pdf(
        file: UploadFile = File(..., description="PDF policy document to summarize"),
    ) -> Dict[str, Any]:
        return await _summarize_pdf_impl(file)

async def _summarize_pdf_impl(
    file: UploadFile,
) -> Dict[str, Any]:
    """
    Quick PDF summarization endpoint with AI-powered BART model.
    
    Optimized for fast summarization of policy documents with:
    - Automatic chunking for long documents
    - Hierarchical summarization 
    - Key points extraction
    - Rate limiting (5 requests/minute)
    
    Returns:
        - summary: AI-generated summary text
        - key_points: List of key sentences
        - metadata: Document info (pages, word count, etc.)
        - filename: Original filename
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are allowed. Please upload a .pdf file."
            )
        
        # Check file size (limit to 10MB)
        max_file_size = 10 * 1024 * 1024  # 10MB
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        if len(contents) > max_file_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large ({file_size_mb:.2f}MB). Maximum size is 10MB."
            )
        
        # Reset file pointer for processing
        await file.seek(0)
        
        logger.info(f"📄 Processing PDF summarization: {file.filename} ({file_size_mb:.2f}MB)")
        
        # Extract text from PDF (returns tuple: text, metadata)
        try:
            full_text, text_metadata = get_pdf_policy_analyzer().extract_text_from_pdf(file.file)
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to extract text from PDF: {str(e)}"
            )
        
        word_count = text_metadata.get('word_count', len(full_text.split()))
        total_pages = text_metadata.get('total_pages', 0)
        
        logger.info(f"📝 Extracted {word_count} words from {total_pages} pages")
        
        # Generate AI summary with chunking for long documents
        summary_result = pdf_policy_analyzer.generate_summary(full_text)
        
        if not summary_result or 'summary' not in summary_result:
            logger.warning(f"⚠️ AI summarization failed, using extractive fallback")
            # Fallback to extractive summarization
            summary_result = pdf_policy_analyzer.extractive_summary(full_text)
        
        # Prepare response
        response = {
            "success": True,
            "message": "PDF summarization completed successfully",
            "filename": file.filename,
            "summary": summary_result.get('summary', 'No summary available'),
            "key_points": summary_result.get('key_points', []),
            "metadata": {
                "total_pages": total_pages,
                "word_count": word_count,
                "file_size_mb": round(file_size_mb, 2),
                "model_used": summary_result.get('model', 'facebook/bart-large-cnn'),
                "processing_method": summary_result.get('method', 'transformer'),
                "confidence": summary_result.get('confidence', 'high'),
                "extraction_method": text_metadata.get('extraction_method', 'unknown')
            }
        }
        
        logger.info(f"✅ PDF summarization completed: {file.filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF summarization failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"PDF summarization failed: {str(e)}"
        )
