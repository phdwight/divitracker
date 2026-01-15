"""Step definitions for edge cases feature."""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from werkzeug.exceptions import InternalServerError, Forbidden, BadRequest

from app.factory import create_app
from app.extensions import db
from app.models import Investment, Dividend
from app.settings import SettingsManager, DEFAULT_SETTINGS


scenarios("../features/edge_cases.feature")


@pytest.fixture
def app():
    """Create and configure test application."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def context():
    """Shared context for test data."""
    return {}


# =============================================================================
# Given Steps - Application & Investment Setup
# =============================================================================

@given("the application is running")
def app_running(app, client):  # pylint: disable=unused-argument
    """Ensure app is running."""
    # Fixtures are requested via function arguments; no additional action needed.


@given(parsers.parse('an investment "{name}" with ticker "{ticker}" and amount {amount:d} exists'))
def create_investment_with_amount(app, context, name, ticker, amount):  # pylint: disable=unused-argument
    """Create an investment with specified amount."""
    del app  # Required for Flask context
    inv = Investment(name=name, ticker=ticker, total_invested=float(amount))
    db.session.add(inv)
    db.session.commit()
    context["investment_id"] = inv.id
    context["investment_name"] = name


@given(parsers.parse('an investment "{name}" with ticker "{ticker}" exists'))
def create_investment(app, context, name, ticker):  # pylint: disable=unused-argument
    """Create an investment without amount."""
    del app  # Required for Flask context
    inv = Investment(name=name, ticker=ticker, total_invested=10000.0)
    db.session.add(inv)
    db.session.commit()
    context[f"investment_{name}_id"] = inv.id
    context["investment_id"] = inv.id
    context["investment_name"] = name


# =============================================================================
# Given Steps - Dividend Creation (Parameterized)
# =============================================================================

@given(
    parsers.re(
        r'a (?P<frequency>quarterly|monthly|yearly|semi-annual) dividend of '
        r'(?P<amount>\d+) for "(?P<inv_name>[^"]+)" with period month (?P<month>\d+) '
        r'and year (?P<year>\d+)'
    )
)
def create_dividend_with_month(  # pylint: disable=too-many-positional-arguments,unused-argument
    app, context, frequency, amount, inv_name, month, year
):
    """Create a dividend with specific period (parameterized by frequency)."""
    del app  # Required for Flask context
    inv = Investment.query.filter_by(name=inv_name).first()
    div = Dividend(
        investment_id=inv.id,
        amount=float(amount),
        frequency=frequency,
        period_month=int(month),
        period_year=int(year),
    )
    db.session.add(div)
    db.session.commit()
    context["dividend_id"] = div.id


@given(
    parsers.re(
        r'a (?P<frequency>quarterly|monthly|yearly|semi-annual) dividend of '
        r'(?P<amount>\d+) for "(?P<inv_name>[^"]+)" with period year (?P<year>\d+)'
    )
)
def create_dividend_year_only(  # pylint: disable=too-many-positional-arguments,unused-argument
    app, context, frequency, amount, inv_name, year
):
    """Create a dividend with only year (no month)."""
    del app  # Required for Flask context
    inv = Investment.query.filter_by(name=inv_name).first()
    div = Dividend(
        investment_id=inv.id,
        amount=float(amount),
        frequency=frequency,
        period_month=None,
        period_year=int(year),
    )
    db.session.add(div)
    db.session.commit()
    context["dividend_id"] = div.id


@given(parsers.parse('a dividend without month for "{inv_name}" with year {year:d}'))
def create_dividend_without_month(app, context, inv_name, year):  # pylint: disable=unused-argument
    """Create a dividend without period month."""
    del app  # Required for Flask context
    inv = Investment.query.filter_by(name=inv_name).first()
    div = Dividend(
        investment_id=inv.id,
        amount=100.0,
        frequency="monthly",
        period_month=None,
        period_year=year,
    )
    db.session.add(div)
    db.session.commit()
    context["dividend_id"] = div.id


@given(
    parsers.parse(
        '{count:d} monthly dividends of {amount:d} for "{inv_name}" in year {year:d}'
    )
)
def create_multiple_monthly_dividends(  # pylint: disable=too-many-positional-arguments,unused-argument
    app, context, count, amount, inv_name, year
):
    """Create multiple monthly dividends."""
    del app, context  # Required for Flask context
    inv = Investment.query.filter_by(name=inv_name).first()
    for month in range(1, count + 1):
        div = Dividend(
            investment_id=inv.id,
            amount=float(amount),
            frequency="monthly",
            period_month=month,
            period_year=year,
        )
        db.session.add(div)
    db.session.commit()


@given(parsers.parse('a dividend with unknown frequency for "{inv_name}" in year {year:d}'))
def create_dividend_unknown_frequency(app, context, inv_name, year):  # pylint: disable=unused-argument
    """Create a dividend with an unknown frequency value."""
    del app, context  # Required for Flask context
    inv = Investment.query.filter_by(name=inv_name).first()
    div = Dividend(
        investment_id=inv.id,
        amount=100.0,
        frequency="unknown_freq",
        period_month=6,
        period_year=year,
    )
    db.session.add(div)
    db.session.commit()


# =============================================================================
# Given Steps - Settings Edge Cases
# =============================================================================

@given("a corrupted settings file exists")
def corrupted_settings_file(context):
    """Create a corrupted settings file."""
    context["temp_dir"] = tempfile.mkdtemp()
    context["settings_path"] = Path(context["temp_dir"]) / "user_settings.json"
    with open(context["settings_path"], "w", encoding="utf-8") as f:
        f.write("{ invalid json }")


@given("settings file is inaccessible")
def inaccessible_settings_file(context):
    """Setup for inaccessible settings file."""
    context["temp_dir"] = tempfile.mkdtemp()
    context["settings_path"] = Path(context["temp_dir"]) / "nonexistent_dir" / "user_settings.json"


# =============================================================================
# When Steps - Navigation
# =============================================================================

@when(parsers.parse('I visit "{url}"'))
def visit_url(client, context, url):
    """Visit a URL."""
    context["response"] = client.get(url)


@when(parsers.parse('I visit the investment "{name}" with page {page:d}'))
def visit_investment_with_page(app, client, context, name, page):  # pylint: disable=unused-argument
    """Visit investment page with specific page number."""
    del app  # Required for Flask context
    inv = Investment.query.filter_by(name=name).first()
    context["response"] = client.get(f"/investments/{inv.id}?page={page}")


@when(parsers.parse('I visit the investment "{name}" with year {year:d}'))
def visit_investment_with_year(app, client, context, name, year):  # pylint: disable=unused-argument
    """Visit investment page with specific year."""
    del app  # Required for Flask context
    inv = Investment.query.filter_by(name=name).first()
    context["response"] = client.get(f"/investments/{inv.id}?year={year}")


@when(parsers.parse('I view the investment "{name}"'))
def view_investment(app, client, context, name):  # pylint: disable=unused-argument
    """View an investment."""
    del app  # Required for Flask context
    inv = Investment.query.filter_by(name=name).first()
    context["response"] = client.get(f"/investments/{inv.id}")


@when(parsers.parse('I filter dividend graph by investment "{name}"'))
def filter_dividend_graph_by_investment(app, client, context, name):  # pylint: disable=unused-argument
    """Filter dividend graph by investment."""
    del app  # Required for Flask context
    inv = Investment.query.filter_by(name=name).first()
    context["response"] = client.get(f"/reports/dividends-chart?investment_id={inv.id}&year=2024")


# =============================================================================
# When Steps - Investment Operations
# =============================================================================

@when(
    parsers.parse(
        'I update investment "{name}" to name "{new_name}" '
        'ticker "{ticker}" and amount "{amount}"'
    )
)
def update_investment(  # pylint: disable=too-many-positional-arguments
    app, client, context, name, new_name, ticker, amount
):
    """Update an investment via POST."""
    del app  # unused but required fixture
    inv = Investment.query.filter_by(name=name).first()
    context["response"] = client.post(
        f"/investments/{inv.id}/edit",
        data={"name": new_name, "ticker": ticker, "amount": amount},
        follow_redirects=True,
    )


@when(parsers.parse("I delete investment with id {investment_id:d}"))
def delete_investment_by_id(client, context, investment_id):
    """Delete investment by ID."""
    context["response"] = client.post(f"/investments/{investment_id}/delete", follow_redirects=True)


# =============================================================================
# When Steps - Admin Settings
# =============================================================================

@when(parsers.parse("I save admin settings with items_per_page {items:d}"))
def save_admin_settings_items_per_page(client, context, items):
    """Save admin settings with specific items_per_page."""
    context["response"] = client.post(
        "/settings/save",
        data={
            "currency_code": "USD",
            "currency_symbol": "$",
            "currency_name": "US Dollar",
            "thousands_separator": ",",
            "decimal_separator": ".",
            "decimal_places": "2",
            "timezone_offset": "0",
            "timezone_name": "UTC",
            "items_per_page": str(items),
        },
        follow_redirects=True,
    )


@when("I save admin settings that causes an exception")
def save_admin_settings_exception(app, client, context):  # pylint: disable=unused-argument
    """Save admin settings that throws an exception."""
    del app  # Required for Flask context
    with patch("app.routes.admin.get_settings_manager") as mock_manager:
        mock_manager.return_value.save_settings.side_effect = Exception("Test error")
        context["response"] = client.post(
            "/settings/save",
            data={
                "currency_code": "USD",
                "currency_symbol": "$",
                "currency_name": "US Dollar",
                "thousands_separator": ",",
                "decimal_separator": ".",
                "decimal_places": "2",
                "timezone_offset": "0",
                "timezone_name": "UTC",
                "items_per_page": "10",
            },
            follow_redirects=True,
        )


# =============================================================================
# When Steps - Dividend Operations
# =============================================================================

@when(
    parsers.parse(
        'I submit dividend with investment_id {inv_id:d} '
        'amount "{amount}" and frequency "{frequency}"'
    )
)
def submit_dividend_invalid_investment(  # pylint: disable=too-many-positional-arguments
    app, client, context, inv_id, amount, frequency
):
    """Submit dividend with invalid investment ID."""
    del app  # unused but required fixture
    context["response"] = client.post(
        "/dividends/new",
        data={"investment_id": str(inv_id), "amount": amount, "frequency": frequency},
        follow_redirects=True,
    )


@when(parsers.parse('I calculate projected yield for "{name}" in year {year:d}'))
def calculate_projected_yield(app, context, name, year):  # pylint: disable=unused-argument
    """Calculate projected yield for investment."""
    del app  # Required for Flask context
    inv = Investment.query.filter_by(name=name).first()
    context["actual_amount"] = inv.calculate_annual_dividends(year)
    context["projected_amount"] = inv.calculate_projected_annual_dividends(year)


@when("I get the period display for the dividend")
def get_period_display(app, context):  # pylint: disable=unused-argument
    """Get period display for a dividend."""
    del app  # Required for Flask context
    div = db.session.get(Dividend, context["dividend_id"])
    context["period_display"] = div.period_label


# =============================================================================
# When Steps - Error Handlers
# =============================================================================

@when("a 500 error occurs")
def trigger_500_error(app, client, context):  # noqa: ARG001
    """Trigger a 500 error."""
    del app, client  # unused but required fixtures
    test_app = create_app("testing")
    with test_app.test_request_context():
        @test_app.route("/trigger-500")
        def trigger_error():
            raise InternalServerError("Test error")
        with test_app.test_client() as test_client:
            context["response"] = test_client.get("/trigger-500")


@when("a 403 error occurs")
def trigger_403_error(app, client, context):  # noqa: ARG001
    """Trigger a 403 error."""
    del app, client  # unused but required fixtures
    test_app = create_app("testing")
    with test_app.app_context():
        @test_app.route("/trigger-403")
        def trigger_forbidden():
            raise Forbidden("Test forbidden")
        with test_app.test_client() as test_client:
            context["response"] = test_client.get("/trigger-403")


@when("a 400 error occurs")
def trigger_400_error(app, client, context):  # noqa: ARG001
    """Trigger a 400 error."""
    del app, client  # unused but required fixtures
    test_app = create_app("testing")
    with test_app.app_context():
        @test_app.route("/trigger-400")
        def trigger_bad_request():
            raise BadRequest("Test bad request")
        with test_app.test_client() as test_client:
            context["response"] = test_client.get("/trigger-400")


@when("I load settings")
def load_settings(context):
    """Load settings from file."""
    manager = SettingsManager(config_path=context["settings_path"])
    context["loaded_settings"] = manager.settings


# =============================================================================
# Then Steps
# =============================================================================

@then(parsers.parse("I should see status code {code:d}"))
def check_status_code(context, code):
    """Check response status code."""
    assert context["response"].status_code == code


@then(parsers.parse('I should see "{text}" in the page'))
def check_text_in_page(context, text):
    """Check if text appears in response."""
    assert text.lower() in context["response"].data.decode().lower()


@then("the projected amount should equal the actual amount")
def check_projected_equals_actual(context):
    """Check that projected amount equals actual."""
    assert context["projected_amount"] == context["actual_amount"]


@then("the projected amount should be calculated")
def check_projected_calculated(context):
    """Check that projected amount was calculated."""
    assert context["projected_amount"] is not None
    assert context["projected_amount"] >= 0


@then(parsers.parse('the period display should be "{expected}"'))
def check_period_display(context, expected):
    """Check period display value."""
    assert context["period_display"] == expected


@then("the settings should be default values")
def check_default_settings(context):
    """Check that loaded settings are defaults."""
    settings = context["loaded_settings"]
    assert settings.currency.code == DEFAULT_SETTINGS["currency"]["code"]
    assert settings.formatting.decimal_places == DEFAULT_SETTINGS["formatting"]["decimal_places"]
