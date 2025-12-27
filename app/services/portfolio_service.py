"""Portfolio service for aggregate business logic operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.services.investment_service import InvestmentService

if TYPE_CHECKING:
    pass


@dataclass
class PortfolioSummary:
    """Data class representing portfolio-level statistics."""

    total_invested: float
    total_annual_dividends: float
    projected_annual_dividends: float
    overall_yield: float
    projected_yield: float
    investment_count: int


class PortfolioService:
    """
    Service class for portfolio-level business logic.

    Follows Dependency Inversion Principle - depends on abstraction (InvestmentService).
    """

    def __init__(self, investment_service: InvestmentService) -> None:
        """
        Initialize PortfolioService with dependencies.

        Args:
            investment_service: Service for investment operations.
        """
        self._investment_service = investment_service

    def get_portfolio_summary(self, year: int | None = None) -> PortfolioSummary:
        """
        Calculate and return portfolio-level statistics for a specific year.

        Uses investment_amount_at_time from most recent dividends for yield calculation.

        Args:
            year: The year to calculate statistics for. If None, uses current year.

        Returns:
            PortfolioSummary dataclass with aggregated metrics.
        """
        investments = self._investment_service.get_all_investments()

        total_invested = sum(inv.total_invested for inv in investments)
        total_annual_dividends = sum(inv.calculate_annual_dividends(year) for inv in investments)
        projected_annual_dividends = sum(inv.calculate_projected_annual_dividends(year) for inv in investments)

        # For yield, use the investment amounts recorded at time of dividends
        total_investment_for_yield = sum(inv.get_investment_amount_for_year(year) for inv in investments)

        overall_yield = 0.0
        projected_yield = 0.0
        if total_investment_for_yield > 0:
            overall_yield = (total_annual_dividends / total_investment_for_yield) * 100
            projected_yield = (projected_annual_dividends / total_investment_for_yield) * 100

        return PortfolioSummary(
            total_invested=total_invested,
            total_annual_dividends=total_annual_dividends,
            projected_annual_dividends=projected_annual_dividends,
            overall_yield=overall_yield,
            projected_yield=projected_yield,
            investment_count=len(investments),
        )
