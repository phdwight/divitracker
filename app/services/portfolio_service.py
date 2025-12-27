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
    overall_yield: float
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

    def get_portfolio_summary(self) -> PortfolioSummary:
        """
        Calculate and return portfolio-level statistics.

        Returns:
            PortfolioSummary dataclass with aggregated metrics.
        """
        investments = self._investment_service.get_all_investments()

        total_invested = sum(inv.total_invested for inv in investments)
        total_annual_dividends = sum(inv.calculate_annual_dividends() for inv in investments)

        overall_yield = 0.0
        if total_invested > 0:
            overall_yield = (total_annual_dividends / total_invested) * 100

        return PortfolioSummary(
            total_invested=total_invested,
            total_annual_dividends=total_annual_dividends,
            overall_yield=overall_yield,
            investment_count=len(investments),
        )
