#!/usr/bin/env python
"""
Test password reset API endpoints end-to-end
"""
import os
import django
import requests
import json
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factly_backend.settings')
django.setup()

from verification.models import PasswordResetToken
from django.contrib.auth.models import User

BASE_URL = 'http://localhost:8000/api'
TEST_EMAIL = 'testlogin@example.com'

def test_api_flow():
    print("=" * 60)
    print("Testing Password Reset API Flow")
    print("=" * 60)
    
    # Step 1: Request password reset
    print("\n1️⃣ Testing Forgot Password Endpoint...")
    response = requests.post(
        f"{BASE_URL}/auth/forgot-password/",
        json={"email": TEST_EMAIL},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code != 200:
        print("✗ Forgot password failed!")
        return
    
    # Step 2: Get the reset link (dev endpoint)
    print("\n2️⃣ Testing Get Reset Link Endpoint (Dev)...")
    response = requests.post(
        f"{BASE_URL}/auth/get-reset-link/",
        json={"email": TEST_EMAIL},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response keys: {list(data.keys())}")
    
    if response.status_code != 200:
        print(f"✗ Get reset link failed: {data}")
        return
    
    reset_token = data.get('token')
    print(f"   Token: {reset_token}")
    
    # Step 3: Verify reset token
    print("\n3️⃣ Testing Verify Reset Token Endpoint...")
    response = requests.post(
        f"{BASE_URL}/auth/verify-reset-token/",
        json={"token": reset_token},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code != 200:
        print("✗ Token verification failed!")
        return
    
    # Step 4: Reset password
    print("\n4️⃣ Testing Reset Password Endpoint...")
    new_password = "newtest123456"
    response = requests.post(
        f"{BASE_URL}/auth/reset-password/",
        json={
            "token": reset_token,
            "new_password": new_password,
            "confirm_password": new_password
        },
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code != 200:
        print("✗ Password reset failed!")
        return
    
    # Step 5: Try to login with new password
    print("\n5️⃣ Testing Login with New Password...")
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={
            "email": TEST_EMAIL,
            "password": new_password
        },
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        login_data = response.json()
        print(f"   ✓ Login successful!")
        print(f"   User: {login_data.get('user')}")
    else:
        print(f"   ✗ Login failed: {response.json()}")
    
    print("\n" + "=" * 60)
    print("✓ All steps completed!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_api_flow()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
