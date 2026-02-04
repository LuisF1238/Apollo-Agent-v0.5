"""Contact and connection point models for Data Science sourcing"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


class PersonaType(str, Enum):
    """Persona categories for sourcing"""
    CONSULTING = "Consulting"
    SOCIAL_GOOD = "Social Good"
    EXTERNAL = "External"
    STARTUP_CAREER_FAIR = "Startup Career Fair"


class ConnectionPoint(BaseModel):
    """A point of connection between user and contact"""
    type: str  # 'company', 'location', 'role', 'skill'
    value: str
    strength: float = Field(ge=0.0, le=1.0, description="Connection strength from 0 to 1")
    details: Optional[str] = None


class Contact(BaseModel):
    """Contact/prospect model for Data Science sourcing"""
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None

    # Sourcing-specific fields
    persona: Optional[PersonaType] = None
    linkedin_url: Optional[str] = None
    years_of_experience: Optional[int] = None
    skills: List[str] = Field(default_factory=list)

    connection_points: List[ConnectionPoint] = Field(default_factory=list)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Apollo.io specific fields
    apollo_id: Optional[str] = None
    industry: Optional[str] = None
    seniority: Optional[str] = None

    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "company": "Meta",
                "title": "Senior Data Scientist",
                "location": "Menlo Park, CA",
                "persona": "External",
                "skills": ["Python", "Machine Learning", "SQL"],
                "connection_points": [{
                    "type": "company",
                    "value": "Google",
                    "strength": 0.9
                }],
                "relevance_score": 0.85
            }
        }


__all__ = ["Contact", "ConnectionPoint", "PersonaType"]
