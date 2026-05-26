# Security Remediation Prompt

Use this prompt to fix the security review findings without unrelated refactors.

```text
You are a senior security-focused full-stack engineer working in the Factly repo. Fix the vulnerabilities found in the security review without unrelated refactors. Preserve existing behavior where possible, add focused tests for each security-sensitive change, and verify the app still runs.

Security findings to fix:

1. Unauthenticated refresh jobs can be abused
- File: backend/verification/views.py
- RefreshDataView currently uses AllowAny and can trigger update_trending_topics, update_global_events, and refresh_realtime_data.
- Make this endpoint staff/admin-only, or protect it with a strong server-side API key permission.
- Keep strict rate limiting.
- Return 403 for non-staff users.
- Add tests proving anonymous and non-staff users cannot trigger refresh jobs.

2. Stored XSS risk in article rendering
- Files: backend/content/serializers.py, backend/content/management/commands/import_rss.py, backend/content/views.py, frontend/src/pages/ArticlePage.js
- Article content is exposed as raw HTML and rendered with dangerouslySetInnerHTML.
- Add real HTML sanitization with an allowlist.
- Ensure scripts, event handlers, javascript: URLs, iframes, SVG, and unsafe styles are removed.
- Add tests for malicious HTML payloads.

3. SSRF protection is incomplete in URL verification
- File: backend/services/nlp_service/url_extraction_service.py
- Revalidate every redirect hop and final URL.
- Block localhost, private, loopback, link-local, multicast, reserved, and metadata IPs such as 169.254.169.254.
- Enforce http/https only.
- Add reasonable response size and content-type limits.
- Add tests for localhost, private IPs, public-to-private redirects, non-http schemes, and oversized/non-HTML responses.

4. Rate limiting trusts spoofable X-Forwarded-For
- File: backend/services/fact_checking_service/api_rate_limiter.py
- Only honor forwarded headers from trusted proxies, or use REMOTE_ADDR by default.
- Add tests proving arbitrary X-Forwarded-For does not bypass limits.

5. Rate limiter fails open on Redis errors
- File: backend/services/fact_checking_service/api_rate_limiter.py
- For expensive public endpoints, fail closed or fall back to a reliable shared limiter.
- Add tests for Redis failure behavior.

6. Production security flags are off by default/config
- File: backend/factly_backend/settings.py
- Ensure production configuration supports SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, HSTS seconds, HSTS subdomains, and HSTS preload.
- Keep local development ergonomic, but make production fail loudly or default safely when DEBUG=False.
- Run python manage.py check --deploy and address avoidable warnings.

7. Public analytics and push endpoints can be abused
- Files: backend/content/dashboard_views.py, backend/content/push_views.py
- Add stricter throttling and validation.
- Validate article_id exists before logging.
- Consider requiring ownership or signed tokens for unsubscribe.
- Add tests for invalid article_id, throttling, and malformed push payloads.

8. JWT authentication is not wired globally
- File: backend/factly_backend/settings.py
- Configure rest_framework_simplejwt.authentication.JWTAuthentication in DEFAULT_AUTHENTICATION_CLASSES.
- Add tests proving JWT-authenticated requests work for protected endpoints and anonymous requests are rejected.

Verification requirements:
- Run backend tests.
- Run Django deployment checks.
- Run frontend build or relevant frontend tests if frontend code changes.
- Run npm audit.
- Summarize exactly what changed, which tests were added, and any remaining risks.

Constraints:
- Do not commit secrets.
- Do not log tokens, password reset tokens, API keys, or authorization headers.
- Do not introduce broad unrelated refactors.
- Preserve public read endpoints unless explicitly securing risky write or job-triggering endpoints.
```
