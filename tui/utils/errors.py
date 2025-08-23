"""
Custom exception classes for the Veo3 Workflow Agents TUI.

This module defines a hierarchy of exceptions that provide clear error messaging
and help with debugging and user feedback.
"""

from typing import Optional, Dict, Any


class TUIError(Exception):
    """Base exception for all TUI-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigurationError(TUIError):
    """Raised when there's a configuration-related error."""
    pass


class APIError(TUIError):
    """Base class for API-related errors."""
    
    def __init__(self, message: str, service: Optional[str] = None, status_code: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.service = service
        self.status_code = status_code


class APIKeyError(APIError):
    """Raised when there's an API key-related error."""
    
    def __init__(self, service: str, message: Optional[str] = None):
        if message is None:
            message = f"Invalid or missing API key for {service}"
        super().__init__(message, service=service)


class APILimitError(APIError):
    """Raised when API limits or quotas are exceeded."""
    
    def __init__(self, service: str, limit_type: str = "rate", message: Optional[str] = None):
        if message is None:
            message = f"{limit_type.title()} limit exceeded for {service}"
        super().__init__(message, service=service)
        self.limit_type = limit_type


class ModelError(TUIError):
    """Raised when there's a model-related error."""
    
    def __init__(self, model: str, message: str, **kwargs):
        super().__init__(f"Model '{model}' error: {message}", **kwargs)
        self.model = model


class ValidationError(TUIError):
    """Raised when input validation fails."""
    
    def __init__(self, field: str, value: Any, message: str, **kwargs):
        super().__init__(f"Validation error for '{field}': {message}", **kwargs)
        self.field = field
        self.value = value


class VideoGenerationError(TUIError):
    """Raised when video generation fails."""
    
    def __init__(self, message: str, prompt: Optional[str] = None, **kwargs):
        super().__init__(f"Video generation failed: {message}", **kwargs)
        self.prompt = prompt


class NetworkError(APIError):
    """Raised when there's a network-related error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(f"Network error: {message}", **kwargs)


class TimeoutError(APIError):
    """Raised when an API request times out."""
    
    def __init__(self, service: str, timeout_seconds: float, **kwargs):
        message = f"Request to {service} timed out after {timeout_seconds}s"
        super().__init__(message, service=service, **kwargs)
        self.timeout_seconds = timeout_seconds


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    
    def __init__(self, service: str, message: Optional[str] = None, **kwargs):
        if message is None:
            message = f"Authentication failed for {service}"
        super().__init__(message, service=service, **kwargs)


class QuotaExceededError(APILimitError):
    """Raised when API quota is exceeded."""
    
    def __init__(self, service: str, quota_type: str = "daily", **kwargs):
        message = f"{quota_type.title()} quota exceeded for {service}"
        super().__init__(service, "quota", message, **kwargs)
        self.quota_type = quota_type


class UnsupportedOperationError(TUIError):
    """Raised when an operation is not supported."""
    
    def __init__(self, operation: str, reason: Optional[str] = None, **kwargs):
        message = f"Unsupported operation: {operation}"
        if reason:
            message += f" ({reason})"
        super().__init__(message, **kwargs)
        self.operation = operation
        self.reason = reason
