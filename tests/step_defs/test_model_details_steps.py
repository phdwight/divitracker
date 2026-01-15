"""Step definitions for model implementation details feature."""

from datetime import datetime, timezone

import pytest
from pytest_bdd import given, when, then, scenarios, parsers

from app.extensions import db
from app.models import Dividend, DividendFrequency, Investment, InvestmentSummary

scenarios("../features/model_details.feature")


@given("the application is configured for testing", target_fixture="app_context")
def app_configured(app):
    """Set up application context for testing."""
    with app.app_context():
        yield app


# Dividend Frequency steps
@then(parsers.parse("the monthly frequency annual multiplier should be {expected:d}"))
def check_monthly_multiplier(expected):
    """Check monthly frequency multiplier."""
    assert DividendFrequency.MONTHLY.annual_multiplier == expected


@then(parsers.parse("the quarterly frequency annual multiplier should be {expected:d}"))
def check_quarterly_multiplier(expected):
    """Check quarterly frequency multiplier."""
    assert DividendFrequency.QUARTERLY.annual_multiplier == expected


@then(parsers.parse("the yearly frequency annual multiplier should be {expected:d}"))
def check_yearly_multiplier(expected):
    """Check yearly frequency multiplier."""
    assert DividendFrequency.YEARLY.annual_multiplier == expected


# Investment creation steps
@given(
    parsers.parse('an investment "{name}" with ticker "{ticker}" and {amount:d} dollars exists'),
    target_fixture="investment",
)
def create_investment_with_ticker(app_context, name, ticker, amount):
    """Create an investment with a ticker."""
    investment = Investment(name=name, ticker=ticker, total_invested=float(amount))
    db.session.add(investment)
    db.session.commit()
    return investment


@given(
    parsers.parse('an investment "{name}" without ticker and {amount:d} dollars exists'),
    target_fixture="investment",
)
def create_investment_without_ticker(app_context, name, amount):
    """Create an investment without a ticker."""
    investment = Investment(name=name, total_invested=float(amount))
    db.session.add(investment)
    db.session.commit()
    return investment


# Investment repr steps
@then(parsers.parse('the investment repr should be "{expected}"'))
def check_investment_repr(investment, expected):
    """Check investment string representation."""
    assert repr(investment) == expected


# Investment to_dict steps
@when("I convert the investment to a dictionary", target_fixture="investment_dict")
def convert_investment_to_dict(investment):
    """Convert investment to dictionary."""
    return investment.to_dict()


@then(parsers.parse('the dictionary should have name "{expected}"'))
def check_dict_name(investment_dict, expected):
    """Check dictionary name field."""
    assert investment_dict["name"] == expected


@then(parsers.parse('the dictionary should have ticker "{expected}"'))
def check_dict_ticker(investment_dict, expected):
    """Check dictionary ticker field."""
    assert investment_dict["ticker"] == expected


@then(parsers.parse("the dictionary should have total_invested {expected:d}"))
def check_dict_total_invested(investment_dict, expected):
    """Check dictionary total_invested field."""
    assert investment_dict["total_invested"] == float(expected)


@then("the dictionary should have a created_at field")
def check_dict_created_at(investment_dict):
    """Check dictionary has created_at field."""
    assert "created_at" in investment_dict


# Investment summary steps
@given(
    parsers.parse(
        "the investment has quarterly dividends of {amount:d} dollars for the current year"
    )
)
def add_quarterly_dividends_current_year(investment, amount):
    """Add quarterly dividends for current year."""
    current_year = datetime.now(timezone.utc).year
    for month in [3, 6, 9, 12]:
        dividend = Dividend(
            investment_id=investment.id,
            amount=float(amount),
            frequency="quarterly",
            period_month=month,
            period_year=current_year,
        )
        db.session.add(dividend)
    db.session.commit()


@when("I get the investment summary", target_fixture="summary")
def get_investment_summary(investment):
    """Get investment summary."""
    return investment.get_summary()


@then(parsers.parse("the summary total_invested should be {expected:d}"))
def check_summary_total_invested(summary, expected):
    """Check summary total_invested."""
    assert isinstance(summary, InvestmentSummary)
    assert summary.total_invested == float(expected)


@then(parsers.parse("the summary annual_dividends should be {expected:d}"))
def check_summary_annual_dividends(summary, expected):
    """Check summary annual_dividends."""
    assert summary.annual_dividends == float(expected)


@then(parsers.parse("the summary dividend_yield should be {expected:f}"))
def check_summary_dividend_yield(summary, expected):
    """Check summary dividend_yield."""
    assert summary.dividend_yield == pytest.approx(expected)


@then(parsers.parse("the summary total_received should be {expected:d}"))
def check_summary_total_received(summary, expected):
    """Check summary total_received."""
    assert summary.total_received == float(expected)


