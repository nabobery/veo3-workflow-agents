from __future__ import annotations

from typing import Dict, Any


def classify_exception(exc: Exception | str) -> Dict[str, Any]:
    """
    Map low-level exceptions/messages to user-friendly categories and suggestions.
    Returns a dict with keys: type, message, suggestion.
    """
    text = str(exc).lower()

    # Invalid or missing credentials
    if any(k in text for k in ["invalid api key", "unauthorized", "401", "forbidden", "403", "permission"]):
        return {
            "type": "auth_error",
            "message": "Authentication failed. Check your Google API key.",
            "suggestion": "Open Settings (F2) and set a valid GOOGLE_API_KEY, then retry.",
        }

    # Quota/credits exhausted or billing issues
    if any(k in text for k in ["quota", "exceed", "credit", "billing", "payment", "insufficient"]):
        return {
            "type": "quota_error",
            "message": "Quota or credits exhausted for the API.",
            "suggestion": "Review your Google AI Studio billing/quotas or switch to a lower-cost model.",
        }

    # Rate limiting
    if any(k in text for k in ["rate limit", "429", "too many requests"]):
        return {
            "type": "rate_limit",
            "message": "Requests are rate limited right now.",
            "suggestion": "Wait a moment and retry. Reduce concurrency or request frequency.",
        }

    # Validation / bad input
    if any(k in text for k in ["invalid", "must", "required", "missing", "parse", "schema"]):
        return {
            "type": "validation_error",
            "message": "Input appears invalid for this operation.",
            "suggestion": "Adjust your prompt/parameters and try again.",
        }

    # Network / server failures
    if any(k in text for k in ["timeout", "timed out", "connection", "network", "503", "500", "unavailable"]):
        return {
            "type": "network_error",
            "message": "Temporary network or server issue.",
            "suggestion": "Retry after a short delay. Check connectivity.",
        }

    return {
        "type": "unknown_error",
        "message": "An unexpected error occurred.",
        "suggestion": "Check logs for details and try again.",
    }


def format_error_summary(info: Dict[str, Any], raw_error: Exception | str) -> str:
    return f"{info.get('message')} Suggestion: {info.get('suggestion')} (Details: {raw_error})"


