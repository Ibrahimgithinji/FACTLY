from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient

from services.trend_collector.models import Claim, Verdict


class Flaw1BrokenAuthorizationTest(TestCase):
    """Prove that a standard user cannot update a claim's verdict."""

    def setUp(self):
        self.client = APIClient()
        self.plain_user = User.objects.create_user(
            username='plain@example.com',
            email='plain@example.com',
            password='testpass123',
        )
        self.staff_user = User.objects.create_user(
            username='staff@example.com',
            email='staff@example.com',
            password='testpass123',
            is_staff=True,
        )
        self.claim = Claim.objects.create(
            claim_text='Test claim for authorization test.',
            source_url='https://example.com/test',
            verdict=Verdict.UNVERIFIED,
        )
        self.verdict_url = reverse('trend_collector:claim_verdict', args=[self.claim.id])

    def test_plain_user_gets_403_when_updating_verdict(self):
        original_verdict = self.claim.verdict

        self.client.force_authenticate(user=self.plain_user)
        response = self.client.patch(
            self.verdict_url,
            {'verdict': 'false'},
            format='json',
        )

        self.assertEqual(response.status_code, 403)

        self.claim.refresh_from_db()
        self.assertEqual(self.claim.verdict, original_verdict)

    def test_staff_user_can_update_verdict(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.patch(
            self.verdict_url,
            {'verdict': 'false'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.claim.refresh_from_db()
        self.assertEqual(self.claim.verdict, 'false')

    def test_unauthenticated_user_gets_401(self):
        response = self.client.patch(
            self.verdict_url,
            {'verdict': 'false'},
            format='json',
        )

        self.assertEqual(response.status_code, 401)
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.verdict, Verdict.UNVERIFIED)

    def test_factchecker_user_can_update_verdict(self):
        factchecker_group, _ = Group.objects.get_or_create(name='FactChecker')
        factchecker_user = User.objects.create_user(
            username='checker@example.com',
            email='checker@example.com',
            password='testpass123',
        )
        factchecker_user.groups.add(factchecker_group)

        self.client.force_authenticate(user=factchecker_user)
        response = self.client.patch(
            self.verdict_url,
            {'verdict': 'true'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.claim.refresh_from_db()
        self.assertEqual(self.claim.verdict, 'true')

    def test_update_with_invalid_verdict_returns_400(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.patch(
            self.verdict_url,
            {'verdict': 'not-a-valid-verdict'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)


class Flaw2PoorInputValidationTest(TestCase):
    """Prove that claim submission rejects malicious or invalid source_url."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='submitter@example.com',
            email='submitter@example.com',
            password='testpass123',
        )
        self.submit_url = reverse('trend_collector:claim_submit')
        self.client.force_authenticate(user=self.user)

    def _claim_count(self):
        return Claim.objects.count()

    def test_empty_source_url_returns_400(self):
        count_before = self._claim_count()
        response = self.client.post(
            self.submit_url,
            {'claim_text': 'Test claim.', 'source_url': ''},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self._claim_count(), count_before)

    def test_malformed_source_url_returns_400(self):
        count_before = self._claim_count()
        response = self.client.post(
            self.submit_url,
            {'claim_text': 'Test claim.', 'source_url': 'not-a-url'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self._claim_count(), count_before)

    def test_xss_javascript_url_returns_400(self):
        count_before = self._claim_count()
        response = self.client.post(
            self.submit_url,
            {'claim_text': 'Test claim.', 'source_url': 'javascript:alert(1)'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self._claim_count(), count_before)

    def test_xss_html_injection_url_returns_400(self):
        count_before = self._claim_count()
        response = self.client.post(
            self.submit_url,
            {'claim_text': 'Test claim.', 'source_url': '<script>alert(1)</script>'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self._claim_count(), count_before)

    def test_valid_submission_creates_claim(self):
        count_before = self._claim_count()
        response = self.client.post(
            self.submit_url,
            {
                'claim_text': 'Legitimate claim.',
                'source_url': 'https://example.com/valid-source',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self._claim_count(), count_before + 1)
        data = response.json()
        self.assertEqual(data['claim_text'], 'Legitimate claim.')
        self.assertEqual(data['source_url'], 'https://example.com/valid-source')

    def test_missing_claim_text_returns_400(self):
        response = self.client.post(
            self.submit_url,
            {'source_url': 'https://example.com/article'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_submission_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.submit_url,
            {
                'claim_text': 'Test claim.',
                'source_url': 'https://example.com/article',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 401)
