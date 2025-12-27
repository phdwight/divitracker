"""Tests for user settings management."""

import json
import tempfile
from pathlib import Path

from app.settings import (
    CURRENCY_PRESETS,
    DEFAULT_SETTINGS,
    CurrencySettings,
    FormattingSettings,
    SettingsManager,
    TimezoneSettings,
    UserSettings,
    format_currency,
    get_user_settings,
)


class TestCurrencySettings:
    """Tests for CurrencySettings dataclass."""

    def test_create_currency_settings(self) -> None:
        """Test creating currency settings."""
        settings = CurrencySettings(code="PHP", symbol="₱", name="Philippine Peso")
        assert settings.code == "PHP"
        assert settings.symbol == "₱"
        assert settings.name == "Philippine Peso"


class TestFormattingSettings:
    """Tests for FormattingSettings dataclass."""

    def test_create_formatting_settings(self) -> None:
        """Test creating formatting settings."""
        settings = FormattingSettings(
            thousands_separator=",",
            decimal_separator=".",
            decimal_places=2,
        )
        assert settings.thousands_separator == ","
        assert settings.decimal_separator == "."
        assert settings.decimal_places == 2


class TestTimezoneSettings:
    """Tests for TimezoneSettings dataclass."""

    def test_create_timezone_settings(self) -> None:
        """Test creating timezone settings."""
        settings = TimezoneSettings(offset_hours=8, name="GMT+8")
        assert settings.offset_hours == 8
        assert settings.name == "GMT+8"

    def test_create_negative_offset(self) -> None:
        """Test creating timezone with negative offset."""
        settings = TimezoneSettings(offset_hours=-5, name="EST")
        assert settings.offset_hours == -5
        assert settings.name == "EST"


class TestUserSettings:
    """Tests for UserSettings dataclass."""

    def test_format_currency_default(self) -> None:
        """Test formatting currency with default settings."""
        settings = UserSettings(
            currency=CurrencySettings(code="PHP", symbol="₱", name="Philippine Peso"),
            formatting=FormattingSettings(
                thousands_separator=",",
                decimal_separator=".",
                decimal_places=2,
            ),
            timezone=TimezoneSettings(offset_hours=8, name="GMT+8"),
        )
        assert settings.format_currency(1234.56) == "₱1,234.56"
        assert settings.format_currency(0) == "₱0.00"
        assert settings.format_currency(1000000) == "₱1,000,000.00"

    def test_format_currency_usd(self) -> None:
        """Test formatting currency with USD settings."""
        settings = UserSettings(
            currency=CurrencySettings(code="USD", symbol="$", name="US Dollar"),
            formatting=FormattingSettings(
                thousands_separator=",",
                decimal_separator=".",
                decimal_places=2,
            ),
            timezone=TimezoneSettings(offset_hours=-5, name="EST"),
        )
        assert settings.format_currency(1234.56) == "$1,234.56"

    def test_format_currency_european(self) -> None:
        """Test formatting currency with European settings (space thousands, comma decimal)."""
        settings = UserSettings(
            currency=CurrencySettings(code="EUR", symbol="€", name="Euro"),
            formatting=FormattingSettings(
                thousands_separator=" ",
                decimal_separator=",",
                decimal_places=2,
            ),
            timezone=TimezoneSettings(offset_hours=1, name="CET"),
        )
        assert settings.format_currency(1234.56) == "€1 234,56"

    def test_format_currency_no_decimal(self) -> None:
        """Test formatting currency with no decimal places."""
        settings = UserSettings(
            currency=CurrencySettings(code="JPY", symbol="¥", name="Japanese Yen"),
            formatting=FormattingSettings(
                thousands_separator=",",
                decimal_separator=".",
                decimal_places=0,
            ),
            timezone=TimezoneSettings(offset_hours=9, name="JST"),
        )
        assert settings.format_currency(1234) == "¥1,234"


