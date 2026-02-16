# Email Configuration Guide

## Password Reset Email Setup

The application sends password reset links via email. To properly receive emails:

### Option 1: Gmail with App Passwords (Recommended for Development)

1. **Enable 2-Factor Authentication on your Gmail account**
   - Go to myaccount.google.com
   - Click "Security" in the left menu
   - Enable "2-Step Verification"

2. **Create an App Password**
   - Go back to Security settings
   - Under "App passwords," select "Mail" and "Windows Computer"
   - Google will generate a 16-character password
   - Copy this password

3. **Configure .env file**
   Create a `.env` file in the `backend/` directory:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   DEBUG=True
   ```

4. **Restart the backend server**
   ```bash
   # The server will auto-detect the new .env file
   ```

### Option 2: File-Based Emails (Development Without Real Email)

If you don't want to set up Gmail, emails will be automatically saved to `.eml` files in the `backend/emails/` directory. You can open these files with any email client to view the password reset links.

### Option 3: Console Output (Development Testing)

Emails are logged to the console, including the full reset link. Look for:
```
============================================================
EMAIL MESSAGE (Development Mode)
============================================================
To: user@example.com
Subject: Password Reset Request - FACTLY

Body: ...reset-password/TOKEN_HERE...
```

## How It Works

1. **User requests password reset** → Email is sent
2. **Check your email** → Find the password reset link
3. **Click the link** → You'll be taken to the reset password page
4. **Enter new password** → Password is updated immediately

## Troubleshooting

**Emails not received:**
- Check your spam/junk folder
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct
- Check the server logs for errors
- File-based emails are saved in `backend/emails/` if SMTP fails

**SMTP Connection Error:**
- Verify the EMAIL_HOST_PASSWORD is an "App Password" (not your regular Gmail password)
- Check that 2-Factor Authentication is enabled
- Verify EMAIL_HOST_USER is correct

**For Production:**
- Use a proper email service (SendGrid, AWS SES, Mailgun, etc.)
- Set `DEBUG=False` in .env
- Use environment variables for all credentials
