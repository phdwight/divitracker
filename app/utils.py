"""Utility functions for the DiviTracker application."""

import re
import subprocess
from dataclasses import dataclass
from math import ceil


@dataclass
class PaginationResult:
    """Result of pagination calculation."""

    page: int
    total_pages: int
    start_idx: int
    end_idx: int


def paginate(total_items: int, page: int, items_per_page: int) -> PaginationResult:
    """
    Calculate pagination bounds.

    Args:
        total_items: Total number of items.
        page: Requested page number (1-indexed).
        items_per_page: Number of items per page.

    Returns:
        PaginationResult with corrected page and slice indices.
    """
    total_pages = ceil(total_items / items_per_page) if total_items > 0 else 1

    # Ensure page is within bounds
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    return PaginationResult(
        page=page,
        total_pages=total_pages,
        start_idx=start_idx,
        end_idx=end_idx,
    )


@dataclass
class DividendData:
    """Data transfer object for dividend creation/update."""

    amount_str: str
    frequency: str
    notes: str | None = None
    investment_amount_at_time_str: str | None = None
    period_month_str: str | None = None
    period_year_str: str | None = None


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


# Cache for version string to avoid repeated subprocess calls
_version_cache: str | None = None


def get_version() -> str:
    """
    Get the application version from git tags.

    Returns:
        Version string (e.g., 'v1.1.3') or 'dev' if not available.
    """
    global _version_cache
    if _version_cache is not None:
        return _version_cache

    try:
        # Try to get the version from git describe
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
            timeout=2,
        )
        version = result.stdout.strip()
        _version_cache = version if version else "dev"
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        # If git is not available or no tags exist, return 'dev'
        _version_cache = "dev"

    return _version_cache
