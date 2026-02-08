# FACTLY - Code Quality Improvements & Action Checklist

## Code Quality Issues & Solutions

---

## Backend Code Quality Improvements

### 1. Add Logging Best Practices

**Current Issue:** Logging sensitive user input

**File:** `backend/verification/views.py`

```python
# ❌ BAD - Logs contains user data
logger.info(f"Starting verification for {'URL' if url else 'text'}: {url or text[:100]}...")

# ✅ GOOD - Only log metadata
logger.info("Verification request received")
logger.debug(f"Input length: {len(text)} characters") if text else None
```

---

### 2. Better Exception Handling

**Current Issue:** Generic error messages don't help debugging

```python
# ❌ BAD
except Exception as e:
    logger.exception("Fact-checking failed")
    return Response(
        {"error": "Fact-checking service error."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

# ✅ GOOD
except requests.Timeout:
    logger.warning(f"Fact-check API timeout after {timeout}s")
    return Response(
        {"error": "Verification service timeout. Please try again."},
        status=status.HTTP_504_GATEWAY_TIMEOUT
    )
except requests.ConnectionError as e:
    logger.error(f"Fact-check API connection failed: {e}")
    return Response(
        {"error": "Unable to reach verification service. Please try again later."},
        status=status.HTTP_503_SERVICE_UNAVAILABLE
    )
except ValueError as e:
    logger.warning(f"Invalid input received: {e}")
    return Response(
        {"error": str(e)},
        status=status.HTTP_400_BAD_REQUEST
    )
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    return Response(
        {"error": "Internal server error"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
```

---

### 3. Use Type Hints Everywhere

```python
# ❌ BAD - No type hints
def verify_claim(self, text, language):
    # ...

# ✅ GOOD - Complete type hints
from typing import Optional, List, Dict, Any

def verify_claim(
    self,
    text: str,
    language: str = 'en',
    cache: bool = True
) -> Optional[VerificationResult]:
    """
    Verify a claim using multiple sources.
    
    Args:
        text: The claim text to verify
        language: Language code (default: 'en')
        cache: Whether to use cached results (default: True)
    
    Returns:
        VerificationResult object or None if verification fails
    
    Raises:
        ValueError: If text is empty or language invalid
        TimeoutError: If external APIs timeout
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    # ... implementation
```

---

### 4. Add Configuration Validation

**File:** `backend/factly_backend/settings.py` (Add at end)

```python
# Validate critical settings on startup
def validate_settings():
    """Validate that all required settings are properly configured."""
    errors = []
    
    if DEBUG and SECRET_KEY == 'django-insecure-factly-secret-key-change-in-production':
        errors.append("WARNING: Using insecure default SECRET_KEY in development")
    
    if not DEBUG:
        if not SECRET_KEY or SECRET_KEY.startswith('django-insecure-'):
            errors.append("CRITICAL: SECRET_KEY not properly configured for production")
        
        if not ALLOWED_HOSTS:
            errors.append("CRITICAL: ALLOWED_HOSTS not configured for production")
        
        if not SECURE_SSL_REDIRECT:
            errors.append("WARNING: SECURE_SSL_REDIRECT not enabled in production")
    
    if not CORS_ALLOWED_ORIGINS:
        if not DEBUG:
            errors.append("CRITICAL: CORS_ALLOWED_ORIGINS not configured")
    
    for error in errors:
        if error.startswith("CRITICAL"):
            raise ImproperlyConfigured(error)
        else:
            import warnings
            warnings.warn(error)

# Run validation on import
validate_settings()
```

---

### 5. Add Request/Response Logging Middleware

**File:** `backend/factly_backend/middleware.py` (NEW)

```python
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """Log all HTTP requests and responses."""
    
    SENSITIVE_FIELDS = {'password', 'token', 'authorization', 'api_key'}
    
    def process_request(self, request: HttpRequest):
        """Log incoming request."""
        # Sanitize sensitive data
        sanitized_data = self._sanitize_data(request.POST or {})
        
        logger.info(
            f"REQUEST {request.method} {request.path_info}",
            extra={
                'method': request.method,
                'path': request.path_info,
                'ip': self.get_client_ip(request),
            }
        )
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse):
        """Log outgoing response."""
        logger.info(
            f"RESPONSE {response.status_code}",
            extra={
                'status': response.status_code,
                'path': request.path_info,
            }
        )
        return response
    
    def _sanitize_data(self, data: dict) -> dict:
        """Remove sensitive fields from data."""
        sanitized = {}
        for key, value in data.items():
            if key.lower() in self.SENSITIVE_FIELDS:
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        return sanitized
    
    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        """Get client IP address, handling proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'UNKNOWN')
```

---

## Frontend Code Quality Improvements

### 6. Add Response Validation Schema

**File:** `frontend/src/services/validation.js` (NEW)

