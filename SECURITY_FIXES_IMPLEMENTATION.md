# FACTLY - Security Fixes & Implementation Examples

## Quick Fix Guide

---

## 1. Fix Authentication System (CRITICAL)

### Step 1: Update Django Settings
**File:** `backend/factly_backend/settings.py`

```python
# Add at the end:
from datetime import timedelta

# JWT Configuration
from rest_framework_simplejwt.settings import SIMPLE_JWT

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.getenv('DJANGO_SECRET_KEY'),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'JTI_CLAIM': 'jti',
    'USER_ID_FIELD': 'id',
    'TOKEN_TYPE_CLAIM': 'token_type',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Update INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'rest_framework_simplejwt',
]

# Django session security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Lax'
```

**Install JWT:**
```bash
pip install djangorestframework-simplejwt
```

### Step 2: Create Authentication API Views
**File:** `backend/verification/auth_views.py` (NEW)

```python
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
import logging

logger = logging.getLogger(__name__)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = authenticate(username=user.username, password=password)
        if not user:
            logger.warning(f"Failed login attempt for user: {email}")
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.first_name or user.username,
            }
        }, status=status.HTTP_200_OK)


class SignupView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        name = request.data.get('name', '')
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validate
        if not email or not password or not name:
            return Response(
                {'error': 'Name, email, and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 12:
            return Response(
                {'error': 'Password must be at least 12 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.first_name,
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Signup error: {e}")
            return Response(
                {'error': 'Unable to create account'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
            })
        except Exception as e:
            logger.warning(f"Invalid refresh token: {e}")
            return Response(
                {'error': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
```

### Step 3: Update URLs
**File:** `backend/verification/urls.py`

```python
from django.urls import path
from . import views, auth_views

app_name = 'verification'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('auth/signup/', auth_views.SignupView.as_view(), name='signup'),
    path('auth/refresh/', auth_views.RefreshTokenView.as_view(), name='refresh'),
    
    # Verification endpoints
    path('verify/', views.VerificationView.as_view(), name='verify'),
    path('health/', views.health_check, name='health_check'),
    
    # Fast verification endpoints
    path('verify/fast/', fast_views.FastVerificationView.as_view(), name='verify_fast'),
]
```

### Step 4: Update Frontend AuthContext
**File:** `frontend/src/context/AuthContext.js`

```javascript
import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);

  useEffect(() => {
    // Check for stored session
    const storedUser = sessionStorage.getItem('user');
    const storedAccessToken = sessionStorage.getItem('accessToken');
    
    if (storedUser && storedAccessToken) {
      try {
        setUser(JSON.parse(storedUser));
        setAccessToken(storedAccessToken);
        setIsAuthenticated(true);
      } catch (e) {
        // Clear invalid data
        sessionStorage.clear();
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || 'Login failed');
      }

      const data = await response.json();
      
      // Store tokens in sessionStorage (not localStorage!)
      // sessionStorage is cleared when browser closes
      sessionStorage.setItem('accessToken', data.access);
      sessionStorage.setItem('refreshToken', data.refresh);
      sessionStorage.setItem('user', JSON.stringify(data.user));
      
      setAccessToken(data.access);
      setRefreshToken(data.refresh);
      setUser(data.user);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (err) {
      console.error('Login error:', err);
      return { success: false, error: err.message };
    }
  };

  const signup = async (name, email, password) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/signup/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || 'Signup failed');
      }

      const data = await response.json();
      
      sessionStorage.setItem('accessToken', data.access);
      sessionStorage.setItem('refreshToken', data.refresh);
      sessionStorage.setItem('user', JSON.stringify(data.user));
      
      setAccessToken(data.access);
      setRefreshToken(data.refresh);
      setUser(data.user);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (err) {
      console.error('Signup error:', err);
      return { success: false, error: err.message };
    }
  };

  const logout = () => {
    sessionStorage.clear();
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    setIsAuthenticated(false);
  };

  const getAuthHeaders = () => {
    return {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    };
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    accessToken,
    login,
    signup,
    logout,
    getAuthHeaders,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
```