# Dividend creation steps - ORDER MATTERS: more specific patterns first
@given(
    parsers.re(
        r'a dividend of (?P<amount>[\d.]+) dollars with frequency "(?P<frequency>[^"]+)" and notes "(?P<notes>[^"]+)" exists for the investment'
    ),
    target_fixture="dividend",
)
def create_dividend_with_notes(investment, amount, frequency, notes):
    """Create a dividend with notes."""
    dividend = Dividend(
        investment_id=investment.id,
        amount=float(amount),
        frequency=frequency,
        notes=notes,
    )
    db.session.add(dividend)
    db.session.commit()
    return dividend


@given(
    parsers.re(
        r'a dividend of (?P<amount>[\d.]+) dollars with frequency "(?P<frequency>[^"]+)" and investment balance (?P<balance>\d+) exists for the investment'
    ),
    target_fixture="dividend",
)
def create_dividend_with_balance(investment, amount, frequency, balance):
    """Create a dividend with investment amount at time."""
    inv_amt = float(balance) if int(balance) > 0 else 0.0
    dividend = Dividend(
        investment_id=investment.id,
        amount=float(amount),
        frequency=frequency,
        investment_amount_at_time=inv_amt if inv_amt > 0 else 0.0,
    )
    db.session.add(dividend)
    db.session.commit()
    return dividend


@given(
    parsers.re(
        r'a dividend of (?P<amount>[\d.]+) dollars with frequency "(?P<frequency>[^"]+)" exists for the investment'
    ),
    target_fixture="dividend",
)
def create_dividend_basic(investment, amount, frequency):
    """Create a basic dividend."""
    amt = float(amount)
    dividend = Dividend(
        investment_id=investment.id,
        amount=amt,
        frequency=frequency,
    )
    db.session.add(dividend)
    db.session.commit()
    return dividend


# Dividend repr steps
@then(parsers.parse('the dividend repr should be "{expected}"'))
def check_dividend_repr(dividend, expected):
    """Check dividend string representation."""
    assert repr(dividend) == expected


# Dividend to_dict steps
@when("I convert the dividend to a dictionary", target_fixture="dividend_dict")
def convert_dividend_to_dict(dividend):
    """Convert dividend to dictionary."""
    return dividend.to_dict()


@then(parsers.parse("the dividend dictionary should have amount {expected:d}"))
def check_dividend_dict_amount(dividend_dict, expected):
    """Check dividend dictionary amount field."""
    assert dividend_dict["amount"] == float(expected)


@then(parsers.parse('the dividend dictionary should have frequency "{expected}"'))
def check_dividend_dict_frequency(dividend_dict, expected):
    """Check dividend dictionary frequency field."""
    assert dividend_dict["frequency"] == expected


@then(parsers.parse('the dividend dictionary should have notes "{expected}"'))
def check_dividend_dict_notes(dividend_dict, expected):
    """Check dividend dictionary notes field."""
    assert dividend_dict["notes"] == expected


@then(parsers.parse("the dividend dictionary should have annualized_amount {expected:d}"))
def check_dividend_dict_annualized(dividend_dict, expected):
    """Check dividend dictionary annualized_amount field."""
    assert dividend_dict["annualized_amount"] == float(expected)


@then("the dividend dictionary should have investment_amount_at_time None")
def check_dividend_dict_inv_amt_none(dividend_dict):
    """Check dividend dictionary investment_amount_at_time is None."""
    assert dividend_dict["investment_amount_at_time"] is None


@then(parsers.parse("the dividend dictionary should have investment_amount_at_time {expected:d}"))
def check_dividend_dict_inv_amt(dividend_dict, expected):
    """Check dividend dictionary investment_amount_at_time field."""
    assert dividend_dict["investment_amount_at_time"] == float(expected)


@then("the dividend dictionary should have yield_at_time None")
def check_dividend_dict_yield_none(dividend_dict):
    """Check dividend dictionary yield_at_time is None."""
    assert dividend_dict["yield_at_time"] is None


@then(parsers.parse("the dividend dictionary should have yield_at_time {expected:f}"))
def check_dividend_dict_yield(dividend_dict, expected):
    """Check dividend dictionary yield_at_time field."""
    assert dividend_dict["yield_at_time"] == pytest.approx(expected)


# Yield at time property steps
@then(parsers.parse("the dividend yield_at_time should be {expected:f}"))
def check_yield_at_time(dividend, expected):
    """Check dividend yield_at_time property."""
    assert dividend.yield_at_time == pytest.approx(expected)


@then("the dividend yield_at_time should be None")
def check_yield_at_time_none(dividend):
    """Check dividend yield_at_time is None."""
    assert dividend.yield_at_time is None


# Cascade delete steps
@when(parsers.parse('I delete the investment "{name}"'))
def delete_investment_by_name(app_context, name, context):
    """Delete an investment by name."""
    investment = Investment.query.filter_by(name=name).first()
    context["dividend_ids"] = [d.id for d in investment.dividends]
    db.session.delete(investment)
    db.session.commit()


@then("the associated dividends should also be deleted")
def check_dividends_deleted(context):
    """Check that associated dividends were cascade deleted."""
    for div_id in context.get("dividend_ids", []):
        assert db.session.get(Dividend, div_id) is None


@pytest.fixture
def context():
    """Shared context for storing state between steps."""
    return {}
