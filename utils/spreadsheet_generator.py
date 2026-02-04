"""Spreadsheet generation utilities for contact exports"""
import csv
import pandas as pd
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from models.contact import Contact, PersonaType


def contacts_to_dataframe(contacts: List[Contact]) -> pd.DataFrame:
    """
    Convert list of Contact objects to pandas DataFrame in sourcing sheet format

    Args:
        contacts: List of Contact objects

    Returns:
        pandas DataFrame with contact data matching sample sourcing sheet format
    """
    data = []
    for contact in contacts:
        # Use first_name and last_name if available, otherwise split the name
        if contact.first_name or contact.last_name:
            first_name = contact.first_name or ""
            last_name = contact.last_name or ""
        else:
            # Fallback: split name into first and last name
            name_parts = contact.name.split(maxsplit=1) if contact.name else ["", ""]
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""

        row = {
            "First Name": first_name,
            "Last Name": last_name,
            "Job Title": contact.title or "",
            "Company": contact.company or "",
            "Email": contact.email or "",
            "Merge status": ""
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
    max_per_sheet: int = 100,
    sheet_name: str = "Contacts"
) -> List[str]:
    """
    Export contacts to a single Excel file with multiple sheets if needed

    Args:
        contacts: List of Contact objects
        output_path: Base output file path (without extension)
        max_per_sheet: Maximum contacts per sheet (default: 100)
        sheet_name: Base name for the Excel sheets

    Returns:
        List containing the single generated file path
    """
    if not contacts:
        raise ValueError("No contacts to export")

    output_path_obj = Path(output_path)
    output_dir = output_path_obj.parent

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate single filename
    filename = f"{output_path_obj.stem}.xlsx"
    file_path = output_dir / filename

    # Split contacts into batches for sheets
    total_sheets = (len(contacts) + max_per_sheet - 1) // max_per_sheet

    # Create Excel writer
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet_idx in range(total_sheets):
            start_idx = sheet_idx * max_per_sheet
            end_idx = min(start_idx + max_per_sheet, len(contacts))
            batch_contacts = contacts[start_idx:end_idx]

            # Generate sheet name
            if total_sheets > 1:
                current_sheet_name = f"{sheet_name}_{sheet_idx + 1}"
            else:
                current_sheet_name = sheet_name

            # Convert to DataFrame and write to sheet
            df = contacts_to_dataframe(batch_contacts)
            df.to_excel(writer, sheet_name=current_sheet_name, index=False)

    return [str(file_path)]


