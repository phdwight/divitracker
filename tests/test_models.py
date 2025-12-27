"""Tests for Investment and Dividend models."""

import pytest

from app.extensions import db
from app.models import (Dividend, DividendFrequency, Investment,
                        InvestmentSummary)


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
        """Test annual dividend calculation sums dividends for the year."""
        from datetime import datetime, timezone

        with app.app_context():
            current_year = datetime.now(timezone.utc).year
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            # Add 12 monthly dividends for current year
            for month in range(1, 13):
                dividend = Dividend(
                    investment_id=investment.id,
                    amount=100.0,
                    frequency="monthly",
                    period_month=month,
                    period_year=current_year,
                )
                db.session.add(dividend)
            db.session.commit()

            assert investment.calculate_annual_dividends() == 1200.0  # 100 * 12 months

    def test_calculate_annual_dividends_quarterly(self, app):
        """Test annual dividend calculation sums quarterly dividends."""
        from datetime import datetime, timezone

        with app.app_context():
            current_year = datetime.now(timezone.utc).year
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            # Add 4 quarterly dividends for current year
            for quarter, month in enumerate([3, 6, 9, 12], start=1):
                dividend = Dividend(
                    investment_id=investment.id,
                    amount=250.0,
                    frequency="quarterly",
                    period_month=month,
                    period_year=current_year,
                )
                db.session.add(dividend)
            db.session.commit()

            assert investment.calculate_annual_dividends() == 1000.0  # 250 * 4 quarters

    def test_calculate_dividend_yield(self, app):
        """Test dividend yield calculation."""
        from datetime import datetime, timezone

        with app.app_context():
            current_year = datetime.now(timezone.utc).year
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            # Add 4 quarterly dividends for current year
            for quarter, month in enumerate([3, 6, 9, 12], start=1):
                dividend = Dividend(
                    investment_id=investment.id,
                    amount=100.0,
                    frequency="quarterly",
                    period_month=month,
                    period_year=current_year,
                )
                db.session.add(dividend)
            db.session.commit()

            # Yield = 400 / 10000 * 100 = 4%
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

    def test_calculate_annual_dividends_multiple_same_frequency(self, app):
        """Test annual dividends sums up when full year of data exists."""
        with app.app_context():
            from datetime import datetime, timedelta

            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            # Add 12 monthly dividends (simulating a year of dividend payments)
            base_date = datetime(2024, 1, 1)
            for i in range(12):
                dividend = Dividend(
                    investment_id=investment.id,
                    amount=100.0,
                    frequency="monthly",
                    date_received=base_date + timedelta(days=30 * i),
                    period_month=i + 1,
                    period_year=2024,
                )
                db.session.add(dividend)
            db.session.commit()

            # With 12 monthly dividends of 100 each, should sum to 1200 for year 2024
            assert investment.calculate_annual_dividends(year=2024) == 1200.0

    def test_calculate_annual_dividends_partial_year(self, app):
        """Test annual dividends returns actual for partial year."""
        with app.app_context():
            from datetime import datetime, timezone

            current_year = datetime.now(timezone.utc).year

            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            # Only 2 monthly dividends for current year (Jan, Feb)
            for i in range(2):
                dividend = Dividend(
                    investment_id=investment.id,
                    amount=100.0,
                    frequency="monthly",
                    date_received=datetime(current_year, i + 1, 1),
                    period_month=i + 1,
                    period_year=current_year,
                )
                db.session.add(dividend)
            db.session.commit()

            # calculate_annual_dividends returns actual total: 200
            assert investment.calculate_annual_dividends() == 200.0
            # calculate_projected_annual_dividends projects for current year: avg(100) * 12 = 1200
            assert investment.calculate_projected_annual_dividends() == 1200.0

    def test_calculate_annual_dividends_varying_amounts(self, app):
        """Test annual dividends with varying dividend amounts."""
        with app.app_context():
            from datetime import datetime, timedelta

            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            # Add 12 monthly dividends with varying amounts
            base_date = datetime(2024, 1, 1)
            amounts = [100, 110, 105, 115, 120, 100, 130, 125, 140, 135, 150, 145]
            for i, amount in enumerate(amounts):
                dividend = Dividend(
                    investment_id=investment.id,
                    amount=amount,
                    frequency="monthly",
                    date_received=base_date + timedelta(days=30 * i),
                    period_month=i + 1,
                    period_year=2024,
                )
                db.session.add(dividend)
            db.session.commit()

            # Should sum all dividends for 2024: 1475
            assert investment.calculate_annual_dividends(year=2024) == sum(amounts)

    def test_get_summary(self, app):
        """Test investment summary generation."""
        from datetime import datetime, timezone

        with app.app_context():
            current_year = datetime.now(timezone.utc).year
            investment = Investment(
                name="Test",
                ticker="TST",
                total_invested=10000.0,
            )
            db.session.add(investment)
            db.session.commit()

            # Add 4 quarterly dividends for current year
            for quarter, month in enumerate([3, 6, 9, 12], start=1):
                dividend = Dividend(
                    investment_id=investment.id,
                    amount=100.0,
                    frequency="quarterly",
                    period_month=month,
                    period_year=current_year,
                )
                db.session.add(dividend)
            db.session.commit()

            summary = investment.get_summary()

            assert isinstance(summary, InvestmentSummary)
            assert summary.total_invested == 10000.0
            assert summary.annual_dividends == 400.0  # 100 * 4
            assert summary.dividend_yield == 4.0
            assert summary.total_received == 400.0

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
            assert data["investment_amount_at_time"] is None
            assert data["yield_at_time"] is None

    def test_to_dict_with_investment_amount_at_time(self, app, sample_investment):
        """Test dividend dictionary conversion with investment amount at time."""
        with app.app_context():
            dividend = Dividend(
                investment_id=sample_investment.id,
                amount=50.0,
                frequency="quarterly",
                investment_amount_at_time=5000.0,
            )
            db.session.add(dividend)
            db.session.commit()

            data = dividend.to_dict()

            assert data["investment_amount_at_time"] == 5000.0
            assert data["yield_at_time"] == pytest.approx(4.0)  # (50 * 4 / 5000) * 100

    def test_yield_at_time_property(self, app, sample_investment):
        """Test yield_at_time property calculation."""
        with app.app_context():
            dividend = Dividend(
                investment_id=sample_investment.id,
                amount=100.0,
                frequency="monthly",
                investment_amount_at_time=10000.0,
            )
            # Yield = (100 * 12 / 10000) * 100 = 12%
            assert dividend.yield_at_time == pytest.approx(12.0)

    def test_yield_at_time_none_when_no_investment_amount(self, app, sample_investment):
        """Test yield_at_time returns None when investment_amount_at_time is not set."""
        with app.app_context():
            dividend = Dividend(
                investment_id=sample_investment.id,
                amount=100.0,
                frequency="monthly",
            )
            assert dividend.yield_at_time is None

    def test_yield_at_time_none_when_investment_amount_is_zero(
        self, app, sample_investment
    ):
        """Test yield_at_time returns None when investment_amount_at_time is zero."""
        with app.app_context():
            dividend = Dividend(
                investment_id=sample_investment.id,
                amount=100.0,
                frequency="monthly",
                investment_amount_at_time=0.0,
            )
            assert dividend.yield_at_time is None


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
