"""Step definitions for web routes feature."""

import re

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.extensions import db
from app.models import Dividend, Investment

scenarios("../features/web_routes.feature")


@pytest.fixture
def context():
    """Shared context for storing state between steps."""
    return {}


@given("the application is configured for testing", target_fixture="app_context")
def app_configured(app):
    """Set up application context for testing."""
    with app.app_context():
        yield app


@given(
    parsers.parse('an investment "{name}" with ticker "{ticker}" exists'),
    target_fixture="investment",
)
def create_investment(app_context, name, ticker):
    """Create an investment."""
    investment = Investment(name=name, ticker=ticker, total_invested=10000.0)
    db.session.add(investment)
    db.session.commit()
    return investment


@given(
    parsers.parse('an investment "{name}" with ticker "{ticker}" and amount {amount:d} exists'),
    target_fixture="investment",
)
def create_investment_with_amount(app_context, name, ticker, amount):
    """Create an investment with specific amount."""
    investment = Investment(name=name, ticker=ticker, total_invested=float(amount))
    db.session.add(investment)
    db.session.commit()
    return investment


@given(parsers.parse('an investment "{name}" with dividends exists'), target_fixture="investment")
def create_investment_with_dividends(app_context, name):
    """Create an investment with dividends."""
    investment = Investment(name=name, ticker="TEST", total_invested=10000.0)
    db.session.add(investment)
    db.session.commit()
    for month in [3, 6, 9, 12]:
        dividend = Dividend(
            investment_id=investment.id,
            amount=50.0,
            frequency="quarterly",
            period_month=month,
            period_year=2025,
        )
        db.session.add(dividend)
    db.session.commit()
    return investment


@when(parsers.parse('I visit "{url}"'), target_fixture="response")
def visit_url(client, url):
    """Visit a URL."""
    return client.get(url)


@when(parsers.parse('I visit "{url}" with redirects'), target_fixture="response")
def visit_url_with_redirects(client, url):
    """Visit a URL with redirects."""
    return client.get(url, follow_redirects=True)


@when(parsers.parse('I view the investment "{name}"'), target_fixture="response")
def view_investment(client, app_context, name):
    """View an investment by name."""
    investment = Investment.query.filter_by(name=name).first()
    return client.get(f"/investments/{investment.id}")


@when(parsers.parse('I visit the edit page for investment "{name}"'), target_fixture="response")
def visit_edit_investment(client, app_context, name):
    """Visit edit page for an investment."""
    investment = Investment.query.filter_by(name=name).first()
    return client.get(f"/investments/{investment.id}/edit")


@when(
    parsers.parse(
        'I submit new investment with name "{name}" ticker "{ticker}" and amount "{amount}"'
    ),
    target_fixture="response",
)
def submit_new_investment(client, name, ticker, amount):
    """Submit a new investment."""
    return client.post(
        "/investments/new",
        data={"name": name, "ticker": ticker, "amount": amount},
        follow_redirects=True,
    )


@when(
    'I submit new investment with name "" ticker "TEST" and amount "1000"',
    target_fixture="response",
)
def submit_new_investment_empty_name(client):
    """Submit a new investment with empty name."""
    return client.post(
        "/investments/new",
        data={"name": "", "ticker": "TEST", "amount": "1000"},
        follow_redirects=True,
    )


@when(
    parsers.parse(
        'I update investment "{name}" to name "{new_name}" ticker "{new_ticker}" and amount "{amount}"'
    ),
    target_fixture="response",
)
def update_investment(client, app_context, name, new_name, new_ticker, amount):
    """Update an investment."""
    investment = Investment.query.filter_by(name=name).first()
    return client.post(
        f"/investments/{investment.id}/edit",
        data={"name": new_name, "ticker": new_ticker, "amount": amount},
        follow_redirects=True,
    )


@when(parsers.parse('I delete investment "{name}"'), target_fixture="response")
def delete_investment(client, app_context, name, context):
    """Delete an investment."""
    investment = Investment.query.filter_by(name=name).first()
    context["deleted_investment_id"] = investment.id
    return client.post(f"/investments/{investment.id}/delete", follow_redirects=True)


