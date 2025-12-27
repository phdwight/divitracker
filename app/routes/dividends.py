"""Dividend routes blueprint."""

import logging

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.services.dividend_service import DividendService
from app.services.investment_service import InvestmentService
from app.exceptions import ValidationError, NotFoundError

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

        try:
            dividend, investment = dividend_service.create_dividend(
                investment_id_str=investment_id_str,
                amount_str=amount_str,
                frequency=frequency,
                notes=notes,
            )

            # Calculate annualized yield for the message
            flash(
                f"Added {frequency} dividend of ${dividend.amount:.2f} to {investment.name}. "
                f"Annualized: ${dividend.annualized_amount:.2f} "
                f"({investment.calculate_dividend_yield():.2f}% yield)",
                "success",
            )
            logger.info(
                "Dividend added to %s: $%.2f (%s)",
                investment.name,
                dividend.amount,
                frequency,
            )
            return redirect(
                url_for("investments.view_investment", investment_id=investment.id)
            )

        except ValidationError as e:
            flash(str(e), "error")
            logger.warning("Validation error adding dividend: %s", e)
            return redirect(url_for("dividends.add_dividend"))

        except NotFoundError as e:
            flash(str(e), "error")
            logger.warning("Investment not found when adding dividend: %s", e)
            return redirect(url_for("dividends.add_dividend"))

    investments = investment_service.get_all_investments()
    investments_json = [inv.to_dict() for inv in investments]
    selected_investment_id = request.args.get("investment_id")

    return render_template(
        "add_dividend.html",
        investments=investments,
        investments_json=investments_json,
        selected_investment_id=selected_investment_id,
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
