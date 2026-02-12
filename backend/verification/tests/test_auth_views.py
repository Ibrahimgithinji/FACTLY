from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.core import mail

from verification.models import PasswordResetToken


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetTests(TestCase):
    def setUp(self):
        self.user_email = 'tester@example.com'
        self.user_password = 'testpass123'
        self.user = User.objects.create_user(username=self.user_email, email=self.user_email, password=self.user_password)

    def test_forgot_password_creates_token_and_sends_email(self):
        url = reverse('verification:forgot_password')
        resp = self.client.post(url, {'email': self.user_email}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # Token created
        token_obj = PasswordResetToken.objects.filter(user=self.user).first()
        self.assertIsNotNone(token_obj)

        # Email sent
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertIn(token_obj.token, sent.body)

    def test_forgot_password_nonexistent_email(self):
        url = reverse('verification:forgot_password')
        resp = self.client.post(url, {'email': 'noone@nowhere.com'}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # No token created and no email
        self.assertFalse(PasswordResetToken.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_verify_reset_token_valid_and_invalid(self):
        # create token
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='my-token-123',
            expires_at=timezone.now() + timezone.timedelta(hours=1)
        )

        url = reverse('verification:verify_reset_token')
        resp = self.client.post(url, {'token': 'my-token-123'}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('valid'))
        self.assertEqual(data.get('email'), self.user_email)

        # invalid token
        resp2 = self.client.post(url, {'token': 'bad-token'}, content_type='application/json')
        self.assertEqual(resp2.status_code, 401)

    def test_reset_password_success_and_token_usage(self):
        token_obj = PasswordResetToken.objects.create(
            user=self.user,
            token='reset-abc-1',
            expires_at=timezone.now() + timezone.timedelta(hours=1)
        )

        url = reverse('verification:reset_password')
        new_password = 'new-secure-pass'
        resp = self.client.post(url, {
            'token': token_obj.token,
            'new_password': new_password,
            'confirm_password': new_password,
        }, content_type='application/json')

        self.assertEqual(resp.status_code, 200)
        # Refresh from DB
        token_obj.refresh_from_db()
        self.user.refresh_from_db()
        self.assertTrue(token_obj.is_used)
        self.assertTrue(self.user.check_password(new_password))

    def test_reset_password_expired_token(self):
        expired = PasswordResetToken.objects.create(
            user=self.user,
            token='expired-1',
            expires_at=timezone.now() - timezone.timedelta(hours=1)
        )

        url = reverse('verification:reset_password')
        resp = self.client.post(url, {
            'token': expired.token,
            'new_password': 'a1b2c3d4',
            'confirm_password': 'a1b2c3d4',
        }, content_type='application/json')

        self.assertEqual(resp.status_code, 401)
