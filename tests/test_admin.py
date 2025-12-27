"""Tests for admin routes."""

import io
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from flask import Flask
from flask.testing import FlaskClient


class TestAdminIndex:
    """Tests for admin index page."""

    def test_admin_index_renders(self, client: FlaskClient) -> None:
        """Test that admin index page renders successfully."""
        response = client.get("/admin/")
        assert response.status_code == 200
        assert b"Admin Settings" in response.data

    def test_admin_index_shows_currency_presets(self, client: FlaskClient) -> None:
        """Test that currency presets are displayed."""
        response = client.get("/admin/")
        assert response.status_code == 200
        assert b"USD" in response.data
        assert b"EUR" in response.data
        assert b"PHP" in response.data

    def test_admin_index_shows_current_settings(self, client: FlaskClient) -> None:
        """Test that current settings are displayed."""
        response = client.get("/admin/")
        assert response.status_code == 200
        # Default currency is PHP
        assert b"PHP" in response.data

    def test_admin_index_shows_database_section(self, client: FlaskClient) -> None:
        """Test that database management section is displayed."""
        response = client.get("/admin/")
        assert response.status_code == 200
        assert b"Database Management" in response.data


class TestSaveSettings:
    """Tests for save settings endpoint."""

    def test_save_settings_success(self, client: FlaskClient, app: Flask) -> None:
        """Test saving settings successfully."""
        with patch("app.routes.admin.get_settings_manager") as mock_manager:
            mock_instance = MagicMock()
            mock_manager.return_value = mock_instance

            response = client.post(
                "/admin/save-settings",
                data={
                    "currency_code": "USD",
                    "currency_symbol": "$",
                    "currency_name": "US Dollar",
                    "thousands_separator": ",",
                    "decimal_separator": ".",
                    "decimal_places": "2",
                    "timezone_offset": "-5",
                    "timezone_name": "EST",
                },
                follow_redirects=True,
            )

            assert response.status_code == 200
            mock_instance.save_settings.assert_called_once()

    def test_save_settings_invalid_decimal_places(self, client: FlaskClient) -> None:
        """Test validation of decimal places."""
        response = client.post(
            "/admin/save-settings",
            data={
                "currency_code": "USD",
                "currency_symbol": "$",
                "currency_name": "US Dollar",
                "thousands_separator": ",",
                "decimal_separator": ".",
                "decimal_places": "10",  # Invalid - max is 4
                "timezone_offset": "0",
                "timezone_name": "UTC",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Decimal places must be between 0 and 4" in response.data

    def test_save_settings_invalid_timezone_offset(self, client: FlaskClient) -> None:
        """Test validation of timezone offset."""
        response = client.post(
            "/admin/save-settings",
            data={
                "currency_code": "USD",
                "currency_symbol": "$",
                "currency_name": "US Dollar",
                "thousands_separator": ",",
                "decimal_separator": ".",
                "decimal_places": "2",
                "timezone_offset": "20",  # Invalid - max is 14
                "timezone_name": "Invalid",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Timezone offset must be between -12 and +14" in response.data

    def test_save_settings_negative_decimal_places(self, client: FlaskClient) -> None:
        """Test validation rejects negative decimal places."""
        response = client.post(
            "/admin/save-settings",
            data={
                "currency_code": "USD",
                "currency_symbol": "$",
                "currency_name": "US Dollar",
                "thousands_separator": ",",
                "decimal_separator": ".",
                "decimal_places": "-1",
                "timezone_offset": "0",
                "timezone_name": "UTC",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Decimal places must be between 0 and 4" in response.data


class TestDownloadDatabase:
    """Tests for database download endpoint."""

    def test_download_db_no_file(self, client: FlaskClient) -> None:
        """Test download when database file doesn't exist."""
        with patch("app.routes.admin.get_db_path") as mock_path:
            mock_path.return_value = Path("/nonexistent/path.db")

            response = client.get("/admin/download-db", follow_redirects=True)

            assert response.status_code == 200
            assert b"Database file not found" in response.data

    def test_download_db_success(self, client: FlaskClient, app: Flask) -> None:
        """Test successful database download."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp.write(b"test database content")
            tmp_path = Path(tmp.name)

        try:
            with patch("app.routes.admin.get_db_path") as mock_path:
                mock_path.return_value = tmp_path

                response = client.get("/admin/download-db")

                assert response.status_code == 200
                assert response.content_type == "application/octet-stream"
                assert b"test database content" in response.data
        finally:
            os.unlink(tmp_path)


class TestUploadDatabase:
    """Tests for database upload endpoint."""

    def test_upload_db_no_file(self, client: FlaskClient) -> None:
        """Test upload without file."""
        response = client.post("/admin/upload-db", follow_redirects=True)

        assert response.status_code == 200
        assert b"No file selected" in response.data

    def test_upload_db_empty_filename(self, client: FlaskClient) -> None:
        """Test upload with empty filename."""
        response = client.post(
            "/admin/upload-db",
            data={"db_file": (io.BytesIO(b""), "")},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"No file selected" in response.data

    def test_upload_db_invalid_extension(self, client: FlaskClient) -> None:
        """Test upload with invalid file extension."""
        response = client.post(
            "/admin/upload-db",
            data={"db_file": (io.BytesIO(b"test"), "test.txt")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Invalid file type" in response.data

    def test_upload_db_success(self, client: FlaskClient, app: Flask) -> None:
        """Test successful database upload."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "dividends.db"
            # Create existing db file
            db_path.write_bytes(b"existing content")

            with patch("app.routes.admin.get_db_path") as mock_path:
                mock_path.return_value = db_path

                response = client.post(
                    "/admin/upload-db",
                    data={"db_file": (io.BytesIO(b"new content"), "backup.db")},
                    content_type="multipart/form-data",
                    follow_redirects=True,
                )

                assert response.status_code == 200
                assert b"Database uploaded successfully" in response.data
                # Verify new content was written
                assert db_path.read_bytes() == b"new content"

    def test_upload_db_creates_backup(self, client: FlaskClient, app: Flask) -> None:
        """Test that upload creates backup of existing database."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "dividends.db"
            db_path.write_bytes(b"original content")

            with patch("app.routes.admin.get_db_path") as mock_path:
                mock_path.return_value = db_path

                client.post(
                    "/admin/upload-db",
                    data={"db_file": (io.BytesIO(b"new content"), "backup.db")},
                    content_type="multipart/form-data",
                )

                # Check that a backup file was created
                backup_files = list(Path(tmp_dir).glob("dividends_backup_*.db"))
                assert len(backup_files) == 1
                assert backup_files[0].read_bytes() == b"original content"


class TestGetDbPath:
    """Tests for get_db_path helper function."""

    def test_get_db_path_returns_path(self) -> None:
        """Test that get_db_path returns a Path object."""
        from app.routes.admin import get_db_path

        result = get_db_path()
        assert isinstance(result, Path)
        assert result.name == "dividends.db"
        assert "instance" in str(result)
