"""Step definitions for period validation feature."""

import pytest
from pytest_bdd import given, when, then, scenarios, parsers

from app.exceptions import ValidationError
from app.services.dividend_service import DividendService

scenarios("../features/period_validation.feature")


@given("the application is configured for testing", target_fixture="app_context")
def app_configured(app):
    """Set up application context for testing."""
    with app.app_context():
        yield app


@when(parsers.parse('I validate period month "{value}"'), target_fixture="validated_month")
def validate_period_month(app_context, value):
    """Validate a period month string."""
    service = DividendService()
    return service._validate_period_month(value)


@when('I validate period month ""', target_fixture="validated_month")
def validate_period_month_empty(app_context):
    """Validate an empty period month."""
    service = DividendService()
    return service._validate_period_month("")


@when("I validate period month with None", target_fixture="validated_month")
def validate_period_month_none(app_context):
    """Validate a None period month."""
    service = DividendService()
    return service._validate_period_month(None)


@when(parsers.parse('I try to validate period month "{value}"'))
def try_validate_period_month(app_context, value, context):
    """Try to validate an invalid period month."""
    service = DividendService()
    try:
        service._validate_period_month(value)
        context["error"] = None
    except ValidationError as e:
        context["error"] = e


@then(parsers.parse("the validated month should be {expected:d}"))
def check_validated_month_int(validated_month, expected):
    """Check validated month equals expected integer."""
    assert validated_month == expected


@then("the validated month should be None")
def check_validated_month_none(validated_month):
    """Check validated month is None."""
    assert validated_month is None


@when(parsers.parse('I validate period year "{value}"'), target_fixture="validated_year")
def validate_period_year(app_context, value):
    """Validate a period year string."""
    service = DividendService()
    return service._validate_period_year(value)


@when('I validate period year ""', target_fixture="validated_year")
def validate_period_year_empty(app_context):
    """Validate an empty period year."""
    service = DividendService()
    return service._validate_period_year("")


@when("I validate period year with None", target_fixture="validated_year")
def validate_period_year_none(app_context):
    """Validate a None period year."""
    service = DividendService()
    return service._validate_period_year(None)


@when(parsers.parse('I try to validate period year "{value}"'))
def try_validate_period_year(app_context, value, context):
    """Try to validate an invalid period year."""
    service = DividendService()
    try:
        service._validate_period_year(value)
        context["error"] = None
    except ValidationError as e:
        context["error"] = e


@then(parsers.parse("the validated year should be {expected:d}"))
def check_validated_year_int(validated_year, expected):
    """Check validated year equals expected integer."""
    assert validated_year == expected


@then("the validated year should be None")
def check_validated_year_none(validated_year):
    """Check validated year is None."""
    assert validated_year is None


@then(parsers.re(r'I should see a validation error containing "(?P<text>[^"]+)"'))
def check_validation_error(context, text):
    """Check that validation error contains expected text."""
    assert context.get("error") is not None, "Expected a validation error but none was raised"
    assert text.lower() in str(context["error"]).lower()


@pytest.fixture
def context():
    """Shared context for storing state between steps."""
    return {}
