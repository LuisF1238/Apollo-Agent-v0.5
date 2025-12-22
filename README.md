# Apollo Agent v0.5 - DSS Sourcing Agent

A data science sourcing tool that leverages the Apollo.io API to search, filter, and export contacts across different personas for recruitment and networking purposes.

## Overview

The DSS Sourcing Agent streamlines the process of finding and organizing data science professionals by:
- Searching contacts via Apollo.io API based on customizable persona filters
- Organizing contacts into three persona categories: Consulting, Social Good, and External
- Enriching contact information with verified email addresses
- Exporting results to CSV or Excel spreadsheets

## Features

- **Multi-Persona Search**: Target contacts across Consulting, Social Good, and External tech sectors
- **Flexible Filtering**: Filter by company names, job titles, seniority levels, and industries
- **Email Enrichment**: Reveal and verify contact email addresses using Apollo.io credits
- **Batch Export**: Export contacts to CSV or Excel with automatic file splitting for large datasets
- **Interactive UI**: Streamlit-based web interface for easy searching and contact management
- **Configurable Limits**: Set maximum contacts per persona and per file

## Project Structure

```
Apollo Agent v0.5/
├── api/
│   └── apollo_client.py          # Apollo.io API client
├── config/
│   ├── personas.py                # Persona filter configurations
│   ├── prompts.py                 # AI prompt templates
│   └── settings.py                # Application settings
├── models/
│   ├── contact.py                 # Contact data model
│   ├── email.py                   # Email model
│   └── user.py                    # User model
├── utils/
│   ├── spreadsheet_generator.py   # CSV/Excel export utilities
│   ├── rate_limiter.py            # API rate limiting
│   └── validators.py              # Data validation utilities
├── agents/
│   └── email_generator.py         # Email generation agent
├── exports/                        # Default export directory
├── streamlit_app.py               # Main Streamlit UI
├── sourcing_workflow.py           # Core workflow orchestration
├── workflow.py                    # Legacy workflow
└── requirements.txt               # Python dependencies
```

## Installation

### Prerequisites

- Python 3.8+
- Apollo.io API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd "Apollo Agent v0.5"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the project root:
```env
APOLLO_API_KEY=your_apollo_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional: for email generation features
```

## Usage

### Running the Streamlit Application

Launch the interactive web interface:
```bash
streamlit run streamlit_app.py
```

The application will open in your browser with the following workflow:

1. **Configure Search Parameters** (Sidebar):
   - Select personas to search (Consulting, Social Good, External)
   - Enter company names (one per line) or leave empty for all companies
   - Set contacts per persona (10-500)
   - Choose export format (CSV or Excel)
   - Set max contacts per file for splitting large datasets

2. **Search Contacts**:
   - Click "Search All Contacts" to query Apollo.io
   - View search summary with contact counts by persona

3. **Enrich Emails** (Optional):
   - Use "Reveal All Emails" to enrich contacts with verified emails
   - Or reveal individual emails by expanding contact cards

4. **Export Results**:
   - Choose output directory
   - Click "Export All" to generate spreadsheet files
   - Files are organized by persona and automatically split if needed

### Programmatic Usage

```python
from sourcing_workflow import SourcingWorkflow
from models.contact import PersonaType

# Initialize workflow
workflow = SourcingWorkflow()

# Search by persona
contacts = workflow.search_by_persona(
    persona=PersonaType.CONSULTING,
    organization_names=["Google", "Meta", "Amazon"],
    max_contacts=100
)

# Search all personas and export
results = workflow.search_all_and_export(
    output_dir="./exports",
    organization_names=["Patagonia", "REI"],
    contacts_per_persona=50,
    file_format="excel",
    max_per_file=100
)

# Enrich contact with email
enriched_contact = workflow.enrich_contact_email(contacts[0])
```

## Persona Definitions

### Consulting
Target professionals in consulting firms with titles including:
- Data Science Directors/Heads
- Product Managers/Directors
- Analytics Directors
- BI Directors
- Data Engineering Leadership

Industries: Management Consulting, Strategy Consulting, Technology Consulting

### Social Good
Target professionals in nonprofit and social impact sectors with titles including:
- Impact Analytics/MEL Directors
- Research Data Scientists
- Program Analytics Directors
- Innovation Program Managers
- Partnerships Directors
- Research & Evaluation Leads
- Data Engineering Leadership

Industries: Nonprofit, Education, Healthcare, Government, Environmental, Social Impact

### External
Target data science practitioners in tech companies:
- Data Scientists (all levels)
- Machine Learning Engineers
- Data Engineers
- Applied Scientists

Industries: Technology, Software, Internet, E-commerce, Financial Services, Fintech

## API Credits

- **Search**: Free contact search with basic information
- **Email Enrichment**: Uses Apollo.io credits to reveal verified email addresses
- Rate limiting is implemented to avoid API throttling

## Export Formats

### CSV Export
- One CSV file per persona (or split into batches if exceeding max per file)
- Columns: Name, Email, Phone, Company, Title, Location, Persona, LinkedIn, Industry, Seniority

### Excel Export
- One Excel workbook per persona (or split into batches)
- Same columns as CSV with enhanced formatting

## Configuration

### Customizing Personas

Edit [config/personas.py](config/personas.py) to modify search filters:
```python
PERSONA_FILTERS[PersonaType.CONSULTING] = {
    "person_titles": ["Your", "Custom", "Titles"],
    "person_seniorities": ["senior", "manager", "director"],
    "organization_industries": ["Your", "Industries"],
}
```


## Development

### Testing Search Parameters
Use the Streamlit UI to test different search combinations before implementing programmatic workflows.

### Extending Personas
Add new persona types in [models/contact.py](models/contact.py) and configure filters in [config/personas.py](config/personas.py).

## Credits

From the Fall 25 Newbies: Luis, Lauren, Praneel

