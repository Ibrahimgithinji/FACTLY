# Security & Code Quality Analysis - FACTLY

## Executive Summary
The FACTLY application has several **critical and high-priority security vulnerabilities** that need immediate attention, along with numerous code quality improvements. This review covers both backend (Django/Python) and frontend (React/JavaScript).

---

## 🔴 CRITICAL VULNERABILITIES

### 1. **Weak Authentication System** (CRITICAL)
**Location:** `frontend/src/context/AuthContext.js`  
**Severity:** CRITICAL

**Issues:**
```javascript
// Mock token generation using predictable timestamp
const mockToken = 'mock-jwt-token-' + Date.now(); // WEAK!
```

- Mock tokens are generated using `Date.now()` - easily guessable
- No actual backend authentication validation
- Tokens stored in vulnerable localStorage
- No token expiration mechanism
- No signature validation

**Impact:** Attackers can forge authentication tokens

**Fix Needed:**
- Implement real JWT tokens on backend with secret key
- Use httpOnly, secure cookies instead of localStorage
- Add token expiration (exp claim)
- Validate token signature on each request

---

### 2. **Insecure Token Storage** (CRITICAL)
**Location:** `frontend/src/context/AuthContext.js`  
**Severity:** CRITICAL

**Current Code:**
```javascript
localStorage.setItem('authToken', data.token);
localStorage.setItem('user', JSON.stringify(data.user));
```

**Problems:**
- Tokens in localStorage are vulnerable to XSS attacks
- Any JavaScript code can access these tokens
- Not automatically cleared when browser closes
- Vulnerable to CSRF attacks

**Better Approach:**
```javascript
// Use httpOnly, Secure cookies set by server
// Frontend cannot access httpOnly cookies (prevents XSS theft)
// Server sets: Set-Cookie: token=...; HttpOnly; Secure; SameSite=Strict
```

---

### 3. **Hardcoded API Endpoints** (HIGH)
**Location:** Multiple files (VerificationForm.js, AuthContext.js, EvidencePanel.js)  
**Severity:** HIGH

**Issues:**
```javascript
const response = await fetch('http://localhost:8000/api/verify/', {
  // No environment-based configuration
  // Hardcoded HTTP (not HTTPS)
  // Exposed in frontend code
});
```

**Problems:**
- Not environment-specific (dev/prod)
- Uses HTTP (unencrypted)
- Easy to find endpoint URLs
- No API versioning

**Fix:**
```javascript
// Create environment configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const API_ENDPOINTS = {
  verify: `${API_BASE_URL}/api/verify/`,
  auth: {
    login: `${API_BASE_URL}/api/auth/login/`,
    signup: `${API_BASE_URL}/api/auth/signup/`,
  }
};
```

---

### 4. **SSRF (Server-Side Request Forgery) Risk** (HIGH)
**Location:** `backend/services/nlp_service/url_extraction_service.py`  
**Severity:** HIGH

**Current Protection:**
```python
def _is_private_hostname(hostname: str) -> bool:
    """Block private IPs - this is good!"""
```

**However, Gaps Exist:**
- No timeout on requests (can hang indefinitely)
- No size limits on downloaded content
- Could be exploited to access internal services
- URL validation could be bypassed with redirects

**Improved Code:**
```python
import socket
import requests
from urllib.parse import urlparse

def _is_safe_url(url: str) -> bool:
    """Comprehensive URL safety check"""
    try:
        parsed = urlparse(url)
        
        # Require HTTP/HTTPS only
        if parsed.scheme not in ('http', 'https'):
            return False
        
        # Block private IP ranges
        BLOCKED_HOSTS = {'localhost', '127.0.0.1', '0.0.0.0'}
        if parsed.hostname in BLOCKED_HOSTS:
            return False
        
        # Check resolved IP addresses
        ip = socket.gethostbyname(parsed.hostname)
        addr = ipaddress.ip_address(ip)
        if addr.is_private or addr.is_loopback:
            return False
        
        return True
    except:
        return False

# Use with timeouts and size limits
response = self.session.get(
    url,
    timeout=10,  # Prevent hanging
    stream=True,
    headers={'User-Agent': self.user_agent}
)

# Check content-length BEFORE downloading
if int(response.headers.get('content-length', 0)) > 50 * 1024 * 1024:  # 50MB max
    raise ValueError("Content too large")
```

---

