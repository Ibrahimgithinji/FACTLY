"""
URL configuration for factly_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import json

def json_error_response(request, status_code, message):
    """
    Create a JSON error response for API requests.
    Falls back to HTML response for non-API requests.
    """
    from django.http import JsonResponse, HttpResponseNotFound
    
    # Check if this looks like an API request
    if request.path.startswith('/api/'):
        return JsonResponse(
            {'error': message},
            status=status_code
        )
    
    # Fall back to default HTML error for non-API routes
    return None

def custom_404(request, exception):
    """Custom 404 error handler that returns JSON for API requests."""
    response = json_error_response(request, 404, 'Endpoint not found')
    if response:
        return response
    
    from django.views.defaults import page_not_found
    return page_not_found(request, exception)

def custom_500(request):
    """Custom 500 error handler that returns JSON for API requests."""
    response = json_error_response(request, 500, 'Internal server error')
    if response:
        return response
    
    from django.views.defaults import server_error
    return server_error(request)

def custom_400(request, exception):
    """Custom 400 error handler that returns JSON for API requests."""
    response = json_error_response(request, 400, 'Bad request')
    if response:
        return response
    
    from django.views.defaults import bad_request
    return bad_request(request, exception)

def custom_403(request, exception):
    """Custom 403 error handler that returns JSON for API requests."""
    response = json_error_response(request, 403, 'Permission denied')
    if response:
        return response
    
    from django.views.defaults import permission_denied
    return permission_denied(request, exception)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('verification.urls')),
]

# Register custom error handlers
handler404 = custom_404
handler500 = custom_500
handler400 = custom_400
handler403 = custom_403