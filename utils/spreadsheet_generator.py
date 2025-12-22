"""Spreadsheet generation utilities for contact exports"""
import csv
import pandas as pd
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from models.contact import Contact, PersonaType


def contacts_to_dataframe(contacts: List[Contact]) -> pd.DataFrame:
    """
    Convert list of Contact objects to pandas DataFrame

    Args:
        contacts: List of Contact objects

    Returns:
        pandas DataFrame with contact data
    """
    data = []
    for contact in contacts:
        row = {
            "Name": contact.name,
            "Email": contact.email or "",
            "Phone": contact.phone or "",
            "Company": contact.company or "",
            "Title": contact.title or "",
            "Location": contact.location or "",
            "Persona": contact.persona.value if contact.persona else "",
            "LinkedIn": contact.linkedin_url or "",
            "Years of Experience": contact.years_of_experience or "",
            "Skills": ", ".join(contact.skills) if contact.skills else "",
            "Industry": contact.industry or "",
            "Seniority": contact.seniority or "",
            "Relevance Score": f"{contact.relevance_score:.2f}",
            "Apollo ID": contact.apollo_id or "",
            "Notes": contact.notes or ""
        }
        data.append(row)

    return pd.DataFrame(data)


def export_to_csv(
    contacts: List[Contact],
    output_path: str,
    max_per_file: int = 100
) -> List[str]:
    """
    Export contacts to CSV file(s), splitting into multiple files if needed

    Args:
        contacts: List of Contact objects
        output_path: Base output file path (without extension)
        max_per_file: Maximum contacts per file (default: 100)

    Returns:
        List of generated file paths
    """
    if not contacts:
        raise ValueError("No contacts to export")

    output_path_obj = Path(output_path)
    base_name = output_path_obj.stem
    output_dir = output_path_obj.parent

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    # Split contacts into batches
    total_batches = (len(contacts) + max_per_file - 1) // max_per_file

    for batch_idx in range(total_batches):
        start_idx = batch_idx * max_per_file
        end_idx = min(start_idx + max_per_file, len(contacts))
        batch_contacts = contacts[start_idx:end_idx]

        # Generate filename
        if total_batches > 1:
            filename = f"{base_name}_batch_{batch_idx + 1}_of_{total_batches}.csv"
        else:
            filename = f"{base_name}.csv"

        file_path = output_dir / filename

        # Convert to DataFrame and save
        df = contacts_to_dataframe(batch_contacts)
        df.to_csv(file_path, index=False)

        generated_files.append(str(file_path))

    return generated_files


def export_to_excel(
    contacts: List[Contact],
    output_path: str,
    max_per_file: int = 100,
    sheet_name: str = "Contacts"
) -> List[str]:
    """
    Export contacts to Excel file(s), splitting into multiple files if needed

    Args:
        contacts: List of Contact objects
        output_path: Base output file path (without extension)
        max_per_file: Maximum contacts per file (default: 100)
        sheet_name: Name of the Excel sheet

    Returns:
        List of generated file paths
    """
    if not contacts:
        raise ValueError("No contacts to export")

    output_path_obj = Path(output_path)
    base_name = output_path_obj.stem
    output_dir = output_path_obj.parent

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    # Split contacts into batches
    total_batches = (len(contacts) + max_per_file - 1) // max_per_file

    for batch_idx in range(total_batches):
        start_idx = batch_idx * max_per_file
        end_idx = min(start_idx + max_per_file, len(contacts))
        batch_contacts = contacts[start_idx:end_idx]

        # Generate filename
        if total_batches > 1:
            filename = f"{base_name}_batch_{batch_idx + 1}_of_{total_batches}.xlsx"
        else:
            filename = f"{base_name}.xlsx"

        file_path = output_dir / filename

        # Convert to DataFrame and save
        df = contacts_to_dataframe(batch_contacts)
        df.to_excel(file_path, sheet_name=sheet_name, index=False)

        generated_files.append(str(file_path))

    return generated_files


def export_by_persona(
    contacts: List[Contact],
    output_dir: str,
    max_per_file: int = 100,
    file_format: str = "csv"
) -> dict:
    """
    Export contacts grouped by persona, each to separate file(s)

    Args:
        contacts: List of Contact objects
        output_dir: Output directory path
        max_per_file: Maximum contacts per file (default: 100)
        file_format: 'csv' or 'excel'

    Returns:
        Dictionary mapping persona to list of generated file paths
    """
    if not contacts:
        raise ValueError("No contacts to export")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Group contacts by persona
    grouped: dict = {}
    for contact in contacts:
        persona = contact.persona or "Unknown"
        if persona not in grouped:
            grouped[persona] = []
        grouped[persona].append(contact)

    # Export each persona group
    results = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for persona, persona_contacts in grouped.items():
        persona_name = persona.value if isinstance(persona, PersonaType) else str(persona)
        base_filename = f"{persona_name}_{timestamp}"
        file_path = output_path / base_filename

        if file_format.lower() == "excel":
            files = export_to_excel(persona_contacts, str(file_path), max_per_file)
        else:
            files = export_to_csv(persona_contacts, str(file_path), max_per_file)

        results[persona_name] = files

    return results


__all__ = [
    "contacts_to_dataframe",
    "export_to_csv",
    "export_to_excel",
    "export_by_persona"
]
