from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# Complaint Models
class ComplaintBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    location: Optional[str] = Field(default=None, max_length=500)
    contact_info: Optional[str] = Field(default=None, max_length=200)

class Complaint(ComplaintBase, table=True):
    __tablename__ = "complaints"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(max_length=50)  # Water, Road, Garbage, Security
    urgency: str = Field(max_length=20)   # low, medium, high, critical
    confidence_score: float = Field(ge=0.0, le=1.0)
    status: str = Field(default="submitted", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    resolved_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    status_updates: List["StatusUpdate"] = Relationship(back_populates="complaint")

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintResponse(BaseModel):
    id: int
    title: str
    category: str
    urgency: str
    status: str
    confidence_score: float
    created_at: datetime
    estimated_resolution: str

# Status Update Models
class StatusUpdateBase(SQLModel):
    status: str = Field(max_length=20)
    message: Optional[str] = Field(default=None, max_length=500)

class StatusUpdate(StatusUpdateBase, table=True):
    __tablename__ = "status_updates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    complaint_id: int = Field(foreign_key="complaints.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None, max_length=100)
    
    # Relationships
    complaint: Optional[Complaint] = Relationship(back_populates="status_updates")

# Policy Models
class PolicyBase(SQLModel):
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=50)
    category: Optional[str] = Field(default=None, max_length=100)

class Policy(PolicyBase, table=True):
    __tablename__ = "policies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    ai_summary: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="draft", max_length=20)  # draft, active, archived
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    sentiment_scores: List["SentimentScore"] = Relationship(back_populates="policy")

class PolicyCreate(PolicyBase):
    pass

class PolicyResponse(BaseModel):
    id: int
    title: str
    ai_summary: Optional[str]
    category: Optional[str]
    status: str
    created_at: datetime

# Sentiment Score Models
class SentimentScoreBase(SQLModel):
    positive_score: float = Field(ge=0.0, le=1.0, default=0.0)
    negative_score: float = Field(ge=0.0, le=1.0, default=0.0)
    neutral_score: float = Field(ge=0.0, le=1.0, default=1.0)
    total_comments: int = Field(ge=0, default=0)

class SentimentScore(SentimentScoreBase, table=True):
    __tablename__ = "sentiment_scores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    policy_id: int = Field(foreign_key="policies.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    policy: Optional[Policy] = Relationship(back_populates="sentiment_scores")

# Media Verification Models (for tracking verification history)
class MediaVerificationBase(SQLModel):
    filename: str = Field(max_length=255)
    file_hash: str = Field(max_length=64)  # SHA-256 hash
    media_type: str = Field(max_length=10)  # image or video
    trust_score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)

class MediaVerification(MediaVerificationBase, table=True):
    __tablename__ = "media_verifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    analysis_details: Optional[str] = Field(default=None)  # JSON string
    processing_time: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(default=None, max_length=45)

class MediaVerificationResponse(BaseModel):
    id: int
    filename: str
    media_type: str
    trust_score: float
    confidence: float
    created_at: datetime

# User Models (for future authentication)
class UserBase(SQLModel):
    email: str = Field(unique=True, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=200)
    is_active: bool = Field(default=True)

class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=255)
    role: str = Field(default="citizen", max_length=20)  # citizen, admin, moderator
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime