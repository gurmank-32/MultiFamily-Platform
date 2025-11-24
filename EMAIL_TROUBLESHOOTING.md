# Email Not Working - Troubleshooting

## Why You're Not Getting Welcome Emails

The welcome email function is working, but **SMTP credentials are not configured** in your `.env` file.

### Current Status:
Your `.env` file has:
```
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
```

These are **placeholder values**, not real credentials.

---

## How to Fix Email

### Step 1: Configure Gmail SMTP

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Housing Compliance Agent"
   - Copy the 16-character password

3. **Update .env file:**
   ```
   SMTP_EMAIL=your_actual_email@gmail.com
   SMTP_PASSWORD=your_16_character_app_password
   ```

### Step 2: Test Email

After updating `.env`, restart the app and try subscribing again.

---

## Alternative: Use Different Email Provider

### Outlook/Hotmail:
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_EMAIL=your_email@outlook.com
SMTP_PASSWORD=your_password
```

### Yahoo:
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_EMAIL=your_email@yahoo.com
SMTP_PASSWORD=your_app_password
```

---

## Check if Email is Being Called

The code is calling `send_welcome_email()` - you can verify by:
1. Check the terminal where Streamlit is running
2. Look for messages like: "Email not configured. Would send welcome email to..."
3. If you see that, SMTP isn't configured

---

## Quick Test

After configuring SMTP, the welcome email should send automatically when you subscribe.