---

## 2. Fix Hardcoded Endpoints (HIGH)

### Create Environment Configuration
**File:** `frontend/.env.local` (for local development)

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

**File:** `frontend/.env.production` (for production)

```
REACT_APP_API_URL=https://api.factly.com
REACT_APP_ENV=production
```

### Create API Service Module
**File:** `frontend/src/services/api.js` (NEW)

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const apiEndpoints = {
  auth: {
    login: `${API_BASE_URL}/api/auth/login/`,
    signup: `${API_BASE_URL}/api/auth/signup/`,
    refresh: `${API_BASE_URL}/api/auth/refresh/`,
  },
  verify: {
    verify: `${API_BASE_URL}/api/verify/`,
    fast: `${API_BASE_URL}/api/verify/fast/`,
    batch: `${API_BASE_URL}/api/verify/batch/`,
  },
  health: `${API_BASE_URL}/api/health/`,
};

// Global fetch wrapper with error handling
export const apiCall = async (url, options = {}) => {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Add auth token if available
  const token = sessionStorage.getItem('accessToken');
  if (token) {
    defaultOptions.headers.Authorization = `Bearer ${token}`;
  }

  const finalOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, finalOptions);

    if (response.status === 401) {
      // Token expired - refresh or logout
      window.location.href = '/login';
      throw new Error('Session expired');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};
```

### Update VerificationForm to Use API Service
**File:** `frontend/src/components/VerificationForm.js`

```javascript
import { apiEndpoints, apiCall } from '../services/api';

// In handleSubmit:
try {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 60000);

  const isUrl = isValidUrl(input.trim());
  const requestBody = isUrl
    ? { url: input.trim() }
    : { text: input.trim() };

  const data = await apiCall(apiEndpoints.verify.verify, {
    method: 'POST',
    body: JSON.stringify(requestBody),
    signal: controller.signal,
  });

  clearTimeout(timeoutId);
  
  // Store result
  sessionStorage.setItem('factCheckResult', JSON.stringify(data));
  sessionStorage.setItem('factCheckQuery', input.trim());
  navigate('/results');
} catch (err) {
  // No mock data fallback!
  if (err.name === 'AbortError') {
    setError('Request timed out. Please try again.');
  } else {
    setError(err.message || 'Verification failed. Please try again.');
  }
}
```

---

## 3. Fix SSRF Vulnerability (HIGH)

### Add Comprehensive URL Safety Check
**File:** `backend/services/nlp_service/url_extraction_service.py`

Update the `_is_private_hostname` function:

```python
import socket
import ipaddress
import re
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

def is_safe_url(url: str, timeout: int = 10, max_size: int = 50 * 1024 * 1024) -> bool:
    """
    Comprehensive URL safety check before fetching.
    
    Args:
        url: URL to check
        timeout: Request timeout in seconds
        max_size: Maximum content size in bytes
        
    Returns:
        True if URL is safe to fetch, False otherwise
    """
    # Blocked schemes
    BLOCKED_SCHEMES = {'ftp', 'file', 'gopher', 'telnet', 'nntp'}
    
    # Blocked hostnames
    BLOCKED_HOSTS = {
        'localhost', '127.0.0.1', '0.0.0.0', '::1',
        'localhost.localdomain'
    }
    
    # Blocked domains
    BLOCKED_DOMAINS = {
        'example.com', 'example.net', 'example.org',
        'localhost', 'internal'
    }
    
    try:
        parsed = urlparse(url)
        
        # 1. Check scheme
        if parsed.scheme not in ('http', 'https'):
            logger.warning(f"Blocked URL scheme: {parsed.scheme}")
            return False
            
        # 2. Check hostname
        hostname = parsed.hostname
        if not hostname:
            logger.warning("URL missing hostname")
            return False
            
        if hostname in BLOCKED_HOSTS:
            logger.warning(f"Blocked hostname: {hostname}")
            return False
            
        # Check domain suffix
        for blocked in BLOCKED_DOMAINS:
            if hostname.endswith(blocked):
                logger.warning(f"Blocked domain: {hostname}")
                return False
        
        # 3. Resolve hostname and check IPs
        try:
            results = socket.getaddrinfo(hostname, parsed.port or 80)
            for family, socktype, proto, canonname, sockaddr in results:
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)
                
                # Block private/loopback/reserved ranges
                if (ip.is_private or ip.is_loopback or ip.is_reserved or 
                    ip.is_multicast or ip.is_link_local):
                    logger.warning(f"Blocked IP address: {ip_str}")
                    return False
                    
        except socket.gaierror:
            logger.warning(f"Failed to resolve hostname: {hostname}")
            return False
        
        # 4. Check path for traversal attacks
        path = parsed.path or ''
        if '..' in path or '..%' in path:
            logger.warning("Path traversal detected")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"URL safety check error: {e}")
        return False


