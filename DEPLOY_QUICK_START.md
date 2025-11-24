# Quick Start: Deploy to Streamlit Cloud (5 Minutes)

## Step 1: Push to GitHub (2 min)

```bash
# If you haven't initialized git yet
git init
git add .
git commit -m "Ready for Streamlit Cloud deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

**Important:** Make sure your repository is **PUBLIC** (required for free Streamlit Cloud)

## Step 2: Deploy on Streamlit Cloud (2 min)

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository
5. Set main file: `app.py`
6. Click **"Deploy"**

## Step 3: Add Secrets (1 min)

1. In your app dashboard, click **"⋮"** → **"Settings"** → **"Secrets"**
2. Click **"Edit secrets"**
3. Add this (replace with your actual values):

```toml
[secrets]
OPENAI_API_KEY = "sk-your-key-here"
```

**Note:** The app works without API key (uses free mode), but works better with one.

4. Click **"Save"** (app will auto-redeploy)

## Step 4: Initialize Data (First Time Only)

1. Open your deployed app
2. Go to **"Settings"** page
3. Click **"Load Regulations from CSV"**
4. Click **"Initialize Vector Store"** (takes 10-30 minutes)

## Done! 🎉

Your app is now live at: `https://YOUR-APP-NAME.streamlit.app`

---

**Need help?** See `STREAMLIT_CLOUD_DEPLOYMENT.md` for detailed instructions.

