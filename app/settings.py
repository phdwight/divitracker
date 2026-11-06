"""User settings management for currency and formatting preferences."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

VALID_SIDEBAR_POSITIONS: tuple[str, ...] = ("left", "right")

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
    "layout": {
        "sidebar_position": "left",
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
class LayoutSettings:
    """UI layout configuration."""

    sidebar_position: str = "left"


@dataclass
class UserSettings:
    """Complete user settings."""

    currency: CurrencySettings
    formatting: FormattingSettings
    timezone: TimezoneSettings
    pagination: PaginationSettings
    layout: LayoutSettings = field(default_factory=LayoutSettings)

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
        self._last_mtime: float | None = None

    def _get_file_mtime(self) -> float | None:
        """Return file modification timestamp if config file exists."""
        try:
            return self._config_path.stat().st_mtime if self._config_path.exists() else None
        except OSError:
            return None

    @property
    def settings(self) -> UserSettings:
        """Get current user settings, loading or refreshing if file changed."""
        current_mtime = self._get_file_mtime()
        if self._settings is None or current_mtime != self._last_mtime:
            self._settings = self._load_settings()
            self._last_mtime = current_mtime
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

        raw_position = str(settings_dict["layout"].get("sidebar_position", "left")).lower()
        if raw_position not in VALID_SIDEBAR_POSITIONS:
            raw_position = "left"
        settings_dict["layout"]["sidebar_position"] = raw_position

        return UserSettings(
            currency=CurrencySettings(**settings_dict["currency"]),
            formatting=FormattingSettings(**settings_dict["formatting"]),
            timezone=TimezoneSettings(**settings_dict["timezone"]),
            pagination=PaginationSettings(**settings_dict["pagination"]),
            layout=LayoutSettings(**settings_dict["layout"]),
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
            "layout": {
                "sidebar_position": settings.layout.sidebar_position,
            },
        }

        # Ensure config directory exists
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        with self._config_path.open("w", encoding="utf-8") as f:
            json.dump(settings_dict, f, indent=4, ensure_ascii=False)

        self._settings = settings
        self._last_mtime = self._get_file_mtime()
        logger.info("Saved user settings to %s", self._config_path)

    def reload(self) -> UserSettings:
        """
        Force reload settings from file.

        Returns:
            Reloaded UserSettings.
        """
        self._settings = None
        self._last_mtime = None
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
