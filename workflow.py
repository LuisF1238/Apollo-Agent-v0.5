"""Main orchestration workflow for coffee chat agent"""
from typing import List, Optional, Dict, Any
from agents.profile_parser import ProfileParserAgent
from agents.contact_matcher import ContactMatcherAgent
from agents.email_generator import EmailGeneratorAgent
from api.apollo_client import apollo_client
from models.user import UserProfile
from models.contact import Contact
from models.email import EmailDraft


class CoffeeChatWorkflow:
    """
    Main workflow orchestrating the coffee chat outreach process
    """

    def __init__(self):
        """Initialize all agents"""
        self.profile_parser = ProfileParserAgent()
        self.contact_matcher = ContactMatcherAgent()
        self.email_generator = EmailGeneratorAgent()
        self.apollo_client = apollo_client

    def run_full_workflow(
        self,
        resume_path: str,
        search_titles: Optional[List[str]] = None,
        search_locations: Optional[List[str]] = None,
        search_seniorities: Optional[List[str]] = None,
        max_contacts: int = 25,
        min_relevance_score: float = 0.5
    ) -> Dict[str, Any]:
        """
        Run the complete workflow from resume to email drafts

        Args:
            resume_path: Path to resume PDF
            search_titles: Job titles to search for
            search_locations: Locations to search in
            search_seniorities: Seniority levels to target
            max_contacts: Maximum number of contacts to find
            min_relevance_score: Minimum relevance score to generate emails

        Returns:
            Dictionary with user_profile, contacts, and email_drafts

        Raises:
            ValueError: If workflow fails at any step
        """
        # Step 1: Parse resume
        print("📄 Parsing resume...")
        user_profile = self.profile_parser.parse_resume_pdf(resume_path)
        print(f"✓ Parsed profile for {user_profile.name}")

        # Step 2: Search for contacts
        print(f"🔍 Searching Apollo for contacts...")
        contacts = self.apollo_client.search_contacts_to_models(
            person_titles=search_titles,
            person_locations=search_locations,
            person_seniorities=search_seniorities,
            max_results=max_contacts
        )
        print(f"✓ Found {len(contacts)} contacts")

        # Step 3: Analyze and score contacts
        print("🔗 Analyzing connection points...")
        analyzed_contacts = self.contact_matcher.analyze_contacts_batch(
            user_profile=user_profile,
            contacts=contacts
        )
        print(f"✓ Analyzed {len(analyzed_contacts)} contacts")

        # Step 4: Filter by relevance score
        relevant_contacts = [
            c for c in analyzed_contacts
            if c.relevance_score >= min_relevance_score
        ]
        print(f"✓ {len(relevant_contacts)} contacts meet relevance threshold ({min_relevance_score})")

        # Step 5: Generate emails for relevant contacts
        print("✉️  Generating personalized emails...")
        email_drafts = []
        for contact in relevant_contacts:
            try:
                draft = self.email_generator.generate_email(user_profile, contact)
                email_drafts.append(draft)
            except Exception as e:
                print(f"⚠️  Failed to generate email for {contact.name}: {str(e)}")

        print(f"✓ Generated {len(email_drafts)} email drafts")

        return {
            "user_profile": user_profile,
            "contacts": analyzed_contacts,
            "relevant_contacts": relevant_contacts,
            "email_drafts": email_drafts
        }

    def parse_and_search(
        self,
        resume_path: str,
        search_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse resume and search for contacts

        Args:
            resume_path: Path to resume PDF
            search_criteria: Apollo search parameters

        Returns:
            Dictionary with user_profile and contacts
        """
        user_profile = self.profile_parser.parse_resume_pdf(resume_path)

        contacts = self.apollo_client.search_contacts_to_models(
            person_titles=search_criteria.get("titles"),
            person_locations=search_criteria.get("locations"),
            person_seniorities=search_criteria.get("seniorities"),
            max_results=search_criteria.get("max_results", 25)
        )

        return {
            "user_profile": user_profile,
            "contacts": contacts
        }

    def match_and_generate(
        self,
        user_profile: UserProfile,
        contacts: List[Contact],
        min_relevance_score: float = 0.5
    ) -> Dict[str, Any]:
        """
        Match contacts and generate emails

        Args:
            user_profile: User's profile
            contacts: List of contacts to analyze
            min_relevance_score: Minimum relevance score

        Returns:
            Dictionary with analyzed contacts and email drafts
        """
        # Analyze contacts
        analyzed_contacts = self.contact_matcher.analyze_contacts_batch(
            user_profile=user_profile,
            contacts=contacts
        )

        # Filter by relevance
        relevant_contacts = [
            c for c in analyzed_contacts
            if c.relevance_score >= min_relevance_score
        ]

        # Generate emails
        email_drafts = []
        for contact in relevant_contacts:
            try:
                draft = self.email_generator.generate_email(user_profile, contact)
                email_drafts.append(draft)
            except Exception as e:
                print(f"Warning: Failed to generate email for {contact.name}: {str(e)}")

        return {
            "analyzed_contacts": analyzed_contacts,
            "relevant_contacts": relevant_contacts,
            "email_drafts": email_drafts
        }

    def generate_single_email(
        self,
        user_profile: UserProfile,
        contact: Contact
    ) -> EmailDraft:
        """
        Generate a single email for a contact

        Args:
            user_profile: User's profile
            contact: Contact to reach out to

        Returns:
            EmailDraft object
        """
        # Analyze connection if not already done
        if not contact.connection_points:
            contact = self.contact_matcher.analyze_contact(user_profile, contact)

        # Generate email
        return self.email_generator.generate_email(user_profile, contact)

    def enrich_contact_email(self, contact: Contact) -> Contact:
        """
        Enrich a single contact with their email using Apollo API
        This will use credits to reveal the email address

        Args:
            contact: Contact to enrich

        Returns:
            Updated Contact object with email

        Raises:
            RuntimeError: If enrichment fails
        """
        return self.apollo_client.enrich_contact_email(contact)


__all__ = ["CoffeeChatWorkflow"]
