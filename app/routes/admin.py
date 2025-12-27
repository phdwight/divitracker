"""Admin routes blueprint for settings and database management."""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename

from app.settings import (
    CURRENCY_PRESETS,
    CurrencySettings,
    FormattingSettings,
    TimezoneSettings,
    UserSettings,
    get_settings_manager,
)
from app.utils import sanitize_log_input

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    """Get the path to the database file."""
    base_dir = Path(__file__).parent.parent.parent
    return base_dir / "instance" / "dividends.db"


@admin_bp.route("/")
def admin_index():
    """
    Render the admin settings page.

    Returns:
        Rendered admin template with current settings.
    """
    settings_manager = get_settings_manager()
    settings = settings_manager.settings

    # Check if database file exists
    db_path = get_db_path()
    db_exists = db_path.exists()
    db_size = db_path.stat().st_size if db_exists else 0
    db_modified = (
        datetime.fromtimestamp(db_path.stat().st_mtime, tz=timezone.utc)
        if db_exists
        else None
    )

    return render_template(
        "admin.html",
        settings=settings,
        currency_presets=CURRENCY_PRESETS,
        db_exists=db_exists,
        db_size=db_size,
        db_modified=db_modified,
    )


@admin_bp.route("/save-settings", methods=["POST"])
def save_settings():
    """
    Save user settings from form submission.

    Returns:
        Redirect to admin page with success/error message.
    """
    try:
        # Get form values
        currency_code = request.form.get("currency_code", "PHP")
        currency_symbol = request.form.get("currency_symbol", "₱")
        currency_name = request.form.get("currency_name", "Philippine Peso")

        thousands_separator = request.form.get("thousands_separator", ",")
        decimal_separator = request.form.get("decimal_separator", ".")
        decimal_places = int(request.form.get("decimal_places", "2"))

        timezone_offset = int(request.form.get("timezone_offset", "8"))
        timezone_name = request.form.get("timezone_name", "GMT+8")

        # Validate
        if decimal_places < 0 or decimal_places > 4:
            flash("Decimal places must be between 0 and 4", "error")
            return redirect(url_for("admin.admin_index"))

        if timezone_offset < -12 or timezone_offset > 14:
            flash("Timezone offset must be between -12 and +14", "error")
            return redirect(url_for("admin.admin_index"))

        # Create settings object
        new_settings = UserSettings(
            currency=CurrencySettings(
                code=currency_code,
                symbol=currency_symbol,
                name=currency_name,
            ),
            formatting=FormattingSettings(
                thousands_separator=thousands_separator,
                decimal_separator=decimal_separator,
                decimal_places=decimal_places,
            ),
            timezone=TimezoneSettings(
                offset_hours=timezone_offset,
                name=timezone_name,
            ),
        )

        # Save settings
        settings_manager = get_settings_manager()
        settings_manager.save_settings(new_settings)

        logger.info(
            "Settings updated: currency=%s, timezone=%s",
            sanitize_log_input(currency_code),
            sanitize_log_input(timezone_name),
        )
        flash("Settings saved successfully!", "success")

    except ValueError as e:
        logger.warning("Invalid settings value: %s", sanitize_log_input(str(e)))
        flash(f"Invalid value: {e}", "error")
    except Exception as e:
        logger.error("Error saving settings: %s", sanitize_log_input(str(e)))
        flash(f"Error saving settings: {e}", "error")

    return redirect(url_for("admin.admin_index"))


@admin_bp.route("/download-db")
def download_db():
    """
    Download the database file.

    Returns:
        Database file as attachment or redirect with error.
    """
    db_path = get_db_path()

    if not db_path.exists():
        flash("Database file not found", "error")
        return redirect(url_for("admin.admin_index"))

    logger.info("Database downloaded by user")
    return send_file(
        db_path,
        as_attachment=True,
        download_name=f"dividends_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
    )


@admin_bp.route("/upload-db", methods=["POST"])
def upload_db():
    """
    Upload and replace the database file.

    Returns:
        Redirect to admin page with success/error message.
    """
    if "db_file" not in request.files:
        flash("No file selected", "error")
        return redirect(url_for("admin.admin_index"))

    file = request.files["db_file"]

    if file.filename == "":
        flash("No file selected", "error")
        return redirect(url_for("admin.admin_index"))

    # Validate file extension
    filename = secure_filename(file.filename)
    if not filename.endswith(".db"):
        flash("Invalid file type. Please upload a .db file", "error")
        return redirect(url_for("admin.admin_index"))

    try:
        db_path = get_db_path()

        # Create backup of existing database
        if db_path.exists():
            backup_name = f"dividends_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = db_path.parent / backup_name
            os.rename(db_path, backup_path)
            logger.info("Created backup: %s", sanitize_log_input(backup_name))

        # Save new database
        file.save(db_path)
        logger.info(
            "Database uploaded: %s (%d bytes)",
            sanitize_log_input(filename),
            db_path.stat().st_size,
        )
        flash(
            "Database uploaded successfully! Please restart the application to apply changes.",
            "success",
        )

    except Exception as e:
        logger.error("Error uploading database: %s", sanitize_log_input(str(e)))
        flash(f"Error uploading database: {e}", "error")

    return redirect(url_for("admin.admin_index"))
