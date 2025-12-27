"""Tests for service layer classes."""

import pytest

from app.extensions import db
from app.models import Investment, Dividend
from app.services.investment_service import InvestmentService
from app.services.dividend_service import DividendService
from app.services.portfolio_service import PortfolioService, PortfolioSummary
from app.exceptions import ValidationError, NotFoundError


class TestInvestmentService:
    """Tests for InvestmentService."""

    def test_get_all_investments_empty(self, app):
        """Test getting all investments when none exist."""
        with app.app_context():
            service = InvestmentService()
            investments = service.get_all_investments()
            assert list(investments) == []

    def test_get_all_investments(self, app, sample_investment):
        """Test getting all investments."""
        with app.app_context():
            service = InvestmentService()
            investments = service.get_all_investments()
            assert len(investments) == 1
            assert investments[0].name == "Test Investment"

    def test_get_investment_by_id(self, app, sample_investment):
        """Test getting investment by ID."""
        with app.app_context():
            service = InvestmentService()
            investment = service.get_investment_by_id(sample_investment.id)
            assert investment.name == "Test Investment"

    def test_get_investment_by_id_not_found(self, app):
        """Test getting non-existent investment raises NotFoundError."""
        with app.app_context():
            service = InvestmentService()
            with pytest.raises(NotFoundError):
                service.get_investment_by_id(99999)

    def test_get_investment_by_name(self, app, sample_investment):
        """Test getting investment by name."""
        with app.app_context():
            service = InvestmentService()
            investment = service.get_investment_by_name("Test Investment")
            assert investment is not None
            assert investment.ticker == "TEST"

    def test_get_investment_by_name_not_found(self, app):
        """Test getting non-existent investment by name returns None."""
        with app.app_context():
            service = InvestmentService()
            investment = service.get_investment_by_name("Non-existent")
            assert investment is None

    def test_create_new_investment(self, app):
        """Test creating a new investment."""
        with app.app_context():
            service = InvestmentService()
            investment, created = service.create_or_update_investment(
                name="New Investment",
                ticker="NEW",
                amount_str="5000",
            )

            assert created is True
            assert investment.name == "New Investment"
            assert investment.ticker == "NEW"
            assert investment.total_invested == 5000.0

    def test_update_existing_investment(self, app, sample_investment):
        """Test updating an existing investment adds to total."""
        with app.app_context():
            service = InvestmentService()
            original_amount = sample_investment.total_invested

            investment, created = service.create_or_update_investment(
                name="Test Investment",
                ticker="TEST",
                amount_str="2000",
            )

            assert created is False
            assert investment.total_invested == original_amount + 2000.0

    def test_create_investment_empty_name_raises_error(self, app):
        """Test creating investment with empty name raises ValidationError."""
        with app.app_context():
            service = InvestmentService()
            with pytest.raises(ValidationError) as exc_info:
                service.create_or_update_investment(
                    name="",
                    ticker="TEST",
                    amount_str="1000",
                )
            assert "required" in str(exc_info.value).lower()

    def test_create_investment_invalid_amount_raises_error(self, app):
        """Test creating investment with invalid amount raises ValidationError."""
        with app.app_context():
            service = InvestmentService()
            with pytest.raises(ValidationError) as exc_info:
                service.create_or_update_investment(
                    name="Test",
                    ticker="TEST",
                    amount_str="not_a_number",
                )
            assert "invalid" in str(exc_info.value).lower()

    def test_create_investment_negative_amount_raises_error(self, app):
        """Test creating investment with negative amount raises ValidationError."""
        with app.app_context():
            service = InvestmentService()
            with pytest.raises(ValidationError) as exc_info:
                service.create_or_update_investment(
                    name="Test",
                    ticker="TEST",
                    amount_str="-1000",
                )
            assert "negative" in str(exc_info.value).lower()

    def test_update_investment(self, app, sample_investment):
        """Test updating investment details."""
        with app.app_context():
            service = InvestmentService()
            updated = service.update_investment(
                investment_id=sample_investment.id,
                name="Updated Name",
                ticker="UPD",
                total_invested_str="15000",
            )

            assert updated.name == "Updated Name"
            assert updated.ticker == "UPD"
            assert updated.total_invested == 15000.0

    def test_delete_investment(self, app, sample_investment):
        """Test deleting an investment."""
        with app.app_context():
            service = InvestmentService()
            inv_id = sample_investment.id
            name = service.delete_investment(inv_id)

            assert name == "Test Investment"
            assert db.session.get(Investment, inv_id) is None

    def test_delete_investment_not_found(self, app):
        """Test deleting non-existent investment raises NotFoundError."""
        with app.app_context():
            service = InvestmentService()
            with pytest.raises(NotFoundError):
                service.delete_investment(99999)


