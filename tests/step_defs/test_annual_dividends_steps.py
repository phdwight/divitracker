"""Step definitions for annual dividends calculation feature."""

from datetime import datetime, timezone

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.extensions import db
from app.models import Dividend, Investment

scenarios("../features/annual_dividends.feature")


@pytest.fixture
def context():
    """Shared context for test state."""
    return {
        "investment_id": None,
        "annual_dividends": None,
        "total_dividends": None,
    }


# Background
@given("the application is configured for testing")
def app_configured(app):
    """Application is configured."""
    pass


# Given steps
@given(
    parsers.parse('an investment "{name}" with {amount:d} dollars exists'),
    target_fixture="context",
)
def investment_exists(app, name, amount, context):
    """Create an investment."""
    with app.app_context():
        investment = Investment(
            name=name,
            ticker=name[:4].upper(),
            total_invested=float(amount),
        )
        db.session.add(investment)
        db.session.commit()
        context["investment_id"] = investment.id
    return context


@given(
    parsers.parse(
        "I recorded {count:d} monthly dividends of {amount:d} dollars each for the current year"
    )
)
def record_monthly_dividends(app, count, amount, context):
    """Record monthly dividends."""
    current_year = datetime.now(timezone.utc).year
    with app.app_context():
        for month in range(1, count + 1):
            dividend = Dividend(
                investment_id=context["investment_id"],
                amount=float(amount),
                frequency="monthly",
                period_month=month,
                period_year=current_year,
            )
            db.session.add(dividend)
        db.session.commit()


@given(
    parsers.parse(
        "I recorded {count:d} quarterly dividends of {amount:d} dollars each for the current year"
    )
)
def record_quarterly_dividends_current(app, count, amount, context):
    """Record quarterly dividends for current year."""
    current_year = datetime.now(timezone.utc).year
    _record_quarterly_dividends(app, context["investment_id"], count, amount, current_year)


@given(
    parsers.parse(
        "I recorded {count:d} quarterly dividends of {amount:d} dollars each for year {year:d}"
    )
)
def record_quarterly_dividends_year(app, count, amount, year, context):
    """Record quarterly dividends for specific year."""
    _record_quarterly_dividends(app, context["investment_id"], count, amount, year)


def _record_quarterly_dividends(app, investment_id, count, amount, year):
    """Helper to record quarterly dividends."""
    months = [3, 6, 9, 12][:count]
    with app.app_context():
        for month in months:
            dividend = Dividend(
                investment_id=investment_id,
                amount=float(amount),
                frequency="quarterly",
                period_month=month,
                period_year=year,
            )
            db.session.add(dividend)
        db.session.commit()


@given(parsers.parse("I recorded a quarterly dividend of {amount:d} dollars for month {month:d}"))
def record_single_quarterly(app, amount, month, context):
    """Record a single quarterly dividend."""
    current_year = datetime.now(timezone.utc).year
    with app.app_context():
        dividend = Dividend(
            investment_id=context["investment_id"],
            amount=float(amount),
            frequency="quarterly",
            period_month=month,
            period_year=current_year,
        )
        db.session.add(dividend)
        db.session.commit()


@given(parsers.parse("I recorded a monthly dividend of {amount:d} dollars for month {month:d}"))
def record_single_monthly(app, amount, month, context):
    """Record a single monthly dividend."""
    current_year = datetime.now(timezone.utc).year
    with app.app_context():
        dividend = Dividend(
            investment_id=context["investment_id"],
            amount=float(amount),
            frequency="monthly",
            period_month=month,
            period_year=current_year,
        )
        db.session.add(dividend)
        db.session.commit()


# When steps
@when("I calculate the annual dividends", target_fixture="context")
def calculate_annual(app, context):
    """Calculate annual dividends for current year."""
    with app.app_context():
        investment = db.session.get(Investment, context["investment_id"])
        context["annual_dividends"] = investment.calculate_annual_dividends()
    return context


@when(parsers.parse("I calculate the annual dividends for year {year:d}"), target_fixture="context")
def calculate_annual_year(app, year, context):
    """Calculate annual dividends for specific year."""
    with app.app_context():
        investment = db.session.get(Investment, context["investment_id"])
        context["annual_dividends"] = investment.calculate_annual_dividends(year)
    return context


@when("I calculate the total dividends received", target_fixture="context")
def calculate_total(app, context):
    """Calculate total dividends received."""
    with app.app_context():
        investment = db.session.get(Investment, context["investment_id"])
        context["total_dividends"] = investment.get_total_dividends_received()
    return context


# Then steps
@then(parsers.parse("the annual dividend total should be {amount:d} dollars"))
def verify_annual_total(context, amount):
    """Verify annual dividend total."""
    assert context["annual_dividends"] == float(amount)


@then(parsers.parse("the total should be {amount:d} dollars"))
def verify_total(context, amount):
    """Verify total dividends."""
    assert context["total_dividends"] == float(amount)
