"""Custom application exceptions."""


class DiviTrackerError(Exception):
    """Base exception for DiviTracker application."""

    pass


class ValidationError(DiviTrackerError):
    """Raised when input validation fails."""

    pass


class NotFoundError(DiviTrackerError):
    """Raised when a requested resource is not found."""

    pass


class DatabaseError(DiviTrackerError):
    """Raised when a database operation fails."""

    pass
