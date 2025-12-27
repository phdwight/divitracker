"""Routes package initialization."""

from app.routes.main import main_bp
from app.routes.investments import investments_bp
from app.routes.dividends import dividends_bp

__all__ = ["main_bp", "investments_bp", "dividends_bp"]
