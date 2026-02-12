# Password Reset Feature Documentation

## Overview
The FACTLY application now includes a secure password reset functionality that allows users who forget their password to reset it via email verification.

## Features
- **Forgot Password**: Users can request a password reset by entering their email address
- **Email Verification**: A secure reset link is sent to the user's email
- **Token Validation**: Reset tokens expire after 24 hours (configurable)
- **Token Protection**: Each token can only be used once
- **Password Reset**: Users can set a new password using the secure reset link

## Flow
1. User clicks "Forgot Password?" on the login page
2. User enters their email address
3. System verifies the email exists in the database
4. A unique reset token is generated and saved
5. An email is sent with a password reset link containing the token
6. User clicks the link in the email
7. System verifies the token is valid and not expired
8. User enters a new password and confirms it
9. Password is updated and token is marked as used

## Setup Instructions

### Backend Configuration

#### 1. Update Environment Variables
Create or update your `.env` file with email configuration:

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@factly.com

# Password Reset Settings
PASSWORD_RESET_TIMEOUT_HOURS=24
FRONTEND_URL=http://localhost:3000
```

**⚠️ Development Mode**: If you leave `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` empty or as placeholders, the system will **automatically fallback to development mode**:
- Password reset tokens will be created and logged to the console/log file
- You can copy the reset link directly from the logs without needing real email credentials
- This is useful for testing and development

#### 2. Gmail Configuration (if using Gmail)
- Go to https://myaccount.google.com/apppasswords
- Select "Mail" and "Windows Computer" (or your device)
- Generate an app-specific password
- Copy the password to `EMAIL_HOST_PASSWORD` in `.env`

#### 3. Run Database Migrations
The new `PasswordResetToken` model requires a database migration:

```bash
# From the backend directory
python manage.py makemigrations
python manage.py migrate
```

#### 4. Test Email Configuration
To verify your email setup (optional), you can test with:

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email from FACTLY',
    settings.DEFAULT_FROM_EMAIL,
    ['recipient@example.com'],
    fail_silently=False,
)
```

### Frontend Configuration
No additional configuration needed. The frontend components will use the API endpoints defined in `src/utils/api.js`.

## API Endpoints

### 1. Forgot Password
**POST** `/api/auth/forgot-password/`

Request:
```json
{
  "email": "user@example.com"
}
```

Response (200):
```json
{
  "message": "If an account exists with this email, a password reset link has been sent."
}
```

### 2. Verify Reset Token
**POST** `/api/auth/verify-reset-token/`

Request:
```json
{
  "token": "reset-token-uuid"
}
```

Response (200):
```json
{
  "valid": true,
  "email": "user@example.com"
}
```

### 3. Reset Password
**POST** `/api/auth/reset-password/`

Request:
```json
{
  "token": "reset-token-uuid",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

Response (200):
```json
{
  "message": "Password has been reset successfully"
}
```

## Frontend Components

### ForgotPasswordPage
- Location: `src/pages/ForgotPasswordPage.js`
- Route: `/forgot-password`
- Allows users to request a password reset by entering their email

### ResetPasswordPage
- Location: `src/pages/ResetPasswordPage.js`
- Route: `/reset-password/:token`
- Verifies the reset token and allows users to set a new password

### Updated LoginPage
- Added "Forgot Password?" link in the authentication footer
- Link directs users to the ForgotPasswordPage

## Security Features

1. **Token Uniqueness**: Each reset request generates a unique UUID token
2. **Token Expiration**: Tokens expire after 24 hours (configurable via `PASSWORD_RESET_TIMEOUT_HOURS`)
3. **One-Time Use**: Tokens can only be used once; after password is reset, token is marked as used
4. **Email Verification**: Confirms the user owns the email address
5. **Password Validation**: 
   - Minimum 6 characters
   - Confirmation password matching
   - Password strength indicator
6. **Error Handling**: 
   - Doesn't reveal if email exists (security through obscurity)
   - Generic error messages for invalid/expired tokens

## Configuration Options

### Environment Variables (Backend)

| Variable | Default | Description |
|----------|---------|-------------|
| `EMAIL_BACKEND` | console | Email backend to use (smtp.EmailBackend for production) |
| `EMAIL_HOST` | smtp.gmail.com | SMTP server hostname |
| `EMAIL_PORT` | 587 | SMTP server port |
| `EMAIL_USE_TLS` | True | Enable TLS encryption |
| `EMAIL_HOST_USER` | '' | Email account username |
| `EMAIL_HOST_PASSWORD` | '' | Email account password or app password |
| `DEFAULT_FROM_EMAIL` | noreply@factly.com | Sender email address |
| `PASSWORD_RESET_TIMEOUT_HOURS` | 24 | Token expiration time in hours |
| `FRONTEND_URL` | http://localhost:3000 | Frontend URL for reset links |

## Troubleshooting

### Emails Not Sending
1. Check `EMAIL_BACKEND` is set to `django.core.mail.backends.smtp.EmailBackend`
2. Verify email credentials are correct
3. For Gmail: ensure App-specific password is used, not main password
4. Check firewall/network allows SMTP port 587
5. Enable "Less secure app access" if using older Gmail settings (not recommended)

### Token Errors
1. Verify frontend `FRONTEND_URL` matches the actual URL users see
2. Ensure database migration has been run: `python manage.py migrate`
3. Check reset link format in email matches frontend route `/reset-password/:token`

### Development Testing
For development, you can set `EMAIL_BACKEND` to use console output:
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

This will print emails to the console instead of sending them.

## Future Enhancements
- [ ] Rate limiting on password reset requests
- [ ] Password reset history/audit log
- [ ] Multi-factor authentication for password reset
- [ ] SMS verification as alternative to email
- [ ] Two-step password reset confirmation
- [ ] Session invalidation after password reset
