"""Tests for utility functions."""

from app.utils import sanitize_log_input


class TestSanitizeLogInput:
    """Tests for sanitize_log_input function (CWE-117 prevention)."""

    def test_sanitize_normal_string(self) -> None:
        """Test that normal strings pass through unchanged."""
        assert sanitize_log_input("Hello World") == "Hello World"

    def test_sanitize_newline(self) -> None:
        """Test that newlines are escaped."""
        assert sanitize_log_input("Line1\nLine2") == "Line1\\nLine2"

    def test_sanitize_carriage_return(self) -> None:
        """Test that carriage returns are escaped."""
        assert sanitize_log_input("Line1\rLine2") == "Line1\\rLine2"

    def test_sanitize_crlf(self) -> None:
        """Test that CRLF sequences are escaped."""
        assert sanitize_log_input("Line1\r\nLine2") == "Line1\\r\\nLine2"

    def test_sanitize_control_characters(self) -> None:
        """Test that control characters are removed."""
        # ASCII control characters 0x00-0x1F (except tab, newline, carriage return)
        result = sanitize_log_input("Hello\x00\x01\x02World")
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x02" not in result
        assert "HelloWorld" == result

    def test_sanitize_tab_preserved(self) -> None:
        """Test that tabs are preserved (not control char to remove)."""
        # Tab is \x09 which should be preserved as it's common in logs
        result = sanitize_log_input("Col1\tCol2")
        assert result == "Col1\tCol2"

    def test_sanitize_long_string_truncated(self) -> None:
        """Test that long strings are truncated to prevent log flooding."""
        long_string = "A" * 300
        result = sanitize_log_input(long_string)
        assert len(result) == 203  # 200 + len("...")
        assert result.endswith("...")

    def test_sanitize_non_string_converted(self) -> None:
        """Test that non-string values are converted to strings."""
        assert sanitize_log_input(123) == "123"  # type: ignore[arg-type]
        assert sanitize_log_input(None) == "None"  # type: ignore[arg-type]

    def test_sanitize_empty_string(self) -> None:
        """Test that empty strings are handled."""
        assert sanitize_log_input("") == ""

    def test_sanitize_injection_attempt(self) -> None:
        """Test that log injection attempts are neutralized."""
        # Attacker tries to inject fake log entry
        malicious = "Normal log\n2025-01-01 INFO Fake entry: Admin logged in"
        result = sanitize_log_input(malicious)
        assert "\n" not in result
        assert "\\n" in result
