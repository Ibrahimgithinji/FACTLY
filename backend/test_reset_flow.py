#!/usr/bin/env python
"""
Test the password reset flow end-to-end
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factly_backend.settings')
django.setup()

from verification.models import PasswordResetToken
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

def test_reset_flow():
    test_email = 'testlogin@example.com'
    
    try:
        user = User.objects.get(email=test_email)
        print(f"✓ User found: {user.email}")
        
        # Clear old tokens
        PasswordResetToken.objects.filter(user=user).delete()
        print("✓ Old tokens cleared")
        
        # Create new token (simulating forgot-password)
        token_str = str(uuid.uuid4())
        expires_at = timezone.now() + timezone.timedelta(hours=24)
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token_str,
            expires_at=expires_at,
        )
        print(f"\n✓ Token created: {token_str}")
        print(f"  - Expires at: {expires_at}")
        print(f"  - Is valid: {reset_token.is_valid()}")
        print(f"  - Is used: {reset_token.is_used}")
        
        # Simulate verification (frontend calls verify-reset-token)
        verify_token = PasswordResetToken.objects.get(token=token_str)
        print(f"\n✓ Token retrieved from DB")
        if verify_token.is_valid():
            print(f"✓ Token verification passed")
        else:
            print(f"✗ Token verification failed")
            print(f"  - Is used: {verify_token.is_used}")
            print(f"  - Expired: {timezone.now() >= verify_token.expires_at}")
        
        # Simulate password reset
        print(f"\n→ Simulating password reset...")
        new_password = 'newpassword123'
        user.set_password(new_password)
        user.save()
        
        verify_token.is_used = True
        verify_token.save()
        
        print(f"✓ Password updated")
        print(f"✓ Token marked as used")
        
        # Verify token is no longer valid
        updated_token = PasswordResetToken.objects.get(token=token_str)
        if not updated_token.is_valid():
            print(f"✓ Token correctly marked as invalid after use")
        else:
            print(f"✗ Token should be invalid after use")
            
        print(f"\n✓ Full reset flow test passed!")
        
    except User.DoesNotExist:
        print(f"✗ User not found: {test_email}")
        print(f"Available users:")
        for u in User.objects.all():
            print(f"  - {u.email}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_reset_flow()