### 5. **Hardcoded Django Secret Key** (HIGH)
**Location:** `backend/factly_backend/settings.py`  
**Severity:** HIGH

**Problem:**
```python
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-factly-secret-key-change-in-production')
```

**Issues:**
- Default secret key in code
- If .env file missing, uses insecure default
- Secret key is used for session signing, CSRF tokens, password reset tokens

**Fix:**
```python
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'dev-only-secret-key'
    else:
        raise ValueError("DJANGO_SECRET_KEY environment variable not set (required for production)")
```

---

### 6. **Insecure Mock Authentication Fallback** (HIGH)
**Location:** `frontend/src/components/VerificationForm.js`, `frontend/src/context/AuthContext.js`  
**Severity:** HIGH

**Problem:**
```javascript
catch (err) {
    // Fallback to mock authentication for demo
    if (email && password.length >= 6) {
        const mockUser = { /* ... */ };
        localStorage.setItem('authToken', mockToken);
        // User is logged in even if backend fails!
    }
}
```

**Issues:**
- Falls back to mock data if backend is unavailable
- Creates false sense of security
- Debugging harder to detect
- Can mask real authentication errors
- In production, this allows login with any 6+ char password

**Fix:**
```javascript
catch (err) {
    // Fail gracefully without mock data
    return { 
        success: false, 
        error: 'Authentication service unavailable. Please try again.' 
    };
}
```

---

## 🟠 HIGH-PRIORITY ISSUES

### 7. **CORS Configuration Too Permissive** (HIGH)
**Location:** `backend/factly_backend/settings.py`  
**Severity:** HIGH

**Current Code:**
```python
_allowed_cors = os.getenv('ALLOWED_CORS', 'http://localhost:3000')
CORS_ALLOWED_ORIGINS = [...]
CORS_ALLOW_CREDENTIALS = True  # Allow cookies/auth headers
```

**Issues:**
- Default allows all requests with credentials
- No restriction in production mode

**Better Configuration:**
```python
if not DEBUG:
    # Production: Only specific domains
    CORS_ALLOWED_ORIGINS = [
        'https://factly.com',
        'https://www.factly.com'
    ]
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'x-csrftoken',
    ]
    # Remove dangerous methods from CORS
    CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
else:
    # Development only
    CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
```

---

### 8. **API Key Exposure in Query Parameters** (HIGH)
**Location:** `backend/services/fact_checking_service/google_fact_check.py`  
**Severity:** HIGH

**Problem:**
```python
params = {
    'key': self.api_key,  # API key in URL!
    'query': query,
}
# URL is visible in: logs, browser history, referrer headers, cache
```

**Issues:**
- API keys in query parameters are logged
- Visible in browser history, network inspection
- Appears in server logs and monitoring logs
- Can be exposed through referrer headers
- Rate limits can be exceeded if key is compromised

**Better Implementation:**
```python
# For Google API, they require URL parameter (constraint)
# But you can still improve:
import logging

# Sanitize logs to hide API keys
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # Remove API keys from log messages
        record.msg = str(record.msg).replace(self.api_key, '[REDACTED]')
        return True

logger.addFilter(SensitiveDataFilter(self.api_key))

# Also log separately with sanitized URLs
logger.info(f"API call to Google Fact Check (key=***)")
```

---

### 9. **Weak Rate Limiting** (HIGH)
**Location:** `backend/verification/views.py`  
**Severity:** HIGH

**Problem:**
```python
class VerificationView(APIView):
    _rate_limit_storage = {}  # In-memory, not persistent!
    
    def _check_rate_limit(self, request):
        # Simple implementation, lost on restart
        # Not thread-safe
        # No distributed support
```

**Issues:**
- Resets on server restart
- Not thread-safe (race conditions)
- Single-server only (no distributed cache)
- Can be bypassed with multiple IPs (distributed attack)

**Better Implementation:**
```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework.throttling import UserRateThrottle

class VerificationRateThrottle(UserRateThrottle):
    scope = 'verification'
    
    def throttle_success(self):
        # Uses Django's cache backend (Redis in production)
        return super().throttle_success()

# In settings.py:
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'verification': '10/hour',  # Per-user rate limit
    }
}

# In views.py:
class VerificationView(APIView):
    throttle_classes = [VerificationRateThrottle]
```

---

### 10. **Duplicate Imports** (MEDIUM)
**Location:** `backend/verification/views.py`  
**Severity:** MEDIUM (Code Quality)

