"""Main routes blueprint for dashboard and home page."""

from datetime import datetime, timezone

from flask import Blueprint, render_template, request

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
    current_year = datetime.now(timezone.utc).year
    
    # Get all years with dividend data across all investments
    all_years = set()
    for inv in investments:
        all_years.update(inv.get_years_with_dividends())
    
    # Always include current year
    all_years.add(current_year)
    years_with_dividends = sorted(all_years, reverse=True)
    
    # Get selected year from query params
    selected_year = request.args.get('year', type=int)
    if selected_year is None or selected_year not in years_with_dividends:
        selected_year = current_year
    
    # Get portfolio summary for selected year
    portfolio_summary = portfolio_service.get_portfolio_summary(year=selected_year)

    return render_template(
        "index.html",
        investments=investments,
        total_invested=portfolio_summary.total_invested,
        total_annual_dividends=portfolio_summary.total_annual_dividends,
        projected_annual_dividends=portfolio_summary.projected_annual_dividends,
        overall_yield=portfolio_summary.overall_yield,
        projected_yield=portfolio_summary.projected_yield,
        selected_year=selected_year,
        years_with_dividends=years_with_dividends,
    )
