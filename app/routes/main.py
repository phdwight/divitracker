"""Main routes blueprint for dashboard and home page."""

from flask import Blueprint, render_template

from app.services.investment_service import InvestmentService
from app.services.portfolio_service import PortfolioService

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    Render the main dashboard with portfolio overview.

    Returns:
        Rendered index template with portfolio statistics.
    """
    investment_service = InvestmentService()
    portfolio_service = PortfolioService(investment_service)

    investments = investment_service.get_all_investments()
    portfolio_summary = portfolio_service.get_portfolio_summary()

    return render_template(
        "index.html",
        investments=investments,
        total_invested=portfolio_summary.total_invested,
        total_annual_dividends=portfolio_summary.total_annual_dividends,
        overall_yield=portfolio_summary.overall_yield,
    )
