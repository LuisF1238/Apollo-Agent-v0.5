# AI-Agents

Professional networking automation platform powered by AI agents for intelligent resume parsing, contact matching, and personalized outreach.

## Overview

AI-Agents is a sophisticated system that helps professionals expand their network by:
- Parsing resumes to extract structured profile information
- Finding relevant contacts based on connection points
- Generating personalized cold emails for coffee chats and informational interviews
- Managing outreach campaigns with rate limiting and tracking

## Features

### 🤖 AI-Powered Resume Parser
- Extract structured data from PDF resumes using OpenAI GPT-4
- Parse education history, work experience, skills, and contact information
- Clean and normalize resume text for accurate extraction

### 🔗 Intelligent Contact Matching
- Identify connection points (shared schools, companies, locations, skills)
- Calculate relevance scores based on multiple factors
- Prioritize contacts with strongest connections

### ✉️ Personalized Email Generation
- Generate authentic, non-salesy cold emails
- Reference specific connection points naturally
- Maintain professional yet approachable tone
- Clear call-to-action for 15-min calls or coffee chats

### 🛡️ Rate Limiting & Compliance
- Built-in rate limiters for API calls
- Email sending rate limits to avoid spam flags
- Validate all contact information before outreach

## Project Structure

```
Apollo-Agent/
├── agents/                  # AI agent implementations
│   ├── profile_parser.py   # Resume parsing agent
│   ├── contact_matcher.py  # Contact matching and scoring
│   ├── email_generator.py  # Email generation agent
│   └── __init__.py
├── api/                     # API client wrappers
│   ├── openai_client.py    # OpenAI API wrapper
│   ├── apollo_client.py    # Apollo.io API client
│   └── __init__.py
├── config/                  # Configuration and prompts
│   ├── settings.py         # Environment settings
│   ├── prompts.py          # AI prompt templates
│   └── __init__.py
├── models/                  # Data models
│   ├── user.py            # UserProfile, Education, Experience
│   ├── contact.py         # Contact, ConnectionPoint
│   ├── email.py           # EmailDraft, EmailStatus
│   └── __init__.py
├── utils/                   # Utility functions
│   ├── pdf_parser.py       # PDF text extraction
│   ├── parse_resume.py     # Resume parsing utilities
│   ├── validators.py       # Data validation
│   ├── rate_limiter.py     # Rate limiting
│   └── __init__.py
├── Resume/                  # Sample resumes
├── workflow.py              # Main workflow orchestration
├── streamlit_app.py         # Streamlit web interface
├── example_usage.py         # Usage examples
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
├── .gitignore
└── README.md
```

## Installation

### Prerequisites
- Python 3.13+
- OpenAI API key
- Apollo.io API key (optional, for contact enrichment)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Apollo-Agent
```

2. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your API keys:
```bash
# OpenAI API
OPENAI_API_KEY=your_openai_key_here

# Apollo.io API
APOLLO_API_KEY=your_apollo_key_here

# Email Services (optional)
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# Rate Limiting
APOLLO_RATE_LIMIT=50
EMAIL_RATE_LIMIT=20

# Environment
ENVIRONMENT=development
```

## Usage

### Web Interface (Streamlit)

The easiest way to use the Coffee Chat Agent is through the Streamlit web interface:

```bash
streamlit run streamlit_app.py
```

Or use the provided shell script:
```bash
./run_streamlit.sh
```

The web interface allows you to:
- Upload your resume (PDF format)
- Parse and view your profile information
- Configure search criteria (job titles, locations, seniority levels)
- Run the full workflow to find contacts and generate emails
- View and download generated email drafts
- Export results as JSON

### Parse a Resume (Python API)

```python
from agents.profile_parser import ProfileParserAgent

# Initialize the parser
parser = ProfileParserAgent()

# Parse a resume PDF
profile = parser.parse_resume_pdf("path/to/resume.pdf")

print(f"Name: {profile.name}")
print(f"Current Role: {profile.current_role} at {profile.current_company}")
print(f"Skills: {', '.join(profile.skills)}")
```

### Run Full Coffee Chat Workflow

```python
from workflow import CoffeeChatWorkflow

# Initialize workflow
workflow = CoffeeChatWorkflow()

# Run complete workflow
result = workflow.run_full_workflow(
    resume_path="Resume/your_resume.pdf",
    search_titles=["Senior Data Scientist", "ML Engineer"],
    search_locations=["San Francisco Bay Area"],
    search_seniorities=["senior", "manager"],
    max_contacts=10,
    min_relevance_score=0.5
)

# Access results
print(f"Found {len(result['relevant_contacts'])} relevant contacts")
print(f"Generated {len(result['email_drafts'])} email drafts")
```

### Validate Contact Information

```python
from utils.validators import validate_email, 

# Validate email
is_valid = validate_email("contact@example.com")



### Use Rate Limiter

```python
from utils.rate_limiter import RateLimiter

# Create rate limiter (50 requests per minute)
limiter = RateLimiter(max_requests=50, time_window=60)

# Before making API call
if limiter.acquire(block=True, timeout=10):
    # Make your API call
    pass
```

## Data Models

### UserProfile
Structured representation of a user's professional profile:
- Personal information (name, email, location)
- Education history
- Work experience
- Skills and competencies

### Contact
Prospect or networking contact with:
- Basic contact information
- Company and role details
- Connection points with relevance scores

### EmailDraft
Generated email with:
- Personalized content
- Tracking status
- Connection points used
- Send/open/reply timestamps

## Configuration

### Environment Variables
All configuration is managed through environment variables in `.env`:

- `OPENAI_API_KEY`: OpenAI API key (required)
- `APOLLO_API_KEY`: Apollo.io API key (optional)
- `APOLLO_RATE_LIMIT`: Apollo API rate limit (default: 50 req/min)
- `EMAIL_RATE_LIMIT`: Email sending rate limit (default: 20/hour)
- `ENVIRONMENT`: development or production

### AI Prompt Templates
Customize AI behavior by editing prompts in `config/prompts.py`:
- `PROFILE_PARSER_SYSTEM_PROMPT`: Resume parsing instructions
- `EMAIL_GENERATOR_SYSTEM_PROMPT`: Email generation guidelines
- `RELEVANCE_ANALYSIS_PROMPT`: Contact matching criteria

## Development

### Running Tests
```bash
source .venv/bin/activate
pytest tests/
```

### Code Style
Follow PEP 8 guidelines. Use type hints for all functions.

### Adding New Agents
1. Create new agent file in `agents/` directory
2. Implement agent class with clear documentation
3. Add to `agents/__init__.py` exports
4. Add corresponding prompts to `config/prompts.py`


## Quick Start

1. Set up your environment (see Installation)
2. Add your API keys to `.env`
3. Launch the Streamlit interface:
   ```bash
   ./run_streamlit.sh
   ```
4. Upload your resume
5. Configure search parameters
6. Run the workflow and get personalized emails!

## Roadmap

- [x] Resume parsing with AI
- [x] Apollo.io integration for contact search
- [x] Contact matching and scoring
- [x] Personalized email generation
- [x] Streamlit web interface
- [x] Email enrichment (reveal contact emails)
- [ ] Database integration for storing contacts and campaigns
- [ ] Email tracking (opens, clicks, replies)
- [ ] A/B testing for email templates
- [ ] Multi-user support with authentication
- [ ] Email sending integration (Gmail, SendGrid)
- [ ] Follow-up email automation


