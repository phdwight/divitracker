"""Main routes blueprint for dashboard and home page."""

from dataclasses import dataclass
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
    selected_year = request.args.get("year", type=int)
    if selected_year is None or selected_year not in years_with_dividends:
        selected_year = current_year

    # Filter to hide zero-amount investments
    hide_zero = request.args.get("hide_zero", type=str, default="true") == "true"
    if hide_zero:
        filtered_investments = [inv for inv in investments if inv.total_invested > 0]
    else:
        filtered_investments = list(investments)

    # Get portfolio summary for selected year
    portfolio_summary = portfolio_service.get_portfolio_summary(year=selected_year)

    return render_template(
        "index.html",
        investments=filtered_investments,
        total_invested=portfolio_summary.total_invested,
        total_annual_dividends=portfolio_summary.total_annual_dividends,
        projected_annual_dividends=portfolio_summary.projected_annual_dividends,
        overall_yield=portfolio_summary.overall_yield,
        projected_yield=portfolio_summary.projected_yield,
        selected_year=selected_year,
        years_with_dividends=years_with_dividends,
        hide_zero=hide_zero,
    )


@dataclass
class InvestmentYieldDetail:
    """Data class for individual investment yield breakdown."""

    name: str
    ticker: str | None
    investment_amount: float
    dividends_received: float
    yield_percent: float


@main_bp.route("/yield-breakdown")
def yield_breakdown():
    """
    Render the yield calculation breakdown page.

    Returns:
        Rendered yield breakdown template with detailed calculations.
    """
    investment_service = InvestmentService()

    investments = investment_service.get_all_investments()
    current_year = datetime.now(timezone.utc).year

    # Get selected year from query params
    selected_year = request.args.get("year", type=int, default=current_year)

    # Build detailed breakdown for each investment
    investment_details: list[InvestmentYieldDetail] = []
    total_investment_for_yield = 0.0
    total_dividends = 0.0

    for inv in investments:
        inv_amount = inv.get_investment_amount_for_year(selected_year)
        div_amount = inv.calculate_annual_dividends(selected_year)

        # Only include investments that have investment amount or dividends
        if inv_amount > 0 or div_amount > 0:
            inv_yield = (div_amount / inv_amount * 100) if inv_amount > 0 else 0.0
            investment_details.append(
                InvestmentYieldDetail(
                    name=inv.name,
                    ticker=inv.ticker,
                    investment_amount=inv_amount,
                    dividends_received=div_amount,
                    yield_percent=inv_yield,
                )
            )
            total_investment_for_yield += inv_amount
            total_dividends += div_amount

    # Calculate overall yield
    overall_yield = 0.0
    if total_investment_for_yield > 0:
        overall_yield = (total_dividends / total_investment_for_yield) * 100

    return render_template(
        "yield_breakdown.html",
        investment_details=investment_details,
        total_investment_for_yield=total_investment_for_yield,
        total_dividends=total_dividends,
        overall_yield=overall_yield,
        selected_year=selected_year,
    )