```python
import time
from typing import Optional, Dict, Any
# ... then later ...
import time as time_module  # Duplicate!
from typing import Optional, Dict, Any  # Duplicate!
```

**Fix:**
```python
import time
import logging
from typing import Optional, Dict, Any
from rest_framework import status
from rest_framework.response import Response
# Remove duplicates
```

---

### 11. **Missing CSRF Protection Function Calls** (HIGH)
**Location:** `frontend/src/context/AuthContext.js`  
**Severity:** HIGH

**Issue:**
```javascript
const response = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    // Missing CSRF token!
    body: JSON.stringify({ email, password }),
});
```

**Django expects CSRF token for state-changing requests:**

```javascript
// Get CSRF token from cookie
function getCookie(name) {
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
}

const response = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),  // Add this
    },
    body: JSON.stringify({ email, password }),
    credentials: 'include',  // Include cookies
});
```

---

## 🟡 MEDIUM-PRIORITY ISSUES

### 12. **No Input Sanitization Before Rendering** (MEDIUM)
**Location:** `frontend/src/components/EvidencePanel.js`  
**Severity:** MEDIUM

```javascript
<p className="claim-text">
    {claim.full_text}  {/* Could contain malicious HTML/JS */}
</p>
```

**Risk:** If backend returns unsanitized data, XSS is possible.

**Fix:**
```javascript
// Always use .textContent or sanitize HTML
import DOMPurify from 'dompurify';

<p className="claim-text">
    {DOMPurify.sanitize(claim.full_text, { 
        ALLOWED_TAGS: ['b', 'i', 'em', 'strong'],
        ALLOWED_ATTR: []
    })}
</p>
```

---

### 13. **Hardcoded Timeouts** (MEDIUM)
**Location:** Multiple files  
**Severity:** MEDIUM

```javascript
const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 seconds hardcoded
```

**Better:**
```javascript
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '60000');
const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
```

---

### 14. **No Request/Response Validation** (MEDIUM)
**Location:** `frontend/src/components/VerificationForm.js`  
**Severity:** MEDIUM

```javascript
const data = await response.json();
// No validation that data has expected structure
localStorage.setItem('factCheckResult', JSON.stringify(data));
```

**Fix:**
```javascript
// Validate response schema
const validateResponse = (data) => {
    if (!data.factly_score || typeof data.factly_score !== 'number') {
        throw new Error('Invalid response format');
    }
    return data;
};

const data = validateResponse(await response.json());
```

---

### 15. **Logging Sensitive Data** (MEDIUM)
**Location:** `backend/verification/views.py`, `backend/services/fact_checking_service/`  
**Severity:** MEDIUM

```python
logger.info(f"Starting verification for {'URL' if url else 'text'}: {url or text[:100]}...")
# Logs contain user input, which may include sensitive information
```

**Fix:**
```python
logger.info(f"Starting verification request")
logger.debug(f"Content length: {len(text)} chars")  # Safe to log metadata
# Don't log actual content
```

---

### 16. **No Input Size Validation on Frontend** (MEDIUM)
**Location:** `frontend/src/components/VerificationForm.js`  
**Severity:** MEDIUM

```javascript
const MAX_CHARS = 5000;  // Good constraint, but...
// Can be bypassed with developer tools
```

**Also validate on backend:**
```python
# In serializers.py
class VerificationRequestSerializer(serializers.Serializer):
    text = serializers.CharField(
        required=False, 
        allow_blank=True,
        max_length=10000  # Server-side limit
    )
    url = serializers.URLField(
        required=False, 
        allow_blank=True,
        max_length=2000
    )
```

---

### 17. **Missing Security Headers** (MEDIUM)
**Location:** `backend/factly_backend/settings.py`  
**Severity:** MEDIUM

**Add missing headers:**
```python
# Django-CSP for Content Security Policy
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # 1 year HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# Additional security headers
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Prevent MIME type sniffing
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'",),
    'style-src': ("'self'", "'unsafe-inline'"),
    'img-src': ("'self'", "data:", "https:"),
    'font-src': ("'self'",),
    'connect-src': ("'self'",),
    'frame-ancestors': ("'none'",),
    'base-uri': ("'self'",),
    'form-action': ("'self'",),
}
```

---

