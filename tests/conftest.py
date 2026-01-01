"""Pytest configuration and fixtures."""

from typing import Generator

import pytest

from app.extensions import db
from app.factory import create_app
from app.models import Dividend, Investment


@pytest.fixture(scope="function")
def app():
    """Create and configure a test application instance."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the application."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """Create a test CLI runner for the application."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def sample_investment(app) -> Generator[Investment, None, None]:
    """Create a sample investment for testing."""
    with app.app_context():
        investment = Investment(
            name="Test Investment",
            ticker="TEST",
            total_invested=10000.0,
        )
        db.session.add(investment)
        db.session.commit()

        # Refresh to get the ID
        db.session.refresh(investment)
        yield investment


@pytest.fixture(scope="function")
def sample_investment_with_dividend(app) -> Generator[Investment, None, None]:
    """Create a sample investment with dividends for testing."""
    from datetime import datetime, timezone

    with app.app_context():
        current_year = datetime.now(timezone.utc).year
        investment = Investment(
            name="Dividend Test Investment",
            ticker="DIV",
            total_invested=5000.0,
        )
        db.session.add(investment)
        db.session.commit()

        # Add 4 quarterly dividends for current year
        for quarter, month in enumerate([3, 6, 9, 12], start=1):
            dividend = Dividend(
                investment_id=investment.id,
                amount=50.0,
                frequency="quarterly",
                notes="Test dividend",
                period_month=month,
                period_year=current_year,
            )
            db.session.add(dividend)
        db.session.commit()

        db.session.refresh(investment)
        yield investment
