# Streamlit Cloud Deployment Guide (FREE)

This guide will help you deploy your Intelligence Platform app to Streamlit Cloud for free.

## Prerequisites

1. **GitHub Account** - You need a GitHub account (free)
2. **GitHub Repository** - Your code must be in a GitHub repository
3. **Streamlit Cloud Account** - Sign up at [share.streamlit.io](https://share.streamlit.io) (free)

## Step 1: Prepare Your Repository

### 1.1 Create a GitHub Repository

If you haven't already:

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Name it (e.g., "intelligence-platform")
4. Make it **Public** (required for free Streamlit Cloud)
5. Click "Create repository"

### 1.2 Push Your Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Intelligence Platform"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Important Files to Include:**
- ✅ `app.py` (main application)
- ✅ `requirements.txt` (dependencies)
- ✅ `sources.csv` (regulation sources)
- ✅ All Python files (`.py`)
- ✅ `.streamlit/config.toml` (configuration)
- ❌ `.env` (should NOT be committed - use Streamlit secrets instead)
- ❌ `chroma_db/` (will be created on first run)
- ❌ `regulations.db` (will be created on first run)
- ❌ `emails/` (local email storage, not needed)

### 1.3 Create .gitignore (if not exists)

Make sure you have a `.gitignore` file:

```
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
chroma_db/
regulations.db
emails/
*.log
.DS_Store
streamlit_log.txt
```

## Step 2: Deploy to Streamlit Cloud

### 2.1 Sign Up / Sign In

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in" and authorize with your GitHub account
3. You'll be redirected to your Streamlit Cloud dashboard

### 2.2 Create New App

1. Click **"New app"** button
2. Fill in the details:
   - **Repository**: Select your GitHub repository
   - **Branch**: `main` (or `master`)
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom subdomain (e.g., `intelligence-platform`)
3. Click **"Deploy"**

### 2.3 Wait for Deployment

- Streamlit will install dependencies from `requirements.txt`
- This may take 2-5 minutes
- You'll see build logs in real-time
- If there are errors, check the logs

## Step 3: Configure Secrets (API Keys)

### 3.1 Access Secrets Settings

1. In your Streamlit Cloud dashboard, click on your app
2. Click the **"⋮"** (three dots) menu → **"Settings"**
3. Go to **"Secrets"** tab

### 3.2 Add Your Secrets

Click **"Edit secrets"** and add:

```toml
[secrets]
OPENAI_API_KEY = "sk-your-actual-api-key-here"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
```

**Notes:**
- Replace values with your actual credentials
- For Gmail, you need an "App Password" (not your regular password)
- `OPENAI_API_KEY` is optional - the app works without it (uses free mode)
- Email settings are optional - only needed for email alerts

### 3.3 Save and Redeploy

1. Click **"Save"**
2. The app will automatically redeploy with new secrets

## Step 4: Initial Setup After Deployment

### 4.1 Load Regulations

1. Open your deployed app
2. Navigate to **"Settings"** page
3. Click **"Load Regulations from CSV"**
4. Wait for confirmation message

### 4.2 Initialize Vector Store

1. Still in **"Settings"** page
2. Click **"Initialize Vector Store"**
3. This will:
   - Scrape all regulations from `sources.csv`
   - Create embeddings
   - Index them for search
   - **This may take 10-30 minutes** (be patient!)

### 4.3 Verify Everything Works

1. Go to **"Intelligence Platform Agent"** page
2. Try asking a question (e.g., "What is ESA?")
3. Go to **"Regulation Explorer"** and search for regulations
4. Test document upload in compliance checker

## Step 5: Update Your App

Whenever you make changes:

1. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```

2. Streamlit Cloud will **automatically redeploy** your app
3. Check the deployment status in your dashboard

## Troubleshooting

### App Won't Deploy

**Error: "Module not found"**
- Check `requirements.txt` includes all dependencies
- Make sure all Python files are in the repository

**Error: "File not found"**
- Ensure `sources.csv` is in the repository
- Check file paths in your code (use relative paths)

**Error: "Import error"**
- Verify all imports are correct
- Check that all `.py` files are committed

### App Deploys But Shows Errors

**"No regulations found"**
- Go to Settings → Load Regulations from CSV
- Then Initialize Vector Store

**"OpenAI API key error"**
- Check secrets are set correctly
- The app works without API key (free mode)

**"Database locked" or "ChromaDB error"**
- This is normal on first run
- The databases will be created automatically

### Performance Issues

**Slow loading**
- Vector store initialization takes time (10-30 min)
- After initial setup, it should be fast

**Memory issues**
- Streamlit Cloud free tier has memory limits
- If you hit limits, consider optimizing or upgrading

## Free Tier Limitations

Streamlit Cloud free tier includes:
- ✅ Unlimited apps
- ✅ Public repositories only
- ✅ Automatic deployments
- ✅ 1GB RAM per app
- ✅ 1 CPU per app
- ⚠️ Apps sleep after 1 hour of inactivity
- ⚠️ Cold starts may take 30-60 seconds

## Upgrading (Optional)

If you need more resources:
- **Team tier**: $20/month per user
- Includes private repos, more RAM, faster performance
- See [pricing](https://streamlit.io/cloud) for details

## Security Best Practices

1. **Never commit secrets** - Use Streamlit secrets only
2. **Keep secrets private** - Don't share your API keys
3. **Use app passwords** - For email, use app-specific passwords
4. **Monitor usage** - Check your OpenAI usage regularly
5. **Review access** - Only share your app URL with trusted users

## Support

- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-cloud
- **Streamlit Community**: https://discuss.streamlit.io
- **GitHub Issues**: Create an issue in your repository

## Quick Checklist

- [ ] Code pushed to GitHub (public repo)
- [ ] `requirements.txt` is complete
- [ ] `.streamlit/config.toml` exists
- [ ] `.gitignore` excludes sensitive files
- [ ] App deployed on Streamlit Cloud
- [ ] Secrets configured (API keys, email)
- [ ] Regulations loaded from CSV
- [ ] Vector store initialized
- [ ] App tested and working

---

**Congratulations!** Your Intelligence Platform is now live on Streamlit Cloud! 🎉

