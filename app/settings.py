"""User settings management for currency and formatting preferences."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default settings
DEFAULT_SETTINGS: dict[str, Any] = {
    "currency": {
        "code": "PHP",
        "symbol": "₱",
        "name": "Philippine Peso",
    },
    "formatting": {
        "thousands_separator": ",",
        "decimal_separator": ".",
        "decimal_places": 2,
    },
    "timezone": {
        "offset_hours": 8,
        "name": "GMT+8",
    },
    "pagination": {
        "items_per_page": 10,
    },
}

# Common currency presets
CURRENCY_PRESETS: dict[str, dict[str, str]] = {
    "PHP": {"code": "PHP", "symbol": "₱", "name": "Philippine Peso"},
    "USD": {"code": "USD", "symbol": "$", "name": "US Dollar"},
    "EUR": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "GBP": {"code": "GBP", "symbol": "£", "name": "British Pound"},
    "JPY": {"code": "JPY", "symbol": "¥", "name": "Japanese Yen"},
    "CNY": {"code": "CNY", "symbol": "¥", "name": "Chinese Yuan"},
    "KRW": {"code": "KRW", "symbol": "₩", "name": "South Korean Won"},
    "INR": {"code": "INR", "symbol": "₹", "name": "Indian Rupee"},
    "AUD": {"code": "AUD", "symbol": "A$", "name": "Australian Dollar"},
    "CAD": {"code": "CAD", "symbol": "C$", "name": "Canadian Dollar"},
    "SGD": {"code": "SGD", "symbol": "S$", "name": "Singapore Dollar"},
    "HKD": {"code": "HKD", "symbol": "HK$", "name": "Hong Kong Dollar"},
    "MYR": {"code": "MYR", "symbol": "RM", "name": "Malaysian Ringgit"},
    "THB": {"code": "THB", "symbol": "฿", "name": "Thai Baht"},
    "IDR": {"code": "IDR", "symbol": "Rp", "name": "Indonesian Rupiah"},
    "VND": {"code": "VND", "symbol": "₫", "name": "Vietnamese Dong"},
}


@dataclass
class CurrencySettings:
    """Currency configuration."""

    code: str
    symbol: str
    name: str


@dataclass
class FormattingSettings:
    """Number formatting configuration."""

    thousands_separator: str
    decimal_separator: str
    decimal_places: int


@dataclass
class TimezoneSettings:
    """Timezone configuration."""

    offset_hours: int
    name: str


@dataclass
class PaginationSettings:
    """Pagination configuration."""

    items_per_page: int


@dataclass
class UserSettings:
    """Complete user settings."""

    currency: CurrencySettings
    formatting: FormattingSettings
    timezone: TimezoneSettings
    pagination: PaginationSettings

    def format_currency(self, amount: float) -> str:
        """
        Format a number as currency with proper formatting.

        Args:
            amount: The amount to format.

        Returns:
            Formatted currency string.
        """
        # Format the number with decimal places
        formatted_number = f"{amount:,.{self.formatting.decimal_places}f}"

        # Replace separators if needed
        if self.formatting.thousands_separator != ",":
            # Temporarily replace comma with placeholder
            formatted_number = formatted_number.replace(",", "THOUSANDS")
            formatted_number = formatted_number.replace(".", "DECIMAL")
            formatted_number = formatted_number.replace(
                "THOUSANDS", self.formatting.thousands_separator
            )
            formatted_number = formatted_number.replace(
                "DECIMAL", self.formatting.decimal_separator
            )
        elif self.formatting.decimal_separator != ".":
            formatted_number = formatted_number.replace(".", self.formatting.decimal_separator)

        return f"{self.currency.symbol}{formatted_number}"


class SettingsManager:
    """Manager for loading and saving user settings."""

    def __init__(self, config_path: Path | None = None) -> None:
        """
        Initialize settings manager.

        Args:
            config_path: Path to user settings JSON file.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "user_settings.json"
        self._config_path = config_path
        self._settings: UserSettings | None = None

    @property
    def settings(self) -> UserSettings:
        """Get current user settings, loading if necessary."""
        if self._settings is None:
            self._settings = self._load_settings()
        return self._settings

    def _load_settings(self) -> UserSettings:
        """
        Load settings from JSON file or return defaults.

        Returns:
            UserSettings instance.
        """
        # Deep copy defaults to avoid mutating the original
        import copy

        settings_dict = copy.deepcopy(DEFAULT_SETTINGS)

        if self._config_path.exists():
            try:
                with self._config_path.open("r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # Deep merge with defaults
                    for key in settings_dict:
                        if key in loaded:
                            if isinstance(settings_dict[key], dict):
                                settings_dict[key].update(loaded[key])
                            else:
                                settings_dict[key] = loaded[key]
                logger.info("Loaded user settings from %s", self._config_path)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(
                    "Failed to load settings from %s, using defaults: %s",
                    self._config_path,
                    e,
                )

        return UserSettings(
            currency=CurrencySettings(**settings_dict["currency"]),
            formatting=FormattingSettings(**settings_dict["formatting"]),
            timezone=TimezoneSettings(**settings_dict["timezone"]),
            pagination=PaginationSettings(**settings_dict["pagination"]),
        )

    def save_settings(self, settings: UserSettings) -> None:
        """
        Save settings to JSON file.

        Args:
            settings: UserSettings to save.
        """
        settings_dict = {
            "currency": {
                "code": settings.currency.code,
                "symbol": settings.currency.symbol,
                "name": settings.currency.name,
            },
            "formatting": {
                "thousands_separator": settings.formatting.thousands_separator,
                "decimal_separator": settings.formatting.decimal_separator,
                "decimal_places": settings.formatting.decimal_places,
            },
            "timezone": {
                "offset_hours": settings.timezone.offset_hours,
                "name": settings.timezone.name,
            },
            "pagination": {
                "items_per_page": settings.pagination.items_per_page,
            },
        }

        # Ensure config directory exists
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        with self._config_path.open("w", encoding="utf-8") as f:
            json.dump(settings_dict, f, indent=4, ensure_ascii=False)

        self._settings = settings
        logger.info("Saved user settings to %s", self._config_path)

    def reload(self) -> UserSettings:
        """
        Force reload settings from file.

        Returns:
            Reloaded UserSettings.
        """
        self._settings = None
        return self.settings


# Global settings manager instance
_settings_manager: SettingsManager | None = None


def get_settings_manager() -> SettingsManager:
    """Get the global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def get_user_settings() -> UserSettings:
    """Get current user settings."""
    return get_settings_manager().settings


def format_currency(amount: float) -> str:
    """
    Format amount as currency using user settings.

    Args:
        amount: Amount to format.

    Returns:
        Formatted currency string.
    """
    return get_user_settings().format_currency(amount)
