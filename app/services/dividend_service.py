"""Dividend service for business logic operations."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.extensions import db
from app.models import Dividend, Investment, DividendFrequency
from app.exceptions import ValidationError, NotFoundError

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class DividendService:
    """
    Service class for dividend-related business logic.

    Follows Single Responsibility Principle - handles only dividend operations.
    """

    VALID_FREQUENCIES: frozenset[str] = frozenset(
        freq.value for freq in DividendFrequency
    )

    def get_dividend_by_id(self, dividend_id: int) -> Dividend:
        """
        Retrieve a dividend by its ID.

        Args:
            dividend_id: The ID of the dividend.

        Returns:
            Dividend object.

        Raises:
            NotFoundError: If dividend is not found.
        """
        dividend = db.session.get(Dividend, dividend_id)
        if dividend is None:
            raise NotFoundError(f"Dividend with ID {dividend_id} not found")
        return dividend

    def create_dividend(
        self,
        investment_id_str: str,
        amount_str: str,
        frequency: str,
        notes: str | None = None,
    ) -> tuple[Dividend, Investment]:
        """
        Create a new dividend record.

        Args:
            investment_id_str: Investment ID as string.
            amount_str: Dividend amount as string.
            frequency: Payment frequency (monthly, quarterly, yearly).
            notes: Optional notes.

        Returns:
            Tuple of (Dividend, Investment).

        Raises:
            ValidationError: If validation fails.
            NotFoundError: If investment not found.
        """
        # Validate inputs
        investment_id = self._validate_investment_id(investment_id_str)
        amount = self._validate_amount(amount_str)
        self._validate_frequency(frequency)

        # Get investment
        investment = db.session.get(Investment, investment_id)
        if investment is None:
            raise NotFoundError(f"Investment with ID {investment_id} not found")

        # Create dividend
        dividend = Dividend(
            investment_id=investment_id,
            amount=amount,
            frequency=frequency,
            notes=notes,
        )
        db.session.add(dividend)
        db.session.commit()

        logger.info(
            "Created dividend for investment %s: $%.2f (%s)",
            investment.name,
            amount,
            frequency,
        )
        return dividend, investment

    def delete_dividend(self, dividend_id: int) -> int:
        """
        Delete a dividend record.

        Args:
            dividend_id: ID of the dividend to delete.

        Returns:
            ID of the associated investment.

        Raises:
            NotFoundError: If dividend not found.
        """
        dividend = self.get_dividend_by_id(dividend_id)
        investment_id = dividend.investment_id

        db.session.delete(dividend)
        db.session.commit()

        logger.info("Deleted dividend ID %d", dividend_id)
        return investment_id

    def get_dividends_for_investment(self, investment_id: int) -> list[Dividend]:
        """
        Get all dividends for an investment.

        Args:
            investment_id: The investment ID.

        Returns:
            List of Dividend objects ordered by date descending.
        """
        return (
            Dividend.query.filter_by(investment_id=investment_id)
            .order_by(Dividend.date_received.desc())
            .all()
        )

    @staticmethod
    def _validate_investment_id(investment_id_str: str) -> int:
        """
        Validate and parse investment ID.

        Args:
            investment_id_str: Investment ID as string.

        Returns:
            Parsed integer ID.

        Raises:
            ValidationError: If ID is invalid.
        """
        if not investment_id_str:
            raise ValidationError("Investment selection is required")
        try:
            return int(investment_id_str)
        except ValueError as e:
            raise ValidationError(f"Invalid investment ID: {investment_id_str}") from e

    @staticmethod
    def _validate_amount(amount_str: str) -> float:
        """
        Validate and parse dividend amount.

        Args:
            amount_str: Amount as string.

        Returns:
            Parsed float amount.

        Raises:
            ValidationError: If amount is invalid or not positive.
        """
        if not amount_str:
            raise ValidationError("Dividend amount is required")
        try:
            amount = float(amount_str)
        except ValueError as e:
            raise ValidationError(f"Invalid amount: {amount_str}") from e

        if amount <= 0:
            raise ValidationError("Dividend amount must be positive")

        return amount

    def _validate_frequency(self, frequency: str) -> None:
        """
        Validate dividend frequency.

        Args:
            frequency: Frequency string to validate.

        Raises:
            ValidationError: If frequency is invalid.
        """
        if not frequency:
            raise ValidationError("Dividend frequency is required")
        if frequency not in self.VALID_FREQUENCIES:
            valid = ", ".join(sorted(self.VALID_FREQUENCIES))
            raise ValidationError(
                f"Invalid frequency '{frequency}'. Must be one of: {valid}"
            )
