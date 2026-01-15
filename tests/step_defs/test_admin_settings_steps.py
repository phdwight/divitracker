"""Step definitions for admin settings feature."""

import io
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from app.routes.admin import get_db_path

scenarios("../features/admin_settings.feature")


@pytest.fixture
def context():
    """Shared context for storing state between steps."""
    return {}


@given("the application is configured for testing", target_fixture="app_context")
def app_configured(app):
    """Set up application context for testing."""
    with app.app_context():
        yield app


@given("the database file does not exist")
def db_file_not_exist(context):
    """Set up non-existent database file."""
    context["db_path"] = Path("/nonexistent/path.db")


@given(parsers.parse('the database file exists with content "{content}"'))
def db_file_exists_with_content(context, content):
    """Create database file with content."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp.write(content.encode())
        context["db_path"] = Path(tmp.name)
        context["temp_file"] = tmp.name


@given("the database file exists at temp path")
def db_file_exists_temp(context):
    """Create database file at temp path."""
    tmp_dir = tempfile.mkdtemp()
    db_path = Path(tmp_dir) / "dividends.db"
    db_path.write_bytes(b"existing content")
    context["db_path"] = db_path
    context["temp_dir"] = tmp_dir


@when(parsers.parse('I visit "{url}"'), target_fixture="response")
def visit_url(client, url):
    """Visit a URL."""
    return client.get(url)


@when(
    parsers.parse('I save settings with currency "{code}" symbol "{symbol}" and name "{name}"'),
    target_fixture="response",
)
def save_settings(client, code, symbol, name, context):
    """Save settings."""
    with patch("app.routes.admin.get_settings_manager") as mock_manager:
        mock_instance = MagicMock()
        mock_manager.return_value = mock_instance
        context["mock_settings_manager"] = mock_instance
        return client.post(
            "/settings/save",
            data={
                "currency_code": code,
                "currency_symbol": symbol,
                "currency_name": name,
                "thousands_separator": ",",
                "decimal_separator": ".",
                "decimal_places": "2",
                "timezone_offset": "0",
                "timezone_name": "UTC",
            },
            follow_redirects=True,
        )


@when(parsers.parse('I save settings with decimal places "{places}"'), target_fixture="response")
def save_settings_decimal_places(client, places):
    """Save settings with specific decimal places."""
    return client.post(
        "/settings/save",
        data={
            "currency_code": "USD",
            "currency_symbol": "$",
            "currency_name": "US Dollar",
            "thousands_separator": ",",
            "decimal_separator": ".",
            "decimal_places": places,
            "timezone_offset": "0",
            "timezone_name": "UTC",
        },
        follow_redirects=True,
    )


@when(parsers.parse('I save settings with timezone offset "{offset}"'), target_fixture="response")
def save_settings_timezone(client, offset):
    """Save settings with specific timezone offset."""
    return client.post(
        "/settings/save",
        data={
            "currency_code": "USD",
            "currency_symbol": "$",
            "currency_name": "US Dollar",
            "thousands_separator": ",",
            "decimal_separator": ".",
            "decimal_places": "2",
            "timezone_offset": offset,
            "timezone_name": "Invalid",
        },
        follow_redirects=True,
    )


@when("I request database download", target_fixture="response")
def request_db_download(client, context):
    """Request database download."""
    with patch("app.routes.admin.get_db_path") as mock_path:
        mock_path.return_value = context.get("db_path", Path("/nonexistent/path.db"))
        return client.get("/settings/database/download", follow_redirects=True)


@when("I upload database without file", target_fixture="response")
def upload_db_no_file(client):
    """Upload database without file."""
    return client.post("/settings/database/upload", follow_redirects=True)


@when("I upload database with empty filename", target_fixture="response")
def upload_db_empty_filename(client):
    """Upload database with empty filename."""
    return client.post(
        "/settings/database/upload",
        data={"db_file": (io.BytesIO(b""), "")},
        follow_redirects=True,
    )


@when(parsers.parse('I upload database file "{filename}"'), target_fixture="response")
def upload_db_file(client, filename):
    """Upload database file."""
    return client.post(
        "/settings/database/upload",
        data={"db_file": (io.BytesIO(b"test"), filename)},
        content_type="multipart/form-data",
        follow_redirects=True,
    )


@when(
    parsers.parse('I upload database file "{filename}" with content "{content}"'),
    target_fixture="response",
)
def upload_db_file_with_content(client, filename, content, context):
    """Upload database file with content."""
    with patch("app.routes.admin.get_db_path") as mock_path:
        mock_path.return_value = context.get("db_path", Path("/tmp/dividends.db"))
        return client.post(
            "/settings/database/upload",
            data={"db_file": (io.BytesIO(content.encode()), filename)},
            content_type="multipart/form-data",
            follow_redirects=True,
        )


@when("I get the database path", target_fixture="db_path_result")
def get_db_path_step():
    """Get database path."""
    return get_db_path()


@then(parsers.parse("I should see status code {code:d}"))
def check_status_code(response, code):
    """Check response status code."""
    assert response.status_code == code


@then(parsers.parse('I should see "{text}" in the page'))
def check_text_in_page(response, text):
    """Check text is in the page."""
    assert text.encode() in response.data


@then("the settings should be saved")
def check_settings_saved(context):
    """Check settings were saved."""
    mock = context.get("mock_settings_manager")
    if mock:
        mock.save_settings.assert_called_once()


@then(parsers.parse('I should receive file with content "{content}"'))
def check_file_content(response, content):
    """Check received file content."""
    assert content.encode() in response.data


@then(parsers.parse('the content type should be "{content_type}"'))
def check_content_type(response, content_type):
    """Check content type."""
    assert response.content_type == content_type


@then(parsers.parse('the database should contain "{content}"'))
def check_db_contains(context, content):
    """Check database contains content."""
    if context.get("db_path"):
        actual = context["db_path"].read_bytes()
        assert content.encode() in actual


@then(parsers.parse('a backup file should exist with content "{content}"'))
def check_backup_exists(context, content):
    """Check backup file exists with content."""
    if context.get("temp_dir"):
        backup_files = list(Path(context["temp_dir"]).glob("dividends_backup_*.db"))
        assert len(backup_files) >= 1
        assert backup_files[0].read_bytes() == content.encode()


@then(parsers.parse('the path should end with "{suffix}"'))
def check_path_ends_with(db_path_result, suffix):
    """Check path ends with suffix."""
    assert db_path_result.name == suffix


@then(parsers.parse('the path should contain "{part}"'))
def check_path_contains(db_path_result, part):
    """Check path contains part."""
    assert part in str(db_path_result)


@pytest.fixture(autouse=True)
def cleanup_temp_files(context):
    """Clean up temporary files after tests."""
    yield
    if context.get("temp_file"):
        try:
            os.unlink(context["temp_file"])
        except FileNotFoundError:
            # File may have already been removed during the test or by the OS; safe to ignore.
            # File was already removed (e.g., by the code under test); safe to ignore.
            pass
    if context.get("temp_dir"):
        try:
            shutil.rmtree(context["temp_dir"])
            # Directory may have already been removed during the test or by the OS; safe to ignore.
        except FileNotFoundError:
            # Directory was already removed; safe to ignore in test cleanup.
            pass
