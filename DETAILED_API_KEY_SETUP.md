# Detailed Step-by-Step: OpenAI API Key Setup

## Important Note
OpenAI API keys are **NOT** like Google Cloud service accounts. There are:
- ❌ NO permissions to select
- ❌ NO service accounts to create
- ✅ Just a simple secret key you copy and paste

---

## Step 1: Go to OpenAI Platform

1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Go to: **https://platform.openai.com/**
3. You'll see the OpenAI login page

---

## Step 2: Sign Up or Log In

### If you DON'T have an account:
1. Click the **"Sign up"** button (top right)
2. You can sign up with:
   - Your email address, OR
   - Google account, OR
   - Microsoft account
3. Choose whichever is easiest for you
4. Complete the sign-up process
5. Verify your email if prompted

### If you ALREADY have an account:
1. Click **"Log in"** (top right)
2. Enter your email and password
3. Or click "Continue with Google/Microsoft" if you used that

---

## Step 3: Navigate to API Keys Page

Once you're logged in:

**Method A - Via Profile Menu:**
1. Look at the **top right corner** of the page
2. You'll see your profile icon/name (or a person icon)
3. Click on it
4. A dropdown menu will appear
5. Click on **"API keys"** in that menu

**Method B - Direct Link:**
1. Simply go to: **https://platform.openai.com/api-keys**
2. This takes you directly to the API keys page

---

## Step 4: Create Your API Key

On the API Keys page:

1. You'll see a button that says: **"+ Create new secret key"** or **"Create new secret key"**
2. Click that button
3. A popup window will appear asking for:
   - **Name** (optional but recommended): Type something like:
     - `Housing Compliance Agent`
     - `My Compliance App`
     - `Texas Housing Regulations`
     - Or any name you want - this is just for your reference
4. Click **"Create secret key"** button in the popup

---

## Step 5: Copy Your Secret Key

**⚠️ CRITICAL STEP - READ CAREFULLY:**

1. A new popup will appear showing your API key
2. The key will look something like:
   ```
   sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
   ```
   (It starts with `sk-` and is a long string of letters and numbers)

3. **YOU MUST COPY THIS NOW!**
   - Click the **copy icon** (looks like two overlapping squares) next to the key
   - OR select all the text and press `Ctrl+C` (Windows) or `Cmd+C` (Mac)
   - **You will NOT be able to see this key again after you close this window!**

4. **Paste it somewhere safe temporarily** (like Notepad) so you don't lose it

5. Click **"Done"** or close the popup

---

## Step 6: Add Payment Method / Credits

**You MUST add credits to use the API:**

1. Go to: **https://platform.openai.com/settings/organization/billing/overview**
   - Or click your profile → "Settings" → "Billing"

2. Click **"Add payment method"** or **"Add credits"**

3. Enter your payment information:
   - Credit card or debit card
   - Or use PayPal if available

4. **Add at least $5-10 to start:**
   - This is just a prepaid balance
   - You only pay for what you use
   - Very affordable - most API calls cost pennies

5. Complete the payment setup

---

## Step 7: Add the Key to Your Project

### Option A: I'll Add It For You (Recommended)

1. Copy your API key (the one that starts with `sk-`)
2. Paste it here in the chat
3. I'll add it to your `.env` file securely

### Option B: Add It Manually

1. Open the `.env` file in your project folder:
   - Location: `C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform\.env`
   - You can open it with Notepad or any text editor

2. Find this line:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Replace `your_openai_api_key_here` with your actual key:
   ```
   OPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
   ```
   (Use YOUR actual key, not this example!)

4. Make sure:
   - There are NO spaces around the `=`
   - There are NO quotes around the key
   - The key is on one line (no line breaks)

5. Save the file (`Ctrl+S`)

---

## Step 8: Verify It Works

1. Restart your Streamlit app (if it's running):
   - Stop it (press `Ctrl+C` in the terminal)
   - Run: `streamlit run app.py` again

2. Try using a feature that requires the API (like Compliance Checker)

3. If you get an error, check:
   - The key is correct in `.env`
   - You added credits to your OpenAI account
   - The key starts with `sk-`

---

## What Your .env File Should Look Like

```
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Email Configuration (Optional - for email alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
```

---

## Common Questions

**Q: Do I need to select permissions?**
A: No! OpenAI API keys don't have permissions. They just give you access to use the API.

**Q: Do I need to create a service account?**
A: No! That's for Google Cloud. OpenAI is much simpler - just create a key and use it.

**Q: How much will this cost?**
A: Very little! For this app:
- Each compliance check: ~$0.01-0.05
- Embedding regulations: ~$0.001 per regulation
- Monthly usage: Usually $2-10 for regular use

**Q: Is my key secure?**
A: Yes, as long as:
- You don't share it publicly
- You don't commit it to Git (it's already in .gitignore)
- You keep it in the `.env` file

**Q: What if I lose my key?**
A: Just create a new one! You can have multiple keys. Revoke the old one if needed.

---

## Troubleshooting

**Error: "Invalid API key"**
- Check that you copied the entire key (it's long!)
- Make sure there are no extra spaces
- Verify the key starts with `sk-`

**Error: "Insufficient credits"**
- Go back to billing and add more credits
- Check your usage at: https://platform.openai.com/usage

**Error: "Rate limit exceeded"**
- You're making too many requests too quickly
- Wait a few minutes and try again
- Consider upgrading your plan if this happens often

---

## Ready to Go!

Once you've:
1. ✅ Created your API key
2. ✅ Added credits
3. ✅ Added the key to `.env`

Your app will be fully functional! 🎉

---

## Need Help?

If you get stuck at any step, let me know exactly where you are and I'll help you through it!
