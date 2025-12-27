"""Dividend routes blueprint."""

import logging
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.exceptions import NotFoundError, ValidationError
from app.services.dividend_service import DividendService
from app.services.investment_service import InvestmentService
from app.settings import format_currency
from app.utils import sanitize_log_input

dividends_bp = Blueprint("dividends", __name__)
logger = logging.getLogger(__name__)


@dividends_bp.route("/add", methods=["GET", "POST"])
def add_dividend():
    """
    Handle adding a new dividend record.

    GET: Display the add dividend form.
    POST: Process the dividend creation.

    Returns:
        GET: Rendered add_dividend template.
        POST: Redirect to investment view on success.
    """
    investment_service = InvestmentService()
    dividend_service = DividendService()

    if request.method == "POST":
        investment_id_str = request.form.get("investment_id", "")
        amount_str = request.form.get("amount", "")
        frequency = request.form.get("frequency", "")
        notes = request.form.get("notes", "").strip() or None
        investment_amount_at_time_str = (
            request.form.get("investment_amount_at_time", "").strip() or None
        )
        period_month_str = request.form.get("period_month", "").strip() or None
        period_year_str = request.form.get("period_year", "").strip() or None

        try:
            dividend, investment = dividend_service.create_dividend(
                investment_id_str=investment_id_str,
                amount_str=amount_str,
                frequency=frequency,
                notes=notes,
                investment_amount_at_time_str=investment_amount_at_time_str,
                period_month_str=period_month_str,
                period_year_str=period_year_str,
            )

            # Calculate annualized yield for the message
            period_info = f" for {dividend.period_label}" if dividend.period_label else ""
            flash(
                f"Added {frequency} dividend of {format_currency(dividend.amount)}"
                f"{period_info} to {investment.name}. "
                f"Annualized: {format_currency(dividend.annualized_amount)} "
                f"({investment.calculate_dividend_yield():.2f}% yield)",
                "success",
            )
            logger.info(
                "Dividend added to %s: $%.2f (%s)",
                sanitize_log_input(investment.name),
                dividend.amount,
                sanitize_log_input(frequency),
            )
            return redirect(url_for("investments.view_investment", investment_id=investment.id))

        except ValidationError as e:
            flash(str(e), "error")
            logger.warning("Validation error adding dividend: %s", sanitize_log_input(str(e)))
            return redirect(url_for("dividends.add_dividend"))

        except NotFoundError as e:
            flash(str(e), "error")
            logger.warning(
                "Investment not found when adding dividend: %s", sanitize_log_input(str(e))
            )
            return redirect(url_for("dividends.add_dividend"))

    investments = investment_service.get_all_investments()
    investments_json = [inv.to_dict() for inv in investments]
    selected_investment_id = request.args.get("investment_id")
    current_year = datetime.now().year

    return render_template(
        "add_dividend.html",
        investments=investments,
        investments_json=investments_json,
        selected_investment_id=selected_investment_id,
        current_year=current_year,
    )


@dividends_bp.route("/<int:dividend_id>/edit", methods=["GET", "POST"])
def edit_dividend(dividend_id: int):
    """
    Handle editing an existing dividend record.

    GET: Display the edit dividend form.
    POST: Process the dividend update.

    Args:
        dividend_id: The ID of the dividend to edit.

    Returns:
        GET: Rendered edit_dividend template.
        POST: Redirect to investment view on success.
    """
    dividend_service = DividendService()

    try:
        dividend = dividend_service.get_dividend_by_id(dividend_id)
    except NotFoundError:
        flash("Dividend not found", "error")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        amount_str = request.form.get("amount", "")
        frequency = request.form.get("frequency", "")
        notes = request.form.get("notes", "").strip() or None
        investment_amount_at_time_str = (
            request.form.get("investment_amount_at_time", "").strip() or None
        )
        period_month_str = request.form.get("period_month", "").strip() or None
        period_year_str = request.form.get("period_year", "").strip() or None

        try:
            updated_dividend = dividend_service.update_dividend(
                dividend_id=dividend_id,
                amount_str=amount_str,
                frequency=frequency,
                notes=notes,
                investment_amount_at_time_str=investment_amount_at_time_str,
                period_month_str=period_month_str,
                period_year_str=period_year_str,
            )

            period_info = (
                f" for {updated_dividend.period_label}" if updated_dividend.period_label else ""
            )
            flash(
                f"Updated {frequency} dividend{period_info} "
                f"to {format_currency(updated_dividend.amount)}",
                "success",
            )
            logger.info("Dividend updated (ID: %d)", dividend_id)
            return redirect(
                url_for(
                    "investments.view_investment",
                    investment_id=updated_dividend.investment_id,
                )
            )

        except ValidationError as e:
            flash(str(e), "error")
            logger.warning("Validation error updating dividend: %s", sanitize_log_input(str(e)))

    current_year = datetime.now().year

    return render_template(
        "edit_dividend.html",
        dividend=dividend,
        current_year=current_year,
    )


@dividends_bp.route("/<int:dividend_id>/delete", methods=["POST"])
def delete_dividend(dividend_id: int):
    """
    Delete a dividend record.

    Args:
        dividend_id: The ID of the dividend to delete.

    Returns:
        Redirect to investment view page.
    """
    dividend_service = DividendService()

    try:
        investment_id = dividend_service.delete_dividend(dividend_id)
        flash("Dividend record deleted successfully!", "success")
        logger.info("Dividend deleted (ID: %d)", dividend_id)
        return redirect(url_for("investments.view_investment", investment_id=investment_id))

    except NotFoundError:
        flash("Dividend not found", "error")
        return redirect(url_for("main.index"))
