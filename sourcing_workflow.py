"""Main orchestration workflow for Data Science sourcing agent"""
from typing import List, Optional, Dict, Any
from api.apollo_client import apollo_client
from models.contact import Contact, PersonaType
from config.personas import get_persona_filters
from utils.spreadsheet_generator import export_to_csv, export_to_excel, export_by_persona


class SourcingWorkflow:
    """
    Main workflow orchestrating the Data Science sourcing process
    """

    def __init__(self):
        """Initialize Apollo client"""
        self.apollo_client = apollo_client

    def search_by_persona(
        self,
        persona: PersonaType,
        person_locations: Optional[List[str]] = None,
        max_contacts: int = 100,
        reveal_emails: bool = False
    ) -> List[Contact]:
        """
        Search for contacts based on persona type

        Args:
            persona: PersonaType (Consulting, Social Good, External)
            person_locations: Optional list of locations to filter by
            max_contacts: Maximum number of contacts to retrieve
            reveal_emails: Whether to reveal personal emails (uses credits)

        Returns:
            List of Contact objects with persona assigned
        """
        # Get persona-specific filters
        filters = get_persona_filters(persona)

        # Search Apollo
        contacts = self.apollo_client.search_contacts_to_models(
            person_titles=filters.get("person_titles"),
            person_locations=person_locations,
            max_results=max_contacts
        )

        # Assign persona to each contact
        for contact in contacts:
            contact.persona = persona

        return contacts

    def search_all_personas(
        self,
        person_locations: Optional[List[str]] = None,
        contacts_per_persona: int = 100,
        reveal_emails: bool = False
    ) -> Dict[PersonaType, List[Contact]]:
        """
        Search for contacts across all persona types

        Args:
            person_locations: Optional list of locations to filter by
            contacts_per_persona: Number of contacts per persona
            reveal_emails: Whether to reveal personal emails (uses credits)

        Returns:
            Dictionary mapping PersonaType to list of contacts
        """
        results = {}

        for persona in PersonaType:
            print(f"🔍 Searching for {persona.value} contacts...")
            contacts = self.search_by_persona(
                persona=persona,
                person_locations=person_locations,
                max_contacts=contacts_per_persona,
                reveal_emails=reveal_emails
            )
            results[persona] = contacts
            print(f"✓ Found {len(contacts)} {persona.value} contacts")

        return results

    def search_and_export(
        self,
        persona: PersonaType,
        output_path: str,
        person_locations: Optional[List[str]] = None,
        max_contacts: int = 100,
        file_format: str = "csv",
        max_per_file: int = 100
    ) -> List[str]:
        """
        Search for contacts and export to spreadsheet(s)

        Args:
            persona: PersonaType to search for
            output_path: Base path for output files
            person_locations: Optional list of locations
            max_contacts: Maximum contacts to retrieve
            file_format: 'csv' or 'excel'
            max_per_file: Maximum contacts per file (default: 100)

        Returns:
            List of generated file paths
        """
        # Search for contacts
        contacts = self.search_by_persona(
            persona=persona,
            person_locations=person_locations,
            max_contacts=max_contacts
        )

        if not contacts:
            raise ValueError(f"No contacts found for persona: {persona.value}")

        # Export to spreadsheet
        if file_format.lower() == "excel":
            files = export_to_excel(contacts, output_path, max_per_file)
        else:
            files = export_to_csv(contacts, output_path, max_per_file)

        return files

    def search_all_and_export(
        self,
        output_dir: str,
        person_locations: Optional[List[str]] = None,
        contacts_per_persona: int = 100,
        file_format: str = "csv",
        max_per_file: int = 100
    ) -> Dict[str, List[str]]:
        """
        Search all personas and export each to separate spreadsheet(s)

        Args:
            output_dir: Directory for output files
            person_locations: Optional list of locations
            contacts_per_persona: Number of contacts per persona
            file_format: 'csv' or 'excel'
            max_per_file: Maximum contacts per file (default: 100)

        Returns:
            Dictionary mapping persona name to list of file paths
        """
        # Search all personas
        all_contacts = self.search_all_personas(
            person_locations=person_locations,
            contacts_per_persona=contacts_per_persona
        )

        # Flatten to single list
        contacts_list = []
        for contacts in all_contacts.values():
            contacts_list.extend(contacts)

        # Export by persona
        print(f"📊 Exporting {len(contacts_list)} total contacts...")
        results = export_by_persona(
            contacts=contacts_list,
            output_dir=output_dir,
            max_per_file=max_per_file,
            file_format=file_format
        )

        print(f"✓ Export complete!")
        return results

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

    def bulk_enrich_emails(self, contacts: List[Contact]) -> List[Contact]:
        """
        Enrich multiple contacts with emails
        WARNING: This uses credits for each contact

        Args:
            contacts: List of contacts to enrich

        Returns:
            List of enriched contacts
        """
        enriched = []
        for i, contact in enumerate(contacts, 1):
            try:
                print(f"Enriching {i}/{len(contacts)}: {contact.name}...")
                enriched_contact = self.enrich_contact_email(contact)
                enriched.append(enriched_contact)
            except Exception as e:
                print(f"⚠️  Failed to enrich {contact.name}: {str(e)}")
                enriched.append(contact)  # Keep original

        return enriched


__all__ = ["SourcingWorkflow"]
