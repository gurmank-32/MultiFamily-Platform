# Testing Guide

## How to Test the Application

### Step 1: Add Test Regulation

1. **Create a test HTML file** (I'll create this for you)
2. **Add to sources.csv** (I'll do this)
3. **Load it into the system**

### Step 2: Test Update Detection

1. **Subscribe to Dallas alerts** (Email Alerts page)
2. **Load the test regulation** (Settings → Load from CSV)
3. **Initialize vector store** (Settings → Initialize Vector Store)
4. **Check for updates** (Home page → Check for Updates)
5. **Verify email received** (if SMTP configured)
6. **Check Update Log** (Update Log page)

---

## Test Scenario: Dallas Rent Control Law

**Test Law:** "Dallas Rent Control Ordinance 2026 - Maximum annual rent increase capped at $200 per year"

---

## Step-by-Step Testing

### 1. Setup Test Data
- I'll create a test HTML file with the rent control law
- Add it to sources.csv
- You load it

### 2. Test Email Subscription
- Go to Email Alerts page
- Subscribe with your email to Dallas
- Check for welcome email (if SMTP configured)

### 3. Test Update Detection
- Modify the test HTML file (simulate law change)
- Run "Check for Updates"
- Should detect change and send email

### 4. Test UI Updates
- Go to Update Log page
- Should see the new update listed
- Should show Dallas as affected city

### 5. Test Q&A
- Ask: "What is the new rent control law in Dallas?"
- Should reference the test regulation

---

## What You'll See

✅ **Update Log:** New update with Dallas rent control summary
✅ **Email Alert:** (If SMTP configured) Email with update details
✅ **Q&A:** Can answer questions about the new law
✅ **Compliance Checker:** Can reference the new law
