"""Step definitions for dividend recording feature."""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.exceptions import NotFoundError, ValidationError
from app.extensions import db
from app.models import Dividend, Investment
from app.services.dividend_service import DividendService
from app.services.investment_service import InvestmentService
from app.utils import DividendData

scenarios("../features/dividend_recording.feature")


@pytest.fixture
def context():
    """Shared context for test state."""
    return {
        "dividend": None,
        "dividend_id": None,
        "investment_id": None,
        "error": None,
    }


# Background
@given("the application is configured for testing")
def app_configured(app):
    """Application is configured."""
    pass


@given(
    parsers.parse('an investment "{name}" with ticker "{ticker}" and {amount:d} dollars exists'),
    target_fixture="context",
)
def investment_exists(app, name, ticker, amount, context):
    """Create an investment."""
    with app.app_context():
        investment = Investment(name=name, ticker=ticker, total_invested=float(amount))
        db.session.add(investment)
        db.session.commit()
        context["investment_id"] = investment.id
        context["investment_name"] = name
    return context


# Given steps for dividends
@given(
    parsers.parse(
        'a dividend of {amount:d} dollars with frequency "{frequency}" exists for "{inv_name}"'
    ),
    target_fixture="context",
)
def dividend_exists(app, amount, frequency, inv_name, context):
    """Create a dividend for an investment."""
    with app.app_context():
        service = InvestmentService()
        investment = service.get_investment_by_name(inv_name)
        dividend_service = DividendService()
        data = DividendData(amount_str=str(amount), frequency=frequency)
        dividend, _ = dividend_service.create_dividend(
            investment_id_str=str(investment.id),
            data=data,
        )
        context["dividend_id"] = dividend.id
        context["investment_id"] = investment.id
    return context


# When steps
@when(
    parsers.re(
        r'I record a dividend of (?P<amount>\d+) dollars with frequency "(?P<frequency>[^"]+)" and notes "(?P<notes>[^"]+)" for "(?P<inv_name>[^"]+)"'
    ),
    target_fixture="context",
)
def record_dividend_with_notes(app, amount, frequency, notes, inv_name, context):
    """Record a dividend with notes."""
    with app.app_context():
        service = InvestmentService()
        investment = service.get_investment_by_name(inv_name)
        dividend_service = DividendService()
        data = DividendData(amount_str=str(amount), frequency=frequency, notes=notes)
        dividend, _ = dividend_service.create_dividend(
            investment_id_str=str(investment.id),
            data=data,
        )
        context["dividend"] = dividend
        context["dividend_id"] = dividend.id
    return context


@when(
    parsers.re(
        r'I record a dividend of (?P<amount>\d+) dollars with frequency "(?P<frequency>[^"]+)" for "(?P<inv_name>[^"]+)"'
    ),
    target_fixture="context",
)
def record_dividend(app, amount, frequency, inv_name, context):
    """Record a dividend."""
    with app.app_context():
        service = InvestmentService()
        investment = service.get_investment_by_name(inv_name)
        dividend_service = DividendService()
        data = DividendData(amount_str=str(amount), frequency=frequency)
        dividend, _ = dividend_service.create_dividend(
            investment_id_str=str(investment.id),
            data=data,
        )
        context["dividend"] = dividend
        context["dividend_id"] = dividend.id
    return context


@when(
    parsers.parse(
        'I record a dividend of {amount:d} dollars with frequency "{frequency}" and investment balance {balance:d} for "{inv_name}"'
    ),
    target_fixture="context",
)
def record_dividend_with_balance(app, amount, frequency, balance, inv_name, context):
    """Record a dividend with investment amount at time."""
    with app.app_context():
        service = InvestmentService()
        investment = service.get_investment_by_name(inv_name)
        dividend_service = DividendService()
        data = DividendData(
            amount_str=str(amount),
            frequency=frequency,
            investment_amount_at_time_str=str(balance),
        )
        dividend, _ = dividend_service.create_dividend(
            investment_id_str=str(investment.id),
            data=data,
        )
        context["dividend"] = dividend
        context["dividend_id"] = dividend.id
    return context


@when(
    parsers.parse(
        'I try to record a dividend of {amount:d} dollars with frequency "{frequency}" without an investment'
    ),
    target_fixture="context",
)
def try_record_without_investment(app, amount, frequency, context):
    """Try to record dividend without investment."""
    with app.app_context():
        dividend_service = DividendService()
        try:
            data = DividendData(amount_str=str(amount), frequency=frequency)
            dividend_service.create_dividend(
                investment_id_str="",
                data=data,
            )
        except ValidationError as e:
            context["error"] = str(e)
    return context


@when(
    parsers.parse(
        'I try to record a dividend of {amount:d} dollars with frequency "{frequency}" for "{inv_name}"'
    ),
    target_fixture="context",
)
def try_record_dividend(app, amount, frequency, inv_name, context):
    """Try to record a dividend (may fail validation)."""
    with app.app_context():
        service = InvestmentService()
        investment = service.get_investment_by_name(inv_name)
        dividend_service = DividendService()
        try:
            data = DividendData(amount_str=str(amount), frequency=frequency)
            dividend, _ = dividend_service.create_dividend(
                investment_id_str=str(investment.id),
                data=data,
            )
            context["dividend"] = dividend
        except ValidationError as e:
            context["error"] = str(e)
    return context


