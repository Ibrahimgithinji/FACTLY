"""
Health Check Views for FACTLY

Provides basic health check endpoints for monitoring and load balancer checks.
"""

import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache

logger = logging.getLogger(__name__)


@require_GET
@never_cache
def liveness_check(request):
    """
    Basic liveness check - returns 200 if the application is running.
    Used by Kubernetes and load balancers to determine if the pod is alive.
    """
    return JsonResponse({
        "status": "alive",
        "service": "factly-backend",
        "timestamp": datetime.now().isoformat() + "Z"
    })


@require_GET
@never_cache
def readiness_check(request):
    """
    Readiness check - returns 200 if the application is ready to serve traffic.
    Checks database connectivity and basic services.
    """
    try:
        # Basic database check
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()

        return JsonResponse({
            "status": "ready",
            "service": "factly-backend",
            "database": "connected",
            "timestamp": datetime.now().isoformat() + "Z"
        })
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JsonResponse({
            "status": "not ready",
            "service": "factly-backend",
            "timestamp": datetime.now().isoformat() + "Z"
        }, status=503)


@require_GET
@never_cache
def startup_check(request):
    """
    Startup check - returns 200 if the application has started successfully.
    Similar to liveness but used during initial startup.
    """
    return JsonResponse({
        "status": "started",
        "service": "factly-backend",
        "timestamp": datetime.now().isoformat() + "Z"
    })


@require_GET
@never_cache
def comprehensive_health_check(request):
    """
    Comprehensive health check - checks all services and dependencies.
    Returns detailed status of all components.
    """
    health_status = {
        "status": "healthy",
        "service": "factly-backend",
        "timestamp": datetime.now().isoformat() + "Z",
        "checks": {}
    }

    # Database check
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        health_status["checks"]["database"] = {"status": "healthy", "details": "connected"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy"}
        health_status["status"] = "unhealthy"

    # Cache check (if Redis is available)
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        result = cache.get('health_check')
        if result == 'ok':
            health_status["checks"]["cache"] = {"status": "healthy", "details": "redis connected"}
        else:
            health_status["checks"]["cache"] = {"status": "unhealthy", "error": "cache not working"}
            health_status["status"] = "unhealthy"
    except Exception:
        health_status["checks"]["cache"] = {"status": "unhealthy"}

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JsonResponse(health_status, status=status_code)
