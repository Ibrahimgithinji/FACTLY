"""
Custom exception handlers for better error responses.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

_SAFE_MESSAGES = {
    400: 'Bad request. Please check your input and try again.',
    401: 'Authentication credentials were not provided or are invalid.',
    403: 'You do not have permission to perform this action.',
    404: 'The requested resource was not found.',
    405: 'Method not allowed.',
    429: 'Request was throttled. Please try again later.',
}


def _sanitize_detail(detail):
    if isinstance(detail, dict):
        return {k: _sanitize_detail(v) for k, v in detail.items()}
    if isinstance(detail, list):
        return [_sanitize_detail(item) for item in detail]
    return str(detail)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns proper error messages
    instead of generic 500 Internal Server Errors.

    Sanitizes exception details before sending to the client to
    prevent information disclosure (e.g. internal stack traces,
    module paths, or database details).
    """
    response = exception_handler(exc, context)

    if response is not None:
        safe_message = _SAFE_MESSAGES.get(response.status_code, 'An error occurred.')

        error_response = {
            'error': True,
            'status_code': response.status_code,
            'message': safe_message,
        }

        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            error_response['errors'] = _sanitize_detail(exc.detail)

        logger.warning(
            "DRF exception handled: status=%s type=%s",
            response.status_code,
            type(exc).__name__,
        )

        response.data = error_response

    return response
