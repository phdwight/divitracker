"""DiviTracker Flask Application Factory."""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from app.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import db, migrate
from app.routes.admin import admin_bp
from app.routes.dividends import dividends_bp
from app.routes.investments import investments_bp
from app.routes.main import main_bp
from app.settings import format_currency, get_user_settings


def create_app(config_name: str = "development") -> Flask:
    """
    Application factory for creating Flask app instances.

    Args:
        config_name: Configuration environment name ('development', 'testing', 'production')

    Returns:
        Configured Flask application instance
    """
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent.parent / "templates"),
        static_folder=str(Path(__file__).parent.parent / "static"),
    )

    # Load configuration
    config_mapping: dict[str, type[Config]] = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    config_class = config_mapping.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)

    # Configure logging
    _configure_logging(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(investments_bp)
    app.register_blueprint(dividends_bp)
    app.register_blueprint(admin_bp)

    # Register template context processors for currency formatting
    @app.context_processor
    def inject_settings() -> dict:
        """Inject user settings into all templates."""
        settings = get_user_settings()

        def get_local_time() -> datetime:
            """Get current time in user's configured timezone."""
            utc_now = datetime.now(timezone.utc)
            local_tz = timezone(timedelta(hours=settings.timezone.offset_hours))
            return utc_now.astimezone(local_tz)

        return {
            "currency_symbol": settings.currency.symbol,
            "currency_code": settings.currency.code,
            "currency_name": settings.currency.name,
            "thousands_separator": settings.formatting.thousands_separator,
            "decimal_separator": settings.formatting.decimal_separator,
            "decimal_places": settings.formatting.decimal_places,
            "format_currency": format_currency,
            "now": get_local_time,
            "timezone_name": settings.timezone.name,
        }

    # Register error handlers
    _register_error_handlers(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    app.logger.info("DiviTracker application initialized successfully")

    return app


def _register_error_handlers(app: Flask) -> None:
    """
    Register custom error handlers for the application.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(404)
    def not_found_error(error: HTTPException) -> tuple[str, int]:
        """Handle 404 Not Found errors."""
        return (
            render_template(
                "errors.html",
                error_code=404,
                error_title="Page Not Found",
                error_message="The page you're looking for doesn't exist or has been moved.",
                error_icon="🔍",
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error: HTTPException) -> tuple[str, int]:
        """Handle 500 Internal Server errors."""
        db.session.rollback()  # Roll back any failed transactions
        return (
            render_template(
                "errors.html",
                error_code=500,
                error_title="Internal Server Error",
                error_message="Something went wrong on our end. Please try again later.",
                error_icon="⚠️",
            ),
            500,
        )

    @app.errorhandler(403)
    def forbidden_error(error: HTTPException) -> tuple[str, int]:
        """Handle 403 Forbidden errors."""
        return (
            render_template(
                "errors.html",
                error_code=403,
                error_title="Access Forbidden",
                error_message="You don't have permission to access this resource.",
                error_icon="🚫",
            ),
            403,
        )

    @app.errorhandler(400)
    def bad_request_error(error: HTTPException) -> tuple[str, int]:
        """Handle 400 Bad Request errors."""
        return (
            render_template(
                "errors.html",
                error_code=400,
                error_title="Bad Request",
                error_message="The server couldn't understand your request.",
                error_icon="❌",
            ),
            400,
        )


def _configure_logging(app: Flask) -> None:
    """
    Configure application logging.

    Args:
        app: Flask application instance
    """
    log_level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    app.logger.setLevel(log_level)
