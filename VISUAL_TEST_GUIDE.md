# Visual Testing Guide - Where to Check Everything

## 📍 Where to Find Updates

### 1. **Home Page** (First Place to Check)
- Click "🔄 Check for Updates" button
- **If update found:** Shows green success message with update details
- **Expand the update** to see summary and affected cities

### 2. **Update Log Page** (Complete History)
- Go to "Update Log" in sidebar
- **Shows:** All detected updates with full details
- **Filter by city:** Select "Dallas" to see only Dallas updates
- **Shows:** Summary, URL, affected cities, date detected

### 3. **'emails' Folder** (Email Notifications)
- Location: `C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform\emails\`
- **Welcome emails:** `email_your_email_*.txt`
- **Update alerts:** `update_*.txt`
- **Open any file** to see the email content

---

## 🧪 Step-by-Step Test (5 Minutes)

### Step 1: Setup (One Time)
1. **Start local server** (if not running):
   ```powershell
   python -m http.server 8000
   ```
2. **In the app:**
   - Settings → "Load Regulations from CSV"
   - Settings → "Initialize Vector Store"

### Step 2: Subscribe
1. **Email Alerts page**
2. Enter email, select "Dallas", click "Subscribe"
3. **Check 'emails' folder** → Should see welcome email file

### Step 3: Create Baseline
1. **Home page** → "Check for Updates"
2. Should say "No new updates" (normal - creates baseline)

### Step 4: Make Change
1. **Open:** `test_regulation_dallas_rent_control.html`
2. **Change:** "$200" to "$250" (line 15)
3. **Save file**

### Step 5: Detect Update
1. **Home page** → "Check for Updates" again
2. **Should show:** "✅ Found 1 new update!"
3. **Expand** to see details

### Step 6: Verify Everywhere
- ✅ **Home page:** Shows update notification
- ✅ **Update Log:** Shows in list (filter by Dallas)
- ✅ **'emails' folder:** Has update email file
- ✅ **Ask Questions:** "What is rent control in Dallas?" → References it

---

## 🔍 Troubleshooting

### "No updates detected" after changing file?

**Check:**
1. ✅ Did you save the HTML file? (Ctrl+S)
2. ✅ Is local server running? Test: http://localhost:8000/test_regulation_dallas_rent_control.html
3. ✅ Did you load from CSV first?
4. ✅ Try refreshing browser to verify change is there

### "Can't find update in Update Log"?

**Check:**
1. ✅ Did you click "Check for Updates" on Home page?
2. ✅ Filter set to "All" or "Dallas"?
3. ✅ Scroll down - updates are listed newest first

### "No email files in 'emails' folder"?

**Check:**
1. ✅ Did you subscribe first?
2. ✅ Folder is created automatically when you subscribe
3. ✅ Check: `C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform\emails\`

---

## ✅ Success Indicators

You'll know it's working when you see:

1. **Home Page:** Green "✅ Found 1 new update!" message
2. **Update Log:** "Dallas Rent Control 2026 (TEST)" in the list
3. **'emails' folder:** New file with update details
4. **Q&A:** Can answer questions about the law

---

## 📂 File Locations

- **Test Regulation:** `test_regulation_dallas_rent_control.html`
- **Email Notifications:** `emails/` folder
- **Database:** `regulations.db`
- **Sources:** `sources.csv`

---

## 🎯 Quick Reference

**To test update:**
1. Modify `test_regulation_dallas_rent_control.html`
2. Home → "Check for Updates"
3. Check Update Log page
4. Check 'emails' folder

**That's it!**
