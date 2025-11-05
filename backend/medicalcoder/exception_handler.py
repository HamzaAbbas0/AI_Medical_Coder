from typing import Any, Dict
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import (
    ValidationError, NotAuthenticated, AuthenticationFailed, PermissionDenied
)
from rest_framework import status
from .api_response import fail

def custom_exception_handler(exc: Exception, context: Dict[str, Any]):
    response = drf_exception_handler(exc, context)

    if response is None:
        return fail(
            message="Internal server error",
            code="INTERNAL_SERVER_ERROR",
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,  # ← note http_status
            detail=str(exc)
        )

    if isinstance(exc, ValidationError):
        return fail(
            message="Validation error",
            code="VALIDATION_ERROR",
            http_status=response.status_code,
            fields=response.data if isinstance(response.data, dict) else {}
        )

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return fail(
            message="Authentication required",
            code="AUTH_REQUIRED",
            http_status=response.status_code,
            detail=response.data.get("detail") if isinstance(response.data, dict) else None
        )

    if isinstance(exc, PermissionDenied):
        return fail(
            message="Permission denied",
            code="PERMISSION_DENIED",
            http_status=response.status_code,
            detail=response.data.get("detail") if isinstance(response.data, dict) else None
        )

    return fail(
        message="Request error",
        code="REQUEST_ERROR",
        http_status=response.status_code,
        fields=response.data if isinstance(response.data, dict) else {}
    )
