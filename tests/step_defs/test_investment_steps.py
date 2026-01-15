"""Step definitions for investment management feature."""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.exceptions import NotFoundError, ValidationError
from app.extensions import db
from app.models import Investment
from app.services.investment_service import InvestmentService

scenarios("../features/investment_management.feature")


@pytest.fixture
def context():
    """Shared context for test state."""
    return {
        "investment": None,
        "investments": [],
        "error": None,
        "created": None,
    }


# Background
@given("the application is configured for testing")
def app_configured(app):
    """Application is configured."""
    pass


# Given steps
@given("no investments exist")
def no_investments(app):
    """Ensure no investments exist."""
    with app.app_context():
        Investment.query.delete()
        db.session.commit()


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
    return context


# When steps
@when(
    parsers.parse('I create an investment named "{name}" with ticker "{ticker}" and {amount:d} dollars'),
    target_fixture="context",
)
def create_investment(app, name, ticker, amount, context):
    """Create or update an investment."""
    with app.app_context():
        service = InvestmentService()
        investment, created = service.create_or_update_investment(
            name=name, ticker=ticker, amount_str=str(amount)
        )
        context["investment"] = investment
        context["investment_id"] = investment.id
        context["created"] = created
    return context


@when(
    parsers.parse("I try to create an investment with empty name and {amount:d} dollars"),
    target_fixture="context",
)
def try_create_empty_name(app, amount, context):
    """Try to create investment with empty name."""
    with app.app_context():
        service = InvestmentService()
        try:
            service.create_or_update_investment(name="", ticker="TEST", amount_str=str(amount))
        except ValidationError as e:
            context["error"] = str(e)
    return context


@when(
    parsers.parse('I try to create an investment named "{name}" with invalid amount "{amount}"'),
    target_fixture="context",
)
def try_create_invalid_amount(app, name, amount, context):
    """Try to create investment with invalid amount."""
    with app.app_context():
        service = InvestmentService()
        try:
            service.create_or_update_investment(name=name, ticker="TEST", amount_str=amount)
        except ValidationError as e:
            context["error"] = str(e)
    return context


@when(
    parsers.parse('I try to create an investment named "{name}" with amount "{amount}"'),
    target_fixture="context",
)
def try_create_negative_amount(app, name, amount, context):
    """Try to create investment with specific amount string."""
    with app.app_context():
        service = InvestmentService()
        try:
            service.create_or_update_investment(name=name, ticker="TEST", amount_str=amount)
        except ValidationError as e:
            context["error"] = str(e)
    return context


@when(
    parsers.parse('I update the investment to name "{name}" ticker "{ticker}" and amount {amount:d}'),
    target_fixture="context",
)
def update_investment(app, name, ticker, amount, context):
    """Update investment details."""
    with app.app_context():
        service = InvestmentService()
        investment = service.update_investment(
            investment_id=context["investment_id"],
            name=name,
            ticker=ticker,
            total_invested_str=str(amount),
        )
        context["investment"] = investment
    return context


@when(parsers.parse('I delete the investment "{name}"'))
def delete_investment(app, name, context):
    """Delete an investment."""
    with app.app_context():
        service = InvestmentService()
        investment = service.get_investment_by_name(name)
        service.delete_investment(investment.id)


@when(
    parsers.parse("I try to delete an investment with ID {inv_id:d}"),
    target_fixture="context",
)
def try_delete_nonexistent(app, inv_id, context):
    """Try to delete non-existent investment."""
    with app.app_context():
        service = InvestmentService()
        try:
            service.delete_investment(inv_id)
        except NotFoundError as e:
            context["error"] = str(e)
    return context


@when(parsers.parse('I view the investment "{name}"'), target_fixture="context")
def view_investment(app, name, context):
    """View investment details."""
    with app.app_context():
        service = InvestmentService()
        investment = service.get_investment_by_name(name)
        context["investment"] = investment
        context["investment_id"] = investment.id
    return context


@when("I list all investments", target_fixture="context")
def list_investments(app, context):
    """List all investments."""
    with app.app_context():
        service = InvestmentService()
        context["investments"] = list(service.get_all_investments())
    return context


# Then steps
@then("the investment should be created successfully")
def investment_created(context):
    """Verify investment was created."""
    assert context["created"] is True


@then(parsers.parse('the investment "{name}" should have {amount:d} dollars invested'))
def verify_investment_amount(app, name, amount):
    """Verify investment amount."""
    with app.app_context():
        service = InvestmentService()
        investment = service.get_investment_by_name(name)
        assert investment.total_invested == float(amount)


@then(parsers.parse('I should see a validation error containing "{text}"'))
def verify_validation_error(context, text):
    """Verify validation error."""
    assert context["error"] is not None
    assert text.lower() in context["error"].lower()


@then("I should see a not found error")
def verify_not_found_error(context):
    """Verify not found error."""
    assert context["error"] is not None


@then(parsers.parse('the investment should be named "{name}"'))
def verify_name(app, name, context):
    """Verify investment name."""
    with app.app_context():
        investment = db.session.get(Investment, context["investment_id"])
        assert investment.name == name


@then(parsers.parse('the investment should have ticker "{ticker}"'))
def verify_ticker(app, ticker, context):
    """Verify investment ticker."""
    with app.app_context():
        investment = db.session.get(Investment, context["investment_id"])
        assert investment.ticker == ticker


@then(parsers.parse("the investment should have {amount:d} dollars invested"))
def verify_amount(app, amount, context):
    """Verify investment amount."""
    with app.app_context():
        investment = db.session.get(Investment, context["investment_id"])
        assert investment.total_invested == float(amount)


@then(parsers.parse('the investment "{name}" should no longer exist'))
def verify_deleted(app, name):
    """Verify investment was deleted."""
    with app.app_context():
        service = InvestmentService()
        investment = service.get_investment_by_name(name)
        assert investment is None


@then(parsers.parse('I should see investment name "{name}"'))
def verify_view_name(context, name):
    """Verify viewed investment name."""
    assert context["investment"].name == name


@then(parsers.parse('I should see ticker "{ticker}"'))
def verify_view_ticker(context, ticker):
    """Verify viewed investment ticker."""
    assert context["investment"].ticker == ticker


@then(parsers.parse("I should see total invested of {amount:d} dollars"))
def verify_view_amount(context, amount):
    """Verify viewed investment amount."""
    assert context["investment"].total_invested == float(amount)


@then(parsers.parse("I should see {count:d} investments"))
def verify_count(context, count):
    """Verify investment count."""
    assert len(context["investments"]) == count


@then(parsers.parse('I should see investment "{name}" in the list'))
def verify_in_list(context, name):
    """Verify investment is in list."""
    names = [inv.name for inv in context["investments"]]
    assert name in names
