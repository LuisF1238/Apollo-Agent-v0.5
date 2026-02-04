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
        person_seniorities: Optional[List[str]] = None,
        organization_names: Optional[List[str]] = None,
        organization_ids: Optional[List[str]] = None,
        organization_industries: Optional[List[str]] = None,
        q_keywords: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
        reveal_personal_emails: bool = False,
        verified_only: bool = False
    ) -> Dict[str, Any]:
        """
        Search for people using Apollo.io People Search API

        Args:
            person_titles: List of job titles to search for
            person_seniorities: List of seniority levels (e.g., ["senior", "vp", "cxo"])
            organization_names: List of company names to filter by
            organization_ids: List of organization IDs
            organization_industries: List of industries to filter by
            q_keywords: Keywords to search for
            page: Page number (starts at 1)
            per_page: Results per page (max 100)
            reveal_personal_emails: If False, won't use credits to reveal emails (default: False)
            verified_only: If True, only return verified Apollo profiles (default: False)

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
        if person_seniorities:
            payload["person_seniorities"] = person_seniorities
        if organization_names:
            payload["q_organization_name"] = " OR ".join(organization_names)
        if organization_ids:
            payload["organization_ids"] = organization_ids
        if organization_industries:
            payload["organization_industry_tag_ids"] = organization_industries
        if q_keywords:
            payload["q_keywords"] = q_keywords
        if verified_only:
            payload["contact_email_status"] = ["verified"]

        # Rate limit
        if not self.rate_limiter.acquire(block=True, timeout=30):
            raise RuntimeError("Rate limit exceeded for Apollo API")

        try:
            print(f"DEBUG: Sending request to Apollo - Page: {page}, Per page: {per_page}")
            print(f"DEBUG: Payload: {payload}")

            response = self.session.post(
                endpoint,
                json=payload,
                headers={"X-Api-Key": self.api_key}
            )
            response.raise_for_status()
            result = response.json()

            print(f"DEBUG: Response pagination: {result.get('pagination', {})}")
            print(f"DEBUG: Number of people in response: {len(result.get('people', []))}")

            return result

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
        organization_names: Optional[List[str]] = None,
        person_seniorities: Optional[List[str]] = None,
        max_results: int = 25,
        verified_only: bool = False,
        reveal_personal_emails: bool = True
    ) -> List[Contact]:
        """
        Search for contacts and convert to Contact models with pagination support

        Args:
            person_titles: List of job titles
            organization_names: List of company names
            person_seniorities: List of seniority levels
            max_results: Maximum number of results to return (up to 500)
            verified_only: If True, only return verified Apollo profiles
            reveal_personal_emails: If True, reveal personal emails (uses credits, default: True)

        Returns:
            List of Contact objects
        """
        # If multiple companies specified, search each one separately and combine
        if organization_names and len(organization_names) > 1:
            import time
            print(f"Searching {len(organization_names)} companies separately...")
            all_contacts = []
            results_per_company = max(1, max_results // len(organization_names))

            for idx, org_name in enumerate(organization_names):
                print(f"Searching company: {org_name}")
                company_contacts = self._search_single_company(
                    person_titles=person_titles,
                    organization_name=org_name,
                    person_seniorities=person_seniorities,
                    max_results=results_per_company,
                    verified_only=verified_only,
                    reveal_personal_emails=reveal_personal_emails
                )
                print(f"Found {len(company_contacts)} contacts for {org_name}")
                all_contacts.extend(company_contacts)

                # Add 1.5 second delay between companies to avoid per-minute rate limit
                # Apollo limit: 50 requests/minute = 1 request per 1.2 seconds
                if idx < len(organization_names) - 1:
                    time.sleep(1.5)

            print(f"Total contacts from all companies: {len(all_contacts)}")
            return all_contacts[:max_results]
        else:
            # Single or no company - use existing logic
            return self._search_single_company(
                person_titles=person_titles,
                organization_name=organization_names[0] if organization_names else None,
                person_seniorities=person_seniorities,
                max_results=max_results,
                verified_only=verified_only,
                reveal_personal_emails=reveal_personal_emails
            )

    def _search_single_company(
        self,
        person_titles: Optional[List[str]] = None,
        organization_name: Optional[str] = None,
        person_seniorities: Optional[List[str]] = None,
        max_results: int = 25,
        verified_only: bool = False,
        reveal_personal_emails: bool = True
    ) -> List[Contact]:
        """
        Search for contacts from a single company with pagination support

        Args:
            person_titles: List of job titles
            organization_name: Single company name
            person_seniorities: List of seniority levels
            max_results: Maximum number of results to return
            verified_only: If True, only return verified Apollo profiles
            reveal_personal_emails: If True, reveal personal emails (uses credits, default: True)

        Returns:
            List of Contact objects
        """
        contacts = []
        page = 1
        per_page = 100  # Apollo max per page

        # Convert single organization_name to list for API call
        org_names_list = [organization_name] if organization_name else None

        while len(contacts) < max_results:
            # Calculate how many more we need
            remaining = max_results - len(contacts)
            current_per_page = min(per_page, remaining)

            print(f"Fetching page {page}, requesting {current_per_page} contacts, total so far: {len(contacts)}")

            results = self.search_people(
                person_titles=person_titles,
                organization_names=org_names_list,
                person_seniorities=person_seniorities,
                page=page,
                per_page=current_per_page,
                verified_only=verified_only,
                reveal_personal_emails=reveal_personal_emails
            )

            people = results.get("people", [])
            print(f"Received {len(people)} contacts from page {page}")

            if not people:
                # No more results
                print("No more results available")
                break

            for person in people:
                contact = self._apollo_person_to_contact(person)
                contacts.append(contact)

            # Check if we've reached the end
            pagination = results.get("pagination", {})
            total_pages = pagination.get("total_pages")
            total_entries = pagination.get("total_entries", 0)

            print(f"Pagination info - Page {page}, Total entries: {total_entries}, Total pages: {total_pages}")

            # Stop if we've reached max_results
            if len(contacts) >= max_results:
                print("Reached max_results limit")
                break

            # If we got fewer results than requested, there are no more pages
            if len(people) < current_per_page:
                print(f"Got {len(people)} results, less than requested {current_per_page} - no more pages")
                break

            # If pagination info says we're done, stop
            if total_pages is not None and page >= total_pages:
                print(f"Reached last page according to pagination: {page}/{total_pages}")
                break

            page += 1

        print(f"Final result: Retrieved {len(contacts)} contacts")
        return contacts[:max_results]

    def enrich_contact_email(self, contact: Contact) -> Contact:
        """
        Enrich a contact with their email by calling Apollo email reveal API
        This uses credits to reveal the email address

        Args:
            contact: Contact object with apollo_id

        Returns:
            Updated Contact object with email filled in

        Raises:
            RuntimeError: If enrichment fails
        """
        # If we already have apollo_id, use it directly
        if contact.apollo_id:
            person_id = contact.apollo_id
        else:
            # Otherwise, match the person first to get their ID
            if contact.first_name and contact.last_name:
                first_name = contact.first_name
                last_name = contact.last_name
            else:
                name_parts = contact.name.split(maxsplit=1)
                first_name = name_parts[0] if name_parts else contact.name
                last_name = name_parts[1] if len(name_parts) > 1 else None

            try:
                enriched_data = self.enrich_person(
                    first_name=first_name,
                    last_name=last_name,
                    organization_name=contact.company
                )
                person = enriched_data.get("person", {})
                person_id = person.get("id")

                if not person_id:
                    print(f"DEBUG: No person ID found for {contact.name}")
                    return contact
            except Exception as e:
                print(f"DEBUG: Failed to match person: {str(e)}")
                return contact

        try:
            # Use /people/match endpoint with reveal_personal_emails to get email
            endpoint = f"{self.BASE_URL}/people/match"

            # Rate limit
            if not self.rate_limiter.acquire(block=True, timeout=30):
                raise RuntimeError("Rate limit exceeded for Apollo API")

            payload = {
                "id": person_id,
                "reveal_personal_emails": True
            }

            print(f"DEBUG: Sending email reveal request for person_id: {person_id}")
            print(f"DEBUG: Payload: {payload}")

            response = self.session.post(
                endpoint,
                json=payload,
                headers={"X-Api-Key": self.api_key}
            )

            print(f"DEBUG: Response status code: {response.status_code}")

            # If this endpoint doesn't work, just return the contact as-is
            if response.status_code == 422 or response.status_code == 404:
                print(f"⚠️  Email reveal failed (likely insufficient credits or email not available)")
                return contact

            response.raise_for_status()
            result = response.json()

            print(f"DEBUG: Response keys: {result.keys()}")
            print(f"DEBUG: Full response: {result}")

            # Extract person data from response
            revealed_data = result.get("person", {})

            print(f"DEBUG: Revealed data keys: {revealed_data.keys() if isinstance(revealed_data, dict) else 'N/A'}")
            print(f"DEBUG: Email field value: {revealed_data.get('email') if isinstance(revealed_data, dict) else 'N/A'}")

            # Update contact with revealed data if it's a dict
            if isinstance(revealed_data, dict):
                # Update first name and last name if available
                if revealed_data.get("first_name"):
                    contact.first_name = revealed_data["first_name"]
                if revealed_data.get("last_name"):
                    contact.last_name = revealed_data["last_name"]

                # Update full name
                if contact.first_name and contact.last_name:
                    contact.name = f"{contact.first_name} {contact.last_name}"
                elif contact.first_name:
                    contact.name = contact.first_name

                # Extract email - check multiple possible fields
                email_status = revealed_data.get("email_status")
                email = revealed_data.get("email") or revealed_data.get("personal_email")

                if email:
                    contact.email = email
                    print(f"DEBUG: Email found: {contact.email}")
                else:
                    print(f"DEBUG: No email available - Status: {email_status}")
                    print(f"DEBUG: Checking email field: {revealed_data.get('email')}")
                    print(f"DEBUG: Checking personal_email field: {revealed_data.get('personal_email')}")
            else:
                print(f"DEBUG: revealed_data is not a dict, cannot extract email")

            # Also update any other missing fields
            if not contact.phone and revealed_data.get("phone_numbers"):
                contact.phone = revealed_data["phone_numbers"][0] if revealed_data["phone_numbers"] else None
            if not contact.title and revealed_data.get("title"):
                contact.title = revealed_data.get("title")

            print(f"DEBUG: Updated contact - Name: {contact.name}, First: {contact.first_name}, Last: {contact.last_name}, Email: {contact.email or 'Not available'}")

            return contact

        except Exception as e:
            print(f"DEBUG: Exception during email reveal: {str(e)}")
            raise RuntimeError(f"Failed to reveal email for {contact.name}: {str(e)}")

    def _apollo_person_to_contact(self, person_data: Dict[str, Any]) -> Contact:
        """
        Convert Apollo.io person data to Contact model

        Args:
            person_data: Person data from Apollo API

        Returns:
            Contact object
        """
        # Extract person fields - prioritize first_name/last_name over name field
        first_name = person_data.get("first_name", "")
        last_name = person_data.get("last_name", "")

        if first_name and last_name:
            name = f"{first_name} {last_name}"
        elif first_name:
            name = first_name
        else:
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
            first_name=first_name or None,
            last_name=last_name or None,
            email=email,
            phone=phone,
            company=company,
            title=title,
            location=location,
            apollo_id=person_data.get("id"),
            industry=industry,
            seniority=seniority
        )


# Lazy singleton instance
_apollo_client_instance = None

def get_apollo_client() -> ApolloClient:
    """Get or create the singleton apollo_client instance"""
    global _apollo_client_instance
    if _apollo_client_instance is None:
        _apollo_client_instance = ApolloClient()
    return _apollo_client_instance

# For backward compatibility, create a property-like accessor
class _ApolloClientProxy:
    def __getattr__(self, name):
        return getattr(get_apollo_client(), name)

    def __call__(self, *args, **kwargs):
        return get_apollo_client()(*args, **kwargs)

apollo_client = _ApolloClientProxy()

__all__ = ["ApolloClient", "apollo_client", "get_apollo_client"]
