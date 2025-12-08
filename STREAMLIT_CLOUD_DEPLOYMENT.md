# 🚀 Streamlit Cloud Deployment Guide

This guide will help you deploy your Intelligence Platform Agent to Streamlit Cloud so your client can see and use the application.

## Prerequisites

1. **GitHub Account**: You need a GitHub account (free)
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io) (free)
3. **OpenAI API Key**: Get one from [platform.openai.com](https://platform.openai.com) (if you want to use LLM features)

## Step 1: Prepare Your Repository

### 1.1 Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon → "New repository"
3. Name it (e.g., `intelligence-platform-agent`)
4. Make it **Public** (required for free Streamlit Cloud)
5. Click "Create repository"

### 1.2 Push Your Code to GitHub

Open your terminal/PowerShell in your project directory and run:

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Ready for Streamlit Cloud deployment"

# Add your GitHub repository (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Important**: Make sure sensitive files are in `.gitignore` (they already are):
- `.env` files
- Database files (`*.db`)
- Vector store (`chroma_db/`)
- Email files (`emails/`)

## Step 2: Deploy to Streamlit Cloud

### 2.1 Sign Up / Sign In

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in" and authorize with your GitHub account

### 2.2 Deploy Your App

1. Click "New app"
2. Select your GitHub repository
3. Select the branch (usually `main`)
4. Set **Main file path** to: `app.py`
5. Click "Deploy!"

### 2.3 Configure Secrets

After deployment, click "☰" (menu) → "Settings" → "Secrets"

Add these secrets (copy from your `.env` file if you have one):

```toml
OPENAI_API_KEY = "sk-..."
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_EMAIL = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"
```

**Minimum Required**:
- `OPENAI_API_KEY` - Required for LLM-powered answers

**Optional** (for email alerts):
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_EMAIL`, `SMTP_PASSWORD` - For email notifications

## Step 3: Initial Setup After Deployment

Once your app is deployed:

### 3.1 Load Regulations

1. Open your deployed app
2. Go to **Settings** tab
3. Click **"Load Regulations from CSV"**
   - This will load all regulations from `sources.csv`
   - The system will automatically scrape and index new regulations

### 3.2 Wait for Indexing

- After loading regulations, the system will automatically scrape and index them
- This may take a few minutes depending on the number of sources
- You'll see progress messages in the UI

### 3.3 Test the Application

1. Go to **"Intelligence Platform Agent"** tab
2. Try asking questions like:
   - "What is ESA?"
   - "What is rent control in Dallas?"
   - "New law in Dallas"

## Step 4: Share with Your Client

Once deployed, you'll get a URL like:
```
https://your-app-name.streamlit.app
```

Share this URL with your client!

## Troubleshooting

### App Won't Deploy

**Problem**: Build fails or app won't start

**Solutions**:
1. Check that `app.py` is in the root directory
2. Verify `requirements.txt` has all dependencies
3. Check the logs in Streamlit Cloud dashboard (under "☰" → "Manage app" → "Logs")

### Database Errors

**Problem**: "Database not found" or similar errors

**Solution**:
- Streamlit Cloud uses ephemeral storage (files are reset on restart)
- You need to reload regulations after each deployment
- Go to Settings → "Load Regulations from CSV" after deployment

### Vector Store Errors

**Problem**: "ChromaDB not found" or search not working

**Solution**:
- After loading regulations, go to Settings → "Re-Index All Regulations"
- This will rebuild the vector search index

### OpenAI API Errors

**Problem**: LLM features not working

**Solutions**:
1. Check that `OPENAI_API_KEY` is set in Streamlit Cloud secrets
2. Verify the API key is valid and has credits
3. The app will fall back to free mode if API is unavailable

### Memory Issues

**Problem**: App crashes or runs out of memory

**Solutions**:
1. Streamlit Cloud free tier has memory limits
2. Consider reducing the number of regulations loaded
3. Optimize by loading only essential regulations

## Important Notes

### ⚠️ Streamlit Cloud Limitations (Free Tier)

1. **Ephemeral Storage**: Files are reset when the app restarts
   - Solution: Users need to reload regulations periodically
   - Or: Use external storage (S3, Google Drive, etc.)

2. **Memory Limits**: Limited RAM for large datasets
   - Solution: Load only essential regulations

3. **Public Repositories Only**: Free tier requires public repos
   - Solution: Don't commit sensitive data (use secrets instead)

### 🔐 Security Best Practices

1. **Never commit** `.env` files or API keys
2. **Use Streamlit Secrets** for sensitive data
3. **Review** your `.gitignore` file before pushing
4. **Regularly rotate** API keys if compromised

### 📊 For Production Use

Consider these upgrades for production:

1. **Upgrade to Streamlit Cloud Teams** (for private repos)
2. **Use external database** (PostgreSQL, MySQL) instead of SQLite
3. **Use cloud storage** for vector database (Pinecone, Weaviate)
4. **Set up CI/CD** for automatic deployments
5. **Use environment-specific configs** (dev/staging/prod)

## Quick Reference

### Files Needed for Deployment

- ✅ `app.py` - Main application
- ✅ `requirements.txt` - Python dependencies
- ✅ `.streamlit/config.toml` - Streamlit config
- ✅ `sources.csv` - Regulation sources
- ✅ All Python modules (`.py` files)
- ✅ `.gitignore` - To exclude sensitive files

### Files Excluded (in .gitignore)

- ❌ `.env` - Use Streamlit Secrets instead
- ❌ `*.db` - Databases (recreated on deployment)
- ❌ `chroma_db/` - Vector store (recreated on deployment)
- ❌ `emails/` - Email storage

## Support

If you encounter issues:

1. Check Streamlit Cloud logs (☰ → Manage app → Logs)
2. Review error messages in the app
3. Verify all secrets are set correctly
4. Ensure all dependencies are in `requirements.txt`

## Next Steps After Deployment

1. ✅ Test all features
2. ✅ Load regulations
3. ✅ Share URL with client
4. ✅ Monitor usage and errors
5. ✅ Set up email alerts (optional)

---

**🎉 Congratulations!** Your Intelligence Platform Agent is now live on Streamlit Cloud!

Your app URL: `https://your-app-name.streamlit.app`

