# PowerShell script to push code to GitHub
# Run this in PowerShell from your project directory

Write-Host "🚀 Setting up GitHub repository..." -ForegroundColor Green
Write-Host ""

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
}

# Add all files
Write-Host "Adding files..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "Creating commit..." -ForegroundColor Yellow
git commit -m "Initial commit - Ready for Streamlit Cloud deployment"

# Check if remote exists
$remoteExists = git remote | Select-String -Pattern "origin"
if (-not $remoteExists) {
    Write-Host "Adding GitHub remote..." -ForegroundColor Yellow
    git remote add origin https://github.com/SafaAzam1/Agent-Intellectual-Platform.git
} else {
    Write-Host "Remote already exists. Updating..." -ForegroundColor Yellow
    git remote set-url origin https://github.com/SafaAzam1/Agent-Intellectual-Platform.git
}

# Rename branch to main
Write-Host "Setting branch to main..." -ForegroundColor Yellow
git branch -M main

# Push
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "You may be prompted for GitHub credentials." -ForegroundColor Cyan
Write-Host "Use your GitHub username and a Personal Access Token (not password)" -ForegroundColor Cyan
Write-Host "Get a token at: https://github.com/settings/tokens" -ForegroundColor Cyan
Write-Host ""

git push -u origin main

Write-Host ""
Write-Host "✅ Done! Your code is now on GitHub." -ForegroundColor Green
Write-Host ""
Write-Host "Now go to Streamlit Cloud and use these settings:" -ForegroundColor Cyan
Write-Host "  Repository: SafaAzam1/Agent-Intellectual-Platform" -ForegroundColor White
Write-Host "  Branch: main" -ForegroundColor White
Write-Host "  Main file: app.py" -ForegroundColor White

