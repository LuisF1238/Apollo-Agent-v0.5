"""Validation utilities for data cleaning and validation"""
import re
from typing import Optional, List


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))





def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format (US format)
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid phone format, False otherwise
    """
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it's a valid US phone number (10 or 11 digits)
    pattern = r'^1?\d{10}$'
    return bool(re.match(pattern, cleaned))


def validate_year(year: int) -> bool:
    """
    Validate graduation year is reasonable
    
    Args:
        year: Year to validate
        
    Returns:
        True if year is between 1950 and 2030, False otherwise
    """
    return 1950 <= year <= 2030


def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing potentially harmful characters
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract common technical skills from text
    
    Args:
        text: Text to extract skills from
        
    Returns:
        List of extracted skills
    """
    # Common technical skills to look for
    common_skills = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'C#',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'FastAPI',
        'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
        'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
        'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision',
        'Git', 'CI/CD', 'Agile', 'Scrum',
        'REST API', 'GraphQL', 'Microservices'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates


__all__ = [
    "validate_email",
    "sanitize_text",
    "validate_phone_number",
    "validate_year",
    "extract_skills_from_text"
]
