"""Persona configurations for Data Science sourcing"""
from typing import List, Dict, Any
from models.contact import PersonaType


# Persona-specific search criteria
PERSONA_FILTERS: Dict[PersonaType, Dict[str, Any]] = {
    PersonaType.CONSULTING: {
        "person_titles": [
            "Project Manager",
            "Master Engineering Technical",
            "Design",
            "Education",
            "Master Finance",
            "Master Human Resources",
            "Master Information Technology",
            "Master Legal",
            "Master Marketing",
            "Medical Health Master Operations",
            "Master Sales",
            "Consulting",
            "Product Management",
            "Head of Data",
            "Head of Data Science",
            "VP Data",
            "VP Analytics",
            "Director of Data Science",
            "Director of Analytics",
            "Director of Insights",
            "Director of Data Strategy",
            "Director of Business Intelligence",
            "BI Director",
            "VP Product",
            "Director of Product",
            "Head of Product",
            "Product Manager",
            "Senior Product Manager",
            "Product Lead",
            "Head of Data Engineering",
            "Director of Data Engineering",
            "Director of Data Platform",
            "Analytics Engineering Manager",
            "Data Engineering Manager",
            "Data Architect",
            "Data Platform Lead",
            "ETL Lead"
        ],
        "person_seniorities": ["senior", "manager", "director", "head", "vp"],
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
            "Project Manager",
            "Master Engineering Technical",
            "Design",
            "Education",
            "Master Finance",
            "Master Human Resources",
            "Master Information Technology",
            "Master Legal",
            "Master Marketing",
            "Medical Health Master Operations",
            "Master Sales",
            "Consulting",
            "Product Management",
            "Head of Data",
            "Head of Data Science",
            "VP Data",
            "VP Analytics",
            "Director of Data Science",
            "Director of Analytics",
            "Director of Insights",
            "Director of Data Strategy",
            "Director of Impact Analytics",
            "Director of Measurement & Learning",
            "Director of Monitoring Evaluation and Learning",
            "MEL Director",
            "Research Data Scientist",
            "Lead Data Scientist",
            "Quantitative Research Lead",
            "Impact Measurement Lead",
            "Evaluation Director",
            "Learning & Impact Director",
            "Director of Business Intelligence",
            "BI Director",
            "VP Product",
            "Director of Product",
            "Head of Product",
            "Product Manager",
            "Senior Product Manager",
            "Product Lead",
            "Director of Program Analytics",
            "Program Data Manager",
            "Director of Digital Services",
            "Innovation Program Manager",
            "Director of Innovation",
            "Service Design Lead",
            "Platform Product Manager",
            "Data Platform Product Manager",
            "Director of Strategic Partnerships",
            "Head of Partnerships",
            "Partnerships Manager",
            "Corporate & Foundation Partnerships Director",
            "Social Impact Partnerships Manager",
            "University Partnerships Manager",
            "Government Partnerships Manager",
            "Community Partnerships Director",
            "Development Director",
            "External Relations Director",
            "Director of Research",
            "Head of Research & Evaluation",
            "Evaluation Scientist",
            "Policy Research Director",
            "Director of Evidence & Learning",
            "Learning & Evaluation Manager",
            "Impact Evaluation Lead",
            "Research Program Manager",
            "Research Scientist",
            "Data for Policy Lead",
            "Head of Data Engineering",
            "Director of Data Engineering",
            "Director of Data Platform",
            "Analytics Engineering Manager",
            "Data Engineering Manager",
            "Data Architect",
            "Data Platform Lead",
            "ETL Lead",
            "Director of Technology",
            "CTO",
            "VP Engineering"
        ],
        "person_seniorities": ["senior", "manager", "director", "head", "vp"],
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
            "Talent Acquisition Specialist",
            "Recruitment Consultant",
            "Talent Partner",
            "Sourcing Specialist",
            "Recruitment Coordinator",
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
    },
    PersonaType.STARTUP_CAREER_FAIR: {
        "person_titles": [
            "Recruiter",
            "Talent Acquisition Specialist",
            "Talent Acquisition Partner",
            "Talent Acquisition Recruiter",
            "Talent Partner",
            "Talent Specialist",
            "Talent Advisor",
            "Recruiting Specialist",
            "Recruiting Partner",
            "Recruiting Manager",
            "Recruiting Lead",
            "Recruiting Coordinator",
            "Talent Acquisition Coordinator",
            "Recruitment Coordinator",
            "Sourcer",
            "Talent Sourcer",
            "Technical Sourcer",
            "Recruiting Sourcer",
            "Technical Recruiter",
            "Senior Technical Recruiter",
            "Principal Recruiter",
            "Lead Recruiter",
            "University Recruiter",
            "Campus Recruiter",
            "Early Career Recruiter",
            "Diversity Recruiter",
            "Staffing Specialist",
            "Staffing Recruiter",
            "Staffing Manager",
            "RPO Recruiter",
            "Head of Recruiting",
            "Head of Talent",
            "Director of Recruiting",
            "Director of Talent Acquisition",
            "VP of Talent Acquisition",
            "VP of Recruiting",
            "Chief People Officer"
        ],
        "person_seniorities": ["founder", "manager", "vp", "head", "director", "senior"],
        "person_locations": ["San Francisco Bay Area"],
        "organization_num_employees_ranges": ["1,10", "11,20", "21,50", "51,100", "101,200", "201,500"],
        "q_keywords": "startup AI machine learning data science software development data solutions cybersecurity tech YC Y Combinator",
        "description": "Recruiters and Talent Acquisition professionals at startups in the San Francisco Bay Area"
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
