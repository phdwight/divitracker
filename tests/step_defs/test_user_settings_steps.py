"""Step definitions for user settings feature."""

import json
import logging
import tempfile
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.settings import (
    CURRENCY_PRESETS,
    DEFAULT_SETTINGS,
    CurrencySettings,
    FormattingSettings,
    PaginationSettings,
    SettingsManager,
    TimezoneSettings,
    UserSettings,
    format_currency,
    get_user_settings,
)

scenarios("../features/user_settings.feature")


@pytest.fixture
def context():
    """Shared context for storing state between steps."""
    return {}


@given("the application is configured for testing", target_fixture="app_context")
def app_configured(app):
    """Set up application context for testing."""
    # Reset global settings manager to ensure fresh settings
    SettingsManager._instance = None
    # Ensure user_settings.json doesn't exist in test environment
    config_path = Path(__file__).parent.parent.parent / "config" / "user_settings.json"
    if config_path.exists():
        config_path.unlink()
    
    with app.app_context():
        yield app


# Currency Settings steps
@when(
    parsers.parse(
        'I create currency settings with code "{code}" symbol "{symbol}" and name "{name}"'
    )
)
def create_currency_settings(context, code, symbol, name):
    """Create currency settings."""
    context["currency_settings"] = CurrencySettings(code=code, symbol=symbol, name=name)


@then(parsers.parse('the currency code should be "{expected}"'))
def check_currency_code(context, expected):
    """Check currency code."""
    if context.get("currency_settings"):
        assert context["currency_settings"].code == expected
    elif context.get("user_settings"):
        assert context["user_settings"].currency.code == expected
    elif context.get("settings"):
        assert context["settings"].currency.code == expected
    elif context.get("global_settings"):
        assert context["global_settings"].currency.code == expected
    else:
        raise ValueError("No settings found in context")


@then(parsers.parse('the currency symbol should be "{expected}"'))
def check_currency_symbol(context, expected):
    """Check currency symbol."""
    if context.get("currency_settings"):
        assert context["currency_settings"].symbol == expected
    elif context.get("user_settings"):
        assert context["user_settings"].currency.symbol == expected
    elif context.get("settings"):
        assert context["settings"].currency.symbol == expected
    else:
        raise ValueError("No settings found in context")


@then(parsers.parse('the currency name should be "{expected}"'))
def check_currency_name(context, expected):
    """Check currency name."""
    if context.get("currency_settings"):
        assert context["currency_settings"].name == expected
    elif context.get("user_settings"):
        assert context["user_settings"].currency.name == expected
    elif context.get("settings"):
        assert context["settings"].currency.name == expected
    else:
        raise ValueError("No settings found in context")


# Formatting Settings steps
@when(
    parsers.parse(
        'I create formatting settings with thousands "{thousands}" decimal "{decimal}" and places {places:d}'
    )
)
def create_formatting_settings(context, thousands, decimal, places):
    """Create formatting settings."""
    context["formatting_settings"] = FormattingSettings(
        thousands_separator=thousands,
        decimal_separator=decimal,
        decimal_places=places,
    )


@then(parsers.parse('the thousands separator should be "{expected}"'))
def check_thousands_separator(context, expected):
    """Check thousands separator."""
    assert context["formatting_settings"].thousands_separator == expected


@then(parsers.parse('the decimal separator should be "{expected}"'))
def check_decimal_separator(context, expected):
    """Check decimal separator."""
    assert context["formatting_settings"].decimal_separator == expected


@then(parsers.parse("the decimal places should be {expected:d}"))
def check_decimal_places(context, expected):
    """Check decimal places."""
    assert context["formatting_settings"].decimal_places == expected


# Timezone Settings steps
@when(parsers.parse('I create timezone settings with offset {offset:d} and name "{name}"'))
def create_timezone_settings(context, offset, name):
    """Create timezone settings."""
    context["timezone_settings"] = TimezoneSettings(offset_hours=offset, name=name)


@then(parsers.parse("the timezone offset should be {expected:d}"))
def check_timezone_offset(context, expected):
    """Check timezone offset."""
    assert context["timezone_settings"].offset_hours == expected


@then(parsers.parse('the timezone name should be "{expected}"'))
def check_timezone_name(context, expected):
    """Check timezone name."""
    assert context["timezone_settings"].name == expected


# Pagination Settings steps
@when(parsers.parse("I create pagination settings with {items:d} items per page"))
def create_pagination_settings(context, items):
    """Create pagination settings."""
    context["pagination_settings"] = PaginationSettings(items_per_page=items)


