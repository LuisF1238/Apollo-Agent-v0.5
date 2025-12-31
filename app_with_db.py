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
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from config.title_groups import TITLE_GROUPS
import math

# Page config
st.set_page_config(
    page_title="Data Science Sourcing Agent",
    page_icon="🔍",
    layout="wide"
)

# Load authentication config from Streamlit secrets
import copy

try:
    # Try to use Streamlit secrets (for deployment)
    if "credentials" in st.secrets:
        # Deep copy to make secrets mutable for authenticator
        config = {
            'credentials': {
                'usernames': {
                    username: dict(user_data)
                    for username, user_data in st.secrets["credentials"]["usernames"].items()
                }
            },
            'cookie': dict(st.secrets["cookie"])
        }
    else:
        raise KeyError("credentials not in secrets")
except (FileNotFoundError, KeyError, AttributeError):
    # Fallback to config.yaml or defaults (for local development)
    try:
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        # Default credentials if neither secrets nor config file exist
        config = {
            'credentials': {
                'usernames': {
                    'DSS': {
                        'email': 'dss.vpsourcing@gmail.com',
                        'name': 'DSS Sourcer',
                        'password': '$2b$12$5NaLydJ1vOvy95BrathZI.T8G9HrOXHgr.V.dxq/Ygnt95Uss3dZ.'  # hashed 'Best_DSorg100'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'dss_sourcing_agent_key',
                'name': 'dss_sourcing_cookie'
            }
        }

# Create authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Login form
authenticator.login(location='main')

# Check authentication
if st.session_state.get("authentication_status") == False:
    st.error('Username/password is incorrect')
    st.stop()
elif st.session_state.get("authentication_status") == None:
    st.warning('Please enter your username and password')
    st.stop()

# Logout button in sidebar
authenticator.logout(location='sidebar')
st.sidebar.write(f'Welcome *{st.session_state["name"]}*')

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = {}
if "revealed_emails" not in st.session_state:
    st.session_state.revealed_emails = {}
if "workflow_instance" not in st.session_state:
    st.session_state.workflow_instance = SourcingWorkflow()
if "export_files" not in st.session_state:
    st.session_state.export_files = {}
if "selected_companies" not in st.session_state:
    st.session_state.selected_companies = ""
if "dataframe_selection" not in st.session_state:
    st.session_state.dataframe_selection = None
if "selected_title_groups" not in st.session_state:
    st.session_state.selected_title_groups = []


# Title and description
st.title("🔍 DSS Sourcing Agent")
st.markdown("Search Apollo API for Contacts and export to spreadsheets by persona")

# Sidebar for configuration
st.sidebar.header("Search Configuration")

# Persona selection
selected_personas = st.sidebar.multiselect(
    "Personas to Search",
    options=[p.value for p in PersonaType],
    default=[p.value for p in PersonaType],
    help="Select which personas to search for"
)

search_companies = st.sidebar.text_area(
    "Companies (one per line)",
    value=st.session_state.selected_companies,
    height=80,
    help="Leave empty to search all companies"
)

verified_only = st.sidebar.toggle(
    "Verified Profiles Only",
    value=False,
    help="Only retrieve verified Apollo profiles"
)

contacts_per_persona = st.sidebar.slider(
    "Contacts per Persona",
    min_value=10,
    max_value=500,
    value=100,
    step=10,
    help="Number of contacts to retrieve per persona (max 500)"
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

tab1, tab2 = st.tabs(["Find Companies", "Search Contacts"])

with tab1:
    st.header("1. Find Companies")
    if not selected_personas:
        st.error("❌ Please select at least one persona to search")
    else:
        st.subheader("Select a database")
        ops = []
        # Determine which radio buttons to show based on selected personas
        if "Social Good" in selected_personas:
            
            ops.extend(["Social Good: For-Profit", "Social Good: Non-Profit"])

        if "Consulting" in selected_personas or "External" in selected_personas:
            ops.extend(["Fortune 1000", "Y-Combinator"])



        db_choice = st.radio(
                "Choose database:",
                options=ops,
                horizontal=True
            )
        # Load the selected database
        if db_choice:
            if "For-Profit" in db_choice:
                df = pd.read_csv("databases/SG_FORPROFIT.csv")
                st.write("**For-Profit Companies Database**")
            elif "Non-Profit" in db_choice:
                df = pd.read_csv("databases/SG_NONPROFIT.csv")
                st.write("**Non-Profit Companies Database**")
            elif "Fortune" in db_choice:
                df = pd.read_csv("databases/FORTUNE1000.csv")
                df = df.drop("Rank", axis = 1)
                st.write("**Fortune 1000 Companies Database (2024)**")
            else:  # Y-Combinator
                df = pd.read_csv("databases/YCOMBINATOR.csv")
                df = df.drop("id", axis = 1)
                st.write("**Y Combinator Companies Database**")
            
            # Display info about the dataframe
            st.info(f"📊 Database contains {len(df)} companies")
            
            # Find the company name column
            company_col = df.columns[0]
            for col in df.columns:
                if 'name' in col.lower() or 'company' in col.lower():
                    company_col = col
                    break
            
            st.write(f"*Company name column: {company_col}*")
            
            # Display dataframe with selection
            selection = st.dataframe(
                df,
                key="data",
                on_select="rerun",
                selection_mode=["multi-row"],
            )
            
            # Handle selection
            if selection.selection.rows:
                selected_indices = selection.selection.rows
                selected_df = df.iloc[selected_indices]
                selected_company_names = selected_df[company_col].tolist()
                
                st.write(f"**Selected {len(selected_company_names)} companies**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("➕ Add Selected to Search List", type="primary"):
                        # Get existing companies
                        existing = [c.strip() for c in st.session_state.selected_companies.split("\n") if c.strip()]
                        existing_set = set(existing)
                        
                        # Add new companies (avoid duplicates)
                        new_companies = [str(c) for c in selected_company_names if str(c) not in existing_set]
                        
                        # Combine
                        all_companies = existing + new_companies
                        st.session_state.selected_companies = "\n".join(all_companies)
                        
                        st.success(f"✅ Added {len(new_companies)} new companies!")
                        st.rerun()
                
                with col2:
                    if st.button("🔄 Replace Search List", type="secondary"):
                        st.session_state.selected_companies = "\n".join([str(c) for c in selected_company_names])
                        st.success(f"✅ Replaced with {len(selected_company_names)} companies!")
                        st.rerun()
            
            # Show current search list
            if st.session_state.selected_companies.strip():
                with st.expander("📋 Current Search List"):
                    companies_list = [c.strip() for c in st.session_state.selected_companies.split("\n") if c.strip()]
                    st.write(f"**{len(companies_list)} companies in search list:**")
                    for i, company in enumerate(companies_list, 1):
                        st.write(f"{i}. {company}")
                    
                    if st.button("🗑️ Clear Search List"):
                        st.session_state.selected_companies = ""
                        st.success("✅ Search list cleared!")
                        st.rerun()



with tab2:
    st.header("2. Search Contacts")

    st.subheader("🎯 Target Titles")

    selected_title_groups = st.multiselect(
        label="Select priority roles to balance results across",
        options=list(TITLE_GROUPS.keys()),
        default=[],
        help="Contacts will be evenly sampled across selected roles"
    )
    st.session_state.selected_title_groups = selected_title_groups

    if st.button("🚀 Search All Contacts", type="primary", help="Search Apollo for all selected personas"):
        if not selected_personas:
            st.error("❌ Please select at least one persona to search")
        else:
            with st.spinner("Searching Apollo API... This may take a few minutes"):
                try:
                    # Parse companies
                    companies_list = [c.strip() for c in search_companies.split("\n") if c.strip()] if search_companies.strip() else None

                    # Convert persona names back to PersonaType
                    personas_to_search = [PersonaType(p) for p in selected_personas]

                    # Search each persona
                    workflow = st.session_state.workflow_instance
                    total_requested = contacts_per_persona
                    title_groups = st.session_state.get("selected_title_groups", [])

                    if title_groups:
                        per_group_limit = math.ceil(total_requested / len(title_groups))
                    else:
                        per_group_limit = total_requested
                    all_results = {}

                    for persona in personas_to_search:
                        st.write(f"🔍 Searching {persona.value} contacts (requesting {contacts_per_persona})...")

                        persona_contacts = []

                        selected_title_groups = st.session_state.get("selected_title_groups", [])

                        # if titles selected, then balance search
                        if selected_title_groups:
                            per_group_limit = math.ceil(contacts_per_persona / len(selected_title_groups))

                            for group in selected_title_groups:
                                st.write(f"   • {group} (up to {per_group_limit})")

                                contacts = workflow.search_by_persona(
                                    persona=persona,
                                    organization_names=companies_list,
                                    max_contacts=per_group_limit,
                                    verified_only=verified_only,
                                    override_titles=TITLE_GROUPS[group]  
                                )

                                persona_contacts.extend(contacts)

                            # keep desired # of contacts in case we scrape too many
                            persona_contacts = persona_contacts[:contacts_per_persona]

                        # no title selection, do what it did originally
                        else:
                            persona_contacts = workflow.search_by_persona(
                                persona=persona,
                                organization_names=companies_list,
                                max_contacts=contacts_per_persona,
                                verified_only=verified_only
                            )

                        all_results[persona.value] = persona_contacts

                        st.write(f"✓ Found {len(persona_contacts)} {persona.value} contacts")

                        if len(persona_contacts) < contacts_per_persona:
                            st.info(
                                f"ℹ️ Requested {contacts_per_persona} but only "
                                f"{len(persona_contacts)} available from Apollo"
                            )
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
                    # Flatten all contacts and merge in revealed emails
                    all_contacts = []
                    for persona_name, contacts in st.session_state.search_results.items():
                        for idx, contact in enumerate(contacts):
                            # Check if this contact has been enriched
                            contact_id = f"{contact.name}_{contact.apollo_id or idx}_{persona_name}"
                            if contact_id in st.session_state.revealed_emails:
                                # Use the enriched version
                                all_contacts.append(st.session_state.revealed_emails[contact_id])
                            else:
                                # Use the original
                                all_contacts.append(contact)

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

                    # Display file list with download buttons
                    st.subheader("Generated Files")
                    for persona_name, file_list in files.items():
                        st.markdown(f"**{persona_name}:**")
                        for file_path in file_list:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"  • `{Path(file_path).name}`")
                            with col2:
                                # Read file and create download button
                                try:
                                    with open(file_path, "rb") as f:
                                        file_data = f.read()
                                    st.download_button(
                                        label="⬇️ Download",
                                        data=file_data,
                                        file_name=Path(file_path).name,
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if file_path.endswith('.xlsx') else "text/csv",
                                        key=f"download_{file_path}"
                                    )
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")

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

                # Count how many contacts need email enrichment
                contacts_without_email = []
                for i, c in enumerate(contacts):
                    contact_id = f"{c.name}_{c.apollo_id or i}_{persona_name}"
                    if not c.email and contact_id not in st.session_state.revealed_emails:
                        contacts_without_email.append((i, c))

                # Add Reveal All button
                if contacts_without_email:
                    if st.button(f"🔓 Reveal All Emails ({len(contacts_without_email)} contacts)", key=f"reveal_all_{persona_name}", type="primary"):
                        with st.spinner(f"Enriching {len(contacts_without_email)} contacts... This may take a few minutes"):
                            progress_bar = st.progress(0)
                            success_count = 0
                            failed_count = 0

                            for idx, (original_idx, contact) in enumerate(contacts_without_email):
                                contact_id = f"{contact.name}_{contact.apollo_id or original_idx}_{persona_name}"
                                try:
                                    enriched = st.session_state.workflow_instance.enrich_contact_email(contact)
                                    st.session_state.revealed_emails[contact_id] = enriched
                                    if enriched.email:
                                        success_count += 1
                                    else:
                                        failed_count += 1
                                except Exception as e:
                                    st.session_state.revealed_emails[contact_id] = contact
                                    failed_count += 1
                                    print(f"Failed to enrich {contact.name}: {str(e)}")

                                progress_bar.progress((idx + 1) / len(contacts_without_email))

                            st.success(f"✅ Enrichment complete! Found {success_count} emails, {failed_count} not found")
                            st.rerun()

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
                                                    st.info("ℹ️ Email not available in Apollo database for this contact")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("From the Fall 25 Newbies Luis, Lauren, Praneel")
