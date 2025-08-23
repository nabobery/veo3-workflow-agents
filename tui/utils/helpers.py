"""
Helper utility functions for the Veo3 Workflow Agents TUI.

This module provides common utility functions for formatting, text processing,
and other general-purpose operations.
"""

import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Union


def format_duration(seconds: Union[int, float]) -> str:
    """
    Format a duration in seconds to a human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string
    """
    if seconds < 0:
        return "0s"
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds:.0f}s"
        return f"{minutes}m"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours < 24:
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{hours}h"
    
    days = hours // 24
    remaining_hours = hours % 24
    
    if remaining_hours > 0:
        return f"{days}d {remaining_hours}h"
    return f"{days}d"


def format_file_size(bytes_size: int) -> str:
    """
    Format a file size in bytes to a human-readable string.
    
    Args:
        bytes_size: Size in bytes
    
    Returns:
        Formatted size string
    """
    if bytes_size < 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_size)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding suffix if truncated.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of the result
        suffix: Suffix to add if text is truncated
    
    Returns:
        Truncated text
    """
    if not isinstance(text, str):
        text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Convert a string to a safe filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        max_length: Maximum length for the filename
    
    Returns:
        Safe filename
    """
    if not isinstance(filename, str):
        filename = str(filename)
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)  # Remove control characters
    filename = re.sub(r'[/\\]', '_', filename)  # Replace path separators
    
    # Replace multiple consecutive spaces/underscores with single underscore
    filename = re.sub(r'[\s_]+', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure it's not empty
    if not filename:
        filename = "untitled"
    
    # Truncate if necessary
    if len(filename) > max_length:
        name_part = filename[:max_length - 4]
        filename = name_part + "..." if len(name_part) > 0 else "file"
    
    return filename


def format_timestamp(timestamp: Optional[Union[float, datetime]] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a timestamp to a string.
    
    Args:
        timestamp: Timestamp to format (defaults to current time)
        format_str: Format string for strftime
    
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        dt = datetime.now()
    elif isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        return str(timestamp)
    
    return dt.strftime(format_str)


def relative_time(timestamp: Union[float, datetime]) -> str:
    """
    Get a relative time string (e.g., "2 minutes ago").
    
    Args:
        timestamp: Timestamp to compare against current time
    
    Returns:
        Relative time string
    """
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        return str(timestamp)
    
    now = datetime.now()
    diff = now - dt
    
    if diff.total_seconds() < 0:
        return "in the future"
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    
    hours = int(minutes // 60)
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    
    days = int(hours // 24)
    if days < 30:
        return f"{days} day{'s' if days != 1 else ''} ago"
    
    months = int(days // 30)
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''} ago"
    
    years = int(months // 12)
    return f"{years} year{'s' if years != 1 else ''} ago"


def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """
    Extract keywords from text using simple heuristics.
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return
    
    Returns:
        List of keywords
    """
    if not isinstance(text, str):
        return []
    
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Common stop words to filter out
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'out', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
        'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
        'some', 'such', 'only', 'own', 'same', 'than', 'too', 'very', 'can',
        'will', 'just', 'should', 'now', 'are', 'was', 'were', 'been', 'being',
        'have', 'has', 'had', 'having', 'this', 'that', 'these', 'those'
    }
    
    # Filter out stop words and count occurrences
    word_counts = {}
    for word in words:
        if word not in stop_words and len(word) > 2:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in keywords[:max_keywords]]


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing line endings.
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return str(text)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple newlines to double
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def parse_duration(duration_str: str) -> Optional[int]:
    """
    Parse a duration string (e.g., "30s", "2m", "1h30m") to seconds.
    
    Args:
        duration_str: Duration string to parse
    
    Returns:
        Duration in seconds, or None if parsing fails
    """
    if not isinstance(duration_str, str):
        return None
    
    duration_str = duration_str.strip().lower()
    
    if not duration_str:
        return None
    
    # Try to parse as plain number (assume seconds)
    if duration_str.isdigit():
        return int(duration_str)
    
    # Parse with units
    total_seconds = 0
    
    # Pattern to match number + unit
    pattern = r'(\d+)\s*([smhd])'
    matches = re.findall(pattern, duration_str)
    
    if not matches:
        return None
    
    unit_multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    for value, unit in matches:
        if unit in unit_multipliers:
            total_seconds += int(value) * unit_multipliers[unit]
    
    return total_seconds if total_seconds > 0 else None


def is_valid_json(text: str) -> bool:
    """
    Check if a string is valid JSON.
    
    Args:
        text: Text to check
    
    Returns:
        True if text is valid JSON, False otherwise
    """
    try:
        import json
        json.loads(text)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def generate_id(length: int = 8) -> str:
    """
    Generate a random alphanumeric ID.
    
    Args:
        length: Length of the ID to generate
    
    Returns:
        Random ID string
    """
    import random
    import string
    
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
