# Complete Testing Steps

## 🧪 Test Scenario: Dallas Rent Control Law 2026

**Test Law:** Maximum annual rent increase capped at $200 per year in Dallas, Texas for 2026.

---

## Step 1: Start Local Web Server

The test regulation is an HTML file. We need to serve it locally:

**Option A: Use Python (Already Running)**
- I've started a server on port 8000
- The test file is accessible at: http://localhost:8000/test_regulation_dallas_rent_control.html

**Option B: Manual Start**
```powershell
cd "C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform"
python -m http.server 8000
```

---

## Step 2: Load Test Regulation

1. **Open the app** (if not already open)
2. **Go to Settings page**
3. **Click "Load Regulations from CSV"**
   - This loads the test regulation from sources.csv
4. **Click "Initialize Vector Store"**
   - This indexes the test regulation for search

---

## Step 3: Test Email Subscription

1. **Go to Email Alerts page**
2. **Enter your email address**
3. **Select "Dallas"**
4. **Click "Subscribe"**
5. **Check your email** (if SMTP configured)

**Note:** If you're not getting emails, SMTP is not configured. See email troubleshooting below.

---

## Step 4: Test Update Detection

### First Check (Baseline):
1. **Go to Home page**
2. **Click "Check for Updates"**
3. This creates a baseline hash of the test regulation

### Simulate Update:
1. **Edit** `test_regulation_dallas_rent_control.html`
2. **Change something** (e.g., change $200 to $250, or add a new paragraph)
3. **Save the file**

### Second Check (Should Detect Change):
1. **Go to Home page**
2. **Click "Check for Updates" again**
3. **Should detect the change!**

---

## Step 5: Verify Results

### Check Update Log:
1. **Go to Update Log page**
2. **Should see:** "Dallas Rent Control 2026 (TEST)" update
3. **Should show:** Dallas as affected city
4. **Should show:** Summary of the change

### Check Email (if SMTP configured):
- You should receive an email about the update
- Email should mention Dallas rent control

### Test Q&A:
1. **Go to Ask Questions page**
2. **Ask:** "What is the new rent control law in Dallas?"
3. **Should reference:** The test regulation

---

## Step 6: Test Compliance Checker

1. **Create a test lease document** (Word or PDF) with:
   - "Rent may be increased by up to $300 per year"
2. **Go to Compliance Checker**
3. **Select "Dallas"**
4. **Upload the test document**
5. **Should flag:** Non-compliant (exceeds $200 limit)

---

## 🔧 Email Troubleshooting

### Why No Welcome Email?

**Check 1: Is SMTP configured?**
```powershell
Get-Content .env | Select-String "SMTP"
```

If you see `your_email@gmail.com` - it's NOT configured.

**Check 2: Configure SMTP**

1. **Get Gmail App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Generate app password
   - Copy the 16-character password

2. **Update .env file:**
   ```
   SMTP_EMAIL=your_real_email@gmail.com
   SMTP_PASSWORD=your_16_char_app_password
   ```

3. **Restart the app**

**Check 3: Test Email Manually**

After configuring, subscribe again. Check terminal for:
- "Email not configured" message (if not configured)
- No error messages (if configured correctly)

---

## 📋 Quick Test Checklist

- [ ] Local server running (port 8000)
- [ ] Test regulation loaded from CSV
- [ ] Vector store initialized
- [ ] Subscribed to Dallas alerts
- [ ] Checked for updates (baseline)
- [ ] Modified test HTML file
- [ ] Checked for updates again (should detect change)
- [ ] Verified in Update Log
- [ ] Tested Q&A with new law
- [ ] Tested compliance checker

---

## 🎯 Expected Results

✅ **Update Log:** Shows Dallas rent control update
✅ **Email:** (If configured) Receives update alert
✅ **Q&A:** Can answer questions about the law
✅ **Compliance:** Flags violations of $200 limit

---

## 🐛 Troubleshooting

**Update not detected?**
- Make sure you modified the HTML file
- Check that local server is running
- Verify regulation was loaded from CSV

**Email not sending?**
- Check SMTP configuration in .env
- Verify Gmail app password is correct
- Check terminal for error messages

**Q&A not finding regulation?**
- Make sure vector store was initialized
- Try re-initializing vector store
- Check that regulation URL is accessible
