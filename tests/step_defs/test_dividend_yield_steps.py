"""Step definitions for dividend yield calculation feature."""

from datetime import datetime, timezone

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.extensions import db
from app.models import Dividend, Investment

# Load all scenarios from the feature file
scenarios("../features/dividend_yield.feature")


# Fixtures for BDD tests
@pytest.fixture
def investment_context():
    """Context to store test state between steps."""
    return {
        "investment_id": None,
        "calculated_yield": None,
        "investment_amount": None,
        "year": None,
    }


# Background step
@given("the application is configured for testing")
def app_configured(app):
    """Ensure the app is configured for testing."""
    pass  # The app fixture handles this


# Given steps - Investment creation
@given(
    parsers.parse('I have an investment "{name}" with {amount:d} dollars invested'),
    target_fixture="investment_context",
)
def create_investment(app, name, amount, investment_context):
    """Create an investment with the specified amount."""
    with app.app_context():
        investment = Investment(
            name=name,
            ticker=name[:4].upper(),
            total_invested=float(amount),
        )
        db.session.add(investment)
        db.session.commit()
        db.session.refresh(investment)
        investment_context["investment_id"] = investment.id
    return investment_context


@given(
    parsers.parse('I have an investment "{name}" with {amount:d} dollars currently invested'),
    target_fixture="investment_context",
)
def create_investment_current(app, name, amount, investment_context):
    """Create an investment with the specified current amount."""
    return create_investment(app, name, amount, investment_context)


# Given steps - Recording dividends
@given(
    parsers.parse(
        "I recorded {count:d} quarterly dividends of {amount:d} dollars each for the current year"
    )
)
def record_quarterly_dividends(app, count, amount, investment_context):
    """Record quarterly dividends for the current year."""
    current_year = datetime.now(timezone.utc).year
    months = [3, 6, 9, 12][:count]

    with app.app_context():
        investment = db.session.get(Investment, investment_context["investment_id"])
        for month in months:
            dividend = Dividend(
                investment_id=investment.id,
                amount=float(amount),
                frequency="quarterly",
                period_month=month,
                period_year=current_year,
            )
            db.session.add(dividend)
        db.session.commit()


@given(
    parsers.parse(
        "I recorded a {quarter} dividend of {amount:d} dollars with investment balance of {balance:d}"
    )
)
def record_dividend_with_balance(app, quarter, amount, balance, investment_context):
    """Record a dividend with investment amount at time."""
    current_year = datetime.now(timezone.utc).year
    _add_dividend(app, investment_context, quarter, amount, balance, current_year)


@given(
    parsers.parse(
        "I recorded a {quarter} dividend of {amount:d} dollars with investment balance of {balance:d} for year {year:d}"
    )
)
def record_dividend_with_balance_for_year(app, quarter, amount, balance, year, investment_context):
    """Record a dividend with investment amount for a specific year."""
    _add_dividend(app, investment_context, quarter, amount, balance, year)


@given(
    parsers.parse(
        "I recorded a {quarter} dividend of {amount:d} dollars without investment balance"
    )
)
def record_dividend_without_balance(app, quarter, amount, investment_context):
    """Record a dividend without investment amount at time."""
    current_year = datetime.now(timezone.utc).year
    _add_dividend(app, investment_context, quarter, amount, None, current_year)


def _add_dividend(app, investment_context, quarter, amount, balance, year):
    """Helper to add a dividend."""
    quarter_to_month = {"Q1": 3, "Q2": 6, "Q3": 9, "Q4": 12}
    month = quarter_to_month.get(quarter, 3)

    with app.app_context():
        dividend = Dividend(
            investment_id=investment_context["investment_id"],
            amount=float(amount),
            frequency="quarterly",
            period_month=month,
            period_year=year,
            investment_amount_at_time=float(balance) if balance is not None else None,
        )
        db.session.add(dividend)
        db.session.commit()


@given("no dividends have been recorded for the current year")
def no_dividends(app, investment_context):
    """Ensure no dividends are recorded."""
    pass  # No action needed, investment was just created


# When steps
@when("I calculate the dividend yield")
def calculate_yield(app, investment_context):
    """Calculate the dividend yield for the investment."""
    with app.app_context():
        investment = db.session.get(Investment, investment_context["investment_id"])
        investment_context["calculated_yield"] = investment.calculate_dividend_yield()
        investment_context["investment_amount"] = investment.get_investment_amount_for_year()


@when(parsers.parse("I calculate the dividend yield for year {year:d}"))
def calculate_yield_for_year(app, year, investment_context):
    """Calculate the dividend yield for a specific year."""
    with app.app_context():
        investment = db.session.get(Investment, investment_context["investment_id"])
        investment_context["calculated_yield"] = investment.calculate_dividend_yield(year)
        investment_context["investment_amount"] = investment.get_investment_amount_for_year(year)
        investment_context["year"] = year


@when("I get the investment amount for yield calculation")
def get_investment_amount(app, investment_context):
    """Get the investment amount used for yield calculation."""
    with app.app_context():
        investment = db.session.get(Investment, investment_context["investment_id"])
        investment_context["investment_amount"] = investment.get_investment_amount_for_year()


# Then steps
@then(parsers.parse("the yield should be {expected:f} percent"))
def verify_yield(investment_context, expected):
    """Verify the calculated yield matches expected value."""
    actual = round(investment_context["calculated_yield"], 2)
    assert actual == expected, f"Expected yield {expected}%, but got {actual}%"


@then(parsers.parse("the average investment balance should be {expected:d} dollars"))
def verify_average_balance(investment_context, expected):
    """Verify the average investment balance."""
    actual = investment_context["investment_amount"]
    assert actual == float(expected), f"Expected ${expected}, but got ${actual}"


@then(parsers.parse("the investment amount should be {expected:d} dollars"))
def verify_investment_amount(investment_context, expected):
    """Verify the investment amount used for calculation."""
    actual = investment_context["investment_amount"]
    assert actual == float(expected), f"Expected ${expected}, but got ${actual}"
