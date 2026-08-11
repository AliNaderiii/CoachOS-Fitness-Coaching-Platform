"""
Custom Exception Handler for RFC 7807 Problem Details.
Phase 04 Foundation - Standardizes error responses across /api/v1 (ADR-033).
"""

import logging
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

STATUS_TITLE_MAP = {
    400: ("Validation Error", "error.validation_failed"),
    401: ("Authentication Required", "error.authentication_required"),
    403: ("Permission Denied", "error.permission_denied"),
    404: ("Resource Not Found", "error.not_found"),
    405: ("Method Not Allowed", "error.method_not_allowed"),
    409: ("Conflict", "error.conflict"),
    429: ("Rate Limit Exceeded", "error.rate_limit_exceeded"),
    500: ("Internal Server Error", "error.internal_error"),
}


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """
    Standardize all DRF exceptions into an RFC 7807 Problem Details envelope with message_key.
    """
    response = exception_handler(exc, context)

    request = context.get("request")
    instance = request.path if request else "/api/v1/unknown"
    correlation_id = getattr(request, "correlation_id", "-") if request else "-"

    if response is not None:
        status_code = response.status_code
        default_title, default_key = STATUS_TITLE_MAP.get(
            status_code, ("API Error", "error.generic")
        )

        detail_text = "An error occurred while processing your request."
        field_errors = None

        if isinstance(response.data, dict):
            if "detail" in response.data:
                detail_text = str(response.data["detail"])
            elif len(response.data) > 0:
                field_errors = response.data
                detail_text = "The submitted payload contained validation errors."
        elif isinstance(response.data, list):
            detail_text = "; ".join(str(item) for item in response.data)

        envelope = {
            "type": f"https://errors.coachos.io/{default_key.replace('.', '-')}",
            "title": default_title,
            "status": status_code,
            "detail": detail_text,
            "instance": instance,
            "message_key": getattr(exc, "message_key", default_key),
            "correlation_id": correlation_id,
        }

        if field_errors:
            envelope["field_errors"] = field_errors

        response.data = envelope
        return response

    # Unhandled 500 server error
    logger.exception(
        "Unhandled exception in request [request_id=%s]: %s",
        correlation_id,
        exc,
    )

    return Response(
        {
            "type": "https://errors.coachos.io/internal-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected server error occurred. Please reference the correlation ID.",
            "instance": instance,
            "message_key": "error.internal_error",
            "correlation_id": correlation_id,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
