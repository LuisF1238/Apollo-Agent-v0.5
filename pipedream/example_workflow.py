"""
Example Pipedream workflow configurations
Copy these into your Pipedream Python steps
"""

# =============================================================================
# STEP 1: HTTP Trigger Configuration
# =============================================================================
# In Pipedream, add an HTTP/Webhook trigger
# This will give you a URL like: https://eoxxx.m.pipedream.net


# =============================================================================
# STEP 2: Parse Resume and Search Contacts
# =============================================================================
def handler(pd: "pipedream"):
    """
    This step parses the resume and searches for contacts
    """
    # Import required packages
    import json
    import sys
    import os

    # Set environment variables from Pipedream secrets
    os.environ['OPENAI_API_KEY'] = pd.secrets['OPENAI_API_KEY']
    os.environ['APOLLO_API_KEY'] = pd.secrets['APOLLO_API_KEY']

    # Import your workflow handler
    # Note: You'll need to upload your code to Pipedream or install as package
    from webhook_handler import handler as workflow_handler

    # Get resume from trigger
    # Option 1: Resume path from form upload
    resume_path = pd.steps["trigger"]["event"]["body"].get("resume_path")

    # Option 2: Base64 encoded resume from file upload
    resume_base64 = pd.steps["trigger"]["event"]["body"].get("resume_base64")

    # Build event
    event = {
        "action": "full_workflow",
        "resume_path": resume_path,
        "resume_base64": resume_base64,
        "search_criteria": {
            "titles": [
                "Senior Software Engineer",
                "Staff Engineer",
                "Engineering Manager",
                "Product Manager"
            ],
            "locations": [
                "San Francisco Bay Area",
                "New York City",
                "Remote"
            ],
            "seniorities": ["senior", "vp", "cxo"],
            "max_contacts": 25
        },
        "min_relevance_score": 0.5
    }

    # Run workflow
    result = workflow_handler(event)

    # Return result for next step
    return result


# =============================================================================
# STEP 3: Filter and Prepare Emails
# =============================================================================
def handler(pd: "pipedream"):
    """
    Filter email drafts and prepare for sending
    """
    workflow_result = pd.steps["step_2"]["$return_value"]

    if not workflow_result.get("success"):
        return {
            "error": workflow_result.get("error"),
            "should_send": False
        }

    email_drafts = workflow_result.get("email_drafts", [])

    # Filter: Only send to contacts with relevance > 0.6
    high_quality_drafts = [
        draft for draft in email_drafts
        if draft.get("relevance_score", 0) > 0.6
    ]

    # Limit to top 5 per day to avoid spam
    drafts_to_send = high_quality_drafts[:5]

    return {
        "should_send": len(drafts_to_send) > 0,
        "draft_count": len(drafts_to_send),
        "drafts": drafts_to_send,
        "summary": f"Found {len(email_drafts)} drafts, sending top {len(drafts_to_send)}"
    }


# =============================================================================
# STEP 4: Send Emails via Gmail
# =============================================================================
def handler(pd: "pipedream"):
    """
    Send emails using Gmail integration
    """
    import time

    drafts = pd.steps["step_3"]["$return_value"]["drafts"]

    if not pd.steps["step_3"]["$return_value"]["should_send"]:
        return {"message": "No emails to send"}

    sent_emails = []

    for draft in drafts:
        # Use Pipedream's built-in Gmail action
        # Or implement SMTP sending here

        email_data = {
            "to": draft["contact_email"],
            "subject": draft["subject"],
            "body": draft["body"],
            "from": pd.secrets["GMAIL_EMAIL"]
        }

        # Add delay between sends (rate limiting)
        time.sleep(5)

        sent_emails.append({
            "to": draft["contact_email"],
            "contact_name": draft["contact_name"],
            "sent_at": time.time()
        })

    return {
        "emails_sent": len(sent_emails),
        "details": sent_emails
    }


