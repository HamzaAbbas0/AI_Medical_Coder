from typing import Any, Dict, Optional
from rest_framework.response import Response
from rest_framework import status as http

def ok(
    data: Optional[Dict[str, Any]] = None,
    message: str = "OK",
    code: str = "OK",
    http_status: int = http.HTTP_200_OK,   # ← rename to avoid shadowing
) -> Response:
    return Response({
        "success": True,
        "message": message,
        "code": code,
        "data": data or {},
        "error": None
    }, status=http_status)

def fail(
    message: str,
    code: str = "ERROR",
    http_status: int = http.HTTP_400_BAD_REQUEST,  # ← rename
    fields: Optional[Dict[str, Any]] = None,
    detail: Optional[str] = None
) -> Response:
    return Response({
        "success": False,
        "message": message,
        "code": code,
        "data": None,
        "error": {
            "fields": fields or {},
            "detail": detail
        }
    }, status=http_status)
