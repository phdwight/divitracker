"""Pytest configuration and fixtures."""

import threading
from typing import Generator

import pytest
from playwright.sync_api import Page

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


# Playwright fixtures for UI tests
@pytest.fixture(scope="session")
def flask_app_for_ui():
    """Create and configure a test application instance for UI tests."""
    app = create_app("testing")
    
    with app.app_context():
        db.create_all()
    
    return app


@pytest.fixture(scope="session")
def live_server(flask_app_for_ui):
    """Start a live Flask server for UI tests."""
    import socket
    
    def is_server_ready(host, port, timeout=5):
        """Check if server is ready to accept connections."""
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                with socket.create_connection((host, port), timeout=1):
                    return True
            except (socket.error, ConnectionRefusedError):
                time.sleep(0.1)
        return False
    
    def run_server():
        flask_app_for_ui.run(host="127.0.0.1", port=5555, debug=False, use_reloader=False, threaded=True)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to be ready with health check
    if not is_server_ready("127.0.0.1", 5555, timeout=10):
        raise RuntimeError("Flask test server failed to start within 10 seconds")
    
    yield "http://127.0.0.1:5555"
    
    # Server will be cleaned up automatically when tests finish


@pytest.fixture(scope="function")
def ui_page(page: Page, live_server: str) -> Generator[Page, None, None]:
    """Provide a Playwright page with live server context."""
    page.base_url = live_server
    yield page


@pytest.fixture(scope="function")
def ui_app(flask_app_for_ui):
    """Create database tables for UI tests."""
    with flask_app_for_ui.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        yield flask_app_for_ui
        # Clean up after test
        db.session.remove()
