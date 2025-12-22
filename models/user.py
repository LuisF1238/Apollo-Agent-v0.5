"""User profile and related data models"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Education(BaseModel):
    """Education history entry"""
    school: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None


class Experience(BaseModel):
    """Work experience entry"""
    company: str
    role: str
    duration: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None


class UserProfile(BaseModel):
    """Complete user profile model"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    current_company: Optional[str] = None
    current_role: Optional[str] = None
    
    education: List[Education] = Field(default_factory=list)
    experiences: List[Experience] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "current_company": "Google",
                "current_role": "Software Engineer",
                "location": "San Francisco, CA",
                "education": [{
                    "school": "Stanford University",
                    "degree": "BS Computer Science",
                    "graduation_year": 2020
                }],
                "skills": ["Python", "Machine Learning", "React"]
            }
        }


__all__ = ["UserProfile", "Education", "Experience"]
