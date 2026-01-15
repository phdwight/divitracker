"""Step definitions for utility functions feature."""

import pytest
from pytest_bdd import given, when, then, scenarios, parsers

from app.utils import sanitize_log_input

scenarios("../features/utility_functions.feature")


@pytest.fixture
def context():
    """Shared context for storing state between steps."""
    return {}


@given("the application is configured for testing")
def app_configured():
    """No special setup needed for utility tests."""
    pass


@when(parsers.parse('I sanitize "{text}"'))
def sanitize_text(context, text):
    """Sanitize text."""
    # Handle escape sequences
    text = text.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
    context["result"] = sanitize_log_input(text)


@when('I sanitize ""')
def sanitize_empty_string(context):
    """Sanitize empty string."""
    context["result"] = sanitize_log_input("")


@when("I sanitize a string with control characters")
def sanitize_control_chars(context):
    """Sanitize string with control characters."""
    context["input"] = "Hello\x00\x01\x02World"
    context["result"] = sanitize_log_input(context["input"])


@when("I sanitize a string of 300 characters")
def sanitize_long_string(context):
    """Sanitize long string."""
    context["result"] = sanitize_log_input("A" * 300)


@when(parsers.parse("I sanitize integer {value:d}"))
def sanitize_integer(context, value):
    """Sanitize integer."""
    context["result"] = sanitize_log_input(value)  # type: ignore


@when("I sanitize None")
def sanitize_none(context):
    """Sanitize None."""
    context["result"] = sanitize_log_input(None)  # type: ignore


@then(parsers.parse('the result should be "{expected}"'))
def check_result(context, expected):
    """Check result equals expected."""
    # Handle escape sequences in expected
    expected = expected.replace("\\\\n", "\\n").replace("\\\\r", "\\r").replace("\\t", "\t")
    assert context["result"] == expected


@then('the result should be ""')
def check_result_empty(context):
    """Check result is empty string."""
    assert context["result"] == ""


@then("the control characters should be removed")
def check_control_removed(context):
    """Check control characters were removed."""
    assert "\x00" not in context["result"]
    assert "\x01" not in context["result"]
    assert "\x02" not in context["result"]
    assert context["result"] == "HelloWorld"


@then(parsers.parse("the result should be {length:d} characters"))
def check_result_length(context, length):
    """Check result length."""
    assert len(context["result"]) == length


@then(parsers.parse('the result should end with "{suffix}"'))
def check_result_ends_with(context, suffix):
    """Check result ends with suffix."""
    assert context["result"].endswith(suffix)


@then("the result should not contain actual newline")
def check_no_actual_newline(context):
    """Check result has no actual newline."""
    assert "\n" not in context["result"]


@then(parsers.parse('the result should contain escaped newline "{escaped}"'))
def check_escaped_newline(context, escaped):
    """Check result contains escaped newline."""
    # The actual escaped newline in the result is \n (backslash-n)
    assert "\\n" in context["result"]
