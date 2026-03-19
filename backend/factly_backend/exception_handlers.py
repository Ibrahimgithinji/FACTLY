"""
Custom exception handlers for better error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns proper error messages
    instead of generic 500 Internal Server Errors.
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # Format the error response consistently
        error_response = {
            'error': True,
            'status_code': response.status_code,
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
        }
        
        # Add field-specific errors if available
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            error_response['errors'] = exc.detail
            
        response.data = error_response
        
    return response