# =============================================================================
# STEP 5: Log to Google Sheets
# =============================================================================
def handler(pd: "pipedream"):
    """
    Log sent emails to Google Sheets for tracking
    """
    from datetime import datetime

    sent_emails = pd.steps["step_4"]["$return_value"]["details"]
    user_profile = pd.steps["step_2"]["$return_value"]["user_profile"]

    # Prepare rows for Google Sheets
    rows = []
    for email in sent_emails:
        rows.append({
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "User": user_profile["name"],
            "Contact": email["contact_name"],
            "Email": email["to"],
            "Status": "Sent",
            "Response": "Pending"
        })

    # Use Pipedream's Google Sheets integration
    # to append these rows to your tracking spreadsheet

    return {
        "rows_added": len(rows),
        "rows": rows
    }


# =============================================================================
# STEP 6: Send Slack Notification
# =============================================================================
def handler(pd: "pipedream"):
    """
    Send summary notification to Slack
    """
    workflow_result = pd.steps["step_2"]["$return_value"]
    emails_sent = pd.steps["step_4"]["$return_value"]["emails_sent"]

    message = f"""
🎯 *Coffee Chat Campaign Update*

📊 *Results:*
• Contacts Found: {workflow_result.get('contacts_found', 0)}
• Relevant Matches: {workflow_result.get('relevant_contacts', 0)}
• Emails Generated: {workflow_result.get('emails_generated', 0)}
• Emails Sent: {emails_sent}

✅ Campaign completed successfully!
"""

    # Use Pipedream's Slack integration to send this message
    return {
        "message": message
    }


# =============================================================================
# ALTERNATIVE: Simple One-Step Workflow
# =============================================================================
def simple_workflow(pd: "pipedream"):
    """
    All-in-one workflow for quick setup
    """
    import os
    import json

    # Set environment
    os.environ['OPENAI_API_KEY'] = pd.secrets['OPENAI_API_KEY']
    os.environ['APOLLO_API_KEY'] = pd.secrets['APOLLO_API_KEY']

    from webhook_handler import handler

    # Run full workflow
    result = handler({
        "action": "full_workflow",
        "resume_path": pd.steps["trigger"]["event"]["body"]["resume_path"],
        "search_criteria": {
            "titles": ["Senior Engineer", "Engineering Manager"],
            "locations": ["San Francisco Bay Area"],
            "max_contacts": 10
        },
        "min_relevance_score": 0.6
    })

    # Format results for display
    if result["success"]:
        summary = {
            "status": "✅ Success",
            "user": result["user_profile"]["name"],
            "contacts_found": result["contacts_found"],
            "emails_ready": result["emails_generated"],
            "top_contact": result["email_drafts"][0]["contact_name"] if result["email_drafts"] else None
        }
    else:
        summary = {
            "status": "❌ Failed",
            "error": result["error"]
        }

    return summary


# =============================================================================
# CRON SCHEDULED WORKFLOW
# =============================================================================
def scheduled_outreach(pd: "pipedream"):
    """
    Scheduled workflow that runs daily
    Use Pipedream's Cron trigger (e.g., daily at 9am)
    """
    import os

    os.environ['OPENAI_API_KEY'] = pd.secrets['OPENAI_API_KEY']
    os.environ['APOLLO_API_KEY'] = pd.secrets['APOLLO_API_KEY']

    from webhook_handler import handler

    # Use stored resume path from Google Drive or S3
    resume_path = pd.secrets['RESUME_PATH']

    # Different search criteria for each day of week
    import datetime
    day = datetime.datetime.now().weekday()

    search_configs = {
        0: {"titles": ["Senior Engineer"], "locations": ["San Francisco"]},  # Monday
        1: {"titles": ["Engineering Manager"], "locations": ["New York"]},   # Tuesday
        2: {"titles": ["Product Manager"], "locations": ["Seattle"]},        # Wednesday
        3: {"titles": ["Staff Engineer"], "locations": ["Austin"]},          # Thursday
        4: {"titles": ["VP Engineering"], "locations": ["Boston"]},          # Friday
    }

    config = search_configs.get(day, search_configs[0])

    result = handler({
        "action": "full_workflow",
        "resume_path": resume_path,
        "search_criteria": {
            **config,
            "max_contacts": 5,
            "seniorities": ["senior", "vp"]
        },
        "min_relevance_score": 0.7
    })

    return result
