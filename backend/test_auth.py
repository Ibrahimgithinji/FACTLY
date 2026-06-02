#!/usr/bin/env python
"""
Quick authentication test script
Run this to verify login endpoint is working correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factly_backend.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth.models import User
from django.test import Client
import json

def test_login():
    """Test the login endpoint"""
    
    print("=" * 60)
    print("AUTHENTICATION ENDPOINT TEST")
    print("=" * 60)
    
    # Check if users exist
    user_count = User.objects.count()
    print(f"\n✓ Users in database: {user_count}")
    
    if user_count == 0:
        print("✗ No users found. Please create a user first:")
        print("  python manage.py createsuperuser")
        return False
    
    # Get first user
    test_user = User.objects.first()
    print(f"✓ Test user: {test_user.email}")
    
    # Test login endpoint
    client = Client()
    print("\n" + "=" * 60)
    print("TESTING LOGIN ENDPOINT")
    print("=" * 60)
    
    # Get password for test (we'll use a test password)
    test_password = "TestPassword123"
    
    # Create a test user with known password if needed
    test_email = "test_auth@example.com"
    try:
        test_user_with_pass = User.objects.get(email=test_email)
    except User.DoesNotExist:
        print(f"\n→ Creating test user: {test_email}")
        test_user_with_pass = User.objects.create_user(
            username=test_email,
            email=test_email,
            password=test_password
        )
        print(f"✓ Test user created")
    
    # Test login
    print(f"\n→ Testing login with: {test_email}")
    response = client.post(
        '/api/verification/auth/login/',
        data=json.dumps({
            'email': test_email,
            'password': test_password
        }),
        content_type='application/json'
    )
    
    print(f"✓ Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Login successful!")
        print(f"  - Access token length: {len(data.get('access', ''))}")
        print(f"  - Refresh token length: {len(data.get('refresh', ''))}")
        print(f"  - User: {data.get('user', {}).get('email')}")
        return True
    else:
        print(f"✗ Login failed!")
        print(f"  Response: {response.json()}")
        return False

if __name__ == '__main__':
    try:
        success = test_login()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
