"""
Validation utilities for the Veo3 Workflow Agents TUI.

This module provides functions to validate user inputs, API keys, and other data.
"""

import re
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse

from .errors import ValidationError


def validate_prompt(prompt: str, min_length: int = 10, max_length: int = 5000) -> str:
    """
    Validate a prompt for video generation.
    
    Args:
        prompt: The prompt text to validate
        min_length: Minimum required length
        max_length: Maximum allowed length
    
    Returns:
        The cleaned prompt
    
    Raises:
        ValidationError: If prompt is invalid
    """
    if not isinstance(prompt, str):
        raise ValidationError("prompt", prompt, "Must be a string")
    
    # Clean whitespace
    prompt = prompt.strip()
    
    if not prompt:
        raise ValidationError("prompt", prompt, "Cannot be empty")
    
    if len(prompt) < min_length:
        raise ValidationError(
            "prompt", 
            prompt, 
            f"Must be at least {min_length} characters long"
        )
    
    if len(prompt) > max_length:
        raise ValidationError(
            "prompt",
            prompt,
            f"Must be no more than {max_length} characters long"
        )
    
    # Check for potentially problematic content
    if re.search(r'[^\x00-\x7F]', prompt):
        # Contains non-ASCII characters - warn but don't fail
        pass
    
    # Check for common prompt injection patterns
    suspicious_patterns = [
        r'ignore\s+previous\s+instructions',
        r'forget\s+everything',
        r'system\s*:',
        r'assistant\s*:',
        r'human\s*:',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            raise ValidationError(
                "prompt",
                prompt,
                "Contains potentially problematic content"
            )
    
    return prompt


def validate_api_key(api_key: str, service: str) -> str:
    """
    Validate an API key format.
    
    Args:
        api_key: The API key to validate
        service: The service the key is for
    
    Returns:
        The validated API key
    
    Raises:
        ValidationError: If API key is invalid
    """
    if not isinstance(api_key, str):
        raise ValidationError("api_key", api_key, "Must be a string")
    
    api_key = api_key.strip()
    
    if not api_key:
        raise ValidationError("api_key", api_key, "Cannot be empty")
    
    # Service-specific validation
    if service.lower() == "google":
        # Google API keys typically start with "AIza" and are 39 characters
        if not api_key.startswith("AIza"):
            raise ValidationError(
                "api_key",
                api_key,
                "Google API keys should start with 'AIza'"
            )
        if len(api_key) != 39:
            raise ValidationError(
                "api_key",
                api_key,
                "Google API keys should be 39 characters long"
            )
    
    elif service.lower() == "tavily":
        # Tavily API keys are typically alphanumeric
        if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
            raise ValidationError(
                "api_key",
                api_key,
                "Tavily API keys should contain only alphanumeric characters, underscores, and hyphens"
            )
    
    # General validation - no whitespace in the middle
    if ' ' in api_key:
        raise ValidationError(
            "api_key",
            api_key,
            "API keys should not contain spaces"
        )
    
    return api_key


def validate_video_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate video generation parameters.
    
    Args:
        params: Dictionary of video generation parameters
    
    Returns:
        Validated and normalized parameters
    
    Raises:
        ValidationError: If any parameter is invalid
    """
    if not isinstance(params, dict):
        raise ValidationError("video_params", params, "Must be a dictionary")
    
    validated = {}
    
    # Duration validation
    if "duration" in params:
        duration = params["duration"]
        if not isinstance(duration, (int, float)):
            raise ValidationError("duration", duration, "Must be a number")
        
        if duration < 1:
            raise ValidationError("duration", duration, "Must be at least 1 second")
        
        if duration > 300:  # 5 minutes max
            raise ValidationError("duration", duration, "Must be no more than 300 seconds")
        
        validated["duration"] = int(duration)
    
    # Quality validation
    if "quality" in params:
        quality = params["quality"]
        valid_qualities = ["low", "medium", "high", "ultra"]
        if quality not in valid_qualities:
            raise ValidationError(
                "quality",
                quality,
                f"Must be one of: {', '.join(valid_qualities)}"
            )
        validated["quality"] = quality
    
    # Aspect ratio validation
    if "aspect_ratio" in params:
        aspect_ratio = params["aspect_ratio"]
        valid_ratios = ["16:9", "9:16", "1:1", "4:3", "3:4"]
        if aspect_ratio not in valid_ratios:
            raise ValidationError(
                "aspect_ratio",
                aspect_ratio,
                f"Must be one of: {', '.join(valid_ratios)}"
            )
        validated["aspect_ratio"] = aspect_ratio
    
    # Resolution validation (if provided)
    if "resolution" in params:
        resolution = params["resolution"]
        if isinstance(resolution, str):
            # Parse string like "1920x1080"
            if not re.match(r'^\d+x\d+$', resolution):
                raise ValidationError(
                    "resolution",
                    resolution,
                    "Must be in format 'WIDTHxHEIGHT' (e.g., '1920x1080')"
                )
            width, height = map(int, resolution.split('x'))
        elif isinstance(resolution, (list, tuple)) and len(resolution) == 2:
            width, height = resolution
        else:
            raise ValidationError(
                "resolution",
                resolution,
                "Must be a string like '1920x1080' or tuple (width, height)"
            )
        
        # Validate resolution bounds
        if width < 256 or height < 256:
            raise ValidationError(
                "resolution",
                resolution,
                "Resolution must be at least 256x256"
            )
        
        if width > 4096 or height > 4096:
            raise ValidationError(
                "resolution",
                resolution,
                "Resolution must be no more than 4096x4096"
            )
        
        validated["resolution"] = f"{width}x{height}"
    
    # Style validation
    if "style" in params:
        style = params["style"]
        valid_styles = [
            "cinematic", "photorealistic", "animated", "artistic", 
            "documentary", "vintage", "modern", "fantasy"
        ]
        if style not in valid_styles:
            raise ValidationError(
                "style",
                style,
                f"Must be one of: {', '.join(valid_styles)}"
            )
        validated["style"] = style
    
    return validated


def validate_model_name(model_name: str, provider: str) -> str:
    """
    Validate a model name for a specific provider.
    
    Args:
        model_name: The model name to validate
        provider: The provider (e.g., 'google', 'openai')
    
    Returns:
        The validated model name
    
    Raises:
        ValidationError: If model name is invalid
    """
    if not isinstance(model_name, str):
        raise ValidationError("model_name", model_name, "Must be a string")
    
    model_name = model_name.strip()
    
    if not model_name:
        raise ValidationError("model_name", model_name, "Cannot be empty")
    
    if provider.lower() == "google":
        # Google model names should start with "gemini" or "video-generation"
        valid_prefixes = ["gemini", "video-generation"]
        if not any(model_name.startswith(prefix) for prefix in valid_prefixes):
            raise ValidationError(
                "model_name",
                model_name,
                f"Google model names should start with one of: {', '.join(valid_prefixes)}"
            )
    
    # General validation
    if not re.match(r'^[a-zA-Z0-9._-]+$', model_name):
        raise ValidationError(
            "model_name",
            model_name,
            "Model names should contain only alphanumeric characters, dots, underscores, and hyphens"
        )
    
    return model_name


def validate_file_path(file_path: str, must_exist: bool = False) -> str:
    """
    Validate a file path.
    
    Args:
        file_path: The file path to validate
        must_exist: Whether the file must already exist
    
    Returns:
        The validated file path
    
    Raises:
        ValidationError: If file path is invalid
    """
    if not isinstance(file_path, str):
        raise ValidationError("file_path", file_path, "Must be a string")
    
    file_path = file_path.strip()
    
    if not file_path:
        raise ValidationError("file_path", file_path, "Cannot be empty")
    
    # Check for invalid characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        if char in file_path:
            raise ValidationError(
                "file_path",
                file_path,
                f"Contains invalid character: '{char}'"
            )
    
    if must_exist:
        from pathlib import Path
        if not Path(file_path).exists():
            raise ValidationError(
                "file_path",
                file_path,
                "File does not exist"
            )
    
    return file_path


def validate_url(url: str) -> str:
    """
    Validate a URL.
    
    Args:
        url: The URL to validate
    
    Returns:
        The validated URL
    
    Raises:
        ValidationError: If URL is invalid
    """
    if not isinstance(url, str):
        raise ValidationError("url", url, "Must be a string")
    
    url = url.strip()
    
    if not url:
        raise ValidationError("url", url, "Cannot be empty")
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("url", url, "Invalid URL format")
        
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError("url", url, "URL must use http or https scheme")
        
    except Exception as e:
        raise ValidationError("url", url, f"Invalid URL: {str(e)}")
    
    return url
