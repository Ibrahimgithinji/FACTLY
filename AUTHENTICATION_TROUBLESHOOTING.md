# Authentication Troubleshooting Guide

## Issue: 500 Internal Server Error on Login

### Symptoms
- Frontend shows: `Error: Server error: 500 Internal Server Error`
- AuthContext.js line 281 logs the error
- Web rendering is broken due to failed authentication

### Root Cause Analysis

The 500 error typically indicates one of:

1. **Request Parsing Error** - The backend fails to parse the JSON request body
2. **Database Error** - User lookup or token generation fails
3. **Middleware/Import Error** - A dependency or middleware is not properly configured
4. **Schema Not Ready** - Auth tables don't exist

### Fixes Applied

#### 1. Enhanced LoginView Error Handling
**File:** `backend/verification/auth_views.py`

Added comprehensive error handling:
- Wrapped schema initialization in try-catch
- Added request parsing validation
- Improved logging at each step
- Better exception handling for token generation

#### 2. Request Validation
The login endpoint now validates:
```python
email = (email or '').strip().lower()  # Safely handle None/empty
password = password or ''              # Safely handle None
```

### Testing the Login Endpoint

#### 1. Direct Backend Test (Python Shell)
```bash
cd backend
python manage.py shell
```

Then:
```python
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

# Check if users exist
user = User.objects.first()
print(f"Users in DB: {User.objects.count()}")

# Test token generation
if user:
    refresh = RefreshToken.for_user(user)
    print(f"Access Token: {str(refresh.access_token)[:50]}...")
    print(f"Refresh Token: {str(refresh)[:50]}...")
```

#### 2. Test with cURL (When Backend is Running)
```bash
curl -X POST http://127.0.0.1:8000/api/verification/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke_3ae5e2a7@example.com","password":"TestPassword123"}'
```

#### 3. Check Backend Logs
When running Django server, watch for:
```
python manage.py runserver 8000
```

Look for error messages in output, especially:
- `Database error during user lookup:`
- `Authentication error:`
- `JWT token generation error:`

### Debugging Checklist

- [ ] **Database Ready**: `python manage.py migrate --check` returns no errors
- [ ] **Users Exist**: `User.objects.count()` > 0
- [ ] **Tokens Generate**: RefreshToken generation succeeds in shell
- [ ] **Backend Running**: Server responds at http://127.0.0.1:8000/health/
- [ ] **CORS Configured**: Frontend origin matches ALLOWED_CORS
- [ ] **API Endpoints**: Verify routes match frontend expectations

### Common Issues & Solutions

#### Issue 1: "Database error during user lookup"
**Cause:** SQLite path not writable or migrations not applied
**Solution:**
```bash
cd backend
python manage.py migrate --no-input
python manage.py shell -c "from django.contrib.auth.models import User; print(f'Users: {User.objects.count()}')"
```

#### Issue 2: "JWT token generation error"
**Cause:** JWT secret key not properly configured
**Solution:** Check `.env` file has `DJANGO_SECRET_KEY` set
```bash
cat .env | grep DJANGO_SECRET_KEY
```

#### Issue 3: "Invalid credentials" on Correct Password
**Cause:** User authentication backend issue
**Solution:** Test directly:
```bash
python manage.py shell
from django.contrib.auth import authenticate
user = authenticate(username='email@example.com', password='password')
print(user)  # Should not be None
```

#### Issue 4: CORS Error from Frontend
**Cause:** Frontend origin not in ALLOWED_CORS
**Solution:** Update `.env`:
```bash
ALLOWED_CORS=http://localhost:3000,http://127.0.0.1:3000
```

### Backend Server Launch

```bash
# Navigate to backend
cd C:\users\dell\OneDrive\Desktop\Factly\backend

# Run migrations (if needed)
python manage.py migrate --no-input

# Start server
python manage.py runserver 127.0.0.1:8000
```

### Frontend Connection Test

Once backend is running:
1. Frontend should proxy requests to http://127.0.0.1:8000 via package.json proxy setting
2. Check Network tab in browser DevTools for request/response details
3. If 500 error appears, check backend console for detailed error message

### File Locations

- **Backend Auth Views:** `backend/verification/auth_views.py`
- **Backend Settings:** `backend/factly_backend/settings.py`
- **Frontend Auth Context:** `frontend/src/context/AuthContext.js`
- **Frontend Login Page:** `frontend/src/pages/LoginPage.js`
- **API Endpoints Config:** `frontend/src/utils/api.js`

### Environment Variables to Check

```bash
# Backend .env
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
ALLOWED_CORS=http://localhost:3000,http://127.0.0.1:3000

# Frontend .env (if needed)
REACT_APP_API_URL=http://127.0.0.1:8000
```

### Performance Notes

The slow bash terminal issue found earlier was due to:
- Multiple Node.js React dev server processes (210MB main process)
- 4 bash shells running concurrently
- Fixed by closing unused bash terminals

Current active processes:
- React dev server: ~210MB (PID 16724)
- Backend server (when running): ~50MB
- Total system: Should be manageable on modern hardware