# Update URLExtractionService
class URLExtractionService:
    MAX_RESPONSE_SIZE = 50 * 1024 * 1024  # 50MB
    REQUEST_TIMEOUT = 10  # seconds

    def extract_content(self, url: str) -> Optional[ExtractedContent]:
        """Extract content from URL with safety checks."""
        
        # 1. Check if URL is safe
        if not is_safe_url(url):
            logger.error(f"URL failed safety check: {url}")
            return None
        
        try:
            # 2. Fetch with timeout and size limits
            response = self.session.get(
                url,
                timeout=self.REQUEST_TIMEOUT,
                stream=True,  # Stream to check size before downloading
                headers={
                    'User-Agent': self.user_agent,
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'en-US,en;q=0.5',
                }
            )
            
            # 3. Check content-length before downloading full body
            content_length = response.headers.get('content-length')
            if content_length:
                try:
                    if int(content_length) > self.MAX_RESPONSE_SIZE:
                        logger.warning(f"Response too large: {content_length} bytes")
                        return None
                except ValueError:
                    pass
            
            # 4. Check status
            if response.status_code != 200:
                logger.warning(f"URL returned {response.status_code}")
                return None
            
            # 5. Download with size check
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.MAX_RESPONSE_SIZE:
                    logger.warning("Downloaded content exceeds size limit")
                    return None
            
            # 6. Parse content safely
            response_text = content.decode('utf-8', errors='ignore')
            
            # Extract from HTML
            soup = BeautifulSoup(response_text, 'html.parser')
            # ... rest of extraction logic
            
        except requests.Timeout:
            logger.error(f"URL request timeout: {url}")
            return None
        except Exception as e:
            logger.error(f"Error extracting content from URL: {e}")
            return None
```

---

## 4. Fix Rate Limiting (HIGH)

### Update to Use Django Cache (Redis)
**File:** `backend/factly_backend/settings.py`

```python
# Use Redis for caching (required for distributed rate limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'factly',
        'TIMEOUT': 3600,  # 1 hour default
    }
}

# REST Framework throttling
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/hour',
        'user': '100/hour',
        'verification': '10/hour',
    }
}
```

### Update Views to Use DRF Throttling
**File:** `backend/verification/views.py`

```python
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class VerificationAnonRateThrottle(AnonRateThrottle):
    scope = 'verification'
    rate = '10/hour'

class VerificationUserRateThrottle(UserRateThrottle):
    scope = 'verification'
    rate = '100/hour'

class VerificationView(APIView):
    throttle_classes = [VerificationAnonRateThrottle, VerificationUserRateThrottle]
    
    # Remove the old _rate_limit_storage and _check_rate_limit methods
    # DRF handles rate limiting now
    
    def post(self, request):
        # Rate limiting is automatic via throttle_classes
        # ... rest of method
