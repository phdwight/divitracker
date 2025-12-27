"""Tests for service layer classes."""

import pytest

from app.exceptions import NotFoundError, ValidationError
from app.extensions import db
from app.models import Dividend, Investment
from app.services.dividend_service import DividendService
from app.services.investment_service import InvestmentService
from app.services.portfolio_service import PortfolioService, PortfolioSummary


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

    def test_create_dividend_with_investment_amount_at_time(
        self, app, sample_investment
    ):
        """Test creating a dividend with investment amount at time."""
        with app.app_context():
            service = DividendService()
            dividend, investment = service.create_dividend(
                investment_id_str=str(sample_investment.id),
                amount_str="100",
                frequency="monthly",
                notes="Historical dividend",
                investment_amount_at_time_str="5000",
            )

            assert dividend.amount == 100.0
            assert dividend.frequency == "monthly"
            assert dividend.investment_amount_at_time == 5000.0
            assert dividend.yield_at_time == pytest.approx(
                24.0
            )  # (100 * 12 / 5000) * 100

    def test_create_dividend_with_empty_investment_amount_at_time(
        self, app, sample_investment
    ):
        """Test creating a dividend with empty investment amount at time."""
        with app.app_context():
            service = DividendService()
            dividend, investment = service.create_dividend(
                investment_id_str=str(sample_investment.id),
                amount_str="100",
                frequency="quarterly",
                investment_amount_at_time_str="",
            )

            assert dividend.investment_amount_at_time is None
            assert dividend.yield_at_time is None

    def test_create_dividend_with_zero_investment_amount_at_time(
        self, app, sample_investment
    ):
        """Test creating a dividend with zero investment amount at time stores None."""
        with app.app_context():
            service = DividendService()
            dividend, investment = service.create_dividend(
                investment_id_str=str(sample_investment.id),
                amount_str="100",
                frequency="quarterly",
                investment_amount_at_time_str="0",
            )

            assert dividend.investment_amount_at_time is None
            assert dividend.yield_at_time is None

    def test_create_dividend_invalid_investment_amount_at_time(
        self, app, sample_investment
    ):
        """Test creating dividend with invalid investment amount at time raises ValidationError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(ValidationError) as exc_info:
                service.create_dividend(
                    investment_id_str=str(sample_investment.id),
                    amount_str="100",
                    frequency="monthly",
                    investment_amount_at_time_str="not_a_number",
                )
            assert "invalid" in str(exc_info.value).lower()

    def test_create_dividend_negative_investment_amount_at_time(
        self, app, sample_investment
    ):
        """Test creating dividend with negative investment amount at time raises ValidationError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(ValidationError) as exc_info:
                service.create_dividend(
                    investment_id_str=str(sample_investment.id),
                    amount_str="100",
                    frequency="monthly",
                    investment_amount_at_time_str="-5000",
                )
            assert "negative" in str(exc_info.value).lower()

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

    def test_update_dividend_success(self, app, sample_investment_with_dividend):
        """Test updating a dividend successfully."""
        with app.app_context():
            service = DividendService()
            dividend = Dividend.query.filter_by(
                investment_id=sample_investment_with_dividend.id
            ).first()

            updated = service.update_dividend(
                dividend_id=dividend.id,
                amount_str="150",
                frequency="monthly",
                notes="Updated notes",
                investment_amount_at_time_str="10000",
                period_month_str="8",
                period_year_str="2025",
            )

            assert updated.amount == 150.0
            assert updated.frequency == "monthly"
            assert updated.notes == "Updated notes"
            assert updated.investment_amount_at_time == 10000.0
            assert updated.period_month == 8
            assert updated.period_year == 2025

    def test_update_dividend_not_found(self, app):
        """Test updating non-existent dividend raises NotFoundError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(NotFoundError):
                service.update_dividend(
                    dividend_id=99999,
                    amount_str="100",
                    frequency="monthly",
                )

    def test_update_dividend_invalid_amount(self, app, sample_investment_with_dividend):
        """Test updating dividend with invalid amount raises ValidationError."""
        with app.app_context():
            service = DividendService()
            dividend = Dividend.query.filter_by(
                investment_id=sample_investment_with_dividend.id
            ).first()

            with pytest.raises(ValidationError) as exc_info:
                service.update_dividend(
                    dividend_id=dividend.id,
                    amount_str="not_a_number",
                    frequency="monthly",
                )
            assert "invalid" in str(exc_info.value).lower()

    def test_update_dividend_invalid_frequency(
        self, app, sample_investment_with_dividend
    ):
        """Test updating dividend with invalid frequency raises ValidationError."""
        with app.app_context():
            service = DividendService()
            dividend = Dividend.query.filter_by(
                investment_id=sample_investment_with_dividend.id
            ).first()

            with pytest.raises(ValidationError) as exc_info:
                service.update_dividend(
                    dividend_id=dividend.id,
                    amount_str="100",
                    frequency="weekly",
                )
            assert "invalid frequency" in str(exc_info.value).lower()

    def test_validate_period_month_valid(self, app):
        """Test validating valid period months."""
        with app.app_context():
            service = DividendService()
            assert service._validate_period_month("1") == 1
            assert service._validate_period_month("6") == 6
            assert service._validate_period_month("12") == 12
            assert service._validate_period_month(None) is None
            assert service._validate_period_month("") is None

    def test_validate_period_month_invalid_string(self, app):
        """Test validating invalid period month string raises ValidationError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(ValidationError) as exc_info:
                service._validate_period_month("invalid")
            assert "invalid period month" in str(exc_info.value).lower()

    def test_validate_period_month_out_of_range(self, app):
        """Test validating out-of-range period month raises ValidationError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(ValidationError) as exc_info:
                service._validate_period_month("0")
            assert "between 1 and 12" in str(exc_info.value).lower()

            with pytest.raises(ValidationError) as exc_info:
                service._validate_period_month("13")
            assert "between 1 and 12" in str(exc_info.value).lower()

    def test_validate_period_year_valid(self, app):
        """Test validating valid period years."""
        with app.app_context():
            service = DividendService()
            assert service._validate_period_year("2025") == 2025
            assert service._validate_period_year("1900") == 1900
            assert service._validate_period_year("2100") == 2100
            assert service._validate_period_year(None) is None
            assert service._validate_period_year("") is None

    def test_validate_period_year_invalid_string(self, app):
        """Test validating invalid period year string raises ValidationError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(ValidationError) as exc_info:
                service._validate_period_year("invalid")
            assert "invalid period year" in str(exc_info.value).lower()

    def test_validate_period_year_out_of_range(self, app):
        """Test validating out-of-range period year raises ValidationError."""
        with app.app_context():
            service = DividendService()
            with pytest.raises(ValidationError) as exc_info:
                service._validate_period_year("1899")
            assert "between 1900 and 2100" in str(exc_info.value).lower()

            with pytest.raises(ValidationError) as exc_info:
                service._validate_period_year("2101")
            assert "between 1900 and 2100" in str(exc_info.value).lower()

    def test_get_dividends_for_investment(self, app, sample_investment_with_dividend):
        """Test getting dividends for an investment."""
        with app.app_context():
            service = DividendService()
            dividends = service.get_dividends_for_investment(
                sample_investment_with_dividend.id
            )

            assert len(dividends) == 4  # 4 quarterly dividends from fixture
            assert all(d.amount == 50.0 for d in dividends)


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
            assert summary.projected_annual_dividends == 0.0
            assert summary.overall_yield == 0.0
            assert summary.projected_yield == 0.0
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
        from datetime import datetime, timezone

        with app.app_context():
            current_year = datetime.now(timezone.utc).year
            # Create multiple investments
            inv1 = Investment(name="Inv1", total_invested=10000.0)
            inv2 = Investment(name="Inv2", total_invested=5000.0)
            db.session.add_all([inv1, inv2])
            db.session.commit()

            # Add 4 quarterly dividends for inv1 (100 * 4 = 400)
            for month in [3, 6, 9, 12]:
                div = Dividend(
                    investment_id=inv1.id,
                    amount=100.0,
                    frequency="quarterly",
                    period_month=month,
                    period_year=current_year,
                )
                db.session.add(div)

            # Add 12 monthly dividends for inv2 (50 * 12 = 600)
            for month in range(1, 13):
                div = Dividend(
                    investment_id=inv2.id,
                    amount=50.0,
                    frequency="monthly",
                    period_month=month,
                    period_year=current_year,
                )
                db.session.add(div)
            db.session.commit()

            investment_service = InvestmentService()
            service = PortfolioService(investment_service)

            summary = service.get_portfolio_summary()

            assert summary.total_invested == 15000.0
            # 400 + 600 = 1000
            assert summary.total_annual_dividends == 1000.0
            # 1000 / 15000 * 100 = 6.666...
            assert abs(summary.overall_yield - 6.666666666666667) < 0.001
            assert summary.investment_count == 2
