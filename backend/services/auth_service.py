"""
Authentication Service for Infosphere
=====================================

Handles user registration, login, and session management using file-based storage.
Provides secure authentication without requiring a database.

Author: Infosphere Team
Date: November 2024
"""

import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pydantic import BaseModel, EmailStr
from fastapi import HTTPException, status

# Data models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    created_at: str
    last_login: Optional[str]

class AuthService:
    """
    File-based authentication service for user management.
    """
    
    def __init__(self, data_file: str = "backend/data/users.json"):
        self.data_file = data_file
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Ensure the users data file exists."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            initial_data = {
                "users": [],
                "sessions": {},
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_users": 0,
                    "version": "1.0.0"
                }
            }
            with open(self.data_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def load_data(self) -> Dict:
        """Load user data from file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ensure_data_file()
            return self.load_data()
    
    def save_data(self, data: Dict):
        """Save user data to file."""
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(32)
    
    def create_user_id(self, username: str) -> str:
        """Create a unique user ID."""
        timestamp = str(int(datetime.now().timestamp()))
        return f"user_{hashlib.md5((username + timestamp).encode()).hexdigest()[:8]}"
    
    def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        data = self.load_data()
        
        # Check if username already exists
        for user in data["users"]:
            if user["username"].lower() == user_data.username.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            if user["email"].lower() == user_data.email.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        user_id = self.create_user_id(user_data.username)
        hashed_password = self.hash_password(user_data.password)
        
        new_user = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "password_hash": hashed_password,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True
        }
        
        data["users"].append(new_user)
        data["metadata"]["total_users"] = len(data["users"])
        self.save_data(data)
        
        # Return user without password hash
        return UserResponse(
            id=new_user["id"],
            username=new_user["username"],
            email=new_user["email"],
            full_name=new_user["full_name"],
            created_at=new_user["created_at"],
            last_login=new_user["last_login"]
        )
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[Dict]:
        """Authenticate user and return user data if valid."""
        data = self.load_data()
        hashed_password = self.hash_password(login_data.password)
        
        for user in data["users"]:
            if (user["username"].lower() == login_data.username.lower() and 
                user["password_hash"] == hashed_password and 
                user["is_active"]):
                
                # Update last login
                user["last_login"] = datetime.now().isoformat()
                self.save_data(data)
                
                return user
        
        return None
    
    def create_session(self, user: Dict) -> str:
        """Create a new session for the user."""
        data = self.load_data()
        session_token = self.generate_session_token()
        
        # Session expires in 24 hours
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        data["sessions"][session_token] = {
            "user_id": user["id"],
            "username": user["username"],
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "is_active": True
        }
        
        self.save_data(data)
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session token and return user data."""
        data = self.load_data()
        
        if session_token not in data["sessions"]:
            return None
        
        session = data["sessions"][session_token]
        
        # Check if session is expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at or not session["is_active"]:
            # Remove expired session
            del data["sessions"][session_token]
            self.save_data(data)
            return None
        
        # Find user
        for user in data["users"]:
            if user["id"] == session["user_id"] and user["is_active"]:
                return {
                    "user": user,
                    "session": session
                }
        
        return None
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user by invalidating session."""
        data = self.load_data()
        
        if session_token in data["sessions"]:
            del data["sessions"][session_token]
            self.save_data(data)
            return True
        
        return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        data = self.load_data()
        
        for user in data["users"]:
            if user["id"] == user_id and user["is_active"]:
                return user
        
        return None
    
    def get_all_users(self) -> List[UserResponse]:
        """Get all active users (admin function)."""
        data = self.load_data()
        
        return [
            UserResponse(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                full_name=user["full_name"],
                created_at=user["created_at"],
                last_login=user["last_login"]
            )
            for user in data["users"] 
            if user["is_active"]
        ]
    
    def get_user_stats(self) -> Dict:
        """Get user statistics."""
        data = self.load_data()
        
        total_users = len(data["users"])
        active_users = sum(1 for user in data["users"] if user["is_active"])
        active_sessions = sum(1 for session in data["sessions"].values() if session["is_active"])
        
        # Users registered today
        today = datetime.now().date()
        users_today = sum(
            1 for user in data["users"] 
            if datetime.fromisoformat(user["created_at"]).date() == today
        )
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "active_sessions": active_sessions,
            "users_registered_today": users_today,
            "data_file_size": os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0
        }

# Global auth service instance
auth_service = AuthService()

# Helper functions for API usage
def register_new_user(user_data: UserCreate) -> UserResponse:
    """Register a new user."""
    return auth_service.register_user(user_data)

def login_user(login_data: UserLogin) -> Dict:
    """Login user and return session data."""
    user = auth_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    session_token = auth_service.create_session(user)
    
    return {
        "user": UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            full_name=user["full_name"],
            created_at=user["created_at"],
            last_login=user["last_login"]
        ),
        "session_token": session_token,
        "message": "Login successful"
    }

def validate_user_session(session_token: str) -> Optional[UserResponse]:
    """Validate session and return user data."""
    session_data = auth_service.validate_session(session_token)
    if not session_data:
        return None
    
    user = session_data["user"]
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        created_at=user["created_at"],
        last_login=user["last_login"]
    )

def logout_user_session(session_token: str) -> bool:
    """Logout user session."""
    return auth_service.logout_user(session_token)