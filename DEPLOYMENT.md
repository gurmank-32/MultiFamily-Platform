# Deployment Guide

## Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. Ensure all files are committed to GitHub
2. Make sure `.env` is in `.gitignore` (it should be)
3. Verify `requirements.txt` is up to date

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set the main file path: `app.py`
6. Click "Deploy"

### Step 3: Configure Environment Variables

In Streamlit Cloud settings, add these secrets:

```
OPENAI_API_KEY=your_openai_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Step 4: Initial Setup After Deployment

1. Navigate to your deployed app
2. Go to Settings page
3. Click "Load Regulations from CSV" to load initial data
4. Click "Initialize Vector Store" to index regulations (this may take 10-30 minutes)

### Step 5: Schedule Updates (Optional)

For automatic update checking, you can:
- Use Streamlit Cloud's scheduled runs (if available)
- Or manually check for updates using the "Check for Updates" button

## Local Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run the app
streamlit run app.py
```

### Database Initialization

The database will be created automatically on first run. To initialize with data:

1. Ensure `sources.csv` is in the project root
2. Run the app and go to Settings
3. Click "Load Regulations from CSV"
4. Click "Initialize Vector Store"

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Make sure your API key is set in environment variables
2. **ChromaDB Errors**: Delete `chroma_db` folder and re-initialize
3. **Email Not Sending**: Check SMTP credentials in `.env`
4. **Import Errors**: Ensure all packages in `requirements.txt` are installed

### Performance Tips

- Vector store indexing can take time for many regulations
- Consider indexing in batches for large datasets
- Use caching for frequently accessed data

## Production Considerations

- Set up proper error logging
- Monitor API usage (OpenAI)
- Consider rate limiting for update checks
- Implement database backups
- Set up monitoring for email delivery
