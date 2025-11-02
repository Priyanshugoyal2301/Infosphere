"""
Authentication API Endpoints for Infosphere
===========================================

FastAPI endpoints for user registration, login, and session management.
Uses file-based storage for user data.

Author: Infosphere Team
Date: November 2024
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import sys
import os

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from backend.services.auth_service import (
        UserCreate, UserLogin, UserResponse, 
        register_new_user, login_user, validate_user_session, logout_user_session,
        auth_service
    )
except ImportError:
    # Try relative import
    from ...services.auth_service import (
        UserCreate, UserLogin, UserResponse, 
        register_new_user, login_user, validate_user_session, logout_user_session,
        auth_service
    )

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """
    Register a new user account.
    
    - **username**: Unique username (3-20 characters)
    - **email**: Valid email address
    - **password**: Password (minimum 6 characters)
    - **full_name**: User's full name
    """
    try:
        # Basic validation
        if len(user_data.username) < 3 or len(user_data.username) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be between 3 and 20 characters"
            )
        
        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        if len(user_data.full_name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Full name is required"
            )
        
        user = register_new_user(user_data)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login")
async def login(login_data: UserLogin):
    """
    Login with username and password.
    
    Returns user data and session token on successful authentication.
    """
    try:
        result = login_user(login_data)
        return {
            "success": True,
            "user": result["user"],
            "session_token": result["session_token"],
            "message": result["message"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: str = Header(None)):
    """
    Get current user information using session token.
    
    Requires Authorization header with Bearer token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    session_token = authorization.replace("Bearer ", "")
    user = validate_user_session(session_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return user

@router.post("/logout")
async def logout(authorization: str = Header(None)):
    """
    Logout user and invalidate session token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    session_token = authorization.replace("Bearer ", "")
    success = logout_user_session(session_token)
    
    return {
        "success": success,
        "message": "Logout successful" if success else "Session not found"
    }

@router.get("/validate")
async def validate_session(authorization: str = Header(None)):
    """
    Validate session token without returning full user data.
    
    Returns basic validation status.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return {"valid": False, "message": "Missing authorization header"}
    
    session_token = authorization.replace("Bearer ", "")
    user = validate_user_session(session_token)
    
    return {
        "valid": user is not None,
        "username": user.username if user else None,
        "message": "Valid session" if user else "Invalid or expired session"
    }

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(authorization: str = Header(None)):
    """
    Get all registered users (for admin purposes).
    
    Requires valid session token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    session_token = authorization.replace("Bearer ", "")
    user = validate_user_session(session_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    users = auth_service.get_all_users()
    return users

@router.get("/stats")
async def get_user_statistics(authorization: str = Header(None)):
    """
    Get user registration and session statistics.
    
    Requires valid session token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    session_token = authorization.replace("Bearer ", "")
    user = validate_user_session(session_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    stats = auth_service.get_user_stats()
    return {
        "success": True,
        "stats": stats,
        "message": "Statistics retrieved successfully"
    }

# Health check for auth service
@router.get("/health")
async def auth_health_check():
    """
    Check authentication service health.
    """
    try:
        stats = auth_service.get_user_stats()
        return {
            "status": "healthy",
            "service": "authentication",
            "version": "1.0.0",
            "total_users": stats["total_users"],
            "active_sessions": stats["active_sessions"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auth service unhealthy: {str(e)}"
        )