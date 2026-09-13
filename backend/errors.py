"""Public, retry-aware error contracts and FastAPI error boundary helpers."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException


_STATUS_CODES = {
    400: "bad_request",
    404: "not_found",
    409: "state_conflict",
    422: "validation_error",
    500: "internal_error",
    503: "provider_unavailable",
}


def error_detail(code: str, message: str, *, retryable: bool = False) -> dict[str, Any]:
    """Return the credential-free error shape consumed by XiaoG clients."""
    return {
        "code": code,
        "message": message,
        "retryable": retryable,
        "retry_action": "retry" if retryable else None,
    }


def normalize_http_detail(error: HTTPException) -> dict[str, Any]:
    """Keep existing detail.message behavior while adding stable error metadata."""
    detail = error.detail
    default_code = _STATUS_CODES.get(error.status_code, "request_failed")
    default_retryable = error.status_code in {500, 503}
    if isinstance(detail, dict):
        message = detail.get("message") if isinstance(detail.get("message"), str) else "请求失败，请稍后重试。"
        code = detail.get("code") if isinstance(detail.get("code"), str) else default_code
        retryable = detail.get("retryable") if isinstance(detail.get("retryable"), bool) else default_retryable
        return error_detail(code, message, retryable=retryable)
    return error_detail(default_code, str(detail), retryable=default_retryable)