@when(parsers.parse('I request "{url}"'), target_fixture="response")
def request_url(client, url):
    """Request a URL."""
    return client.get(url)


@when(
    parsers.parse('I visit add dividend page with preselected investment "{name}"'),
    target_fixture="response",
)
def visit_add_dividend_preselected(client, app_context, name):
    """Visit add dividend page with preselected investment."""
    investment = Investment.query.filter_by(name=name).first()
    return client.get(f"/dividends/new?investment_id={investment.id}")


@when(
    parsers.re(
        r'I submit dividend of "(?P<amount>[^"]+)" with frequency "(?P<frequency>[^"]+)" and notes "(?P<notes>[^"]+)" for "(?P<name>[^"]+)"'
    ),
    target_fixture="response",
)
def submit_dividend(client, app_context, amount, frequency, notes, name, context):
    """Submit a dividend with notes."""
    investment = Investment.query.filter_by(name=name).first()
    context["investment_id"] = investment.id
    return client.post(
        "/dividends/new",
        data={
            "investment_id": str(investment.id),
            "amount": amount,
            "frequency": frequency,
            "notes": notes,
        },
        follow_redirects=True,
    )


@when(
    parsers.re(
        r'I submit dividend of "(?P<amount>[^"]+)" with frequency "(?P<frequency>[^"]+)" for "(?P<name>[^"]+)"'
    ),
    target_fixture="response",
)
def submit_dividend_no_notes(client, app_context, amount, frequency, name, context):
    """Submit a dividend without notes."""
    investment = Investment.query.filter_by(name=name).first()
    context["investment_id"] = investment.id
    return client.post(
        "/dividends/new",
        data={
            "investment_id": str(investment.id),
            "amount": amount,
            "frequency": frequency,
        },
        follow_redirects=True,
    )


@when(
    parsers.parse(
        'I submit dividend of "{amount}" with frequency "{frequency}" without investment'
    ),
    target_fixture="response",
)
def submit_dividend_no_investment(client, amount, frequency):
    """Submit a dividend without investment."""
    return client.post(
        "/dividends/new",
        data={"investment_id": "", "amount": amount, "frequency": frequency},
        follow_redirects=True,
    )


@when(parsers.parse('I delete a dividend for "{name}"'), target_fixture="response")
def delete_dividend(client, app_context, name, context):
    """Delete a dividend."""
    investment = Investment.query.filter_by(name=name).first()
    dividend = Dividend.query.filter_by(investment_id=investment.id).first()
    context["deleted_dividend_id"] = dividend.id
    return client.post(f"/dividends/{dividend.id}/delete", follow_redirects=True)


@when(parsers.parse("I try to delete dividend with ID {div_id:d}"), target_fixture="response")
def try_delete_dividend(client, div_id):
    """Try to delete a dividend by ID."""
    return client.post(f"/dividends/{div_id}/delete", follow_redirects=True)


@when(parsers.parse('I visit the edit page for a dividend of "{name}"'), target_fixture="response")
def visit_edit_dividend(client, app_context, name, context):
    """Visit edit page for a dividend."""
    investment = Investment.query.filter_by(name=name).first()
    dividend = Dividend.query.filter_by(investment_id=investment.id).first()
    context["dividend_id"] = dividend.id
    return client.get(f"/dividends/{dividend.id}/edit")


@when(
    parsers.parse(
        'I update a dividend for "{name}" to amount "{amount}" frequency "{frequency}" and notes "{notes}"'
    ),
    target_fixture="response",
)
def update_dividend(client, app_context, name, amount, frequency, notes, context):
    """Update a dividend."""
    investment = Investment.query.filter_by(name=name).first()
    dividend = Dividend.query.filter_by(investment_id=investment.id).first()
    context["dividend_id"] = dividend.id
    return client.post(
        f"/dividends/{dividend.id}/edit",
        data={
            "amount": amount,
            "frequency": frequency,
            "notes": notes,
            "period_month": "6",
            "period_year": "2025",
        },
        follow_redirects=True,
    )


