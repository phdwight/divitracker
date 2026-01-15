"""
Shared step definitions for BDD tests.

This module contains common step definitions that can be reused across
multiple feature files. Import steps from here in step definition files
that need them.

Usage in step definition files:
    from tests.step_defs.shared_steps import *
"""

from datetime import datetime, timezone

from pytest_bdd import given, when, then, parsers

from app.extensions import db
from app.models import Dividend, Investment


# =============================================================================
# Application Setup Steps
# =============================================================================

@given("the application is configured for testing")
def app_configured_basic(app):
    """Application is configured for testing (basic version)."""
    pass


@given("the application is configured for testing", target_fixture="app_context")
def app_configured_with_context(app):
    """Application is configured for testing (with app_context fixture)."""
    return app.app_context()


@given("the application is running")
def app_running(app, client):
    """Ensure app is running."""
    pass


# =============================================================================
# Investment Creation Steps (Parameterized)
# =============================================================================

@given(parsers.parse('an investment "{name}" with ticker "{ticker}" and {amount:d} dollars exists'))
def create_investment_full(app, context, name, ticker, amount):
    """Create an investment with name, ticker and amount."""
    investment = Investment(name=name, ticker=ticker, total_invested=float(amount))
    db.session.add(investment)
    db.session.commit()
    context["investment_id"] = investment.id
    context["investment_name"] = name
    context[f"investment_{name}_id"] = investment.id
    return context


@given(parsers.parse('an investment "{name}" with ticker "{ticker}" exists'))
def create_investment_no_amount(app, context, name, ticker):
    """Create an investment with name and ticker (default amount)."""
    investment = Investment(name=name, ticker=ticker, total_invested=10000.0)
    db.session.add(investment)
    db.session.commit()
    context["investment_id"] = investment.id
    context["investment_name"] = name
    context[f"investment_{name}_id"] = investment.id


@given(parsers.parse('an investment "{name}" with {amount:d} dollars exists'))
def create_investment_no_ticker(app, context, name, amount):
    """Create an investment with name and amount (no ticker)."""
    investment = Investment(name=name, ticker=None, total_invested=float(amount))
    db.session.add(investment)
    db.session.commit()
    context["investment_id"] = investment.id
    context["investment_name"] = name
    context[f"investment_{name}_id"] = investment.id


@given("no investments exist")
def no_investments_basic(app):
    """Ensure no investments exist."""
    Dividend.query.delete()
    Investment.query.delete()
    db.session.commit()


# =============================================================================
# Dividend Creation Steps (Parameterized)
# =============================================================================

@given(parsers.parse('a {frequency} dividend of {amount:d} for "{inv_name}" with period month {month:d} and year {year:d}'))
def create_dividend_with_period(app, context, frequency, amount, inv_name, month, year):
    """Create a dividend with specific period."""
    inv = Investment.query.filter_by(name=inv_name).first()
    div = Dividend(
        investment_id=inv.id,
        amount=float(amount),
        frequency=frequency,
        period_month=month,
        period_year=year,
    )
    db.session.add(div)
    db.session.commit()
    context["dividend_id"] = div.id


@given(parsers.parse('a {frequency} dividend of {amount:d} for "{inv_name}" with year {year:d}'))
def create_dividend_year_only(app, context, frequency, amount, inv_name, year):
    """Create a dividend with only year (no month)."""
    inv = Investment.query.filter_by(name=inv_name).first()
    div = Dividend(
        investment_id=inv.id,
        amount=float(amount),
        frequency=frequency,
        period_month=None,
        period_year=year,
    )
    db.session.add(div)
    db.session.commit()
    context["dividend_id"] = div.id


@given(parsers.parse('{count:d} {frequency} dividends of {amount:d} for "{inv_name}" in year {year:d}'))
def create_multiple_dividends(app, context, count, frequency, amount, inv_name, year):
    """Create multiple dividends for an investment."""
    inv = Investment.query.filter_by(name=inv_name).first()
    for month in range(1, count + 1):
        div = Dividend(
            investment_id=inv.id,
            amount=float(amount),
            frequency=frequency,
            period_month=month if frequency == "monthly" else None,
            period_year=year,
        )
        db.session.add(div)
    db.session.commit()


@given(parsers.parse('the investment has {frequency} dividends of {amount:d} dollars for the current year'))
def add_current_year_dividends(app, context, frequency, amount):
    """Add dividends to the investment for current year."""
    current_year = datetime.now(timezone.utc).year
    inv_id = context.get("investment_id")

    freq_months = {
        "monthly": list(range(1, 13)),
        "quarterly": [3, 6, 9, 12],
        "semi-annual": [6, 12],
        "yearly": [12],
    }

    months = freq_months.get(frequency, [12])
    for month in months:
        div = Dividend(
            investment_id=inv_id,
            amount=float(amount),
            frequency=frequency,
            period_month=month,
            period_year=current_year,
        )
        db.session.add(div)
    db.session.commit()


# =============================================================================
# Common Then Steps
# =============================================================================

@then(parsers.parse("I should see status code {code:d}"))
def check_status_code_common(context, code):
    """Check response status code from context."""
    assert context["response"].status_code == code


@then(parsers.parse('I should see "{text}" in the page'))
def check_text_in_page_common(context, text):
    """Check if text appears in response from context."""
    assert text.lower() in context["response"].data.decode().lower()


@then("I should see a not found error")
def check_not_found_error(context):
    """Check for not found error."""
    error = context.get("error")
    assert error is not None
    assert "not found" in str(error).lower()


@then(parsers.parse('I should see a validation error containing "{text}"'))
def check_validation_error_common(context, text):
    """Check for validation error message."""
    error = context.get("error") or context.get("validation_error", "")
    assert text.lower() in str(error).lower()


# =============================================================================
# Common When Steps
# =============================================================================

@when(parsers.parse('I visit "{url}"'))
def visit_url_common(client, context, url):
    """Visit a URL and store response in context."""
    context["response"] = client.get(url)


@when(parsers.parse('I visit "{url}" with redirects'))
def visit_url_with_redirects_common(client, context, url):
    """Visit a URL following redirects."""
    context["response"] = client.get(url, follow_redirects=True)
