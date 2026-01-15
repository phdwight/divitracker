"""Step definitions for portfolio summary feature."""

from datetime import datetime, timezone

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.extensions import db
from app.models import Dividend, Investment
from app.services.investment_service import InvestmentService
from app.services.portfolio_service import PortfolioService

scenarios("../features/portfolio_summary.feature")


@pytest.fixture
def test_context():
    """Shared context for test state."""
    return {
        "summary": None,
        "investment_ids": {},
    }


# Background
@given("the application is configured for testing")
def app_configured(app):  # pylint: disable=unused-argument
    """Application is configured - app fixture ensures test context."""
    del app  # Ensure fixture is used


# Given steps
@given("no investments exist")
def no_investments(app):
    """Ensure no investments exist."""
    with app.app_context():
        Dividend.query.delete()
        Investment.query.delete()
        db.session.commit()


@given(
    parsers.parse('an investment "{name}" with {amount:d} dollars exists'),
    target_fixture="test_context",
)
def investment_exists(app, name, amount, test_context):
    """Create an investment."""
    with app.app_context():
        investment = Investment(
            name=name,
            ticker=name[:4].upper(),
            total_invested=float(amount),
        )
        db.session.add(investment)
        db.session.commit()
        test_context["investment_ids"][name] = investment.id
        test_context["current_investment_id"] = investment.id
    return test_context


@given(
    parsers.parse(
        "the investment has quarterly dividends of {amount:d} dollars for the current year"
    )
)
def add_quarterly_dividends_current(app, amount, test_context):
    """Add quarterly dividends for current year."""
    current_year = datetime.now(timezone.utc).year
    _add_quarterly_dividends(app, test_context["current_investment_id"], amount, current_year)


@given(
    parsers.parse(
        'the investment "{name}" has quarterly dividends of '
        '{amount:d} dollars for the current year'
    )
)
def add_named_investment_dividends(app, name, amount, test_context):
    """Add quarterly dividends for named investment."""
    current_year = datetime.now(timezone.utc).year
    inv_id = test_context["investment_ids"][name]
    _add_quarterly_dividends(app, inv_id, amount, current_year)


@given(
    parsers.parse(
        'the investment "{name}" has quarterly dividends of '
        '{amount:d} dollars for year {year:d}'
    )
)
def add_named_investment_dividends_year(app, name, amount, year, test_context):
    """Add quarterly dividends for named investment for specific year."""
    inv_id = test_context["investment_ids"][name]
    _add_quarterly_dividends(app, inv_id, amount, year)


def _add_quarterly_dividends(app, investment_id, amount, year):
    """Helper to add quarterly dividends."""
    with app.app_context():
        for month in [3, 6, 9, 12]:
            dividend = Dividend(
                investment_id=investment_id,
                amount=float(amount),
                frequency="quarterly",
                period_month=month,
                period_year=year,
            )
            db.session.add(dividend)
        db.session.commit()


# When steps
@when("I request the portfolio summary", target_fixture="test_context")
def request_summary(app, test_context):
    """Request portfolio summary."""
    with app.app_context():
        investment_service = InvestmentService()
        service = PortfolioService(investment_service)
        test_context["summary"] = service.get_portfolio_summary()
    return test_context


@when(
    parsers.parse("I request the portfolio summary for year {year:d}"),
    target_fixture="test_context"
)
def request_summary_for_year(app, year, test_context):
    """Request portfolio summary for specific year."""
    with app.app_context():
        investment_service = InvestmentService()
        service = PortfolioService(investment_service)
        test_context["summary"] = service.get_portfolio_summary(year=year)
        test_context["year"] = year
    return test_context


# Then steps
@then(parsers.parse("the total invested should be {amount:d} dollars"))
def verify_total_invested(test_context, amount):
    """Verify total invested."""
    assert test_context["summary"].total_invested == float(amount)


@then(parsers.parse("the total annual dividends should be {amount:d} dollars"))
def verify_annual_dividends(test_context, amount):
    """Verify total annual dividends."""
    assert test_context["summary"].total_annual_dividends == float(amount)


@then(parsers.parse("the overall yield should be {yield_pct:f} percent"))
def verify_overall_yield(test_context, yield_pct):
    """Verify overall yield."""
    assert test_context["summary"].overall_yield == pytest.approx(yield_pct, rel=0.01)


@then(
    parsers.parse('the yield calculation should only include the {amount:d} dollars from "{name}"')
)
def verify_yield_investment_amount(app, amount, name, test_context):  # pylint: disable=unused-argument
    """Verify yield calculation uses correct investment amount."""
    # The yield should be calculated only from investments with dividends
    # Total annual dividends / investment amount * 100 = yield
    # If yield is 4% and dividends are from 10000 investment with 400 dividends
    # Note: 'app' fixture needed for Flask context, 'name' used for readability in Gherkin
    assert test_context["summary"].total_investment_for_yield == float(amount)


@then(parsers.parse("the total annual dividends for {year:d} should be {amount:d} dollars"))
def verify_annual_dividends_year(test_context, year, amount):  # pylint: disable=unused-argument
    """Verify total annual dividends for specific year."""
    # Note: 'year' captured from Gherkin for documentation, actual year is baked in test data
    assert test_context["summary"].total_annual_dividends == float(amount)