class TestSettingsManager:
    """Tests for SettingsManager class."""

    def test_load_default_settings_when_no_file(self) -> None:
        """Test loading defaults when config file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent" / "settings.json"
            manager = SettingsManager(config_path)

            settings = manager.settings
            assert settings.currency.code == DEFAULT_SETTINGS["currency"]["code"]
            assert settings.currency.symbol == DEFAULT_SETTINGS["currency"]["symbol"]
            assert settings.formatting.thousands_separator == ","

    def test_load_settings_from_file(self) -> None:
        """Test loading settings from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "settings.json"
            config_data = {
                "currency": {
                    "code": "USD",
                    "symbol": "$",
                    "name": "US Dollar",
                },
                "formatting": {
                    "thousands_separator": ",",
                    "decimal_separator": ".",
                    "decimal_places": 2,
                },
            }
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(config_data, f)

            manager = SettingsManager(config_path)
            settings = manager.settings

            assert settings.currency.code == "USD"
            assert settings.currency.symbol == "$"

    def test_save_settings(self) -> None:
        """Test saving settings to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "settings.json"
            manager = SettingsManager(config_path)

            new_settings = UserSettings(
                currency=CurrencySettings(code="EUR", symbol="€", name="Euro"),
                formatting=FormattingSettings(
                    thousands_separator=" ",
                    decimal_separator=",",
                    decimal_places=2,
                ),
                timezone=TimezoneSettings(offset_hours=1, name="CET"),
            )
            manager.save_settings(new_settings)

            # Verify file was created with correct content
            assert config_path.exists()
            with config_path.open("r", encoding="utf-8") as f:
                saved_data = json.load(f)

            assert saved_data["currency"]["code"] == "EUR"
            assert saved_data["currency"]["symbol"] == "€"
            assert saved_data["formatting"]["thousands_separator"] == " "
            assert saved_data["timezone"]["offset_hours"] == 1
            assert saved_data["timezone"]["name"] == "CET"

    def test_reload_settings(self) -> None:
        """Test reloading settings from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "settings.json"

            # Write initial settings
            initial_data = {
                "currency": {
                    "code": "USD",
                    "symbol": "$",
                    "name": "US Dollar",
                },
                "formatting": {
                    "thousands_separator": ",",
                    "decimal_separator": ".",
                    "decimal_places": 2,
                },
            }
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(initial_data, f)

            manager = SettingsManager(config_path)
            assert manager.settings.currency.code == "USD"

            # Update file externally
            updated_data = {
                "currency": {
                    "code": "EUR",
                    "symbol": "€",
                    "name": "Euro",
                },
                "formatting": {
                    "thousands_separator": " ",
                    "decimal_separator": ",",
                    "decimal_places": 2,
                },
            }
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(updated_data, f)

            # Reload and verify
            reloaded = manager.reload()
            assert reloaded.currency.code == "EUR"

    def test_partial_settings_merge_with_defaults(self) -> None:
        """Test that partial settings are merged with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "settings.json"

            # Only provide currency, not formatting
            partial_data = {
                "currency": {
                    "code": "GBP",
                    "symbol": "£",
                    "name": "British Pound",
                },
            }
            with config_path.open("w", encoding="utf-8") as f:
                json.dump(partial_data, f)

            manager = SettingsManager(config_path)
            settings = manager.settings

            # Currency should be from file
            assert settings.currency.code == "GBP"
            # Formatting should use defaults
            assert settings.formatting.thousands_separator == ","


class TestCurrencyPresets:
    """Tests for currency presets."""

    def test_php_preset_exists(self) -> None:
        """Test that PHP preset exists and has correct values."""
        assert "PHP" in CURRENCY_PRESETS
        php = CURRENCY_PRESETS["PHP"]
        assert php["code"] == "PHP"
        assert php["symbol"] == "₱"
        assert php["name"] == "Philippine Peso"

    def test_common_currencies_exist(self) -> None:
        """Test that common currencies are available."""
        expected_currencies = ["PHP", "USD", "EUR", "GBP", "JPY", "CNY"]
        for code in expected_currencies:
            assert code in CURRENCY_PRESETS


class TestGlobalFunctions:
    """Tests for global helper functions."""

    def test_format_currency_function(self, app) -> None:
        """Test the global format_currency function."""
        with app.app_context():
            # Should use default PHP settings
            result = format_currency(1234.56)
            assert "₱" in result
            assert "1,234.56" in result or "1234.56" in result

    def test_get_user_settings_function(self, app) -> None:
        """Test the global get_user_settings function."""
        with app.app_context():
            settings = get_user_settings()
            assert isinstance(settings, UserSettings)
            assert settings.currency.code == "PHP"
