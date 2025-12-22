"""Profile parser agent for extracting structured data from resumes"""
import json
from typing import Dict, Any
from api.openai_client import openai_client
from config.prompts import PROFILE_PARSER_SYSTEM_PROMPT, PROFILE_PARSER_USER_PROMPT
from models.user import UserProfile, Education, Experience
from utils.pdf_parser import extract_resume_text


class ProfileParserAgent:
    """
    Agent for parsing resume PDFs into structured UserProfile objects
    """
    
    def __init__(self):
        """Initialize the profile parser agent"""
        self.client = openai_client
    
    def parse_resume_pdf(self, pdf_path: str) -> UserProfile:
        """
        Parse a resume PDF file into a structured UserProfile
        
        Args:
            pdf_path: Path to the resume PDF file
            
        Returns:
            UserProfile object with extracted information
            
        Raises:
            ValueError: If PDF parsing or profile extraction fails
        """
        # Extract text from PDF
        try:
            resume_text = extract_resume_text(pdf_path)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
        
        # Parse the resume text
        return self.parse_resume_text(resume_text)
    
    def parse_resume_text(self, resume_text: str) -> UserProfile:
        """
        Parse resume text into a structured UserProfile
        
        Args:
            resume_text: Resume text to parse
            
        Returns:
            UserProfile object with extracted information
            
        Raises:
            ValueError: If profile extraction fails
        """
        # Prepare the prompt
        user_prompt = PROFILE_PARSER_USER_PROMPT.format(resume_text=resume_text)
        
        # Call OpenAI API
        try:
            response = self.client.json_completion(
                system_prompt=PROFILE_PARSER_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )
            
            # Parse JSON response
            profile_data = json.loads(response)
            
            # Convert to UserProfile model
            return self._build_user_profile(profile_data)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to extract profile from resume: {str(e)}")
    
    def _build_user_profile(self, data: Dict[str, Any]) -> UserProfile:
        """
        Build a UserProfile from parsed data
        
        Args:
            data: Dictionary with profile data
            
        Returns:
            UserProfile object
        """
        # Parse education
        education = []
        for edu in data.get("education", []):
            education.append(Education(
                school=edu.get("school", ""),
                degree=edu.get("degree", ""),
                field_of_study=edu.get("field_of_study"),
                graduation_year=edu.get("graduation_year")
            ))
        
        # Parse experiences
        experiences = []
        for exp in data.get("experiences", []):
            experiences.append(Experience(
                company=exp.get("company", ""),
                role=exp.get("role", ""),
                duration=exp.get("duration", ""),
                start_date=exp.get("start_date"),
                end_date=exp.get("end_date"),
                description=exp.get("description"),
                location=exp.get("location")
            ))
        
        # Build UserProfile
        return UserProfile(
            name=data.get("name", ""),
            email=data.get("email"),
            phone=data.get("phone"),
            location=data.get("location"),
            current_company=data.get("current_company"),
            current_role=data.get("current_role"),
            education=education,
            experiences=experiences,
            skills=data.get("skills", [])
        )


__all__ = ["ProfileParserAgent"]
