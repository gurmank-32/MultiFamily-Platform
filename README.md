# Housing Regulation Compliance Agent

A comprehensive AI-powered platform for tracking, analyzing, and ensuring compliance with Texas housing regulations.

## Features

- 📋 **Regulation Tracking**: Aggregate and organize regulations from federal, state, and city sources
- 🔍 **Compliance Checking**: Upload lease documents and get detailed compliance analysis
- 🔔 **Update Alerts**: Receive email notifications when regulations are updated
- 📊 **Regulation Explorer**: Search and browse all regulations with vector search
- 🏙️ **City-Specific**: Support for Dallas, Houston, Austin, San Antonio, and Texas-wide regulations

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

4. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_key_here
```

5. (Optional) Configure email settings for alerts:
```
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🚀 Quick Deploy to Streamlit Cloud (FREE)

**Ready to show your client?** Deploy in 5 minutes!

### Quick Start (5 minutes)
👉 **[DEPLOY_QUICK_START.md](DEPLOY_QUICK_START.md)** - Get deployed in 5 minutes

### Detailed Guide
👉 **[STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)** - Complete step-by-step guide

### Deployment Checklist
👉 **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Ensure everything is ready

**What you need:**
- GitHub account (free)
- Streamlit Cloud account (free)
- OpenAI API key (for LLM features)

## Usage

### Running Locally

```bash
streamlit run app.py
```

### Initial Setup

1. **Load Regulations**: Go to Settings → "Load Regulations from CSV"
2. **Index Regulations**: Go to Settings → "Initialize Vector Store" (this may take a while)
3. **Check for Updates**: Use the "Check for Updates" button to monitor regulation changes

### Using the Compliance Checker

1. Navigate to "Compliance Checker"
2. Select your city
3. Upload a PDF or DOCX lease document
4. Click "Check Compliance"
5. Review the detailed compliance report

### Email Alerts

1. Navigate to "Email Alerts"
2. Enter your email and select a city
3. Click "Subscribe"
4. You'll receive emails when regulations are updated for your city

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── config.py              # Configuration settings
├── database.py            # SQLite database operations
├── scraper.py             # Web scraping for regulations
├── vector_store.py        # ChromaDB vector store
├── update_checker.py      # Regulation update detection
├── document_parser.py     # PDF/DOCX parsing
├── compliance_checker.py  # Compliance analysis
├── email_alerts.py        # Email notification system
├── requirements.txt       # Python dependencies
├── sources.csv            # Regulation sources
└── README.md              # This file
```

## Legal Disclaimer

⚠️ **This tool is for informational purposes only. It is not legal advice. No legal accountability is assumed. Consult qualified legal counsel before making decisions. Always perform your own due diligence.**

## Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Set environment variables (OPENAI_API_KEY, etc.)
5. Deploy!

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for web scraping
- (Optional) Email account for alerts

## License

This project is provided as-is for educational and informational purposes.

## Support

For issues or questions, please review the code comments or consult with legal professionals for compliance matters.
