# 🚀 Setup GitHub Repository for Deployment

Follow these steps to set up your GitHub repository, then deploy to Streamlit Cloud.

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Repository name: `Agent-Intellectual-Platform`
4. Description: (optional) "AI-Powered Housing Regulation Compliance Agent"
5. **Make it PUBLIC** ✅ (required for free Streamlit Cloud)
6. **DO NOT** check "Initialize with README" 
7. Click **"Create repository"**

## Step 2: Initialize Git and Push Code

Open PowerShell or Terminal in your project folder and run:

```powershell
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - Ready for Streamlit Cloud deployment"

# Add your GitHub repository (replace YOUR_USERNAME if different)
git remote add origin https://github.com/SafaAzam1/Agent-Intellectual-Platform.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note**: You may be prompted for GitHub username and password. 
- Use your GitHub username
- Use a Personal Access Token (not password) - get one at: https://github.com/settings/tokens

## Step 3: Verify on GitHub

1. Go to: https://github.com/SafaAzam1/Agent-Intellectual-Platform
2. Verify all files are uploaded (especially `app.py` should be visible)
3. Check that the branch is called `main` (not `master`)

## Step 4: Deploy to Streamlit Cloud

Now go back to Streamlit Cloud and use these settings:

### Correct Settings:

- **Repository**: 
  - Select from dropdown: `SafaAzam1/Agent-Intellectual-Platform`
  - OR paste: `SafaAzam1/Agent-Intellectual-Platform.git`

- **Branch**: 
  - Type: `main` (not master!)

- **Main file path**: 
  - Type: `app.py` (not streamlit_app.py!)

- **App URL**: 
  - `agent-intellectual-platform` (or leave default)

Then click **"Deploy!"**

## Troubleshooting

### "Repository does not exist" Error
- Make sure you've created the repo on GitHub first
- Verify the repository name is exactly: `Agent-Intellectual-Platform`
- Check that the repository is PUBLIC
- Try refreshing the Streamlit Cloud page

### "Branch does not exist" Error
- Make sure you pushed to `main` branch (not `master`)
- Run: `git branch -M main` and push again

### "Main file does not exist" Error
- Verify `app.py` is in the root directory
- Check that you pushed all files: `git add .` and `git push`

### Git Push Issues
If you get authentication errors:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name like "Streamlit Deployment"
4. Check "repo" scope
5. Generate and copy the token
6. Use this token as your password when pushing

---

**Need help?** Check the [DEPLOY_QUICK_START.md](DEPLOY_QUICK_START.md) guide.

