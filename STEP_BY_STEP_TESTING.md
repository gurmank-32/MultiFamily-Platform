# Step-by-Step Testing Guide

## 🎯 Goal: Test Dallas Rent Control Update Detection

---

## Step 1: Verify Local Server is Running

**Check if server is running:**
1. Open a new terminal
2. Run: `netstat -ano | findstr :8000`
3. If you see output, server is running ✅
4. If not, start it:
   ```powershell
   cd "C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform"
   python -m http.server 8000
   ```

**Test the URL:**
- Open browser: http://localhost:8000/test_regulation_dallas_rent_control.html
- Should see the rent control law page ✅

---

## Step 2: Load Test Regulation

1. **Open the app** (http://localhost:8501)
2. **Go to Settings page**
3. **Click "Load Regulations from CSV"**
   - Should show: "Regulations loaded! (X loaded, Y skipped)"
   - The test regulation should be in the count
4. **Click "Initialize Vector Store"**
   - Wait for it to finish (may take 1-2 minutes)
   - Should show: "Indexed X regulations!"

---

## Step 3: Subscribe to Dallas Alerts

1. **Go to Email Alerts page**
2. **Enter your email address**
3. **Select "Dallas"**
4. **Click "Subscribe"**
5. **Check the 'emails' folder** (created automatically)
   - Should see: `emails/email_your_email_*.txt`
   - This is your welcome email (saved to file since SMTP not configured)

---

## Step 4: Create Baseline (First Check)

1. **Go to Home page**
2. **Click "🔄 Check for Updates"**
3. **Wait for it to finish**
4. **Result:** Should say "No new updates detected" (this is normal - creates baseline)

---

## Step 5: Modify Test Regulation (Simulate Update)

1. **Open:** `test_regulation_dallas_rent_control.html`
2. **Change line 15:** 
   - FROM: `Maximum Annual Rent Increase: Landlords in the City of Dallas are prohibited from increasing rent by more than $200 per year`
   - TO: `Maximum Annual Rent Increase: Landlords in the City of Dallas are prohibited from increasing rent by more than $250 per year`
3. **OR add a new paragraph** anywhere in the file
4. **Save the file**

---

## Step 6: Detect the Update

1. **Go back to Home page** (in the app)
2. **Click "🔄 Check for Updates" again**
3. **Should now show:** "✅ Found 1 new update(s)!"
4. **Expand the update** to see details

---

## Step 7: Verify in Update Log

1. **Go to Update Log page**
2. **Should see:** "Dallas Rent Control 2026 (TEST)" in the list
3. **Click to expand** and see:
   - Summary of the change
   - Affected Cities: Dallas
   - URL to the regulation

---

## Step 8: Check Email Notification

1. **Check the 'emails' folder** in your project directory
2. **Should see a new file:** `emails/update_Dallas_Rent_Control_*.txt`
3. **Open it** to see the email that would have been sent

---

## Step 9: Test Q&A

1. **Go to Ask Questions page**
2. **Ask:** "What is the new rent control law in Dallas?"
3. **Should reference:** The test regulation
4. **Should mention:** $200 (or $250 if you changed it) limit

---

## Step 10: Test Compliance Checker

1. **Create a simple text file** with: "Rent may be increased by up to $300 per year"
2. **Save as:** `test_lease.txt`
3. **Go to Compliance Checker**
4. **Select "Dallas"**
5. **Upload the file** (or create a Word doc with that text)
6. **Should flag:** Non-compliant (exceeds $200/$250 limit)

---

## 🔍 Troubleshooting

### "No updates detected" after modifying file?

**Check:**
1. Did you save the HTML file?
2. Is local server still running? (http://localhost:8000/test_regulation_dallas_rent_control.html)
3. Did you load the regulation from CSV first?
4. Try refreshing the page in browser to verify change

### "Regulation not found" in Q&A?

**Check:**
1. Did you initialize vector store?
2. Wait a moment and try again
3. Check Settings → see if regulation is loaded

### Email folder not created?

**Check:**
1. The folder is created automatically when you subscribe
2. Check project directory: `C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform\emails\`
3. If not there, subscribe again

---

## ✅ Success Checklist

- [ ] Local server running (port 8000)
- [ ] Test regulation loads from CSV
- [ ] Vector store initialized
- [ ] Subscribed to Dallas alerts
- [ ] Welcome email saved to 'emails' folder
- [ ] Baseline check completed (no updates)
- [ ] Modified test HTML file
- [ ] Update detected (shows in Home page)
- [ ] Update appears in Update Log
- [ ] Email notification saved to 'emails' folder
- [ ] Q&A can find the regulation
- [ ] Compliance checker flags violations

---

## 📁 Where to Check Results

1. **Update Log Page** - See all detected updates
2. **Home Page** - See update notifications
3. **'emails' folder** - See saved email notifications
4. **Ask Questions** - Test if Q&A finds the regulation
5. **Compliance Checker** - Test if it flags violations

---

## 🎉 You're Done!

If all steps work, your system is functioning correctly!
