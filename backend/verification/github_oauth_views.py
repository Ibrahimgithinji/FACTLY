import logging
import os
import secrets
import requests
from urllib.parse import urlencode
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .cookie_auth import set_jwt_cookies, unset_jwt_cookies

logger = logging.getLogger(__name__)

GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', '')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000').rstrip('/')

GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_USER_URL = 'https://api.github.com/user'
GITHUB_EMAIL_URL = 'https://api.github.com/user/emails'


class OAuthInitRateThrottle(AnonRateThrottle):
    rate = '10/minute'
    scope = 'oauth_init'


class GitHubLoginInitView(APIView):
    """Initiates GitHub OAuth by redirecting to GitHub."""
    permission_classes = [AllowAny]
    throttle_classes = [OAuthInitRateThrottle]

    def get(self, request):
        state = secrets.token_urlsafe(32)
        request.session['github_oauth_state'] = state

        params = {
            'client_id': GITHUB_CLIENT_ID,
            'redirect_uri': request.build_absolute_uri('/api/verification/auth/github/callback/'),
            'scope': 'read:user user:email',
            'state': state,
        }
        return HttpResponseRedirect(f'{GITHUB_AUTHORIZE_URL}?{urlencode(params)}')


class GitHubCallbackView(APIView):
    """Handles GitHub OAuth callback, creates/finds user, returns JWT to frontend."""
    permission_classes = [AllowAny]
    throttle_classes = [OAuthInitRateThrottle]

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')
        stored_state = request.session.pop('github_oauth_state', None)

        if error:
            logger.warning(f'GitHub OAuth error: {error}')
            return self._redirect_with_error('GitHub authorization was denied')

        if not code:
            return self._redirect_with_error('No authorization code received')

        if not stored_state or state != stored_state:
            logger.warning('GitHub OAuth state mismatch — possible CSRF')
            return self._redirect_with_error('Security validation failed. Please try again.')

        try:
            access_token = self._exchange_code(code, request)
            if not access_token:
                return self._redirect_with_error('Failed to get access token from GitHub')

            user_info = self._get_user_info(access_token)
            if not user_info or not user_info.get('email'):
                return self._redirect_with_error('Could not retrieve email from GitHub')

            user = self._find_or_create_user(user_info)

            refresh = RefreshToken.for_user(user)
            user_data = {
                'id': user.id,
                'email': user.email,
                'name': user.first_name or user.username,
                'picture': user_info.get('avatar_url', ''),
            }

            response = self._render_callback_page(user_data)
            set_jwt_cookies(response, str(refresh.access_token), str(refresh))
            return response

        except Exception as e:
            logger.exception('GitHub OAuth callback failed')
            return self._redirect_with_error('Authentication failed. Please try again.')

    def _exchange_code(self, code, request):
        resp = requests.post(
            GITHUB_TOKEN_URL,
            headers={'Accept': 'application/json'},
            data={
                'client_id': GITHUB_CLIENT_ID,
                'client_secret': GITHUB_CLIENT_SECRET,
                'code': code,
                'redirect_uri': request.build_absolute_uri('/api/verification/auth/github/callback/'),
            },
            timeout=10,
        )
        if resp.status_code != 200:
            logger.error(f'GitHub token exchange failed: {resp.status_code} {resp.text[:200]}')
            return None
        data = resp.json()
        if 'access_token' not in data:
            logger.error(f'GitHub token exchange missing access_token: {data.get("error_description", data)}')
            return None
        return data['access_token']

    def _get_user_info(self, access_token):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github+json',
        }
        user_resp = requests.get(GITHUB_USER_URL, headers=headers, timeout=10)
        if user_resp.status_code != 200:
            logger.error(f'GitHub user API failed: {user_resp.status_code}')
            return None
        user_data = user_resp.json()

        email_resp = requests.get(GITHUB_EMAIL_URL, headers=headers, timeout=10)
        primary_email = ''
        if email_resp.status_code == 200:
            emails = email_resp.json()
            for e in emails:
                if e.get('primary'):
                    primary_email = e['email']
                    break
            if not primary_email and emails:
                primary_email = emails[0]['email']

        return {
            'id': str(user_data['id']),
            'email': primary_email or user_data.get('email', ''),
            'name': user_data.get('name') or user_data.get('login', ''),
            'avatar_url': user_data.get('avatar_url', ''),
        }

    def _find_or_create_user(self, user_info):
        email = user_info['email'].lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=None,
                first_name=user_info['name'],
            )
            user.set_unusable_password()
            user.save()

        from allauth.socialaccount.models import SocialAccount
        SocialAccount.objects.get_or_create(
            user=user,
            provider='github',
            uid=user_info['id'],
        )
        return user

    def _render_callback_page(self, user_data):
        import json
        html = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Signing in...</title></head>
<body>
<script>
(function() {{
    if (window.opener) {{
        window.opener.postMessage({{user: {json.dumps(user_data)}}}, "{FRONTEND_URL}");
        window.close();
    }} else {{
        window.location.href = "{FRONTEND_URL}/login?error=popup_blocked";
    }}
}})();
</script>
<p>Signing in... Please close this window if it doesn't close automatically.</p>
</body>
</html>'''
        return HttpResponse(html)

    def _redirect_with_error(self, message):
        from urllib.parse import quote
        return HttpResponseRedirect(f'{FRONTEND_URL}/login?error={quote(message)}')
