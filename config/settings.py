"""Application settings and configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

# Try to import streamlit secrets, fallback to environment variables
try:
    import streamlit as st
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    APOLLO_API_KEY = st.secrets.get("APOLLO_API_KEY") or os.getenv("APOLLO_API_KEY")
except (ImportError, FileNotFoundError, KeyError):
    # Fallback to environment variables if streamlit not available or secrets not configured
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")

# Email Services
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Gmail SMTP (Development)
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///apollo_coffee.db")

# Redis (Optional)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Rate Limiting
APOLLO_RATE_LIMIT = int(os.getenv("APOLLO_RATE_LIMIT", "50"))  # requests per minute
EMAIL_RATE_LIMIT = int(os.getenv("EMAIL_RATE_LIMIT", "20"))   # emails per hour

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# API Settings
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 2000

__all__ = [
    "OPENAI_API_KEY",
    "APOLLO_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "SENDGRID_API_KEY",
    "GMAIL_EMAIL",
    "GMAIL_APP_PASSWORD",
    "DATABASE_URL",
    "REDIS_URL",
    "APOLLO_RATE_LIMIT",
    "EMAIL_RATE_LIMIT",
    "ENVIRONMENT",
    "OPENAI_MODEL",
    "OPENAI_TEMPERATURE",
    "OPENAI_MAX_TOKENS",
]
