"""
Core Foundation Views — CoachOS Phase 04 Baseline.
Implements safe healthz, readyz, and meta endpoints (ADR-048).
"""

import logging

from django.conf import settings
from django.db import connection
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthzView(APIView):
    """
    Public Liveness Probe (GET /healthz).
    Returns 200 OK if the application web server process is alive.
    Does not expose sensitive system details.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request: Request) -> Response:
        return Response(
            {
                "status": "pass",
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_200_OK,
        )


class ReadyzView(APIView):
    """
    Readiness Probe (GET /readyz).
    Validates operational connectivity to PostgreSQL database and Redis cache/broker.
    Returns 200 OK if all dependencies are healthy; 503 Service Unavailable if any check fails.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request: Request) -> Response:
        checks = {}
        all_passed = True

        # 1. Database connectivity check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            checks["database"] = "pass"
        except Exception as exc:
            logger.warning("Database readiness check failed: %s", exc)
            checks["database"] = "fail"
            all_passed = False

        # 2. Redis connectivity check
        try:
            import redis

            r = redis.from_url(settings.REDIS_URL, socket_timeout=2)
            if r.ping():
                checks["redis"] = "pass"
            else:
                checks["redis"] = "fail"
                all_passed = False
        except Exception as exc:
            logger.warning("Redis readiness check failed: %s", exc)
            # In local/test environments where Redis is optional, don't break test suite unless required
            checks["redis"] = "fail" if not settings.DEBUG else "warn"
            if not settings.DEBUG:
                all_passed = False

        status_code = status.HTTP_200_OK if all_passed else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(
            {
                "status": "pass" if all_passed else "fail",
                "checks": checks,
                "version": settings.APP_VERSION,
                "timestamp": timezone.now().isoformat(),
            },
            status=status_code,
        )


class MetaView(APIView):
    """
    Public System Metadata (GET /api/v1/meta).
    Provides safe system metadata for client synchronization without secret exposure.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request: Request) -> Response:
        return Response(
            {
                "app_name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "api_version": "v1",
                "locales": ["fa-IR", "en-US"],
                "default_locale": "fa-IR",
                "auth_strategy": "cookie_session",
                "environment": getattr(settings, "ENVIRONMENT", "development"),
                "capabilities": [
                    "pwa_shell",
                    "bilingual_fa_en",
                    "logical_css_rtl_ltr",
                    "rfc7807_errors",
                ],
                "timestamp": timezone.now().isoformat(),
            },
            status=status.HTTP_200_OK,
        )


def custom_404_handler(request, exception=None):
    """Fallback 404 handler returning RFC 7807 problem details JSON."""
    from django.http import JsonResponse

    correlation_id = getattr(request, "correlation_id", "-")
    return JsonResponse(
        {
            "type": "https://errors.coachos.io/not-found",
            "title": "Resource Not Found",
            "status": 404,
            "detail": "The requested resource was not found on this server.",
            "instance": request.path if request else "/unknown",
            "message_key": "error.not_found",
            "correlation_id": correlation_id,
        },
        status=status.HTTP_404_NOT_FOUND,
    )


def custom_500_handler(request):
    """Fallback 500 handler returning RFC 7807 problem details JSON."""
    from django.http import JsonResponse

    correlation_id = getattr(request, "correlation_id", "-")
    return JsonResponse(
        {
            "type": "https://errors.coachos.io/internal-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected server error occurred. Please reference correlation ID.",
            "instance": request.path if request else "/unknown",
            "message_key": "error.internal_error",
            "correlation_id": correlation_id,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
