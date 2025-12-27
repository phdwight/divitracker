"""Tests for Investment and Dividend models."""

import pytest
from datetime import datetime

from app.extensions import db
from app.models import Investment, Dividend, DividendFrequency, InvestmentSummary


class TestDividendFrequency:
    """Tests for DividendFrequency enum."""

    def test_monthly_multiplier(self):
        """Test monthly frequency returns 12 as multiplier."""
        assert DividendFrequency.MONTHLY.annual_multiplier == 12

    def test_quarterly_multiplier(self):
        """Test quarterly frequency returns 4 as multiplier."""
        assert DividendFrequency.QUARTERLY.annual_multiplier == 4

    def test_yearly_multiplier(self):
        """Test yearly frequency returns 1 as multiplier."""
        assert DividendFrequency.YEARLY.annual_multiplier == 1


class TestInvestmentModel:
    """Tests for Investment model."""

    def test_create_investment(self, app):
        """Test creating a new investment."""
        with app.app_context():
            investment = Investment(
                name="Apple Inc.",
                ticker="AAPL",
                total_invested=5000.0,
            )
            db.session.add(investment)
            db.session.commit()

            assert investment.id is not None
            assert investment.name == "Apple Inc."
            assert investment.ticker == "AAPL"
            assert investment.total_invested == 5000.0
            assert investment.created_at is not None

    def test_investment_repr(self, app):
        """Test investment string representation."""
        with app.app_context():
            investment = Investment(name="Test", ticker="TST", total_invested=1000.0)
            assert repr(investment) == "<Investment Test (TST)>"

    def test_investment_repr_no_ticker(self, app):
        """Test investment string representation without ticker."""
        with app.app_context():
            investment = Investment(name="Test", total_invested=1000.0)
            assert repr(investment) == "<Investment Test (N/A)>"

    def test_calculate_annual_dividends_monthly(self, app):
        """Test annual dividend calculation for monthly dividends."""
        with app.app_context():
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            dividend = Dividend(
                investment_id=investment.id,
                amount=100.0,
                frequency="monthly",
            )
            db.session.add(dividend)
            db.session.commit()

            assert investment.calculate_annual_dividends() == 1200.0  # 100 * 12

    def test_calculate_annual_dividends_quarterly(self, app):
        """Test annual dividend calculation for quarterly dividends."""
        with app.app_context():
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            dividend = Dividend(
                investment_id=investment.id,
                amount=250.0,
                frequency="quarterly",
            )
            db.session.add(dividend)
            db.session.commit()

            assert investment.calculate_annual_dividends() == 1000.0  # 250 * 4

    def test_calculate_dividend_yield(self, app):
        """Test dividend yield calculation."""
        with app.app_context():
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            dividend = Dividend(
                investment_id=investment.id,
                amount=100.0,
                frequency="quarterly",
            )
            db.session.add(dividend)
            db.session.commit()

            # Yield = (100 * 4) / 10000 * 100 = 4%
            assert investment.calculate_dividend_yield() == 4.0

    def test_calculate_dividend_yield_zero_invested(self, app):
        """Test dividend yield calculation with zero investment."""
        with app.app_context():
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=0.0,
            )
            db.session.add(investment)
            db.session.commit()

            assert investment.calculate_dividend_yield() == 0.0

    def test_get_total_dividends_received(self, app):
        """Test total dividends received calculation."""
        with app.app_context():
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            dividend1 = Dividend(
                investment_id=investment.id,
                amount=100.0,
                frequency="monthly",
            )
            dividend2 = Dividend(
                investment_id=investment.id,
                amount=200.0,
                frequency="quarterly",
            )
            db.session.add_all([dividend1, dividend2])
            db.session.commit()

            assert investment.get_total_dividends_received() == 300.0

    def test_get_summary(self, app):
        """Test investment summary generation."""
        with app.app_context():
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            dividend = Dividend(
                investment_id=investment.id,
                amount=100.0,
                frequency="quarterly",
            )
            db.session.add(dividend)
            db.session.commit()

            summary = investment.get_summary()

            assert isinstance(summary, InvestmentSummary)
            assert summary.total_invested == 10000.0
            assert summary.annual_dividends == 400.0
            assert summary.dividend_yield == 4.0
            assert summary.total_received == 100.0

    def test_to_dict(self, app):
        """Test investment dictionary conversion."""
        with app.app_context():
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=1000.0,
            )
            db.session.add(investment)
            db.session.commit()

            data = investment.to_dict()

            assert data["id"] == investment.id
            assert data["name"] == "Test"
            assert data["ticker"] == "TST"
            assert data["total_invested"] == 1000.0
            assert "created_at" in data


class TestDividendModel:
    """Tests for Dividend model."""

    def test_create_dividend(self, app, sample_investment):
        """Test creating a new dividend."""
        with app.app_context():
            dividend = Dividend(
                investment_id=sample_investment.id,
                amount=50.0,
                frequency="monthly",
                notes="Test note",
            )
            db.session.add(dividend)
            db.session.commit()

            assert dividend.id is not None
            assert dividend.amount == 50.0
            assert dividend.frequency == "monthly"
            assert dividend.notes == "Test note"

    def test_dividend_repr(self, app, sample_investment):
        """Test dividend string representation."""
        with app.app_context():
            dividend = Dividend(
                investment_id=sample_investment.id,
                amount=75.50,
                frequency="quarterly",
            )
            assert repr(dividend) == "<Dividend $75.5 (quarterly)>"

    def test_annualized_amount_monthly(self, app, sample_investment):
        """Test annualized amount for monthly dividend."""
        with app.app_context():
            dividend = Dividend(
                investment_id=sample_investment.id,
                amount=100.0,
                frequency="monthly",
            )
            assert dividend.annualized_amount == 1200.0

    def test_annualized_amount_quarterly(self, app, sample_investment):
        """Test annualized amount for quarterly dividend."""
        with app.app_context():
            dividend = Dividend(
                investment_id=sample_investment.id,
                amount=100.0,
                frequency="quarterly",
            )
            assert dividend.annualized_amount == 400.0

    def test_annualized_amount_yearly(self, app, sample_investment):
        """Test annualized amount for yearly dividend."""
        with app.app_context():
            dividend = Dividend(
                investment_id=sample_investment.id,
                amount=100.0,
                frequency="yearly",
            )
            assert dividend.annualized_amount == 100.0

    def test_to_dict(self, app, sample_investment):
        """Test dividend dictionary conversion."""
        with app.app_context():
            dividend = Dividend(
                investment_id=sample_investment.id,
                amount=50.0,
                frequency="quarterly",
                notes="Test",
            )
            db.session.add(dividend)
            db.session.commit()

            data = dividend.to_dict()

            assert data["id"] == dividend.id
            assert data["investment_id"] == sample_investment.id
            assert data["amount"] == 50.0
            assert data["frequency"] == "quarterly"
            assert data["notes"] == "Test"
            assert data["annualized_amount"] == 200.0


class TestCascadeDelete:
    """Tests for cascade delete behavior."""

    def test_delete_investment_deletes_dividends(self, app):
        """Test that deleting investment deletes associated dividends."""
        with app.app_context():
            investment = Investment(
                name="Cascade Test",
                ticker="CSC",
                total_invested=1000.0,
            )
            db.session.add(investment)
            db.session.commit()

            dividend = Dividend(
                investment_id=investment.id,
                amount=10.0,
                frequency="monthly",
            )
            db.session.add(dividend)
            db.session.commit()

            dividend_id = dividend.id

            db.session.delete(investment)
            db.session.commit()

            # Dividend should be deleted
            assert db.session.get(Dividend, dividend_id) is None
