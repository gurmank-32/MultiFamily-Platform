# Quick Test - 5 Minutes

## Fastest Way to Test Update Detection

### 1. Make Sure Server is Running
```powershell
# In a separate terminal
cd "C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform"
python -m http.server 8000
```

### 2. In the App (Streamlit)

**Step A: Load Test Data**
- Settings → "Load Regulations from CSV"
- Settings → "Initialize Vector Store" (wait for it to finish)

**Step B: Create Baseline**
- Home → "Check for Updates"
- Should say "No new updates" (this is normal)

**Step C: Make a Change**
- Open `test_regulation_dallas_rent_control.html`
- Change "$200" to "$250" on line 15
- Save the file

**Step D: Detect Change**
- Home → "Check for Updates" again
- Should now say "Found 1 new update!"

**Step E: Verify**
- Update Log page → Should see the update
- 'emails' folder → Should have email file

---

## Where to Check Results

1. **Home Page** - Shows update notification
2. **Update Log Page** - Lists all updates
3. **'emails' folder** - Contains email notifications (since SMTP not configured)
4. **Ask Questions** - Ask "What is rent control in Dallas?"

---

## Email Alternative (No SMTP Needed!)

Since SMTP isn't configured, emails are **automatically saved to files** in the `emails` folder:
- Welcome emails: `emails/email_your_email_*.txt`
- Update alerts: `emails/update_*.txt`

**This way you can test everything without configuring SMTP!**
