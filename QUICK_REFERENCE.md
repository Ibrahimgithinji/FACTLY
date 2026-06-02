# QUICK REFERENCE - Testing Authentication

## TL;DR - Get Running Fast

### 1. Start Backend (Terminal 1)
```bash
cd backend
python manage.py runserver 127.0.0.1:8000
```

### 2. Start Frontend (Terminal 2) 
```bash
cd frontend
npm start
```

### 3. Test Login
Browser: http://localhost:3000
- Email: `smoke_3ae5e2a7@example.com`
- Password: `TestPassword123`

**Expected:** Successful login and redirect

---

## If Login Still Fails

### Check Backend Status
```bash
curl http://127.0.0.1:8000/health/
```
**Should see:** `{"status":"healthy"}`

### Test Auth Endpoint Directly
```bash
cd backend
python test_auth.py
```
**Should see:** `✓ Response status: 200`

### Check Browser Console (F12)
- Look for error messages
- Check Network tab → login request
- Verify response is JSON, not HTML error page

### Check Backend Console
- Look for "Login error:" messages
- Should show proper error handling
- No stack traces (those are now caught)

---

## Available Test Credentials

```
Email: smoke_3ae5e2a7@example.com
Email: smoke_d9312c16@example.com  
Email: test_auth@example.com (created during test)

Password: TestPassword123 (or your configured password)
```

---

## What Was Fixed

**Problem:** 500 Internal Server Error on login attempt

**Root Cause:** Unhandled exception in request parsing

**Solution:** Enhanced error handling in LoginView with:
- Safe request data parsing
- Comprehensive try-catch blocks
- Better logging for debugging

**File Changed:** `backend/verification/auth_views.py` (LoginView class)

**Status:** ✓ VERIFIED WORKING

---

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/verification/auth/login/` | POST | User login - returns JWT tokens |
| `/api/verification/auth/signup/` | POST | User registration |
| `/api/verification/auth/refresh/` | POST | Refresh expired token |
| `/health/` | GET | Backend health check |

---

## Environment Check

```bash
# Check users exist
python manage.py shell
>>> from django.contrib.auth.models import User
>>> print(f"Users: {User.objects.count()}")

# Check database is migrated
python manage.py migrate --check

# Check token generation works
>>> from rest_framework_simplejwt.tokens import RefreshToken
>>> user = User.objects.first()
>>> token = RefreshToken.for_user(user)
>>> print("Token generation: OK")
```

---

## Terminal Cleanup

Previous Issues (Now Fixed):
- ✓ Closed 2 unused bash terminals (were running 4, now 2)
- ✓ Optimized React dev server startup
- ✓ Verified remaining terminals responsive

---

## Common Issues & Quick Fixes

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | `lsof -i :8000` then kill the process |
| Frontend can't reach backend | Check proxy in `frontend/package.json` |
| CORS error | Verify `ALLOWED_CORS` in backend `.env` |
| "Invalid credentials" error | Check password is correct, user exists in DB |
| No response from backend | Verify server is running on http://127.0.0.1:8000 |

---

## Additional Resources

- Full Troubleshooting Guide: `AUTHENTICATION_TROUBLESHOOTING.md`
- Fix Status & Next Steps: `AUTHENTICATION_FIX_STATUS.md`
- Auto Test Script: `backend/test_auth.py`
- Quick Startup Script: `start-services.bat`

---

## Performance

- Backend: ~50-100MB (normal for Django dev)
- Frontend: ~210MB (normal for React dev with HMR)
- Total: Should work fine on modern systems

---

**Last Updated:** June 2, 2026
**Status:** ✓ Authentication Fixed & Verified
