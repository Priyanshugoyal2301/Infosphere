from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime
import os
import json
import uuid

from database.database import get_session
from database.models import Complaint, ComplaintCreate, ComplaintResponse, StatusUpdate
from services.cit_service import CITService

router = APIRouter()

@router.post("/report", response_model=ComplaintResponse)
async def report_issue(
    title: str = Form(...),
    description: str = Form(...),
    location: Optional[str] = Form(None),
    contact_info: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    videos: Optional[List[UploadFile]] = File(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    session: Session = Depends(get_session)
):
    """
    Report a new citizen issue.
    
    This endpoint:
    1. Receives the complaint data
    2. Uses CIT AI model to classify and prioritize
    3. Stores in database with initial status
    4. Returns complaint ID and routing information
    """
    try:
        # Initialize CIT service
        cit_service = CITService()
        
        # Classify the complaint using AI
        classification_result = await cit_service.classify_complaint(
            text=description,
            location=location
        )
        
        # Prepare upload directories
        base_upload_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
        )
        uploads_dir = os.path.join(base_upload_dir, 'uploads')
        images_dir = os.path.join(uploads_dir, 'images')
        videos_dir = os.path.join(uploads_dir, 'videos')
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(videos_dir, exist_ok=True)

        saved_images: List[str] = []
        saved_videos: List[str] = []
        saved_geotag: Optional[str] = None

        # Save uploaded files to disk
        if images:
            for f in images:
                unique_name = f"{uuid.uuid4().hex}_{f.filename}"
                file_path = os.path.join(images_dir, unique_name)
                with open(file_path, 'wb') as out:
                    out.write(await f.read())
                saved_images.append(file_path)

        if videos:
            for f in videos:
                unique_name = f"{uuid.uuid4().hex}_{f.filename}"
                file_path = os.path.join(videos_dir, unique_name)
                with open(file_path, 'wb') as out:
                    out.write(await f.read())
                saved_videos.append(file_path)

        # No file-based geotag; latitude/longitude captured if provided

        # Create complaint record
        complaint = Complaint(
            title=title,
            description=description,
            location=location,
            contact_info=contact_info,
            category=classification_result["category"],
            urgency=classification_result["urgency"],
            confidence_score=classification_result["confidence"],
            status="submitted",
            created_at=datetime.utcnow()
        )
        
        session.add(complaint)
        session.commit()
        session.refresh(complaint)
        
        # Create initial status update
        status_update = StatusUpdate(
            complaint_id=complaint.id,
            status="submitted",
            message="Complaint submitted and classified",
            created_at=datetime.utcnow()
        )
        session.add(status_update)
        session.commit()

        # Append submission to file-based user database (JSONL)
        data_dir = os.path.join(base_upload_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        db_file = os.path.join(data_dir, 'user_submissions.jsonl')
        record = {
            "id": complaint.id,
            "title": title,
            "description": description,
            "location": location,
            "contact_info": contact_info,
            "category": complaint.category,
            "urgency": complaint.urgency,
            "confidence_score": complaint.confidence_score,
            "created_at": complaint.created_at.isoformat(),
            "images": saved_images,
            "videos": saved_videos,
            "geotag": saved_geotag,
            "latitude": latitude,
            "longitude": longitude
        }
        with open(db_file, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        return ComplaintResponse(
            id=complaint.id,
            title=complaint.title,
            category=complaint.category,
            urgency=complaint.urgency,
            status=complaint.status,
            confidence_score=complaint.confidence_score,
            created_at=complaint.created_at,
            estimated_resolution="2-5 business days"  # TODO: Dynamic estimation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing complaint: {str(e)}")

@router.get("/{complaint_id}/status")
async def get_complaint_status(
    complaint_id: int,
    session: Session = Depends(get_session)
):
    """
    Get detailed status history and timeline for a complaint.
    
    Returns complete audit trail for E-commerce style tracking.
    """
    try:
        # Get complaint
        complaint = session.get(Complaint, complaint_id)
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        # Get all status updates
        status_updates = session.query(StatusUpdate).filter(
            StatusUpdate.complaint_id == complaint_id
        ).order_by(StatusUpdate.created_at).all()
        
        return {
            "complaint": {
                "id": complaint.id,
                "title": complaint.title,
                "category": complaint.category,
                "urgency": complaint.urgency,
                "current_status": complaint.status,
                "created_at": complaint.created_at
            },
            "status_history": [
                {
                    "status": update.status,
                    "message": update.message,
                    "timestamp": update.created_at
                }
                for update in status_updates
            ],
            "progress_percentage": _calculate_progress(complaint.status)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving status: {str(e)}")

@router.get("/")
async def list_complaints(
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """
    List complaints with optional filtering.
    """
    try:
        query = session.query(Complaint)
        
        if category:
            query = query.filter(Complaint.category == category)
        if status:
            query = query.filter(Complaint.status == status)
            
        complaints = query.offset(offset).limit(limit).all()
        
        return {
            "complaints": [
                {
                    "id": complaint.id,
                    "title": complaint.title,
                    "category": complaint.category,
                    "urgency": complaint.urgency,
                    "status": complaint.status,
                    "created_at": complaint.created_at
                }
                for complaint in complaints
            ],
            "total": query.count()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing complaints: {str(e)}")

def _calculate_progress(status: str) -> int:
    """Calculate progress percentage based on status"""
    status_progress = {
        "submitted": 10,
        "under_review": 25,
        "assigned": 40,
        "in_progress": 65,
        "testing": 85,
        "resolved": 100,
        "closed": 100
    }
    return status_progress.get(status, 0)