```

**Install Redis support:**
```bash
pip install django-redis redis djangorestframework
```

---

## 5. Fix CSRF Protection (HIGH)

### Add CSRF Middleware Enforcement
**File:** `backend/factly_backend/settings.py`

```python
# Already included, but make sure it's enabled
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CSRF configuration
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',  # for development
    'https://factly.com',     # for production
]
```

### Add CSRF Token Utility to Frontend
**File:** `frontend/src/services/csrf.js` (NEW)

```javascript
export const getCsrfToken = () => {
  const name = 'csrftoken';
  let cookieValue = null;
  
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === `${name}=`) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  
  return cookieValue;
};

export const getCSRFHeaders = () => {
  return {
    'X-CSRFToken': getCsrfToken(),
  };
};
```

### Update API Service to Include CSRF Token
**File:** `frontend/src/services/api.js`

```javascript
import { getCSRFHeaders } from './csrf';

export const apiCall = async (url, options = {}) => {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...getCSRFHeaders(),  // Add CSRF token
    },
  };

  const token = sessionStorage.getItem('accessToken');
  if (token) {
    defaultOptions.headers.Authorization = `Bearer ${token}`;
  }

  // ... rest of function
};
```

---

## 6. Add Security Headers

**File:** `backend/factly_backend/settings.py`

```python
# Add to settings
import os
from datetime import timedelta

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "cdn.jsdelivr.net"),  # Add trusted CDNs if needed
    'style-src': ("'self'", "'unsafe-inline'"),  # Try to remove unsafe-inline
    'img-src': ("'self'", "data:", "https:"),
    'font-src': ("'self'",),
    'connect-src': ("'self'",),  # API calls only to same origin
    'frame-ancestors': ("'none'",),
    'base-uri': ("'self'",),
    'form-action': ("'self'",),
}

# HSTS - Force HTTPS
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SECURE_HSTS_SECONDS = 0
    SECURE_SSL_REDIRECT = False

SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'
```

---

## 7. Remove Duplicate Imports

**File:** `backend/verification/views.py`

Remove duplicates at the top:

```python
# ❌ BEFORE (has duplicates):
import logging
import time
from typing import Optional, Dict, Any
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import JsonResponse
import time  # DUPLICATE
from typing import Optional, Dict, Any  # DUPLICATE
...

# ✅ AFTER (cleaned up):
import logging
import time
from typing import Optional, Dict, Any
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import JsonResponse

from .serializers import (
    VerificationRequestSerializer,
    VerificationResponseSerializer
)
# ... rest of imports
```

---

## 8. Add Input Validation in Serializers

**File:** `backend/verification/serializers.py`

```python
from rest_framework import serializers
from typing import Dict, Any, List
from datetime import datetime

class VerificationRequestSerializer(serializers.Serializer):
    """Serializer for verification request data."""
    text = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10000,  # Server-side limit
        trim_whitespace=True
    )
    url = serializers.URLField(
        required=False,
        allow_blank=True,
        max_length=2000
    )
    language = serializers.CharField(
        required=False,
        default='en',
        max_length=10,
        regex=r'^[a-z]{2}(-[A-Z]{2})?$'  # Validate language code
    )

    def validate(self, data):
        """Validate that either text or url is provided."""
        text = data.get('text', '').strip()
        url = data.get('url', '').strip()
        
        if not text and not url:
            raise serializers.ValidationError(
                "Either 'text' or 'url' must be provided."
            )
        
        # If text provided, check minimum length
        if text and len(text) < 10:
            raise serializers.ValidationError(
                "Text must be at least 10 characters."
            )
        
        # If both provided, prefer text
        if text and url:
            data['url'] = ''
        
        return data
```

---

## Testing the Fixes

```bash
# Install dependencies
pip install -r backend/requirements.txt
pip install djangorestframework-simplejwt django-redis redis

# Run migrations (after adding new auth models)
python backend/manage.py makemigrations
python backend/manage.py migrate

# Test authentication
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"SecurePassword123"}'

# Test token refresh
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'

# Test verification with auth
curl -X POST http://localhost:8000/api/verify/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"text":"Some claim to verify"}'
```

