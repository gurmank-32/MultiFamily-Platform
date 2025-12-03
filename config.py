"""
Configuration file for Housing Regulation Compliance Agent
Supports both local .env files and Streamlit Cloud secrets
"""
import os
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

def get_secret(key: str, default: str = "") -> str:
    """Get secret from Streamlit secrets or environment variable"""
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        import streamlit as st
        # Check if we're in a Streamlit runtime context
        if hasattr(st, 'secrets'):
            try:
                # Try to access the secret, catching the specific error
                if key in st.secrets:
                    return st.secrets[key]
            except Exception:
                # StreamlitSecretNotFoundError or other errors - secrets file doesn't exist
                # This is fine for local development
                pass
    except (ImportError, RuntimeError, AttributeError):
        # Not in Streamlit context or secrets not available
        pass
    
    # Fall back to environment variable (for local development)
    return os.getenv(key, default)

# OpenAI Configuration
OPENAI_API_KEY = get_secret("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o"  # Using GPT-4o (or gpt-4o-mini for faster/cheaper)
TEMPERATURE = 0  # For accuracy

# Database Configuration
DATABASE_PATH = "regulations.db"
VECTOR_DB_PATH = "./chroma_db"

# Email Configuration (SMTP)
SMTP_SERVER = get_secret("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(get_secret("SMTP_PORT", "587"))
SMTP_EMAIL = get_secret("SMTP_EMAIL", "")
SMTP_PASSWORD = get_secret("SMTP_PASSWORD", "")

# Supported Cities
SUPPORTED_CITIES = ["Dallas", "Houston", "Austin", "San Antonio", "Texas-Statewide"]

# Regulation Categories
REGULATION_CATEGORIES = [
    "Fair Housing",
    "ESA",
    "Rent Caps",
    "Zoning",
    "Landlord/Tenant",
    "Rental Registration",
    "Housing Programs",
    "State Housing Rules",
    "Federal Housing Updates",
    "Legislative Bills",
    "Legal Opinions",
    "Safety Codes",
    "Other"
]

# Legal Disclaimer
LEGAL_DISCLAIMER = (
    "⚠️ **LEGAL DISCLAIMER:** This tool is for informational purposes only. "
    "It is not legal advice. No legal accountability is assumed. "
    "Consult qualified legal counsel before making decisions. "
    "Always perform your own due diligence."
)

# Data Sources - REQUIRED: finalsource11.xlsx with columns: category, city, level, hyperlink
SOURCES_FILE = "finalsource11.xlsx"
