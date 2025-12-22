"""Persona configurations for Data Science sourcing"""
from typing import List, Dict, Any
from models.contact import PersonaType


# Persona-specific search criteria
PERSONA_FILTERS: Dict[PersonaType, Dict[str, Any]] = {
    PersonaType.CONSULTING: {
        "person_titles": [
            "Data Scientist",
            "Senior Data Scientist",
            "Lead Data Scientist",
            "Principal Data Scientist",
            "Staff Data Scientist",
            "Data Science Consultant",
            "Analytics Consultant",
            "Machine Learning Consultant"
        ],
        "organization_industries": [
            "Management Consulting",
            "Consulting",
            "Strategy Consulting",
            "Technology Consulting"
        ],
        "q_keywords": "consulting data science analytics",
        "description": "Data Scientists working in consulting firms"
    },
    PersonaType.SOCIAL_GOOD: {
        "person_titles": [
            "Data Scientist",
            "Senior Data Scientist",
            "Lead Data Scientist",
            "Principal Data Scientist",
            "Data Analyst",
            "Research Scientist"
        ],
        "organization_industries": [
            "Nonprofit",
            "Education",
            "Healthcare",
            "Government",
            "Environmental",
            "Social Impact"
        ],
        "q_keywords": "nonprofit social impact public health education environment",
        "description": "Data Scientists in social good/nonprofit sectors"
    },
    PersonaType.EXTERNAL: {
        "person_titles": [
            "Data Scientist",
            "Senior Data Scientist",
            "Lead Data Scientist",
            "Principal Data Scientist",
            "Staff Data Scientist",
            "Machine Learning Engineer",
            "Data Engineer",
            "Applied Scientist"
        ],
        "organization_industries": [
            "Technology",
            "Software",
            "Internet",
            "E-commerce",
            "Financial Services",
            "Fintech"
        ],
        "q_keywords": "data science machine learning AI",
        "description": "Data Scientists in external tech companies"
    }
}


def get_persona_filters(persona: PersonaType) -> Dict[str, Any]:
    """
    Get search filters for a specific persona

    Args:
        persona: PersonaType enum value

    Returns:
        Dictionary of Apollo search filters
    """
    return PERSONA_FILTERS.get(persona, {})


def get_all_personas() -> List[PersonaType]:
    """Get list of all available personas"""
    return list(PersonaType)


__all__ = ["PERSONA_FILTERS", "get_persona_filters", "get_all_personas"]
