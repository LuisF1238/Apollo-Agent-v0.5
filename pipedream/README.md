# Pipedream Integration Guide

This directory contains files for integrating the Apollo Coffee Chat Agent with Pipedream workflows.

## Overview

Pipedream allows you to create automated workflows that can:
- Trigger when you upload a resume
- Search for relevant contacts via Apollo.io
- Generate personalized coffee chat emails
- Send emails via Gmail/SendGrid
- Store results in a database or spreadsheet

## Quick Start

### 1. Set up Pipedream Workflow

1. Go to [Pipedream.com](https://pipedream.com) and create a new workflow
2. Choose "HTTP/Webhook" as the trigger
3. Copy your webhook URL

### 2. Configure Python Environment

Add a Python code step in Pipedream with the following:

```python
import sys
sys.path.append('/tmp')

# Your Apollo Agent code will be deployed here
from webhook_handler import handler

def handler(pd: "pipedream"):
    event = {
        "action": "full_workflow",
        "resume_path": pd.steps["trigger"]["event"]["body"]["resume_path"],
        "search_criteria": {
            "titles": ["Senior Engineer", "Engineering Manager"],
            "locations": ["San Francisco Bay Area"],
            "seniorities": ["senior", "vp"],
            "max_contacts": 25
        },
        "min_relevance_score": 0.5
    }

    result = handler(event)
    return result
```

### 3. Add Environment Variables

In Pipedream, go to Settings > Environment Variables and add:

- `OPENAI_API_KEY`: Your OpenAI API key
- `APOLLO_API_KEY`: Your Apollo.io API key

## Available Actions

### 1. Full Workflow (`action: "full_workflow"`)

Runs the complete process from resume parsing to email generation.

**Request:**
```json
{
  "action": "full_workflow",
  "resume_path": "/path/to/resume.pdf",
  "search_criteria": {
    "titles": ["Senior Engineer", "Product Manager"],
    "locations": ["San Francisco Bay Area", "New York"],
    "seniorities": ["senior", "vp"],
    "max_contacts": 25
  },
  "min_relevance_score": 0.5
}
```

**Alternative (Base64 Resume):**
```json
{
  "action": "full_workflow",
  "resume_base64": "JVBERi0xLjQKJeLjz9MKMyAwIG9iaiA8...",
  "search_criteria": {...}
}
```

**Response:**
```json
{
  "success": true,
  "user_profile": {
    "name": "John Doe",
    "current_company": "Tech Corp",
    "current_role": "Software Engineer"
  },
  "contacts_found": 25,
  "relevant_contacts": 10,
  "emails_generated": 10,
  "email_drafts": [
    {
      "contact_name": "Jane Smith",
      "contact_email": "jane@example.com",
      "subject": "Stanford alum interested in your AI work",
      "body": "Hi Jane,\n\nI noticed we both studied at Stanford..."
    }
  ]
}
```

### 2. Parse Resume Only (`action: "parse_resume"`)

**Request:**
```json
{
  "action": "parse_resume",
  "resume_path": "/path/to/resume.pdf"
}
```

**Response:**
```json
{
  "success": true,
  "user_profile": {
    "name": "John Doe",
    "education": [...],
    "experiences": [...],
    "skills": [...]
  }
}
```

### 3. Search Contacts (`action: "search_contacts"`)

**Request:**
```json
{
  "action": "search_contacts",
  "titles": ["Senior Engineer", "Staff Engineer"],
  "locations": ["San Francisco Bay Area"],
  "seniorities": ["senior"],
  "max_results": 50
}
```

**Response:**
```json
{
  "success": true,
  "count": 50,
  "contacts": [
    {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "company": "Meta",
      "title": "Senior Engineer"
    }
  ]
}
```

### 4. Generate Emails (`action: "generate_emails"`)

**Request:**
```json
{
  "action": "generate_emails",
  "user_profile": {...},
  "contacts": [...],
  "min_relevance_score": 0.5
}
```

**Response:**
```json
{
  "success": true,
  "contacts_analyzed": 25,
  "relevant_contacts": 10,
  "emails_generated": 10,
  "email_drafts": [...]
}
```

## Example Pipedream Workflows

### Workflow 1: Resume Upload → Email Generation

```
1. HTTP Trigger (receives resume upload)
2. Python: Parse Resume
3. Python: Search Apollo Contacts
4. Python: Match & Generate Emails
5. Gmail: Send Emails (with rate limiting)
6. Google Sheets: Log Results
```

### Workflow 2: Scheduled Daily Outreach

```
1. Schedule Trigger (daily at 9am)
2. Google Drive: Get Latest Resume
3. Python: Full Workflow
4. Filter: Only contacts with score > 0.7
5. SendGrid: Send Top 5 Emails
6. Airtable: Update Campaign Tracker
```

### Workflow 3: Manual Trigger with Slack

```
1. Slack: New Message in #networking
2. Parse Resume from Slack Attachment
3. Python: Full Workflow
4. Slack: Send Summary to Channel
5. User: Approve Emails
6. Gmail: Send Approved Emails
```

## Deploying Your Code to Pipedream

### Option 1: Inline Code

Copy the contents of `webhook_handler.py` and all dependencies directly into a Pipedream Python step.

### Option 2: PyPI Package (Recommended)

1. Package your code as a Python package
2. Publish to PyPI
3. Install in Pipedream: `pip install your-package-name`

### Option 3: GitHub Integration

1. Push code to GitHub repository
2. Use Pipedream's GitHub integration to import code
3. Set up auto-sync for updates

## Environment Variables Required

```
OPENAI_API_KEY=sk-...
APOLLO_API_KEY=...
GMAIL_EMAIL=your-email@gmail.com (optional)
GMAIL_APP_PASSWORD=... (optional)
SENDGRID_API_KEY=... (optional)
```

## Rate Limiting

The workflow includes built-in rate limiting:
- Apollo API: 50 requests/minute (configurable)
- Email sending: 20 emails/hour (configurable)

Configure in `.env`:
```
APOLLO_RATE_LIMIT=50
EMAIL_RATE_LIMIT=20
```

## Error Handling

All handlers return a consistent response format:

**Success:**
```json
{
  "success": true,
  "data": {...}
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message details"
}
```

## Testing Locally

Test the webhook handler locally before deploying to Pipedream:

```python
from pipedream.webhook_handler import handler

# Test full workflow
event = {
    "action": "full_workflow",
    "resume_path": "Resume/your_resume.pdf",
    "search_criteria": {
        "titles": ["Senior Engineer"],
        "locations": ["San Francisco"],
        "max_contacts": 5
    }
}

result = handler(event)
print(result)
```

## Next Steps

1. ✅ Set up Pipedream account
2. ✅ Create new workflow with HTTP trigger
3. ✅ Add environment variables
4. ✅ Deploy webhook handler code
5. ✅ Test with sample resume
6. ✅ Connect email sending service (Gmail/SendGrid)
7. ✅ Add logging/tracking (Google Sheets/Airtable)
8. ✅ Schedule automated runs

## Support

For issues or questions:
- Check Pipedream docs: https://pipedream.com/docs
- Apollo.io API docs: https://apolloio.github.io/apollo-api-docs
- OpenAI API docs: https://platform.openai.com/docs
