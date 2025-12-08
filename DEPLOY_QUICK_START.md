# ⚡ Quick Start: Deploy to Streamlit Cloud in 5 Minutes

Get your Intelligence Platform Agent live on Streamlit Cloud quickly!

## Step 1: Push to GitHub (2 minutes)

```bash
# In your project directory
git init
git add .
git commit -m "Deploy to Streamlit Cloud"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**Important**: Make sure your repository is **Public** (required for free Streamlit Cloud).

## Step 2: Deploy to Streamlit Cloud (2 minutes)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository and branch (`main`)
5. Set **Main file path** to: `app.py`
6. Click **"Deploy!"**

## Step 3: Add Secrets (1 minute)

After deployment:

1. Click **"☰"** (menu) → **"Settings"** → **"Secrets"**
2. Add your OpenAI API key:

```toml
OPENAI_API_KEY = "sk-your-key-here"
```

3. Save and wait for the app to restart

## Step 4: Initialize the App

1. Open your deployed app
2. Go to **Settings** tab
3. Click **"Load Regulations from CSV"**
4. Wait for indexing to complete (~2-5 minutes)

## ✅ Done!

Your app is now live! Share the URL with your client:
```
https://your-app-name.streamlit.app
```

## Need Help?

See the detailed guide: **[STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)**

## Common Issues

**App won't start?**
- Check that `app.py` is in the root directory
- Verify `requirements.txt` exists and is complete

**Can't find regulations?**
- Go to Settings → "Load Regulations from CSV"
- Then Settings → "Re-Index All Regulations" if needed

**LLM not working?**
- Check that `OPENAI_API_KEY` is set in Secrets
- App will work in free mode if API key is missing

---

🚀 **That's it!** Your client can now access the application!

