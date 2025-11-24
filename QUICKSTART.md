# Quick Start Guide

## First Time Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

(Optional) For email alerts:
```env
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 4. Initialize Data

1. **Load Regulations**: 
   - Go to Settings page
   - Click "Load Regulations from CSV"
   - This loads regulations from `sources.csv`

2. **Index Regulations** (Important for search):
   - Still in Settings page
   - Click "Initialize Vector Store"
   - This will scrape and index all regulations (may take 10-30 minutes)
   - Progress will be shown in the UI

### 5. Start Using

- **Check Compliance**: Upload a lease document in the Compliance Checker
- **Explore Regulations**: Browse and search regulations in the Explorer
- **Subscribe to Alerts**: Set up email alerts for your city
- **Check for Updates**: Use the update checker to monitor regulation changes

## Common Tasks

### Checking a Lease for Compliance

1. Navigate to "Compliance Checker"
2. Select your city (Dallas, Houston, Austin, San Antonio, or Texas-Statewide)
3. Upload a PDF or DOCX lease document
4. Click "Check Compliance"
5. Review the detailed report

### Adding New Regulations

1. Edit `sources.csv` with new regulation URLs
2. Go to Settings → "Load Regulations from CSV"
3. Go to Settings → "Initialize Vector Store" to index new regulations

### Setting Up Email Alerts

1. Navigate to "Email Alerts"
2. Enter your email address
3. Select a city
4. Click "Subscribe"
5. You'll receive emails when regulations are updated

## Troubleshooting

### "No regulations found"
- Make sure you've loaded regulations from CSV
- Check that `sources.csv` exists and has valid URLs

### "Vector search not working"
- Run "Initialize Vector Store" in Settings
- This may take time depending on number of regulations

### "OpenAI API Error"
- Check your `.env` file has a valid `OPENAI_API_KEY`
- Ensure you have API credits

### "Email not sending"
- Check SMTP settings in `.env`
- For Gmail, use an App Password (not your regular password)

## Next Steps

- Review the [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions
- Customize categories and cities in `config.py` if needed