```javascript
/**
 * Validation schema for API responses
 */

export const schemas = {
  factlyScore: {
    required: ['factly_score', 'classification', 'confidence_level'],
    validate: (data) => {
      if (typeof data.factly_score !== 'number') {
        throw new Error('factly_score must be a number');
      }
      if (data.factly_score < 0 || data.factly_score > 100) {
        throw new Error('factly_score must be between 0 and 100');
      }
      if (!['True', 'False', 'Likely Authentic', 'Likely Inauthentic', 'Mixed'].includes(data.classification)) {
        throw new Error('Invalid classification');
      }
      return true;
    }
  },
  
  verificationResult: {
    required: ['original_text', 'factly_score'],
    validate: (data) => {
      if (!data.original_text || typeof data.original_text !== 'string') {
        throw new Error('original_text is required');
      }
      schemas.factlyScore.validate(data.factly_score);
      return true;
    }
  }
};

export const validateResponse = (data, schemaName) => {
  const schema = schemas[schemaName];
  if (!schema) {
    throw new Error(`Unknown schema: ${schemaName}`);
  }
  
  // Check required fields
  for (const field of schema.required) {
    if (!(field in data)) {
      throw new Error(`Missing required field: ${field}`);
    }
  }
  
  // Run custom validation
  if (schema.validate) {
    schema.validate(data);
  }
  
  return true;
};
```

### Usage:

```javascript
// In VerificationForm.js
import { validateResponse } from '../services/validation';

try {
  const data = await apiCall(apiEndpoints.verify.verify, {
    method: 'POST',
    body: JSON.stringify(requestBody),
  });
  
  // Validate response
  validateResponse(data, 'verificationResult');
  
  sessionStorage.setItem('factCheckResult', JSON.stringify(data));
  navigate('/results');
} catch (err) {
  setError(err.message);
}
```

---

### 7. Add Input Sanitization

**File:** `frontend/src/services/sanitizer.js` (NEW)

```javascript
/**
 * Input sanitization utilities
 */

export const sanitizeText = (text) => {
  if (typeof text !== 'string') return '';
  
  return text
    .trim()
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};

export const sanitizeUrl = (url) => {
  if (typeof url !== 'string') return '';
  
  try {
    const parsed = new URL(url);
    
    // Only allow http/https
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return '';
    }
    
    return parsed.toString();
  } catch {
    return '';
  }
};

export const sanitizeHtml = (html) => {
  const div = document.createElement('div');
  div.textContent = html;
  return div.innerHTML;
};

export const validateEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email) && email.length <= 254;
};

export const validateUrl = (url) => {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
};
```

---

### 8. Better Error Boundaries

**File:** `frontend/src/components/ErrorBoundary.js` (NEW)

```javascript
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Could send to error tracking service here
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary" role="alert">
          <h2>Something went wrong</h2>
          <p>We're sorry for the inconvenience. Please try refreshing the page.</p>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error?.toString()}
          </details>
          <button 
            onClick={() => window.location.reload()}
            className="retry-button"
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

**Update App.js:**

```javascript
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          {/* ... rest of app */}
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}
```

---

### 9. Remove Hardcoded Strings

**File:** `frontend/src/constants/index.js` (NEW)

```javascript
export const API_TIMEOUTS = {
  SHORT: 10000,      // 10 seconds
  MEDIUM: 30000,     // 30 seconds
  LONG: 60000,       // 60 seconds
};

export const VALIDATION_RULES = {
  TEXT_MIN_LENGTH: 10,
  TEXT_MAX_LENGTH: 5000,
  URL_MAX_LENGTH: 2000,
  PASSWORD_MIN_LENGTH: 12,
  EMAIL_MAX_LENGTH: 254,
  NAME_MIN_LENGTH: 2,
  NAME_MAX_LENGTH: 100,
};

export const ERROR_MESSAGES = {
  EMPTY_INPUT: 'Please enter some text to verify',
  MIN_LENGTH: `Please enter at least ${VALIDATION_RULES.TEXT_MIN_LENGTH} characters`,
  MAX_LENGTH: `Maximum ${VALIDATION_RULES.TEXT_MAX_LENGTH} characters allowed`,
  INVALID_EMAIL: 'Please enter a valid email address',
  WEAK_PASSWORD: 'Password must be at least 12 characters with uppercase and numbers',
  NETWORK_ERROR: 'Network error. Please check your connection.',
  TIMEOUT: 'Request timed out. Please try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
};

