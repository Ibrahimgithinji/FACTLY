# Password Reset System Guide

## Overview
The FACTLY application now includes a complete password reset system with email verification. Users who forget their password can reset it by verifying their email address.

## How It Works

### User Flow
1. User clicks "Forgot password?" on the login page
2. Enters their registered email address
3. Receives a password reset link in their email
4. Clicks the link and sets a new password
5. Is automatically redirected to login with the new password

### Security Features
- **Time-limited tokens**: Reset links expire after 24 hours (configurable)
- **Single-use tokens**: Each token can only be used once
- **Secure hashing**: Tokens are stored securely in the database
- **Email verification**: Only the email owner can reset the password

## Development Setup

### Default Behavior (No Email Configuration)
By default, FACTLY runs in **development mode** with a console email backend:
- Emails are NOT sent to external services
- Password reset links are printed to the **backend terminal/logs**
- This is perfect for development and testing

**To test in development:**
1. Open the backend server terminal
2. Trigger a "Forgot Password" request
3. Look for the password reset link in the backend logs
4. Copy the reset link and paste it in your browser

Example log output:
```
======================== EMAIL MESSAGE (Development Mode) ========================
To: user@example.com
From: noreply@factly.com
Subject: Password Reset Request - FACTLY

Body:
Hello John Doe,

You have requested to reset your password. Click the link below to set a new password:

http://localhost:3000/reset-password/31b9370c-4140-4cd5-ae88-8a65c1f9cf1f

This link will expire in 24 hours.
======================================================================================
```

## Production Setup (Sending Real Emails)

### Configure Gmail SMTP
1. Go to https://myaccount.google.com/apppasswords
2. Create an "App password" for Django
3. Create a `.env` file in the backend directory:

```bash
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@factly.com

# Frontend URL
FRONTEND_URL=https://yourdomain.com

# Password Reset
PASSWORD_RESET_TIMEOUT_HOURS=24
```

### Configure Other Email Providers
Replace EMAIL_HOST and credentials with your provider:
- **SendGrid**: smtp.sendgrid.net, port 587
- **Mailgun**: smtp.mailgun.org, port 587
- **AWS SES**: email-smtp.region.amazonaws.com, port 587

## API Endpoints

### 1. Request Password Reset
**POST** `/api/auth/forgot-password/`
```json
{
  "email": "user@example.com"
}
```
Response: 200 (always returns success for security)

### 2. Verify Reset Token
**POST** `/api/auth/verify-reset-token/`
```json
{
  "token": "31b9370c-4140-4cd5-ae88-8a65c1f9cf1f"
}
```
Response:
```json
{
  "valid": true,
  "email": "user@example.com"
}
```

### 3. Reset Password
**POST** `/api/auth/reset-password/`
```json
{
  "token": "31b9370c-4140-4cd5-ae88-8a65c1f9cf1f",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```
Response:
```json
{
  "message": "Password has been reset successfully"
}
```

## Troubleshooting

### Link not appearing in development
- Check the **backend terminal** where you ran `python manage.py runserver`
- Look for log entries starting with "EMAIL MESSAGE (Development Mode)"
- Copy the full reset link from the body

### Email not being sent in production
1. **Check credentials**: Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in `.env`
2. **Check EMAIL_BACKEND**: Should be `django.core.mail.backends.smtp.EmailBackend`
3. **Check firewall**: Port 587 should be open for outbound connections
4. **Enable 2FA apps**: If using Gmail, ensure you created an "App password"
5. **Check logs**: Run with `DEBUG=True` to see detailed error messages

### Token expired
- Tokens expire after 24 hours (configured in `PASSWORD_RESET_TIMEOUT_HOURS`)
- User must request a new password reset link

### Token already used
- Each token can only be used once
- If user clicked the link twice, they must request a new token

## Configuration Parameters

### Environment Variables
```bash
# Email Backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# SMTP Server
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Credentials
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# Email From Address
DEFAULT_FROM_EMAIL=noreply@factly.com

# Frontend URL (for links in emails)
FRONTEND_URL=http://localhost:3000

# Token Expiration
PASSWORD_RESET_TIMEOUT_HOURS=24
```

### Django Settings
These are configured in `backend/factly_backend/settings.py`:
```python
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'verification.email_backend.DevelopmentEmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@factly.com')
PASSWORD_RESET_TIMEOUT_HOURS = int(os.getenv('PASSWORD_RESET_TIMEOUT_HOURS', 24))
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
```

## Database Schema

### PasswordResetToken Model
```python
class PasswordResetToken(models.Model):
    user = models.OneToOneField(User)  # User requesting password reset
    token = models.CharField(unique=True)  # UUID token
    created_at = models.DateTimeField()  # When token was created
    expires_at = models.DateTimeField()  # When token expires
    is_used = models.BooleanField()  # Has token been used?
```

### Migrations
Database migration for `PasswordResetToken` is in:
`backend/verification/migrations/0001_initial.py`

Apply with:
```bash
python manage.py migrate
```

## Testing Checklist

- [ ] Development mode: Check backend logs for reset links
- [ ] Password validation: Links expire after 24 hours
- [ ] Single use: Token can't be used twice
- [ ] Email format validation: Proper error for invalid emails
- [ ] Non-existent accounts: Returns generic message for security
- [ ] Token validation: Invalid tokens are rejected
- [ ] Password requirements: New password must be 6+ characters
- [ ] Password matching: Passwords must match
- [ ] Redirect: User is redirected to login after reset
- [ ] Production: Real emails sent with configured SMTP

## Files Modified/Created

### Backend
- `backend/factly_backend/settings.py` - Email configuration
- `backend/verification/auth_views.py` - Password reset endpoints
- `backend/verification/models.py` - PasswordResetToken model
- `backend/verification/email_backend.py` - Development email backend
- `backend/verification/urls.py` - API routes
- `backend/.env.example` - Environment variables

### Frontend
- `frontend/src/pages/ForgotPasswordPage.js` - Request password reset
- `frontend/src/pages/ResetPasswordPage.js` - Reset password form
- `frontend/src/context/AuthContext.js` - Auth functions
- `frontend/src/pages/LoginPage.js` - Added forgot password link
- `frontend/src/App.js` - Routes for password reset pages
- `frontend/src/utils/api.js` - API endpoints

## Security Considerations

1. **Tokens are time-limited**: Expires after 24 hours
2. **Tokens are single-use**: Can't be reused
3. **Tokens are random**: UUID v4 format
4. **Email verification**: Only email owner can reset
5. **Generic messages**: For security, same message for existing/non-existing accounts
6. **Password hashing**: New password is hashed with Django's password hasher
7. **HTTPS recommended**: Use SSL/TLS in production

## Support

For issues or questions:
1. Check the backend logs for error messages
2. Verify environment variables are set correctly
3. Test with a valid email address
4. Ensure both frontend and backend are running