@then(parsers.parse("the items per page should be {expected:d}"))
def check_items_per_page(context, expected):
    """Check items per page."""
    assert context["pagination_settings"].items_per_page == expected


# User Settings Currency Formatting steps
@given("user settings with PHP currency")
def user_settings_php(context):
    """Create user settings with PHP currency."""
    context["user_settings"] = UserSettings(
        currency=CurrencySettings(code="PHP", symbol="₱", name="Philippine Peso"),
        formatting=FormattingSettings(
            thousands_separator=",", decimal_separator=".", decimal_places=2
        ),
        timezone=TimezoneSettings(offset_hours=8, name="GMT+8"),
        pagination=PaginationSettings(items_per_page=10),
    )


@given("user settings with USD currency")
def user_settings_usd(context):
    """Create user settings with USD currency."""
    context["user_settings"] = UserSettings(
        currency=CurrencySettings(code="USD", symbol="$", name="US Dollar"),
        formatting=FormattingSettings(
            thousands_separator=",", decimal_separator=".", decimal_places=2
        ),
        timezone=TimezoneSettings(offset_hours=-5, name="EST"),
        pagination=PaginationSettings(items_per_page=10),
    )


@given("user settings with EUR currency and European formatting")
def user_settings_eur(context):
    """Create user settings with EUR currency and European formatting."""
    context["user_settings"] = UserSettings(
        currency=CurrencySettings(code="EUR", symbol="€", name="Euro"),
        formatting=FormattingSettings(
            thousands_separator=" ", decimal_separator=",", decimal_places=2
        ),
        timezone=TimezoneSettings(offset_hours=1, name="CET"),
        pagination=PaginationSettings(items_per_page=10),
    )


@given("user settings with JPY currency and no decimals")
def user_settings_jpy(context):
    """Create user settings with JPY currency and no decimals."""
    context["user_settings"] = UserSettings(
        currency=CurrencySettings(code="JPY", symbol="¥", name="Japanese Yen"),
        formatting=FormattingSettings(
            thousands_separator=",", decimal_separator=".", decimal_places=0
        ),
        timezone=TimezoneSettings(offset_hours=9, name="JST"),
        pagination=PaginationSettings(items_per_page=10),
    )


@when(parsers.parse("I format amount {amount:f}"))
def format_amount_float(context, amount):
    """Format amount as float."""
    context["formatted_result"] = context["user_settings"].format_currency(amount)


@when(parsers.parse("I format amount {amount:d}"))
def format_amount_int(context, amount):
    """Format amount as int."""
    context["formatted_result"] = context["user_settings"].format_currency(amount)


@then(parsers.parse('the formatted result should be "{expected}"'))
def check_formatted_result(context, expected):
    """Check formatted result."""
    assert context["formatted_result"] == expected


# Settings Manager steps
@given("no settings file exists")
def no_settings_file(context):
    """Set up non-existent settings file."""
    context["temp_dir"] = tempfile.mkdtemp()
    context["config_path"] = Path(context["temp_dir"]) / "nonexistent" / "settings.json"


@given("a settings file with USD currency exists")
def settings_file_usd(context):
    """Create settings file with USD currency."""
    context["temp_dir"] = tempfile.mkdtemp()
    context["config_path"] = Path(context["temp_dir"]) / "settings.json"
    config_data = {
        "currency": {"code": "USD", "symbol": "$", "name": "US Dollar"},
        "formatting": {"thousands_separator": ",", "decimal_separator": ".", "decimal_places": 2},
    }
    with context["config_path"].open("w", encoding="utf-8") as f:
        json.dump(config_data, f)


@given("a new settings file path")
def new_settings_path(context):
    """Set up new settings file path."""
    context["temp_dir"] = tempfile.mkdtemp()
    context["config_path"] = Path(context["temp_dir"]) / "settings.json"


@given("a settings file with only currency defined")
def settings_file_partial(context):
    """Create settings file with only currency."""
    context["temp_dir"] = tempfile.mkdtemp()
    context["config_path"] = Path(context["temp_dir"]) / "settings.json"
    partial_data = {
        "currency": {"code": "GBP", "symbol": "£", "name": "British Pound"},
    }
    with context["config_path"].open("w", encoding="utf-8") as f:
        json.dump(partial_data, f)


@given("the settings are loaded")
def settings_loaded(context):
    """Load settings."""
    context["manager"] = SettingsManager(context["config_path"])
    context["settings"] = context["manager"].settings


@when("I load settings")
def load_settings(context):
    """Load settings from manager."""
    context["manager"] = SettingsManager(context["config_path"])
    context["settings"] = context["manager"].settings


