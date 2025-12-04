"""
Admin Reports API Endpoints
Handles CRUD operations for report management
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["admin"])

# Path to reports data file
REPORTS_FILE = Path(__file__).parent.parent.parent.parent / "backend" / "data" / "reports.json"

def load_reports() -> List[Dict[str, Any]]:
    """Load reports from JSON file"""
    if not REPORTS_FILE.exists():
        REPORTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(REPORTS_FILE, 'w') as f:
            json.dump([], f)
        return []
    
    try:
        with open(REPORTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading reports: {e}")
        return []

def save_reports(reports: List[Dict[str, Any]]) -> bool:
    """Save reports to JSON file"""
    try:
        REPORTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(REPORTS_FILE, 'w') as f:
            json.dump(reports, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving reports: {e}")
        return False

@router.get("/reports")
async def get_all_reports():
    """
    Get all submitted reports
    Admin only endpoint
    """
    reports = load_reports()
    # Sort by submitted_at descending (newest first)
    reports.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
    return reports

@router.put("/reports/{report_id}/approve")
async def approve_report(report_id: str):
    """
    Approve a pending report
    """
    reports = load_reports()
    
    # Find and update the report
    report_found = False
    for report in reports:
        if report.get('id') == report_id:
            report['status'] = 'approved'
            report['reviewed_at'] = datetime.utcnow().isoformat()
            report_found = True
            break
    
    if not report_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if save_reports(reports):
        return {"message": "Report approved successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save report"
        )

@router.put("/reports/{report_id}/reject")
async def reject_report(report_id: str):
    """
    Reject a pending report
    """
    reports = load_reports()
    
    # Find and update the report
    report_found = False
    for report in reports:
        if report.get('id') == report_id:
            report['status'] = 'rejected'
            report['reviewed_at'] = datetime.utcnow().isoformat()
            report_found = True
            break
    
    if not report_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if save_reports(reports):
        return {"message": "Report rejected successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save report"
        )

@router.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    """
    Delete a report permanently
    """
    reports = load_reports()
    
    # Filter out the report to delete
    original_count = len(reports)
    reports = [r for r in reports if r.get('id') != report_id]
    
    if len(reports) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if save_reports(reports):
        return {"message": "Report deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )

@router.get("/reports/stats")
async def get_report_stats():
    """
    Get statistics about reports
    """
    reports = load_reports()
    
    total = len(reports)
    pending = len([r for r in reports if r.get('status') == 'pending'])
    approved = len([r for r in reports if r.get('status') == 'approved'])
    rejected = len([r for r in reports if r.get('status') == 'rejected'])
    
    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected
    }