@when(
    parsers.parse("I try to record a dividend of {amount:d} dollars for investment ID {inv_id:d}"),
    target_fixture="context",
)
def try_record_for_nonexistent(app, amount, inv_id, context):
    """Try to record dividend for non-existent investment."""
    with app.app_context():
        dividend_service = DividendService()
        try:
            data = DividendData(amount_str=str(amount), frequency="monthly")
            dividend_service.create_dividend(
                investment_id_str=str(inv_id),
                data=data,
            )
        except NotFoundError as e:
            context["error"] = str(e)
    return context


@when(
    parsers.parse('I update the dividend to {amount:d} dollars with frequency "{frequency}"'),
    target_fixture="context",
)
def update_dividend(app, amount, frequency, context):
    """Update dividend amount and frequency."""
    with app.app_context():
        dividend_service = DividendService()
        data = DividendData(amount_str=str(amount), frequency=frequency)
        dividend = dividend_service.update_dividend(
            dividend_id=context["dividend_id"],
            data=data,
        )
        context["dividend"] = dividend
    return context


@when(
    parsers.parse("I update the dividend with period month {month:d} and year {year:d}"),
    target_fixture="context",
)
def update_dividend_period(app, month, year, context):
    """Update dividend period information."""
    with app.app_context():
        dividend_service = DividendService()
        dividend = db.session.get(Dividend, context["dividend_id"])
        data = DividendData(
            amount_str=str(dividend.amount),
            frequency=dividend.frequency,
            period_month_str=str(month),
            period_year_str=str(year),
        )
        updated = dividend_service.update_dividend(
            dividend_id=context["dividend_id"],
            data=data,
        )
        context["dividend"] = updated
    return context


@when("I delete the dividend")
def delete_dividend(app, context):
    """Delete the dividend."""
    with app.app_context():
        dividend_service = DividendService()
        dividend_service.delete_dividend(context["dividend_id"])


@when(
    parsers.parse("I try to delete a dividend with ID {div_id:d}"),
    target_fixture="context",
)
def try_delete_nonexistent_dividend(app, div_id, context):
    """Try to delete non-existent dividend."""
    with app.app_context():
        dividend_service = DividendService()
        try:
            dividend_service.delete_dividend(div_id)
        except NotFoundError as e:
            context["error"] = str(e)
    return context


# Then steps
@then("the dividend should be recorded successfully")
def dividend_recorded(context):
    """Verify dividend was recorded."""
    assert context["dividend"] is not None
    assert context["dividend_id"] is not None


@then(parsers.parse("the dividend should have amount {amount:d} dollars"))
def verify_dividend_amount(app, amount, context):
    """Verify dividend amount."""
    with app.app_context():
        dividend = db.session.get(Dividend, context["dividend_id"])
        assert dividend.amount == float(amount)


@then(parsers.parse('the dividend should have frequency "{frequency}"'))
def verify_dividend_frequency(app, frequency, context):
    """Verify dividend frequency."""
    with app.app_context():
        dividend = db.session.get(Dividend, context["dividend_id"])
        assert dividend.frequency == frequency


@then(parsers.parse('the dividend notes should be "{notes}"'))
def verify_dividend_notes(app, notes, context):
    """Verify dividend notes."""
    with app.app_context():
        dividend = db.session.get(Dividend, context["dividend_id"])
        assert dividend.notes == notes


@then(parsers.parse("the dividend investment amount at time should be {amount:d} dollars"))
def verify_investment_at_time(app, amount, context):
    """Verify investment amount at time."""
    with app.app_context():
        dividend = db.session.get(Dividend, context["dividend_id"])
        assert dividend.investment_amount_at_time == float(amount)


@then(parsers.parse("the dividend yield at time should be {yield_pct:f} percent"))
def verify_yield_at_time(app, yield_pct, context):
    """Verify yield at time."""
    with app.app_context():
        dividend = db.session.get(Dividend, context["dividend_id"])
        assert dividend.yield_at_time == pytest.approx(yield_pct, rel=0.01)


@then(parsers.parse('I should see a validation error containing "{text}"'))
def verify_validation_error(context, text):
    """Verify validation error."""
    assert context["error"] is not None
    assert text.lower() in context["error"].lower()


@then("I should see a not found error")
def verify_not_found(context):
    """Verify not found error."""
    assert context["error"] is not None


@then(parsers.parse("the dividend period month should be {month:d}"))
def verify_period_month(app, month, context):
    """Verify period month."""
    with app.app_context():
        dividend = db.session.get(Dividend, context["dividend_id"])
        assert dividend.period_month == month


@then(parsers.parse("the dividend period year should be {year:d}"))
def verify_period_year(app, year, context):
    """Verify period year."""
    with app.app_context():
        dividend = db.session.get(Dividend, context["dividend_id"])
        assert dividend.period_year == year


@then("the dividend should no longer exist")
def verify_dividend_deleted(app, context):
    """Verify dividend was deleted."""
    with app.app_context():
        dividend = db.session.get(Dividend, context["dividend_id"])
        assert dividend is None


@then(parsers.parse("the annualized amount should be {amount:d} dollars"))
def verify_annualized(app, amount, context):
    """Verify annualized amount."""
    with app.app_context():
        dividend = db.session.get(Dividend, context["dividend_id"])
        assert dividend.annualized_amount == float(amount)