### 18. **Missing Error Recovery** (MEDIUM)
**Location:** `backend/services/fact_checking_service/evidence_search_service.py`  
**Severity:** MEDIUM

**Issue:**
```python
def __init__(self, cache_manager: Optional[CacheManager] = None):
    # If external services are down, no graceful degradation
    pass
```

**Better approach:**
```python
def __init__(self, cache_manager: Optional[CacheManager] = None):
    self.cache = cache_manager or CacheManager()
    # Add circuit breaker pattern
    self.circuit_breaker = CircuitBreaker(
        failure_threshold=5,
        recovery_timeout=60  # seconds
    )
```

---

## 🟢 LOW-PRIORITY IMPROVEMENTS

### 19. **Missing Environment Configuration** (LOW)
- Create `.env.example` file
- Document all required environment variables
- Add validation in startup

### 20. **No Request Logging/Audit Trail** (LOW)
- Add request logging middleware
- Log user actions for compliance

### 21. **Password Validation Too Weak** (LOW)
**Location:** `frontend/src/pages/SignupPage.js`  

```python
# Current frontend validation
if (formData.password.length < 6) {
    newErrors.password = 'Password must be at least 6 characters';
}

# Add backend validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### 22. **No Database Encryption** (LOW)
- If storing sensitive data, encrypt at rest
- Use Django encrypted model fields

### 23. **Missing `.gitignore` Entries** (LOW)
```
.env
.env.local
*.pem
*.key
db.sqlite3
node_modules/
venv/
__pycache__/
*.pyc
.DS_Store
```

---

## Summary Table

| ID | Issue | Severity | Type | File(s) |
|----|-------|----------|------|---------|
| 1 | Weak Mock Authentication | CRITICAL | Security | AuthContext.js |
| 2 | Insecure Token Storage | CRITICAL | Security | AuthContext.js |
| 3 | Hardcoded API Endpoints | HIGH | Security | VerificationForm.js, AuthContext.js |
| 4 | SSRF Risk | HIGH | Security | url_extraction_service.py |
| 5 | Hardcoded Secret Key | HIGH | Security | settings.py |
| 6 | Insecure Fallback | HIGH | Security | VerificationForm.js, AuthContext.js |
| 7 | CORS Too Permissive | HIGH | Security | settings.py |
| 8 | API Key in Query | HIGH | Security | google_fact_check.py |
| 9 | Weak Rate Limiting | HIGH | Security | views.py |
| 10 | Duplicate Imports | MEDIUM | Code Quality | views.py |
| 11 | Missing CSRF | HIGH | Security | AuthContext.js |
| 12 | No Input Sanitization | MEDIUM | Security | EvidencePanel.js |
| 13 | Hardcoded Timeouts | MEDIUM | Config | VerificationForm.js |
| 14 | No Response Validation | MEDIUM | Code Quality | VerificationForm.js |
| 15 | Logging Sensitive Data | MEDIUM | Security | views.py |
| 16 | No Input Validation (BE) | MEDIUM | Security | serializers.py |
| 17 | Missing Security Headers | MEDIUM | Security | settings.py |
| 18 | No Error Recovery | MEDIUM | Reliability | evidence_search_service.py |
| 19 | Missing Env Config | LOW | Config | Various |
| 20 | No Audit Logs | LOW | Compliance | Various |
| 21 | Weak Passwords | LOW | Security | SignupPage.js, settings.py |
| 22 | No DB Encryption | LOW | Security | settings.py |
| 23 | Missing .gitignore | LOW | Process | .gitignore |

---

## Recommended Fix Priority

### Phase 1 (Immediate - Week 1)
1. ✅ Fix authentication (real JWT, httpOnly cookies)
2. ✅ Remove mock data fallbacks
3. ✅ Fix secret key configuration
4. ✅ Add proper rate limiting with Redis
5. ✅ Add CSRF token handling

### Phase 2 (High Priority - Week 2-3)
6. ✅ Implement proper CORS
7. ✅ Fix SSRF protection
8. ✅ Add request validation
9. ✅ Add security headers
10. ✅ API key sanitization

### Phase 3 (Medium Priority - Week 4)
11. ✅ Input sanitization
12. ✅ Environment configuration
13. ✅ Audit logging
14. ✅ Better error handling

### Phase 4 (Nice to Have)
15. ✅ Database encryption
16. ✅ Advanced monitoring
17. ✅ Load testing for rate limits

