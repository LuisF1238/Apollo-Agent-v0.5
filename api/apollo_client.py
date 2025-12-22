"""Apollo.io API client wrapper"""
import requests
from typing import List, Optional, Dict, Any
from models.contact import Contact
from config.settings import APOLLO_API_KEY, APOLLO_RATE_LIMIT
from utils.rate_limiter import RateLimiter


class ApolloClient:
    """
    Wrapper for Apollo.io API with rate limiting and contact enrichment
    """

    BASE_URL = "https://api.apollo.io/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Apollo client

        Args:
            api_key: Apollo API key (defaults to settings)
        """
        self.api_key = api_key or APOLLO_API_KEY
        if not self.api_key:
            raise ValueError("Apollo API key is required")

        # Initialize rate limiter (default: 50 requests per minute)
        rate_limit = APOLLO_RATE_LIMIT or 50
        self.rate_limiter = RateLimiter(max_requests=rate_limit, time_window=60)

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        })

    def search_people(
        self,
        person_titles: Optional[List[str]] = None,
        person_locations: Optional[List[str]] = None,
        person_seniorities: Optional[List[str]] = None,
        organization_locations: Optional[List[str]] = None,
        organization_ids: Optional[List[str]] = None,
        organization_industries: Optional[List[str]] = None,
        q_keywords: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
        reveal_personal_emails: bool = False
    ) -> Dict[str, Any]:
        """
        Search for people using Apollo.io People Search API

        Args:
            person_titles: List of job titles to search for
            person_locations: List of person locations
            person_seniorities: List of seniority levels (e.g., ["senior", "vp", "cxo"])
            organization_locations: List of company locations
            organization_ids: List of organization IDs
            organization_industries: List of industries to filter by
            q_keywords: Keywords to search for
            page: Page number (starts at 1)
            per_page: Results per page (max 100)
            reveal_personal_emails: If False, won't use credits to reveal emails (default: False)

        Returns:
            Dictionary with search results including 'people', 'pagination', etc.

        Raises:
            RuntimeError: If API request fails
        """
        endpoint = f"{self.BASE_URL}/mixed_people/api_search"

        # Build request payload
        payload = {
            "page": page,
            "per_page": min(per_page, 100),
            "reveal_personal_emails": reveal_personal_emails
        }

        if person_titles:
            payload["person_titles"] = person_titles
        if person_locations:
            payload["person_locations"] = person_locations
        if person_seniorities:
            payload["person_seniorities"] = person_seniorities
        if organization_locations:
            payload["organization_locations"] = organization_locations
        if organization_ids:
            payload["organization_ids"] = organization_ids
        if organization_industries:
            payload["organization_industry_tag_ids"] = organization_industries
        if q_keywords:
            payload["q_keywords"] = q_keywords

        # Rate limit
        if not self.rate_limiter.acquire(block=True, timeout=30):
            raise RuntimeError("Rate limit exceeded for Apollo API")

        try:
            response = self.session.post(
                endpoint,
                json=payload,
                headers={"X-Api-Key": self.api_key}
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Apollo API HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Apollo API error: {str(e)}")

    def enrich_person(
        self,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        organization_name: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enrich a person's information using Apollo.io Person Enrichment API

        Args:
            email: Person's email address
            first_name: Person's first name
            last_name: Person's last name
            organization_name: Company name
            domain: Company domain

        Returns:
            Dictionary with enriched person data

        Raises:
            RuntimeError: If API request fails
        """
        endpoint = f"{self.BASE_URL}/people/match"

        payload = {}
        if email:
            payload["email"] = email
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if organization_name:
            payload["organization_name"] = organization_name
        if domain:
            payload["domain"] = domain

        if not payload:
            raise ValueError("At least one search parameter must be provided")

        # Rate limit
        if not self.rate_limiter.acquire(block=True, timeout=30):
            raise RuntimeError("Rate limit exceeded for Apollo API")

        try:
            response = self.session.post(
                endpoint,
                json=payload,
                headers={"X-Api-Key": self.api_key}
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Apollo API HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Apollo API error: {str(e)}")

    def search_contacts_to_models(
        self,
        person_titles: Optional[List[str]] = None,
        person_locations: Optional[List[str]] = None,
        person_seniorities: Optional[List[str]] = None,
        max_results: int = 25
    ) -> List[Contact]:
        """
        Search for contacts and convert to Contact models

        Args:
            person_titles: List of job titles
            person_locations: List of locations
            person_seniorities: List of seniority levels
            max_results: Maximum number of results to return

        Returns:
            List of Contact objects
        """
        results = self.search_people(
            person_titles=person_titles,
            person_locations=person_locations,
            person_seniorities=person_seniorities,
            per_page=max_results
        )

        contacts = []
        for person in results.get("people", []):
            contact = self._apollo_person_to_contact(person)
            contacts.append(contact)

        return contacts

    def enrich_contact_email(self, contact: Contact) -> Contact:
        """
        Enrich a contact with their email by calling Apollo enrichment API
        This uses credits to reveal the email address

        Args:
            contact: Contact object with at least name and company

        Returns:
            Updated Contact object with email filled in

        Raises:
            RuntimeError: If enrichment fails
        """
        # Split name into first and last
        name_parts = contact.name.split(maxsplit=1)
        first_name = name_parts[0] if name_parts else contact.name
        last_name = name_parts[1] if len(name_parts) > 1 else None

        try:
            enriched_data = self.enrich_person(
                first_name=first_name,
                last_name=last_name,
                organization_name=contact.company
            )

            # Debug: print the response structure
            print(f"DEBUG: Enriched data keys: {enriched_data.keys()}")
            print(f"DEBUG: Full enriched data: {enriched_data}")

            # Extract email from enriched data
            person = enriched_data.get("person", {})
            if person.get("email"):
                contact.email = person["email"]

                # Also update any other missing fields
                if not contact.phone and person.get("phone_numbers"):
                    contact.phone = person["phone_numbers"][0] if person["phone_numbers"] else None
                if not contact.title:
                    contact.title = person.get("title")
            else:
                # Try alternate paths in the response
                if enriched_data.get("email"):
                    contact.email = enriched_data["email"]
                print(f"DEBUG: No email found in person object. Person keys: {person.keys() if person else 'person is None'}")

            return contact

        except Exception as e:
            print(f"DEBUG: Exception during enrichment: {str(e)}")
            raise RuntimeError(f"Failed to enrich contact {contact.name}: {str(e)}")

    def _apollo_person_to_contact(self, person_data: Dict[str, Any]) -> Contact:
        """
        Convert Apollo.io person data to Contact model

        Args:
            person_data: Person data from Apollo API

        Returns:
            Contact object
        """
        # Extract person fields
        name = person_data.get("name", "")
        email = person_data.get("email")
        phone = person_data.get("phone_numbers", [None])[0] if person_data.get("phone_numbers") else None
        title = person_data.get("title")
        seniority = person_data.get("seniority")

        # Extract organization fields
        organization = person_data.get("organization", {})
        company = organization.get("name")
        industry = organization.get("industry")

        # Extract location (city, state, country)
        city = person_data.get("city")
        state = person_data.get("state")
        country = person_data.get("country")
        location_parts = [p for p in [city, state, country] if p]
        location = ", ".join(location_parts) if location_parts else None

        return Contact(
            name=name,
            email=email,
            phone=phone,
            company=company,
            title=title,
            location=location,
            apollo_id=person_data.get("id"),
            industry=industry,
            seniority=seniority
        )


# Singleton instance
apollo_client = ApolloClient()

__all__ = ["ApolloClient", "apollo_client"]
