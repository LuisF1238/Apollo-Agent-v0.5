"""
Streamlit UI for Data Science Sourcing Agent
Search Apollo for Data Science contacts and export to spreadsheets
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from sourcing_workflow import SourcingWorkflow
from models.contact import PersonaType

# Page config
st.set_page_config(
    page_title="Data Science Sourcing Agent",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = {}
if "revealed_emails" not in st.session_state:
    st.session_state.revealed_emails = {}
if "workflow_instance" not in st.session_state:
    st.session_state.workflow_instance = SourcingWorkflow()
if "export_files" not in st.session_state:
    st.session_state.export_files = {}

# Title and description
st.title("🔍 Data Science Sourcing Agent")
st.markdown("Search Apollo API for Data Science contacts and export to spreadsheets by persona")

# Sidebar for configuration
st.sidebar.header("Search Configuration")

# Persona selection
selected_personas = st.sidebar.multiselect(
    "Personas to Search",
    options=[p.value for p in PersonaType],
    default=[p.value for p in PersonaType],
    help="Select which personas to search for"
)

search_locations = st.sidebar.text_area(
    "Locations (one per line)",
    value="San Francisco Bay Area\nNew York\nBoston",
    height=80,
    help="Leave empty to search all locations"
)

contacts_per_persona = st.sidebar.slider(
    "Contacts per Persona",
    min_value=10,
    max_value=500,
    value=100,
    step=10,
    help="Number of contacts to retrieve per persona"
)

max_per_file = st.sidebar.slider(
    "Max Contacts per File",
    min_value=50,
    max_value=200,
    value=100,
    step=50,
    help="Split results into multiple files if exceeded"
)

file_format = st.sidebar.selectbox(
    "Export Format",
    options=["CSV", "Excel"],
    index=0
)

# Main content
st.header("1. Search & Export Contacts")

if st.button("🚀 Search All Personas", type="primary", help="Search Apollo for all selected personas"):
    if not selected_personas:
        st.error("❌ Please select at least one persona to search")
    else:
        with st.spinner("Searching Apollo API... This may take a few minutes"):
            try:
                # Parse locations
                locations_list = [l.strip() for l in search_locations.split("\n") if l.strip()] if search_locations.strip() else None

                # Convert persona names back to PersonaType
                personas_to_search = [PersonaType(p) for p in selected_personas]

                # Search each persona
                workflow = st.session_state.workflow_instance
                all_results = {}

                for persona in personas_to_search:
                    st.write(f"🔍 Searching {persona.value} contacts...")
                    contacts = workflow.search_by_persona(
                        persona=persona,
                        person_locations=locations_list,
                        max_contacts=contacts_per_persona
                    )
                    all_results[persona.value] = contacts
                    st.write(f"✓ Found {len(contacts)} {persona.value} contacts")

                st.session_state.search_results = all_results
                st.success(f"✅ Search completed! Found {sum(len(c) for c in all_results.values())} total contacts")

                # Display summary
                st.subheader("Search Summary")
                cols = st.columns(len(personas_to_search))
                for idx, (persona_name, contacts) in enumerate(all_results.items()):
                    with cols[idx]:
                        st.metric(persona_name, len(contacts))

            except Exception as e:
                st.error(f"❌ Error during search: {str(e)}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())

# Export section
if st.session_state.search_results:
    st.header("2. Export to Spreadsheets")

    col1, col2 = st.columns([2, 1])

    with col1:
        output_dir = st.text_input(
            "Output Directory",
            value="./exports",
            help="Directory where spreadsheets will be saved"
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        export_button = st.button("📊 Export All", type="secondary")

    if export_button:
        with st.spinner("Exporting to spreadsheets..."):
            try:
                # Flatten all contacts
                all_contacts = []
                for contacts in st.session_state.search_results.values():
                    all_contacts.extend(contacts)

                # Export by persona
                from utils.spreadsheet_generator import export_by_persona

                files = export_by_persona(
                    contacts=all_contacts,
                    output_dir=output_dir,
                    max_per_file=max_per_file,
                    file_format=file_format.lower()
                )

                st.session_state.export_files = files
                st.success(f"✅ Export complete! Generated {sum(len(f) for f in files.values())} file(s)")

                # Display file list
                st.subheader("Generated Files")
                for persona_name, file_list in files.items():
                    st.markdown(f"**{persona_name}:**")
                    for file_path in file_list:
                        st.write(f"  • `{file_path}`")

            except Exception as e:
                st.error(f"❌ Error during export: {str(e)}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())

# Display results
if st.session_state.search_results:
    st.header("3. View Contacts")

    # Tabs for different personas
    persona_tabs = st.tabs([p for p in st.session_state.search_results.keys()])

    for tab_idx, (persona_name, contacts) in enumerate(st.session_state.search_results.items()):
        with persona_tabs[tab_idx]:
            st.subheader(f"{persona_name} Contacts ({len(contacts)})")

            # Sort options
            sort_by = st.selectbox(f"Sort by", ["Name", "Company", "Title"], key=f"sort_{persona_name}")

            contacts_to_show = contacts.copy()
            if sort_by == "Name":
                contacts_to_show.sort(key=lambda x: x.name)
            elif sort_by == "Company":
                contacts_to_show.sort(key=lambda x: x.company or "")
            elif sort_by == "Title":
                contacts_to_show.sort(key=lambda x: x.title or "")

            # Display contacts in a table-like format
            for idx, contact in enumerate(contacts_to_show):
                contact_id = f"{contact.name}_{contact.apollo_id or idx}_{persona_name}"

                with st.expander(f"👤 {contact.name} - {contact.title or 'N/A'} at {contact.company or 'N/A'}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Contact Info**")
                        st.write(f"**Name:** {contact.name}")
                        st.write(f"**Title:** {contact.title or 'N/A'}")
                        st.write(f"**Company:** {contact.company or 'N/A'}")
                        st.write(f"**Location:** {contact.location or 'N/A'}")
                        st.write(f"**Seniority:** {contact.seniority or 'N/A'}")

                    with col2:
                        st.markdown("**Additional Details**")
                        st.write(f"**Industry:** {contact.industry or 'N/A'}")
                        st.write(f"**Persona:** {contact.persona.value if contact.persona else 'N/A'}")

                        # Check if email is revealed
                        enriched_contact = st.session_state.revealed_emails.get(contact_id)
                        if enriched_contact:
                            st.write(f"**Email:** {enriched_contact.email or 'Not found'}")
                            if enriched_contact.phone:
                                st.write(f"**Phone:** {enriched_contact.phone}")
                        else:
                            if contact.email:
                                st.write(f"**Email:** {contact.email}")
                            else:
                                if st.button(f"🔓 Reveal Email", key=f"reveal_{contact_id}"):
                                    with st.spinner(f"Enriching {contact.name}'s email..."):
                                        try:
                                            enriched = st.session_state.workflow_instance.enrich_contact_email(contact)
                                            st.session_state.revealed_emails[contact_id] = enriched
                                            if enriched.email:
                                                st.success(f"✅ Email: {enriched.email}")
                                            else:
                                                st.warning("⚠️ No email found")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("From the Agentic Interal Project Team")
