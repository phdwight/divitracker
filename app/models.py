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

    def calculate_annual_dividends(self) -> float:
        """
        Calculate total annualized dividends for this investment.

        Returns:
            Total annual dividend amount based on all dividend records.
        """
        total = 0.0
        for dividend in self.dividends.all():
            frequency = DividendFrequency(dividend.frequency)
            total += dividend.amount * frequency.annual_multiplier
        return total

    def calculate_dividend_yield(self) -> float:
        """
        Calculate annualized dividend yield percentage.

        Returns:
            Dividend yield as a percentage (0.0 if no investment).
        """
        if self.total_invested <= 0:
            return 0.0
        annual_dividends = self.calculate_annual_dividends()
        return (annual_dividends / self.total_invested) * 100

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
            "date_received": self.date_received.isoformat() if self.date_received else None,
            "notes": self.notes,
            "annualized_amount": self.annualized_amount,
        }
