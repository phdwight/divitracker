"""Database models for DiviTracker."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

if TYPE_CHECKING:
    pass


def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


class DividendFrequency(Enum):
    """Enumeration of dividend payment frequencies."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

    @property
    def annual_multiplier(self) -> int:
        """Return the multiplier to annualize the dividend."""
        multipliers = {
            DividendFrequency.MONTHLY: 12,
            DividendFrequency.QUARTERLY: 4,
            DividendFrequency.YEARLY: 1,
        }
        return multipliers[self]


@dataclass
class InvestmentSummary:
    """Data class for investment summary statistics."""

    total_invested: float
    annual_dividends: float
    dividend_yield: float
    total_received: float


class Investment(db.Model):
    """Model representing an investment holding."""

    __tablename__ = "investments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    ticker: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    total_invested: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )

    # Relationship
    dividends: Mapped[list["Dividend"]] = relationship(
        "Dividend",
        back_populates="investment",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the investment."""
        return f"<Investment {self.name} ({self.ticker or 'N/A'})>"

    def calculate_annual_dividends(self, year: int | None = None) -> float:
        """
        Calculate total dividends for a specific year.

        Args:
            year: The year to calculate dividends for. If None, uses current year.

        Returns:
            Total dividend amount for the specified year.
        """
        if year is None:
            year = datetime.now(timezone.utc).year

        all_dividends = self.dividends.all()
        
        # Sum dividends for the specified year based on period_year
        total = 0.0
        for dividend in all_dividends:
            if dividend.period_year == year:
                total += dividend.amount
        
        return total

    def calculate_dividend_yield(self, year: int | None = None) -> float:
        """
        Calculate dividend yield percentage for a specific year.

        Args:
            year: The year to calculate yield for. If None, uses current year.

        Returns:
            Dividend yield as a percentage (0.0 if no investment).
        """
        if self.total_invested <= 0:
            return 0.0
        annual_dividends = self.calculate_annual_dividends(year)
        return (annual_dividends / self.total_invested) * 100

    def get_years_with_dividends(self) -> list[int]:
        """
        Get list of years that have dividend records.

        Returns:
            List of years sorted in descending order.
        """
        years = set()
        for dividend in self.dividends.all():
            if dividend.period_year:
                years.add(dividend.period_year)
        return sorted(years, reverse=True)

    def get_total_dividends_received(self) -> float:
        """
        Get total dividends received to date.

        Returns:
            Sum of all dividend amounts.
        """
        return sum(d.amount for d in self.dividends.all())

    def get_summary(self) -> InvestmentSummary:
        """
        Get a complete summary of the investment.

        Returns:
            InvestmentSummary dataclass with all calculated metrics.
        """
        return InvestmentSummary(
            total_invested=self.total_invested,
            annual_dividends=self.calculate_annual_dividends(),
            dividend_yield=self.calculate_dividend_yield(),
            total_received=self.get_total_dividends_received(),
        )

    def to_dict(self) -> dict:
        """
        Convert investment to dictionary representation.

        Returns:
            Dictionary with investment data.
        """
        return {
            "id": self.id,
            "name": self.name,
            "ticker": self.ticker,
            "total_invested": self.total_invested,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Dividend(db.Model):
    """Model representing a dividend payment record."""

    __tablename__ = "dividends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    investment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("investments.id"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    investment_amount_at_time: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    period_month: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    period_year: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    date_received: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Relationship
    investment: Mapped["Investment"] = relationship(
        "Investment", back_populates="dividends"
    )

    def __repr__(self) -> str:
        """Return string representation of the dividend."""
        return f"<Dividend ${self.amount} ({self.frequency})>"

    @property
    def annualized_amount(self) -> float:
        """
        Calculate the annualized amount for this dividend.

        Returns:
            Dividend amount multiplied by frequency multiplier.
        """
        frequency = DividendFrequency(self.frequency)
        return self.amount * frequency.annual_multiplier

    @property
    def yield_at_time(self) -> Optional[float]:
        """
        Calculate the yield percentage at the time the dividend was recorded.

        Returns:
            Yield percentage or None if investment amount was not recorded.
        """
        if self.investment_amount_at_time and self.investment_amount_at_time > 0:
            return (self.annualized_amount / self.investment_amount_at_time) * 100
        return None

    @property
    def period_label(self) -> Optional[str]:
        """
        Get a formatted label for the dividend period.

        Returns:
            Formatted period string (e.g., 'Jan 2025', 'Q1 2025') or None.
        """
        if not self.period_year:
            return None

        month_names = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]

        if self.frequency == 'monthly' and self.period_month:
            return f"{month_names[self.period_month - 1]} {self.period_year}"
        elif self.frequency == 'quarterly' and self.period_month:
            quarter = (self.period_month - 1) // 3 + 1
            return f"Q{quarter} {self.period_year}"
        elif self.frequency == 'yearly':
            return str(self.period_year)
        elif self.period_month:
            return f"{month_names[self.period_month - 1]} {self.period_year}"
        else:
            return str(self.period_year)

    def to_dict(self) -> dict:
        """
        Convert dividend to dictionary representation.

        Returns:
            Dictionary with dividend data.
        """
        return {
            "id": self.id,
            "investment_id": self.investment_id,
            "amount": self.amount,
            "frequency": self.frequency,
            "investment_amount_at_time": self.investment_amount_at_time,
            "period_month": self.period_month,
            "period_year": self.period_year,
            "period_label": self.period_label,
            "date_received": self.date_received.isoformat() if self.date_received else None,
            "notes": self.notes,
            "annualized_amount": self.annualized_amount,
            "yield_at_time": self.yield_at_time,
        }
