import os
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.JWT_AUTH_COOKIE) or None

        if raw_token is None:
            return super().authenticate(request)

        try:
            validated_token = self.get_validated_token(raw_token)
        except (InvalidToken, AuthenticationFailed):
            return None

        user = self.get_user(validated_token)
        return (user, validated_token)


def set_jwt_cookies(response, access_token, refresh_token=None):
    cookie_settings = {
        'httponly': True,
        'secure': os.getenv('JWT_COOKIE_SECURE', 'False').lower() in ('true', '1'),
        'samesite': 'Lax',
        'path': '/',
    }
    response.set_cookie(
        settings.JWT_AUTH_COOKIE,
        access_token,
        max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
        **cookie_settings,
    )
    if refresh_token:
        response.set_cookie(
            settings.JWT_AUTH_REFRESH_COOKIE,
            refresh_token,
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
            **cookie_settings,
        )


def unset_jwt_cookies(response):
    response.delete_cookie(settings.JWT_AUTH_COOKIE, path='/')
    response.delete_cookie(settings.JWT_AUTH_REFRESH_COOKIE, path='/')
