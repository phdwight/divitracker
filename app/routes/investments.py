"""Investment routes blueprint."""

import logging

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.exceptions import NotFoundError, ValidationError
from app.services.investment_service import InvestmentService
from app.utils import sanitize_log_input

investments_bp = Blueprint("investments", __name__)
logger = logging.getLogger(__name__)


@investments_bp.route("/add", methods=["GET", "POST"])
def add_investment():
    """
    Handle adding a new investment or updating an existing one.

    GET: Display the add investment form.
    POST: Process the investment creation/update.

    Returns:
        GET: Rendered add_investment template.
        POST: Redirect to index on success, back to form on error.
    """
    investment_service = InvestmentService()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        ticker = request.form.get("ticker", "").strip().upper() or None
        amount_str = request.form.get("amount", "0")

        try:
            investment, created = investment_service.create_or_update_investment(
                name=name,
                ticker=ticker,
                amount_str=amount_str,
            )

            if created:
                flash(
                    f"Created new investment: {investment.name} "
                    f"with ${investment.total_invested:.2f}",
                    "success",
                )
            else:
                flash(
                    f"Added ${float(amount_str):.2f} to existing investment: {investment.name}",
                    "success",
                )

            logger.info(
                "Investment %s: %s (amount: %s)",
                "created" if created else "updated",
                sanitize_log_input(investment.name),
                sanitize_log_input(amount_str),
            )
            return redirect(url_for("main.index"))

        except ValidationError as e:
            flash(str(e), "error")
            logger.warning("Validation error adding investment: %s", sanitize_log_input(str(e)))
            return redirect(url_for("investments.add_investment"))

    investments = investment_service.get_all_investments()
    return render_template("add_investment.html", investments=investments)


@investments_bp.route("/<int:investment_id>")
def view_investment(investment_id: int):
    """
    Display detailed view of a specific investment.

    Args:
        investment_id: The ID of the investment to view.

    Returns:
        Rendered view_investment template or 404 error.
    """
    from datetime import datetime
    from math import ceil

    from app.models import Dividend
    from app.settings import get_user_settings

    investment_service = InvestmentService()
    user_settings = get_user_settings()

    try:
        investment = investment_service.get_investment_by_id(investment_id)
        # Get dividends sorted by date descending
        all_dividends = (
            Dividend.query.filter_by(investment_id=investment_id)
            .order_by(Dividend.date_received.desc())
            .all()
        )

        # Get years with dividends for the year selector
        years_with_dividends = investment.get_years_with_dividends()

        # Get selected year from query params, default to current year
        current_year = datetime.now().year
        selected_year = request.args.get("year", type=int)

        # If no year selected or year has no data, use current year or most recent year with data
        if selected_year is None or selected_year not in years_with_dividends:
            if current_year in years_with_dividends:
                selected_year = current_year
            elif years_with_dividends:
                selected_year = years_with_dividends[0]  # Most recent year (list is desc sorted)
            else:
                selected_year = current_year  # No dividends yet, show current year

        # Pagination for dividends
        items_per_page = request.args.get(
            "per_page", type=int, default=user_settings.pagination.items_per_page
        )
        page = request.args.get("page", type=int, default=1)
        total_items = len(all_dividends)
        total_pages = ceil(total_items / items_per_page) if total_items > 0 else 1

        # Ensure page is within bounds
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages

        # Slice dividends for current page
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        dividends = all_dividends[start_idx:end_idx]

        return render_template(
            "view_investment.html",
            investment=investment,
            dividends=dividends,
            years_with_dividends=years_with_dividends,
            selected_year=selected_year,
            # Pagination data
            page=page,
            total_pages=total_pages,
            total_items=total_items,
            items_per_page=items_per_page,
        )
    except NotFoundError:
        flash("Investment not found", "error")
        return redirect(url_for("main.index"))


@investments_bp.route("/<int:investment_id>/edit", methods=["GET", "POST"])
def edit_investment(investment_id: int):
    """
    Handle editing an existing investment.

    Args:
        investment_id: The ID of the investment to edit.

    Returns:
        GET: Rendered edit_investment template.
        POST: Redirect to view page on success.
    """
    investment_service = InvestmentService()

    try:
        investment = investment_service.get_investment_by_id(investment_id)
    except NotFoundError:
        flash("Investment not found", "error")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name = request.form.get("name", investment.name).strip()
        ticker = request.form.get("ticker", "").strip().upper() or None
        amount_str = request.form.get("amount", str(investment.total_invested))

        try:
            investment_service.update_investment(
                investment_id=investment_id,
                name=name,
                ticker=ticker,
                total_invested_str=amount_str,
            )
            flash("Investment updated successfully!", "success")
            logger.info("Investment updated: %s (ID: %d)", sanitize_log_input(name), investment_id)
            return redirect(url_for("investments.view_investment", investment_id=investment_id))

        except ValidationError as e:
            flash(str(e), "error")
            logger.warning(
                "Validation error updating investment %d: %s",
                investment_id,
                sanitize_log_input(str(e)),
            )

    return render_template("edit_investment.html", investment=investment)


@investments_bp.route("/<int:investment_id>/delete", methods=["POST"])
def delete_investment(investment_id: int):
    """
    Delete an investment and all associated dividend records.

    Args:
        investment_id: The ID of the investment to delete.

    Returns:
        Redirect to index page.
    """
    investment_service = InvestmentService()

    try:
        investment_name = investment_service.delete_investment(investment_id)
        flash(f'Investment "{investment_name}" deleted successfully!', "success")
        logger.info(
            "Investment deleted: %s (ID: %d)", sanitize_log_input(investment_name), investment_id
        )
    except NotFoundError:
        flash("Investment not found", "error")

    return redirect(url_for("main.index"))


@investments_bp.route("/api/list")
def api_investments():
    """
    API endpoint to get all investments for autocomplete.

    Returns:
        JSON list of investment data.
    """
    investment_service = InvestmentService()
    investments = investment_service.get_all_investments()

    return jsonify([inv.to_dict() for inv in investments])
