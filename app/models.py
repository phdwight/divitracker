"""Database models for DiviTracker."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
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
    SEMI_ANNUAL = "semi-annual"
    YEARLY = "yearly"

    @property
    def annual_multiplier(self) -> int:
        """Return the multiplier to annualize the dividend."""
        multipliers = {
            DividendFrequency.MONTHLY: 12,
            DividendFrequency.QUARTERLY: 4,
            DividendFrequency.SEMI_ANNUAL: 2,
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

    def calculate_projected_annual_dividends(self, year: int | None = None) -> float:
        """
        Calculate projected annual dividends for a specific year.

        For past/completed years, returns actual total.
        For current year, projects based on dividend frequency and entries received.

        Args:
            year: The year to calculate for. If None, uses current year.

        Returns:
            Projected annual dividend amount.
        """
        if year is None:
            year = datetime.now(timezone.utc).year

        actual_total = self.calculate_annual_dividends(year)
        current_year = datetime.now(timezone.utc).year

        # For past years, return actual total
        if year < current_year:
            return actual_total

        # For current year, project based on dividend entries
        if actual_total == 0:
            return 0.0

        # Get dividends for this year
        year_dividends = [d for d in self.dividends.all() if d.period_year == year]

        if not year_dividends:
            return actual_total

        # Group by frequency and calculate projection for each
        # Use the most common frequency to determine projection method
        frequency_totals: dict[str, tuple[float, int]] = {}  # frequency -> (total_amount, count)
        for div in year_dividends:
            freq = div.frequency
            if freq not in frequency_totals:
                frequency_totals[freq] = (0.0, 0)
            current_total, current_count = frequency_totals[freq]
            frequency_totals[freq] = (current_total + div.amount, current_count + 1)

        # Calculate projection for each frequency type
        projected_total = 0.0
        for freq, (total_amount, count) in frequency_totals.items():
            try:
                frequency_enum = DividendFrequency(freq)
                expected_per_year = (
                    frequency_enum.annual_multiplier
                )  # 12 for monthly, 4 for quarterly, 1 for yearly

                if count >= expected_per_year:
                    # Full year of data, use actual
                    projected_total += total_amount
                else:
                    # Partial year, project based on entries received
                    avg_per_entry = total_amount / count
                    projected_total += avg_per_entry * expected_per_year
            except ValueError:
                # Unknown frequency, just use actual
                projected_total += total_amount

        return projected_total

    def get_investment_amount_for_year(self, year: int | None = None) -> float:
        """
        Get the investment amount to use for yield calculation for a specific year.

        Uses investment_amount_at_time from the most recent dividend in that year,
        falling back to current total_invested if not available.

        Args:
            year: The year to get investment amount for. If None, uses current year.

        Returns:
            Investment amount to use for yield calculation.
        """
        if year is None:
            year = datetime.now(timezone.utc).year

        # Get dividends for this year, sorted by period_month descending
        year_dividends = [d for d in self.dividends.all() if d.period_year == year]

        if not year_dividends:
            return self.total_invested

        # Sort by period_month descending to get most recent
        year_dividends.sort(key=lambda d: (d.period_month or 0, d.date_received), reverse=True)

        # Use investment_amount_at_time from most recent dividend if available
        most_recent = year_dividends[0]
        if most_recent.investment_amount_at_time and most_recent.investment_amount_at_time > 0:
            return most_recent.investment_amount_at_time

        return self.total_invested

    def calculate_dividend_yield(self, year: int | None = None, projected: bool = False) -> float:
        """
        Calculate dividend yield percentage for a specific year.

        Uses investment_amount_at_time from the most recent dividend in that year
        for more accurate yield calculation.

        Args:
            year: The year to calculate yield for. If None, uses current year.
            projected: If True, uses projected annual dividends for current year.

        Returns:
            Dividend yield as a percentage (0.0 if no investment).
        """
        investment_amount = self.get_investment_amount_for_year(year)
        if investment_amount <= 0:
            return 0.0
        if projected:
            annual_dividends = self.calculate_projected_annual_dividends(year)
        else:
            annual_dividends = self.calculate_annual_dividends(year)
        return (annual_dividends / investment_amount) * 100

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
    investment_amount_at_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    period_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    period_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    date_received: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Relationship
    investment: Mapped["Investment"] = relationship("Investment", back_populates="dividends")

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
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

        if self.frequency == "monthly" and self.period_month:
            return f"{month_names[self.period_month - 1]} {self.period_year}"
        elif self.frequency == "quarterly" and self.period_month:
            quarter = (self.period_month - 1) // 3 + 1
            return f"Q{quarter} {self.period_year}"
        elif self.frequency == "yearly":
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
            "date_received": (self.date_received.isoformat() if self.date_received else None),
            "notes": self.notes,
            "annualized_amount": self.annualized_amount,
            "yield_at_time": self.yield_at_time,
        }