@when(
    parsers.parse('I update a dividend for "{name}" with invalid amount'), target_fixture="response"
)
def update_dividend_invalid(client, app_context, name, context):
    """Update a dividend with invalid amount."""
    investment = Investment.query.filter_by(name=name).first()
    dividend = Dividend.query.filter_by(investment_id=investment.id).first()
    context["dividend_id"] = dividend.id
    return client.post(
        f"/dividends/{dividend.id}/edit",
        data={"amount": "invalid", "frequency": "monthly"},
        follow_redirects=True,
    )


@when(
    parsers.parse('I update a dividend for "{name}" with investment amount "{inv_amount}"'),
    target_fixture="response",
)
def update_dividend_with_inv_amount(client, app_context, name, inv_amount, context):
    """Update a dividend with investment amount at time."""
    investment = Investment.query.filter_by(name=name).first()
    dividend = Dividend.query.filter_by(investment_id=investment.id).first()
    context["dividend_id"] = dividend.id
    return client.post(
        f"/dividends/{dividend.id}/edit",
        data={
            "amount": "100",
            "frequency": "quarterly",
            "investment_amount_at_time": inv_amount,
            "period_month": "3",
            "period_year": "2025",
        },
        follow_redirects=True,
    )


@then(parsers.parse("I should see status code {code:d}"))
def check_status_code(response, code):
    """Check response status code."""
    assert response.status_code == code


@then(parsers.parse('I should see "{text}" in the page'))
def check_text_in_page(response, text):
    """Check text is in the page."""
    assert text.encode() in response.data or text.lower().encode() in response.data.lower()


@then("I should see navigation to dashboard")
def check_navigation_to_dashboard(response):
    """Check navigation to dashboard exists."""
    assert b"Dashboard" in response.data or b'href="/"' in response.data


@then(
    parsers.parse(
        'the investment "{name}" should exist with ticker "{ticker}" and amount {amount:d}'
    )
)
def check_investment_exists(app_context, name, ticker, amount):
    """Check investment exists with values."""
    investment = Investment.query.filter_by(name=name).first()
    assert investment is not None
    assert investment.ticker == ticker
    assert investment.total_invested == float(amount)


@then(parsers.parse('the investment "{name}" should have total {total:d}'))
def check_investment_total(app_context, name, total):
    """Check investment total."""
    investment = Investment.query.filter_by(name=name).first()
    assert investment.total_invested == float(total)


@then(parsers.parse('the investment "{name}" should not exist'))
def check_investment_not_exists(app_context, name):
    """Check investment does not exist."""
    investment = Investment.query.filter_by(name=name).first()
    assert investment is None


@then(parsers.parse('I should get JSON with investment "{name}"'))
def check_json_investment(response, name):
    """Check JSON contains investment."""
    data = response.get_json()
    assert len(data) >= 1
    assert any(inv["name"] == name for inv in data)


@then(parsers.parse('the dividend should exist with amount {amount:d} and frequency "{frequency}"'))
def check_dividend_exists(app_context, context, amount, frequency):
    """Check dividend exists."""
    dividend = Dividend.query.filter_by(investment_id=context["investment_id"]).first()
    assert dividend is not None
    assert dividend.amount == float(amount)
    assert dividend.frequency == frequency


@then(parsers.parse("the dividend should have investment amount at time {amount:d}"))
def check_dividend_inv_amount(app_context, context, amount):
    """Check dividend investment amount at time."""
    dividend = db.session.get(Dividend, context["dividend_id"])
    assert dividend.investment_amount_at_time == float(amount)


@then("the page should contain version in footer")
def check_version_in_footer(response):
    """Check version is present in footer."""
    data = response.data.decode("utf-8")
    # Check that the footer contains "Version" followed by either a version number or "dev"
    assert "Version" in data
    # Use a regex to verify the version format (v1.2.3 or dev)
    pattern = r"Version (v\d+\.\d+\.\d+|dev)"
    assert re.search(pattern, data), "Footer should contain 'Version' followed by a version number or 'dev'"
