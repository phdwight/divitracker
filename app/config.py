"""Application configuration classes."""

import os
from pathlib import Path


class Config:
    """Base configuration class."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Base directory for the application
    BASE_DIR: Path = Path(__file__).parent.parent

    # Database configuration
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'dividends.db'}",
    )


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{Config.BASE_DIR / 'instance' / 'dividends.db'}",
    )


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING: bool = True
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    WTF_CSRF_ENABLED: bool = False


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG: bool = False
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")

    @classmethod
    def init_app(cls, app) -> None:
        """Production-specific initialization."""
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")
