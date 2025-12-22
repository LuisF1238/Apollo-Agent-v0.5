"""Contact matcher agent for identifying connection points between users and contacts"""
import json
from typing import List
from api.openai_client import openai_client
from config.prompts import RELEVANCE_ANALYSIS_PROMPT
from models.user import UserProfile
from models.contact import Contact, ConnectionPoint


class ContactMatcherAgent:
    """
    Agent for analyzing and scoring connection points between a user and contacts
    """

    def __init__(self):
        """Initialize the contact matcher agent"""
        self.client = openai_client

    def analyze_contact(self, user_profile: UserProfile, contact: Contact) -> Contact:
        """
        Analyze connection points between user and contact, update contact with results

        Args:
            user_profile: The user's profile
            contact: Contact to analyze

        Returns:
            Updated Contact object with connection_points and relevance_score

        Raises:
            ValueError: If analysis fails
        """
        # Prepare user profile summary
        user_summary = self._format_user_profile(user_profile)
        contact_summary = self._format_contact_info(contact)

        # Prepare the prompt
        prompt = RELEVANCE_ANALYSIS_PROMPT.format(
            user_profile=user_summary,
            contact_info=contact_summary
        )

        # Call OpenAI API
        try:
            response = self.client.json_completion(
                system_prompt="You are an expert at identifying professional connections and networking opportunities.",
                user_prompt=prompt
            )

            # Parse JSON response
            connection_data = json.loads(response)

            # Handle both array and object formats
            if isinstance(connection_data, dict):
                # If it's an object, try to find the array inside
                connection_data = connection_data.get("connection_points", connection_data.get("connections", []))

            # Build ConnectionPoint objects
            connection_points = []
            for conn in connection_data:
                if isinstance(conn, dict):
                    connection_points.append(ConnectionPoint(
                        type=conn.get("type", "unknown"),
                        value=conn.get("value", ""),
                        strength=conn.get("strength", 0.0),
                        details=conn.get("details")
                    ))

            # Calculate overall relevance score (weighted average of strengths)
            relevance_score = self._calculate_relevance_score(connection_points)

            # Update contact
            contact.connection_points = connection_points
            contact.relevance_score = relevance_score

            return contact

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to analyze contact connections: {str(e)}")

    def analyze_contacts_batch(
        self,
        user_profile: UserProfile,
        contacts: List[Contact]
    ) -> List[Contact]:
        """
        Analyze multiple contacts and sort by relevance

        Args:
            user_profile: The user's profile
            contacts: List of contacts to analyze

        Returns:
            List of contacts sorted by relevance_score (descending)
        """
        analyzed_contacts = []

        for contact in contacts:
            try:
                analyzed_contact = self.analyze_contact(user_profile, contact)
                analyzed_contacts.append(analyzed_contact)
            except Exception as e:
                # Log error but continue processing other contacts
                print(f"Warning: Failed to analyze contact {contact.name}: {str(e)}")
                contact.relevance_score = 0.0
                analyzed_contacts.append(contact)

        # Sort by relevance score (highest first)
        analyzed_contacts.sort(key=lambda c: c.relevance_score, reverse=True)

        return analyzed_contacts

    def _format_user_profile(self, profile: UserProfile) -> str:
        """Format user profile for the prompt"""
        parts = [f"Name: {profile.name}"]

        if profile.current_company and profile.current_role:
            parts.append(f"Current: {profile.current_role} at {profile.current_company}")

        if profile.location:
            parts.append(f"Location: {profile.location}")

        if profile.education:
            schools = [f"{edu.school} ({edu.degree})" for edu in profile.education]
            parts.append(f"Education: {', '.join(schools)}")

        if profile.experiences:
            companies = list(set([exp.company for exp in profile.experiences]))[:5]
            parts.append(f"Past companies: {', '.join(companies)}")

        if profile.skills:
            parts.append(f"Skills: {', '.join(profile.skills[:10])}")

        return "\n".join(parts)

    def _format_contact_info(self, contact: Contact) -> str:
        """Format contact info for the prompt"""
        parts = [f"Name: {contact.name}"]

        if contact.title and contact.company:
            parts.append(f"Current: {contact.title} at {contact.company}")

        if contact.location:
            parts.append(f"Location: {contact.location}")

        if contact.industry:
            parts.append(f"Industry: {contact.industry}")

        if contact.seniority:
            parts.append(f"Seniority: {contact.seniority}")

        return "\n".join(parts)

    def _calculate_relevance_score(self, connection_points: List[ConnectionPoint]) -> float:
        """
        Calculate overall relevance score from connection points

        Weights:
        - Company (current/past): 1.0
        - Location: 0.3
        - Role/Industry: 0.6
        - Skills: 0.4
        """
        if not connection_points:
            return 0.0

        weights = {
            "company": 1.0,
            "location": 0.3,
            "role": 0.6,
            "industry": 0.6,
            "skill": 0.4
        }

        weighted_sum = 0.0
        total_weight = 0.0

        for cp in connection_points:
            weight = weights.get(cp.type, 0.5)
            weighted_sum += cp.strength * weight
            total_weight += weight

        # Return weighted average, capped at 1.0
        return min(weighted_sum / total_weight if total_weight > 0 else 0.0, 1.0)


__all__ = ["ContactMatcherAgent"]
