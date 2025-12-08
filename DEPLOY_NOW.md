# 🚀 Deploy to Streamlit Cloud - Step by Step

Now that your code is on GitHub, follow these steps to deploy to Streamlit Cloud.

## Step 1: Go to Streamlit Cloud

1. Open your browser
2. Go to: **https://share.streamlit.io**
3. Sign in with your GitHub account

## Step 2: Deploy New App

1. Click the **"New app"** button (or "Deploy an app" button)

## Step 3: Fill in the Deployment Form

Use these **EXACT** settings:

### Repository
- **Option 1**: Click the dropdown and select: `SafaAzam1/Agent-Intellectual-Platform`
- **Option 2**: Paste this URL: `https://github.com/SafaAzam1/Agent-Intellectual-Platform.git`

### Branch
- Type exactly: **`main`**
- ⚠️ NOT `master` - make sure it's `main`

### Main file path
- Type exactly: **`app.py`**
- ⚠️ NOT `streamlit_app.py` - make sure it's `app.py`

### App URL (optional)
- Your current value looks good: `agent-intellectual-platform`
- Or you can leave the default

## Step 4: Deploy!

1. Click the **"Deploy!"** button
2. Wait for the build to complete (2-5 minutes)
3. Watch the logs to see the progress

## Step 5: Add Secrets (Required)

After deployment, you MUST add your OpenAI API key:

1. Click the **"☰"** (hamburger menu) in the top right
2. Click **"Settings"**
3. Click **"Secrets"** in the left sidebar
4. Paste this into the secrets editor:

```toml
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
```

5. Click **"Save"**
6. The app will automatically restart

**Get your OpenAI API key**: https://platform.openai.com/api-keys

## Step 6: Initialize the App

Once deployed and secrets are added:

1. Open your app URL: `https://agent-intellectual-platform.streamlit.app`
2. Go to the **"Settings"** tab
3. Click **"Load Regulations from CSV"** button
4. Wait for it to complete (2-5 minutes)
5. The app will automatically scrape and index regulations

## Step 7: Test Your App

Test these features:

1. **Q&A System**: Go to "Intelligence Platform Agent" tab
   - Try: "What is ESA?"
   - Try: "What is rent control in Dallas?"
   - Try: "New law in Dallas"

2. **Regulation Explorer**: Browse regulations

3. **Compliance Checker**: Upload a lease document

## ✅ Done!

Your app is now live! Share the URL with your client:
```
https://agent-intellectual-platform.streamlit.app
```

## Troubleshooting

### "Repository does not exist"
- Make sure you pushed to GitHub first
- Verify the repo name is exactly: `Agent-Intellectual-Platform`
- Check it's PUBLIC (required for free tier)
- Refresh the Streamlit Cloud page

### "Branch does not exist"
- Make sure you pushed to `main` branch
- Check on GitHub: https://github.com/SafaAzam1/Agent-Intellectual-Platform
- Verify the branch is called `main`

### "Main file does not exist"
- Verify `app.py` is in the root of your GitHub repo
- Check: https://github.com/SafaAzam1/Agent-Intellectual-Platform/blob/main/app.py

### Build Fails
- Check the logs in Streamlit Cloud (☰ → Manage app → Logs)
- Verify `requirements.txt` exists and is complete
- Make sure all Python files are committed

### App Won't Start
- Check that secrets are added correctly
- Verify `OPENAI_API_KEY` is set
- Check logs for error messages

## Quick Reference

| Setting | Value |
|---------|-------|
| Repository | `SafaAzam1/Agent-Intellectual-Platform` |
| Branch | `main` |
| Main file | `app.py` |
| App URL | `agent-intellectual-platform` |

---

**Ready?** Go to https://share.streamlit.io and deploy! 🚀

