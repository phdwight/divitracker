"""Investment service for business logic operations."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.exceptions import NotFoundError, ValidationError
from app.extensions import db
from app.models import Investment
from app.utils import sanitize_log_input

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class InvestmentService:
    """
    Service class for investment-related business logic.

    Follows Single Responsibility Principle - handles only investment operations.
    """

    def get_all_investments(self) -> Sequence[Investment]:
        """
        Retrieve all investments ordered by name.

        Returns:
            Sequence of Investment objects.
        """
        return Investment.query.order_by(Investment.name).all()

    def get_investment_by_id(self, investment_id: int) -> Investment:
        """
        Retrieve an investment by its ID.

        Args:
            investment_id: The ID of the investment.

        Returns:
            Investment object.

        Raises:
            NotFoundError: If investment is not found.
        """
        investment = db.session.get(Investment, investment_id)
        if investment is None:
            raise NotFoundError(f"Investment with ID {investment_id} not found")
        return investment

    def get_investment_by_name(self, name: str) -> Investment | None:
        """
        Retrieve an investment by its name.

        Args:
            name: The name of the investment.

        Returns:
            Investment object or None if not found.
        """
        return Investment.query.filter_by(name=name).first()

    def create_or_update_investment(
        self,
        name: str,
        ticker: str | None,
        amount_str: str,
    ) -> tuple[Investment, bool]:
        """
        Create a new investment or update an existing one.

        Args:
            name: Investment name.
            ticker: Optional ticker symbol.
            amount_str: Investment amount as string.

        Returns:
            Tuple of (Investment, created) where created is True if new.

        Raises:
            ValidationError: If validation fails.
        """
        # Validate inputs
        self._validate_name(name)
        amount = self._validate_amount(amount_str)

        # Check if investment exists
        existing = self.get_investment_by_name(name)

        if existing:
            existing.total_invested += amount
            if ticker:
                existing.ticker = ticker
            db.session.commit()
            logger.info("Updated investment %s with amount %.2f", sanitize_log_input(name), amount)
            return existing, False

        # Create new investment
        investment = Investment(
            name=name,
            ticker=ticker,
            total_invested=amount,
        )
        db.session.add(investment)
        db.session.commit()
        logger.info("Created new investment: %s", sanitize_log_input(name))
        return investment, True

    def update_investment(
        self,
        investment_id: int,
        name: str,
        ticker: str | None,
        total_invested_str: str,
    ) -> Investment:
        """
        Update an existing investment.

        Args:
            investment_id: ID of the investment to update.
            name: New name.
            ticker: New ticker symbol.
            total_invested_str: New total invested amount as string.

        Returns:
            Updated Investment object.

        Raises:
            NotFoundError: If investment not found.
            ValidationError: If validation fails.
        """
        investment = self.get_investment_by_id(investment_id)

        self._validate_name(name)
        total_invested = self._validate_amount(total_invested_str)

        investment.name = name
        investment.ticker = ticker
        investment.total_invested = total_invested

        db.session.commit()
        logger.info("Updated investment ID %d: %s", investment_id, sanitize_log_input(name))
        return investment

    def delete_investment(self, investment_id: int) -> str:
        """
        Delete an investment and all associated dividends.

        Args:
            investment_id: ID of the investment to delete.

        Returns:
            Name of the deleted investment.

        Raises:
            NotFoundError: If investment not found.
        """
        investment = self.get_investment_by_id(investment_id)
        name = investment.name

        db.session.delete(investment)
        db.session.commit()
        logger.info("Deleted investment: %s (ID: %d)", name, investment_id)
        return name

    @staticmethod
    def _validate_name(name: str) -> None:
        """
        Validate investment name.

        Args:
            name: Name to validate.

        Raises:
            ValidationError: If name is empty.
        """
        if not name or not name.strip():
            raise ValidationError("Investment name is required")

    @staticmethod
    def _validate_amount(amount_str: str) -> float:
        """
        Validate and parse amount string.

        Args:
            amount_str: Amount as string.

        Returns:
            Parsed float amount.

        Raises:
            ValidationError: If amount is invalid or negative.
        """
        try:
            amount = float(amount_str) if amount_str else 0.0
        except ValueError as e:
            raise ValidationError(f"Invalid amount: {amount_str}") from e

        if amount < 0:
            raise ValidationError("Amount cannot be negative")

        return amount
