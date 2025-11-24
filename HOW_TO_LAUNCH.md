# How to Launch the App

## ✅ Everything is Saved!

All your code, configuration, and data are saved in:
```
C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform\
```

---

## 🚀 Quick Launch (3 Steps)

### Step 1: Open Terminal
- Press `Windows Key + X`
- Select "Windows PowerShell" or "Terminal"
- OR open Command Prompt

### Step 2: Navigate to Project
```powershell
cd "C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform"
```

### Step 3: Run the App
```powershell
streamlit run app.py
```

**That's it!** The app will open in your browser automatically.

---

## 📝 Alternative: Create a Shortcut

### Option 1: Batch File (Easiest)

1. Create a new file called `launch_app.bat` in your project folder
2. Add this content:
```batch
@echo off
cd /d "C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform"
streamlit run app.py
pause
```

3. Double-click `launch_app.bat` to start the app!

### Option 2: PowerShell Script

1. Create `launch_app.ps1` in your project folder
2. Add this content:
```powershell
Set-Location "C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform"
streamlit run app.py
```

3. Right-click → "Run with PowerShell"

---

## 🔄 If App Doesn't Open

### Check if Already Running
```powershell
Get-Process -Name streamlit -ErrorAction SilentlyContinue
```

### Stop Existing Process
```powershell
Get-Process -Name streamlit -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Then Launch Again
```powershell
streamlit run app.py
```

---

## 📍 What's Saved

✅ **All Python code** (.py files)
✅ **Configuration** (.env, config.py)
✅ **Database** (regulations.db)
✅ **Vector Store** (chroma_db folder)
✅ **Regulation Sources** (sources.csv)
✅ **All Settings** (Streamlit config)

**Nothing is lost when you close!**

---

## 🎯 Quick Reference

**To Launch:**
```powershell
cd "C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform"
streamlit run app.py
```

**To Stop:**
- Press `Ctrl + C` in the terminal
- OR close the terminal window

**App URL:**
- http://localhost:8501

---

## 💡 Pro Tip

Bookmark this folder in File Explorer for quick access:
`C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform`