export const CLASSIFICATION_COLORS = {
  'True': '#4CAF50',           // Green
  'Likely Authentic': '#81C784', // Light green
  'False': '#f44336',          // Red
  'Likely Inauthentic': '#ef5350', // Light red
  'Mixed': '#FF9800',          // Orange
};
```

---

## Action Checklist

### Phase 1: Critical Fixes (Week 1)

- [ ] **Authentication System**
  - [ ] Install `djangorestframework-simplejwt`
  - [ ] Create `auth_views.py` with JWT implementation
  - [ ] Update Django settings with JWT configuration
  - [ ] Update URLs to include new auth endpoints
  - [ ] Update frontend `AuthContext.js` to use sessionStorage
  - [ ] Test login/signup/token refresh endpoints
  - [ ] Remove mock authentication fallbacks

- [ ] **Secret Management**
  - [ ] Verify `DJANGO_SECRET_KEY` environment variable is set
  - [ ] Add error if `SECRET_KEY` not configured in production
  - [ ] Document required environment variables
  - [ ] Create `.env.example` file

- [ ] **Rate Limiting**
  - [ ] Install `redis` and `django-redis`
  - [ ] Configure Redis cache in settings
  - [ ] Replace in-memory rate limiting with DRF throttling
  - [ ] Test rate limiting with multiple requests
  - [ ] Configure appropriate limits for production

- [ ] **CSRF Protection**
  - [ ] Create CSRF utility functions on frontend
  - [ ] Update API service to include CSRF tokens
  - [ ] Test form submissions with CSRF validation
  - [ ] Verify middleware is enabled

### Phase 2: High Priority (Week 2)

- [ ] **Remove Mock Data**
  - [ ] Remove fallback mock authentication
  - [ ] Remove fallback mock verification results
  - [ ] Update error handling to fail gracefully

- [ ] **SSRF Protection**
  - [ ] Implement comprehensive URL validation
  - [ ] Add timeout and size limits to requests
  - [ ] Test with private IP addresses
  - [ ] Test with localhost variations

- [ ] **API Endpoint Security**
  - [ ] Create `.env` configuration files
  - [ ] Create `api.js` service module
  - [ ] Replace hardcoded endpoints throughout frontend
  - [ ] Update to use HTTPS in production

- [ ] **Input Validation**
  - [ ] Update serializers with max_length constraints
  - [ ] Add language code validation with regex
  - [ ] Create validation schema on frontend
  - [ ] Add server-side validation for all inputs

### Phase 3: Medium Priority (Week 3)

- [ ] **Security Headers**
  - [ ] Add Content-Security-Policy
  - [ ] Add HSTS headers
  - [ ] Add X-Frame-Options
  - [ ] Test headers with OWASP ZAP or similar

- [ ] **Input Sanitization**
  - [ ] Create sanitization utilities
  - [ ] Sanitize all user input before rendering
  - [ ] Escape HTML special characters
  - [ ] Add HTML sanitizer library if needed

- [ ] **Error Handling**
  - [ ] Update all exception handlers with specific error types
  - [ ] Add logging middleware
  - [ ] Remove logging of sensitive data
  - [ ] Create error boundary component

- [ ] **Code Quality**
  - [ ] Remove duplicate imports
  - [ ] Add type hints to all Python functions
  - [ ] Remove hardcoded magic numbers
  - [ ] Create constants file for configuration

- [ ] **Response Validation**
  - [ ] Create response validation schemas
  - [ ] Validate all API responses before use
  - [ ] Test with malformed responses

### Phase 4: Low Priority (Week 4+)

- [ ] **Monitoring & Logging**
  - [ ] Set up request logging middleware
  - [ ] Add error tracking service (Sentry, etc.)
  - [ ] Create audit logs for sensitive operations
  - [ ] Set up alerts for security events

- [ ] **Testing**
  - [ ] Write security unit tests
  - [ ] Add integration tests for auth flow
  - [ ] Add load testing for rate limits
  - [ ] Perform OWASP top 10 testing

- [ ] **Documentation**
  - [ ] Document API endpoints and authentication
  - [ ] Create security requirements document
  - [ ] Document deployment procedures
  - [ ] Create incident response plan

- [ ] **Database Security**
  - [ ] Add encryption for sensitive fields
  - [ ] Implement database access control
  - [ ] Set up regular backups
  - [ ] Test backup/restore process

- [ ] **Infrastructure**
  - [ ] Configure firewall rules
  - [ ] Enable HTTPS/TLS
  - [ ] Set up DDoS protection
  - [ ] Configure WAF (Web Application Firewall)

---

## Testing Commands

### Test Authentication
```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "SecurePassword123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123"
  }'

# Store the access token from response, then:
curl -X POST http://localhost:8000/api/verify/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Some claim to verify"}'
```

### Test Rate Limiting
```bash
# Run 11 requests quickly (should fail on 11th)
for i in {1..11}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/api/verify/ \
    -H "Authorization: Bearer <TOKEN>" \
    -H "Content-Type: application/json" \
    -d '{"text": "Test claim"}' \
    -w "Status: %{http_code}\n"
done
```

### Test CORS
```bash
curl -X OPTIONS http://localhost:8000/api/verify/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

---

## Security Checklist for Deployment

- [ ] All hardcoded credentials removed
- [ ] DEBUG = False in production
- [ ] SECRET_KEY configured via environment variable
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enabled
- [ ] Database password changed from default
- [ ] CORS configured for specific domains only
- [ ] Rate limiting tested and configured
- [ ] Logging configured without sensitive data
- [ ] Error handling doesn't expose stack traces
- [ ] All dependencies updated and scanned for vulnerabilities
- [ ] Security headers implemented
- [ ] CSRF protection enabled
- [ ] API keys rotated
- [ ] Database backups configured
- [ ] Monitoring and alerting configured
- [ ] Load testing performed
- [ ] Security testing (OWASP ZAP) performed
- [ ] Documentation complete
- [ ] Incident response plan in place

