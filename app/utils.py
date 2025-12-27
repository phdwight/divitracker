"""Utility functions for the DiviTracker application."""

import re


def sanitize_log_input(value: str) -> str:
    """
    Sanitize user input for safe logging to prevent log injection (CWE-117).

    Removes or escapes newlines, carriage returns, and other control characters
    that could be used for log injection attacks.

    Args:
        value: The user input string to sanitize.

    Returns:
        Sanitized string safe for logging.
    """
    if not isinstance(value, str):
        return str(value)

    # Replace newlines and carriage returns with escaped versions
    sanitized = value.replace("\n", "\\n").replace("\r", "\\r")

    # Remove other control characters (ASCII 0-31 except tab)
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", sanitized)

    # Limit length to prevent log flooding
    max_length = 200
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized
