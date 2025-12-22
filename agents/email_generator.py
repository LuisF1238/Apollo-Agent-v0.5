"""Email generator agent for creating personalized outreach emails"""
import json
from typing import Optional
from api.openai_client import openai_client
from config.prompts import EMAIL_GENERATOR_SYSTEM_PROMPT, EMAIL_GENERATOR_USER_PROMPT
from models.user import UserProfile
from models.contact import Contact
from models.email import EmailDraft, EmailStatus


class EmailGeneratorAgent:
    """
    Agent for generating personalized cold emails for coffee chats
    """

    def __init__(self):
        """Initialize the email generator agent"""
        self.client = openai_client

    def generate_email(
        self,
        user_profile: UserProfile,
        contact: Contact,
        user_name_override: Optional[str] = None
    ) -> EmailDraft:
        """
        Generate a personalized email for a contact

        Args:
            user_profile: The user's profile
            contact: Contact to reach out to
            user_name_override: Optional name to use instead of profile name

        Returns:
            EmailDraft object with generated subject and body

        Raises:
            ValueError: If email generation fails or contact email is missing
        """
        if not contact.email:
            raise ValueError(f"Contact {contact.name} has no email address")

        # Format connection points for the prompt
        connection_points_str = self._format_connection_points(contact)

        # Prepare user profile summary
        user_summary = self._format_user_profile(user_profile)

        # Prepare the prompt
        prompt = EMAIL_GENERATOR_USER_PROMPT.format(
            user_profile=user_summary,
            contact_name=contact.name,
            contact_title=contact.title or "Professional",
            contact_company=contact.company or "their company",
            connection_points=connection_points_str
        )

        # Call OpenAI API
        try:
            response = self.client.json_completion(
                system_prompt=EMAIL_GENERATOR_SYSTEM_PROMPT,
                user_prompt=prompt + '\n\nReturn JSON with "subject" and "body" fields.'
            )

            # Parse JSON response
            email_data = json.loads(response)

            # Build EmailDraft
            draft = EmailDraft(
                contact_name=contact.name,
                contact_email=contact.email,
                subject=email_data.get("subject", f"Coffee chat with {contact.name}"),
                body=email_data.get("body", ""),
                status=EmailStatus.DRAFT,
                user_name=user_name_override or user_profile.name,
                contact_company=contact.company,
                contact_title=contact.title,
                connection_points=[cp.value for cp in contact.connection_points]
            )

            return draft

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to generate email: {str(e)}")

    def generate_email_simple(
        self,
        from_name: str,
        to_name: str,
        to_email: str,
        connection_point: str,
        context: Optional[str] = None
    ) -> EmailDraft:
        """
        Generate a simple email without full profile objects

        Args:
            from_name: Sender's name
            to_name: Recipient's name
            to_email: Recipient's email
            connection_point: Main connection point (e.g., "Stanford University")
            context: Optional additional context

        Returns:
            EmailDraft object with generated subject and body
        """
        # Build simple prompt
        prompt = f"""Write a personalized cold email from {from_name} to {to_name} requesting a brief coffee chat or 15-minute call.

Connection point: {connection_point}
{f"Additional context: {context}" if context else ""}

The email should:
1. Be concise (<150 words)
2. Naturally reference the connection point
3. Be genuine and professional
4. Have a clear call-to-action

Return JSON with "subject" and "body" fields."""

        try:
            response = self.client.json_completion(
                system_prompt=EMAIL_GENERATOR_SYSTEM_PROMPT,
                user_prompt=prompt
            )

            email_data = json.loads(response)

            return EmailDraft(
                contact_name=to_name,
                contact_email=to_email,
                subject=email_data.get("subject", f"Coffee chat with {to_name}"),
                body=email_data.get("body", ""),
                status=EmailStatus.DRAFT,
                user_name=from_name,
                connection_points=[connection_point]
            )

        except Exception as e:
            raise ValueError(f"Failed to generate simple email: {str(e)}")

    def _format_user_profile(self, profile: UserProfile) -> str:
        """Format user profile for the prompt"""
        parts = [f"Name: {profile.name}"]

        if profile.current_company and profile.current_role:
            parts.append(f"Current: {profile.current_role} at {profile.current_company}")

        if profile.location:
            parts.append(f"Location: {profile.location}")

        if profile.education:
            schools = [f"{edu.school} ({edu.degree})" for edu in profile.education[:2]]
            parts.append(f"Education: {', '.join(schools)}")

        if profile.skills:
            parts.append(f"Key skills: {', '.join(profile.skills[:5])}")

        return "\n".join(parts)

    def _format_connection_points(self, contact: Contact) -> str:
        """Format connection points for the prompt"""
        if not contact.connection_points:
            return "No specific connection points identified"

        # Sort by strength and take top 3
        top_connections = sorted(
            contact.connection_points,
            key=lambda cp: cp.strength,
            reverse=True
        )[:3]

        lines = []
        for cp in top_connections:
            detail_str = f" - {cp.details}" if cp.details else ""
            lines.append(f"- {cp.type.capitalize()}: {cp.value} (strength: {cp.strength:.2f}){detail_str}")

        return "\n".join(lines)


__all__ = ["EmailGeneratorAgent"]
