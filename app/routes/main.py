"""Main routes blueprint for dashboard and home page."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from flask import Blueprint, current_app, render_template, request, send_from_directory, url_for

from app.models import Investment
from app.services.investment_service import InvestmentService
from app.services.portfolio_service import PortfolioService
from app.settings import get_user_settings
from app.utils import paginate

main_bp = Blueprint("main", __name__)

# Sortable dashboard columns: key -> header label ("{year}" is replaced with the selected year)
SORT_COLUMNS: dict[str, str] = {
    "name": "Holding",
    "invested": "Invested",
    "current": "Current value",
    "received": "Received {year}",
    "yield": "Yield act | proj",
}
DEFAULT_SORT = "name"
SORT_DIRECTIONS: tuple[str, ...] = ("asc", "desc")


def _sort_value(investment: Investment, key: str, year: int) -> float | str:
    """
    Get the value used to sort an investment by the given column key.

    Args:
        investment: Investment to read the value from.
        key: Sort column key (one of SORT_COLUMNS).
        year: Selected dashboard year (used for dividend-based columns).

    Returns:
        Comparable sort value.
    """
    if key == "invested":
        return investment.total_invested
    if key == "current":
        return investment.effective_current_value
    if key == "received":
        return investment.calculate_annual_dividends(year)
    if key == "yield":
        return investment.calculate_dividend_yield(year)
    return investment.name.lower()


def sort_investments(
    investments: Sequence[Investment], key: str, direction: str, year: int
) -> list[Investment]:
    """
    Sort investments by a dashboard column.

    Args:
        investments: Investments to sort.
        key: Sort column key; unknown keys fall back to name.
        direction: "asc" or "desc"; unknown values fall back to "asc".
        year: Selected dashboard year.

    Returns:
        New sorted list of investments.
    """
    safe_key = key if key in SORT_COLUMNS else DEFAULT_SORT
    reverse = direction == "desc"
    return sorted(
        investments, key=lambda inv: _sort_value(inv, safe_key, year), reverse=reverse
    )


def search_investments(investments: Sequence[Investment], query: str) -> list[Investment]:
    """
    Filter investments whose name or ticker contains the query (case-insensitive).

    Args:
        investments: Investments to filter.
        query: Search text; blank returns all investments.

    Returns:
        Matching investments.
    """
    needle = query.strip().lower()
    if not needle:
        return list(investments)
    return [
        inv
        for inv in investments
        if needle in inv.name.lower() or (inv.ticker and needle in inv.ticker.lower())
    ]


@main_bp.route("/favicon.ico")
def favicon():
    """Serve the application favicon."""
    return send_from_directory(
        current_app.static_folder or "static", "favicon.svg", mimetype="image/svg+xml"
    )


@main_bp.route("/")
@main_bp.route("/year/<int:year>")
def index(year: int | None = None):
    """
    Render the main dashboard with portfolio overview.

    Returns:
        Rendered index template with portfolio statistics.
    """
    investment_service = InvestmentService()
    portfolio_service = PortfolioService(investment_service)
    user_settings = get_user_settings()

    investments = investment_service.get_all_investments()
    current_year = datetime.now(timezone.utc).year

    # Get all years with dividend data across all investments
    all_years = set()
    for inv in investments:
        all_years.update(inv.get_years_with_dividends())

    # Always include current year
    all_years.add(current_year)
    years_with_dividends = sorted(all_years, reverse=True)

    # Get selected year from URL path parameter or query params (for backward compatibility)
    selected_year = year or request.args.get("year", type=int)
    if selected_year is None or selected_year not in years_with_dividends:
        selected_year = current_year

    # Filter to hide investments with zero dividends received (for selected year)
    hide_zero = request.args.get("hide_zero", type=str, default="true") == "true"
    # Filter to hide investments with zero amount invested
    hide_zero_investments = (
        request.args.get("hide_zero_investments", type=str, default="true") == "true"
    )

    filtered_investments = list(investments)
    if hide_zero:
        filtered_investments = [
            inv for inv in filtered_investments if inv.calculate_annual_dividends(selected_year) > 0
        ]
    if hide_zero_investments:
        filtered_investments = [inv for inv in filtered_investments if inv.total_invested > 0]

    # Search by name or ticker
    search_query = request.args.get("q", type=str, default="").strip()
    filtered_investments = search_investments(filtered_investments, search_query)

    # Sorting
    sort_key = request.args.get("sort", type=str, default=DEFAULT_SORT)
    if sort_key not in SORT_COLUMNS:
        sort_key = DEFAULT_SORT
    sort_dir = request.args.get("dir", type=str, default="asc")
    if sort_dir not in SORT_DIRECTIONS:
        sort_dir = "asc"
    filtered_investments = sort_investments(
        filtered_investments, sort_key, sort_dir, selected_year
    )

    # Pagination
    items_per_page = request.args.get(
        "per_page", type=int, default=user_settings.pagination.items_per_page
    )
    page = request.args.get("page", type=int, default=1)
    total_items = len(filtered_investments)

    pagination = paginate(total_items, page, items_per_page)
    paginated_investments = filtered_investments[pagination.start_idx : pagination.end_idx]

    # Get portfolio summary for selected year
    portfolio_summary = portfolio_service.get_portfolio_summary(year=selected_year)

    # Only show paper gain/loss when at least one current value has been recorded
    has_current_values = any(inv.current_value is not None for inv in investments)

    # Query state shared by sort links (page is intentionally reset to 1 on re-sort)
    query_state: dict[str, Any] = {
        "hide_zero": "true" if hide_zero else "false",
        "hide_zero_investments": "true" if hide_zero_investments else "false",
        "per_page": items_per_page,
    }
    if search_query:
        query_state["q"] = search_query

    sort_columns = []
    for key, label in SORT_COLUMNS.items():
        is_active = key == sort_key
        if is_active:
            next_dir = "desc" if sort_dir == "asc" else "asc"
        else:
            next_dir = "asc" if key == "name" else "desc"
        sort_columns.append(
            {
                "key": key,
                "label": label.format(year=selected_year),
                "active": is_active,
                "dir": sort_dir if is_active else None,
                "url": url_for(
                    "main.index", year=selected_year, sort=key, dir=next_dir, **query_state
                ),
            }
        )

    return render_template(
        "index.html",
        investments=paginated_investments,
        total_invested=portfolio_summary.total_invested,
        total_current_value=portfolio_summary.total_current_value,
        total_paper_gain_loss=portfolio_summary.total_paper_gain_loss,
        total_paper_gain_loss_percentage=portfolio_summary.total_paper_gain_loss_percentage,
        total_annual_dividends=portfolio_summary.total_annual_dividends,
        projected_annual_dividends=portfolio_summary.projected_annual_dividends,
        overall_yield=portfolio_summary.overall_yield,
        projected_yield=portfolio_summary.projected_yield,
        has_current_values=has_current_values,
        selected_year=selected_year,
        years_with_dividends=years_with_dividends,
        hide_zero=hide_zero,
        hide_zero_investments=hide_zero_investments,
        search_query=search_query,
        sort_key=sort_key,
        sort_dir=sort_dir,
        sort_columns=sort_columns,
        # Pagination data
        page=pagination.page,
        total_pages=pagination.total_pages,
        total_items=total_items,
        items_per_page=items_per_page,
    )


@dataclass
class InvestmentYieldDetail:
    """Data class for individual investment yield breakdown."""

    name: str
    ticker: str | None
    investment_amount: float
    dividends_received: float
    yield_percent: float


@main_bp.route("/reports/yield-breakdown")
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

        # Only include investments that have dividends for the year
        if div_amount > 0:
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


@main_bp.route("/reports/dividends-chart")
def dividend_graph():
    """
    Render the dividend graph visualization page.

    Returns:
        Rendered dividend graph template with chart data.
    """
    investment_service = InvestmentService()

    investments = investment_service.get_all_investments()
    current_year = datetime.now(timezone.utc).year

    # Get all years with dividend data across all investments
    all_years = set()
    for inv in investments:
        all_years.update(inv.get_years_with_dividends())

    # Always include current year
    all_years.add(current_year)
    years_with_dividends = sorted(all_years, reverse=True)

    # Get selected year from query params (default to all years if not specified)
    selected_year = request.args.get("year", type=int)
    selected_investment_id = request.args.get("investment_id", type=int)

    # Build chart data with detailed dividend breakdown
    chart_data = []

    if selected_year:
        # Monthly breakdown for a specific year
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        monthly_totals: dict[int, float] = {i: 0.0 for i in range(1, 13)}
        monthly_details: dict[int, list[dict]] = {i: [] for i in range(1, 13)}

        for inv in investments:
            if selected_investment_id and inv.id != selected_investment_id:
                continue
            for div in inv.dividends.all():
                if div.period_year == selected_year and div.period_month:
                    monthly_totals[div.period_month] += div.amount
                    monthly_details[div.period_month].append(
                        {
                            "investment_name": inv.name,
                            "investment_id": inv.id,
                            "amount": div.amount,
                            "frequency": div.frequency,
                            "date_received": div.date_received.strftime("%Y-%m-%d"),
                        }
                    )

        chart_data = [
            {
                "label": months[i - 1],
                "value": monthly_totals[i],
                "details": monthly_details[i],
            }
            for i in range(1, 13)
        ]
    else:
        # Yearly totals with details
        for year in sorted(years_with_dividends):
            year_total = 0.0
            year_details: list[dict] = []
            for inv in investments:
                if selected_investment_id and inv.id != selected_investment_id:
                    continue
                inv_year_total = inv.calculate_annual_dividends(year)
                if inv_year_total > 0:
                    year_total += inv_year_total
                    year_details.append(
                        {
                            "investment_name": inv.name,
                            "investment_id": inv.id,
                            "amount": inv_year_total,
                            "frequency": "Annual Total",
                            "date_received": str(year),
                        }
                    )
            chart_data.append({"label": str(year), "value": year_total, "details": year_details})

    # Get investment list for filter dropdown
    investment_list = [{"id": inv.id, "name": inv.name} for inv in investments]

    return render_template(
        "dividend_graph.html",
        chart_data=chart_data,
        years_with_dividends=years_with_dividends,
        selected_year=selected_year,
        selected_investment_id=selected_investment_id,
        investments=investment_list,
    )