class TestDividendService:
    """Tests for DividendService."""

    def test_create_dividend(self, app, sample_investment):
        """Test creating a dividend."""
        with app.app_context():
            service = DividendService()
            dividend, investment = service.create_dividend(
                investment_id_str=str(sample_investment.id),
                amount_str="100",
                frequency="quarterly",
                notes="Q1 dividend",
            )

            assert dividend.amount == 100.0
            assert dividend.frequency == "quarterly"
            assert dividend.notes == "Q1 dividend"
            assert investment.id == sample_investment.id

    def test_create_dividend_missing_investment_id(self, app):
        """Test creating dividend without investment ID raises ValidationError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(ValidationError) as exc_info:
                service.create_dividend(
                    investment_id_str="",
                    amount_str="100",
                    frequency="monthly",
                )
            assert "required" in str(exc_info.value).lower()

    def test_create_dividend_missing_amount(self, app, sample_investment):
        """Test creating dividend without amount raises ValidationError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(ValidationError) as exc_info:
                service.create_dividend(
                    investment_id_str=str(sample_investment.id),
                    amount_str="",
                    frequency="monthly",
                )
            assert "required" in str(exc_info.value).lower()

    def test_create_dividend_zero_amount(self, app, sample_investment):
        """Test creating dividend with zero amount raises ValidationError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(ValidationError) as exc_info:
                service.create_dividend(
                    investment_id_str=str(sample_investment.id),
                    amount_str="0",
                    frequency="monthly",
                )
            assert "positive" in str(exc_info.value).lower()

    def test_create_dividend_invalid_frequency(self, app, sample_investment):
        """Test creating dividend with invalid frequency raises ValidationError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(ValidationError) as exc_info:
                service.create_dividend(
                    investment_id_str=str(sample_investment.id),
                    amount_str="100",
                    frequency="weekly",
                )
            assert "invalid frequency" in str(exc_info.value).lower()

    def test_create_dividend_investment_not_found(self, app):
        """Test creating dividend for non-existent investment raises NotFoundError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(NotFoundError):
                service.create_dividend(
                    investment_id_str="99999",
                    amount_str="100",
                    frequency="monthly",
                )

    def test_delete_dividend(self, app, sample_investment_with_dividend):
        """Test deleting a dividend."""
        with app.app_context():
            service = DividendService()
            dividend = Dividend.query.filter_by(
                investment_id=sample_investment_with_dividend.id
            ).first()

            investment_id = service.delete_dividend(dividend.id)

            assert investment_id == sample_investment_with_dividend.id
            assert db.session.get(Dividend, dividend.id) is None

    def test_delete_dividend_not_found(self, app):
        """Test deleting non-existent dividend raises NotFoundError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(NotFoundError):
                service.delete_dividend(99999)

    def test_get_dividends_for_investment(self, app, sample_investment_with_dividend):
        """Test getting dividends for an investment."""
        with app.app_context():
            service = DividendService()
            dividends = service.get_dividends_for_investment(
                sample_investment_with_dividend.id
            )

            assert len(dividends) == 1
            assert dividends[0].amount == 50.0


class TestPortfolioService:
    """Tests for PortfolioService."""

    def test_get_portfolio_summary_empty(self, app):
        """Test portfolio summary with no investments."""
        with app.app_context():
            investment_service = InvestmentService()
            service = PortfolioService(investment_service)

            summary = service.get_portfolio_summary()

            assert isinstance(summary, PortfolioSummary)
            assert summary.total_invested == 0.0
            assert summary.total_annual_dividends == 0.0
            assert summary.overall_yield == 0.0
            assert summary.investment_count == 0

    def test_get_portfolio_summary_with_investments(
        self, app, sample_investment_with_dividend
    ):
        """Test portfolio summary with investments and dividends."""
        with app.app_context():
            investment_service = InvestmentService()
            service = PortfolioService(investment_service)

            summary = service.get_portfolio_summary()

            assert summary.total_invested == 5000.0
            assert summary.total_annual_dividends == 200.0  # 50 * 4 (quarterly)
            assert summary.overall_yield == 4.0  # 200 / 5000 * 100
            assert summary.investment_count == 1

    def test_get_portfolio_summary_multiple_investments(self, app):
        """Test portfolio summary with multiple investments."""
        with app.app_context():
            # Create multiple investments
            inv1 = Investment(name="Inv1", total_invested=10000.0)
            inv2 = Investment(name="Inv2", total_invested=5000.0)
            db.session.add_all([inv1, inv2])
            db.session.commit()

            div1 = Dividend(investment_id=inv1.id, amount=100.0, frequency="quarterly")
            div2 = Dividend(investment_id=inv2.id, amount=50.0, frequency="monthly")
            db.session.add_all([div1, div2])
            db.session.commit()

            investment_service = InvestmentService()
            service = PortfolioService(investment_service)

            summary = service.get_portfolio_summary()

            assert summary.total_invested == 15000.0
            # 100*4 + 50*12 = 400 + 600 = 1000
            assert summary.total_annual_dividends == 1000.0
            # 1000 / 15000 * 100 = 6.666...
            assert abs(summary.overall_yield - 6.666666666666667) < 0.001
            assert summary.investment_count == 2
