"""Email draft and status models"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class EmailStatus(str, Enum):
    """Email status enum"""
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    REPLIED = "replied"


class EmailDraft(BaseModel):
    """Email draft model"""
    contact_name: str
    contact_email: str
    subject: str
    body: str
    
    status: EmailStatus = EmailStatus.DRAFT
    
    # Metadata
    user_name: Optional[str] = None
    contact_company: Optional[str] = None
    contact_title: Optional[str] = None
    connection_points: List[str] = Field(default_factory=list)
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    
    # Error tracking
    error_message: Optional[str] = None
    retry_count: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "contact_name": "Jane Smith",
                "contact_email": "jane@example.com",
                "subject": "Stanford alum interested in Meta's AI work",
                "body": "Hi Jane,\n\nI noticed we both studied at Stanford...",
                "status": "draft",
                "connection_points": ["Stanford University", "AI/ML"]
            }
        }


__all__ = ["EmailDraft", "EmailStatus"]
