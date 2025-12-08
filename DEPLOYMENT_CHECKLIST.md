# ✅ Deployment Checklist

Use this checklist to ensure your app is ready for Streamlit Cloud deployment.

## Pre-Deployment Checklist

### Code Preparation
- [ ] All code files are in the repository
- [ ] `app.py` is in the root directory
- [ ] `requirements.txt` is complete and up-to-date
- [ ] `.streamlit/config.toml` exists (created)
- [ ] `sources.csv` exists with regulation sources
- [ ] All Python modules are present and functional

### Security
- [ ] `.gitignore` excludes sensitive files (`.env`, `*.db`, `chroma_db/`, `emails/`)
- [ ] No API keys or secrets are committed to the repository
- [ ] Database files are not committed (they'll be recreated)
- [ ] Vector store directory is not committed (will be recreated)

### Testing (Optional but Recommended)
- [ ] App runs locally: `streamlit run app.py`
- [ ] All features work locally
- [ ] Regulations can be loaded from CSV
- [ ] Vector store indexing works
- [ ] Q&A system responds correctly

## Deployment Steps

### GitHub Setup
- [ ] Created GitHub repository (must be **Public** for free tier)
- [ ] Pushed all code to GitHub
- [ ] Verified `.gitignore` is working (no sensitive files in repo)

### Streamlit Cloud Setup
- [ ] Signed up at [share.streamlit.io](https://share.streamlit.io)
- [ ] Connected GitHub account
- [ ] Created new app
- [ ] Selected correct repository
- [ ] Set main file path to `app.py`
- [ ] App deployed successfully

### Configuration
- [ ] Added `OPENAI_API_KEY` to Streamlit Secrets
- [ ] (Optional) Added SMTP settings for email alerts
- [ ] App restarted and loaded successfully

## Post-Deployment Setup

### Initial Data Load
- [ ] Opened deployed app
- [ ] Navigated to Settings tab
- [ ] Clicked "Load Regulations from CSV"
- [ ] Waited for regulations to load
- [ ] Verified indexing completed successfully

### Testing on Cloud
- [ ] Tested Q&A feature
- [ ] Tested regulation explorer
- [ ] Tested compliance checker (if applicable)
- [ ] Verified sources are displayed correctly

## Client Handoff

### Documentation
- [ ] Shared app URL with client
- [ ] Provided brief usage instructions
- [ ] Explained any limitations (ephemeral storage, etc.)
- [ ] Documented how to reload regulations if needed

### Ongoing Maintenance
- [ ] Understand that databases reset on app restart
- [ ] Know how to reload regulations (Settings → Load Regulations)
- [ ] Know how to re-index if needed (Settings → Re-Index)
- [ ] Monitor app usage and errors

## Quick Commands Reference

```bash
# Test locally before deployment
streamlit run app.py

# Git commands for deployment
git add .
git commit -m "Ready for deployment"
git push origin main
```

## Troubleshooting

If something goes wrong:

1. **Check Streamlit Cloud Logs**
   - Click "☰" → "Manage app" → "Logs"
   - Look for error messages

2. **Verify Secrets**
   - Settings → Secrets
   - Ensure all required keys are set

3. **Check Requirements**
   - Ensure `requirements.txt` is complete
   - All dependencies should be listed

4. **Verify File Structure**
   - `app.py` must be in root
   - All modules must be accessible

---

**🎯 Ready to Deploy?**

Follow the [Quick Start Guide](DEPLOY_QUICK_START.md) or the [Detailed Deployment Guide](STREAMLIT_CLOUD_DEPLOYMENT.md)