@when("I save EUR settings")
def save_eur_settings(context):
    """Save EUR settings."""
    context["manager"] = SettingsManager(context["config_path"])
    new_settings = UserSettings(
        currency=CurrencySettings(code="EUR", symbol="€", name="Euro"),
        formatting=FormattingSettings(
            thousands_separator=" ", decimal_separator=",", decimal_places=2
        ),
        timezone=TimezoneSettings(offset_hours=1, name="CET"),
        pagination=PaginationSettings(items_per_page=20),
    )
    context["manager"].save_settings(new_settings)


@when("the file is updated to EUR externally")
def update_file_to_eur(context):
    """Update file to EUR externally."""
    updated_data = {
        "currency": {"code": "EUR", "symbol": "€", "name": "Euro"},
        "formatting": {"thousands_separator": " ", "decimal_separator": ",", "decimal_places": 2},
    }
    with context["config_path"].open("w", encoding="utf-8") as f:
        json.dump(updated_data, f)


@when("I reload settings")
def reload_settings(context):
    """Reload settings."""
    context["settings"] = context["manager"].reload()


@then(parsers.parse('the currency code should be the default "{expected}"'))
def check_default_currency_code(context, expected):
    """Check default currency code."""
    assert context["settings"].currency.code == DEFAULT_SETTINGS["currency"]["code"]


@then(parsers.parse('the currency symbol should be the default "{expected}"'))
def check_default_currency_symbol(context, expected):
    """Check default currency symbol."""
    assert context["settings"].currency.symbol == DEFAULT_SETTINGS["currency"]["symbol"]


@then(parsers.parse('the file should contain currency code "{expected}"'))
def check_file_currency_code(context, expected):
    """Check file contains currency code."""
    with context["config_path"].open("r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert saved_data["currency"]["code"] == expected


@then(parsers.parse('the file should contain currency symbol "{expected}"'))
def check_file_currency_symbol(context, expected):
    """Check file contains currency symbol."""
    with context["config_path"].open("r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert saved_data["currency"]["symbol"] == expected


@then("the currency should be from the file")
def check_currency_from_file(context):
    """Check currency is from file."""
    assert context["settings"].currency.code == "GBP"


@then("the formatting should use defaults")
def check_formatting_defaults(context):
    """Check formatting uses defaults."""
    assert context["settings"].formatting.thousands_separator == ","


# Currency Presets steps
@then(parsers.parse('the PHP preset should have code "{expected}"'))
def check_php_preset_code(expected):
    """Check PHP preset code."""
    assert CURRENCY_PRESETS["PHP"]["code"] == expected


@then(parsers.parse('the PHP preset should have symbol "{expected}"'))
def check_php_preset_symbol(expected):
    """Check PHP preset symbol."""
    assert CURRENCY_PRESETS["PHP"]["symbol"] == expected


@then(parsers.parse('the PHP preset should have name "{expected}"'))
def check_php_preset_name(expected):
    """Check PHP preset name."""
    assert CURRENCY_PRESETS["PHP"]["name"] == expected


@then(parsers.parse('the preset "{code}" should exist'))
def check_preset_exists(code):
    """Check preset exists."""
    assert code in CURRENCY_PRESETS


# Global Functions steps
@when(parsers.parse("I use the global format_currency function with {amount:f}"))
def use_global_format_currency(context, app_context, amount):
    """Use global format_currency function."""
    context["global_result"] = format_currency(amount)


@when("I use the global get_user_settings function")
def use_global_get_user_settings(context, app_context):
    """Use global get_user_settings function."""
    context["global_settings"] = get_user_settings()


@then(parsers.parse('the result should contain "{expected}"'))
def check_result_contains(context, expected):
    """Check result contains string."""
    assert expected in context["global_result"]


@then(parsers.parse('the result should contain "{opt1}" or "{opt2}"'))
def check_result_contains_either(context, opt1, opt2):
    """Check result contains either string."""
    assert opt1 in context["global_result"] or opt2 in context["global_result"]


@then("the settings should be UserSettings type")
def check_settings_type(context):
    """Check settings type."""
    assert isinstance(context["global_settings"], UserSettings)


@pytest.fixture(autouse=True)
def cleanup_temp_dir(context):
    """Clean up temporary directory after tests."""
    yield
    if context.get("temp_dir"):
        import shutil

        try:
            shutil.rmtree(context["temp_dir"])
        except FileNotFoundError:
            # The temporary directory may have already been removed by the test; ignore.
            logging.getLogger(__name__).debug(
                "Temporary directory %s already removed during cleanup",
                context["temp_dir"],
            )