def export_by_persona(
    contacts: List[Contact],
    output_dir: str,
    max_per_file: int = 100,
    file_format: str = "csv"
) -> dict:
    """
    Export contacts grouped by persona
    - CSV: Multiple files with max_per_file contacts each
    - Excel: Single file with multiple sheets (max_per_file contacts per sheet)

    Args:
        contacts: List of Contact objects
        output_dir: Output directory path
        max_per_file: Maximum contacts per file/sheet (default: 100)
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
            # Excel: single file with multiple sheets
            files = export_to_excel(persona_contacts, str(file_path), max_per_sheet=max_per_file)
        else:
            # CSV: multiple files
            files = export_to_csv(persona_contacts, str(file_path), max_per_file)

        results[persona_name] = files

    return results


def export_by_company(
    contacts: List[Contact],
    output_dir: str,
    max_per_file: int = 100,
    file_format: str = "csv"
) -> dict:
    """
    Export contacts grouped by company (separate files for each company)
    - CSV: Multiple files with max_per_file contacts each
    - Excel: Single file with multiple sheets (max_per_file contacts per sheet)

    Args:
        contacts: List of Contact objects
        output_dir: Output directory path
        max_per_file: Maximum contacts per file/sheet (default: 100)
        file_format: 'csv' or 'excel'

    Returns:
        Dictionary mapping company name to list of generated file paths
    """
    if not contacts:
        raise ValueError("No contacts to export")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Group contacts by company
    grouped: dict = {}
    for contact in contacts:
        company = contact.company or "Unknown"
        if company not in grouped:
            grouped[company] = []
        grouped[company].append(contact)

    # Export each company group
    results = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for company, company_contacts in grouped.items():
        # Sanitize company name for filename
        safe_company_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in company)
        base_filename = f"{safe_company_name}_{timestamp}"
        file_path = output_path / base_filename

        if file_format.lower() == "excel":
            # Excel: single file with multiple sheets
            files = export_to_excel(company_contacts, str(file_path), max_per_sheet=max_per_file)
        else:
            # CSV: multiple files
            files = export_to_csv(company_contacts, str(file_path), max_per_file)

        results[company] = files

    return results


def export_by_company_single_file(
    contacts: List[Contact],
    output_dir: str,
    max_per_sheet: int = 100,
    file_format: str = "csv"
) -> str:
    """
    Export contacts grouped by company into a single file with multiple sheets
    - CSV: Creates a ZIP file containing CSV files for each company
    - Excel: Single Excel file with one sheet per company

    Args:
        contacts: List of Contact objects
        output_dir: Output directory path
        max_per_sheet: Maximum contacts per sheet (default: 100)
        file_format: 'csv' or 'excel'

    Returns:
        Path to the generated file
    """
    if not contacts:
        raise ValueError("No contacts to export")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Group contacts by company
    grouped: dict = {}
    for contact in contacts:
        company = contact.company or "Unknown"
        if company not in grouped:
            grouped[company] = []
        grouped[company].append(contact)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if file_format.lower() == "excel":
        # Excel: single file with multiple sheets (one per company)
        filename = f"Companies_Export_{timestamp}.xlsx"
        file_path = output_path / filename

        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for company, company_contacts in grouped.items():
                # Sanitize sheet name (Excel has 31 char limit and no special chars)
                safe_sheet_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in company)
                safe_sheet_name = safe_sheet_name[:31]  # Excel sheet name limit

                # If contacts exceed max_per_sheet, split into multiple sheets
                total_sheets_for_company = (len(company_contacts) + max_per_sheet - 1) // max_per_sheet

                for sheet_idx in range(total_sheets_for_company):
                    start_idx = sheet_idx * max_per_sheet
                    end_idx = min(start_idx + max_per_sheet, len(company_contacts))
                    batch_contacts = company_contacts[start_idx:end_idx]

                    # Generate sheet name
                    if total_sheets_for_company > 1:
                        current_sheet_name = f"{safe_sheet_name}_{sheet_idx + 1}"[:31]
                    else:
                        current_sheet_name = safe_sheet_name

                    # Convert to DataFrame and write to sheet
                    df = contacts_to_dataframe(batch_contacts)
                    df.to_excel(writer, sheet_name=current_sheet_name, index=False)

        return str(file_path)
    else:
        # CSV: Create a ZIP file with one CSV per company
        import zipfile

        filename = f"Companies_Export_{timestamp}.zip"
        file_path = output_path / filename

        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for company, company_contacts in grouped.items():
                # Sanitize company name for filename
                safe_company_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in company)

                # If contacts exceed max_per_sheet, split into multiple files
                total_files_for_company = (len(company_contacts) + max_per_sheet - 1) // max_per_sheet

                for file_idx in range(total_files_for_company):
                    start_idx = file_idx * max_per_sheet
                    end_idx = min(start_idx + max_per_sheet, len(company_contacts))
                    batch_contacts = company_contacts[start_idx:end_idx]

                    # Generate filename
                    if total_files_for_company > 1:
                        csv_filename = f"{safe_company_name}_{file_idx + 1}.csv"
                    else:
                        csv_filename = f"{safe_company_name}.csv"

                    # Convert to DataFrame and save to CSV in memory
                    df = contacts_to_dataframe(batch_contacts)
                    csv_data = df.to_csv(index=False)

                    # Add to ZIP
                    zipf.writestr(csv_filename, csv_data)

        return str(file_path)


__all__ = [
    "contacts_to_dataframe",
    "export_to_csv",
    "export_to_excel",
    "export_by_persona",
    "export_by_company",
    "export_by_company_single_file"
]
