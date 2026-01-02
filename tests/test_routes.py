"""Tests for Flask routes."""

from app.extensions import db
from app.models import Dividend, Investment


class TestErrorHandlers:
    """Tests for error handlers."""

    def test_404_page_not_found(self, client):
        """Test that 404 error page is displayed for non-existent routes."""
        response = client.get("/this-page-does-not-exist")
        assert response.status_code == 404
        assert b"404" in response.data
        assert b"Page Not Found" in response.data

    def test_404_has_navigation_links(self, client):
        """Test that 404 page includes navigation links."""
        response = client.get("/non-existent-page")
        assert response.status_code == 404
        # Should have a link back to dashboard
        assert b"Dashboard" in response.data or b'href="/"' in response.data

    def test_404_invalid_route_with_numbers(self, client):
        """Test 404 for invalid route with numeric segments."""
        response = client.get("/settings/99999/nonexistent")
        assert response.status_code == 404

    def test_404_shows_error_icon(self, client):
        """Test that 404 page shows an error icon."""
        response = client.get("/does-not-exist")
        assert response.status_code == 404
        # Error icon is part of the error page template
        assert b"error-icon" in response.data


class TestMainRoutes:
    """Tests for main blueprint routes."""

    def test_index_page_loads(self, client):
        """Test that the index page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"DiviTracker" in response.data

    def test_index_shows_empty_state(self, client):
        """Test that index shows empty state when no investments."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"No investments yet" in response.data

    def test_index_shows_investments(self, client, app, sample_investment):
        """Test that index shows investments when they exist."""
        # hide_zero=false needed because sample_investment has no dividends
        response = client.get("/?hide_zero=false")
        assert response.status_code == 200
        assert b"Test Investment" in response.data

    def test_yield_breakdown_page_loads(self, client):
        """Test that the yield breakdown page loads successfully."""
        response = client.get("/reports/yield-breakdown")
        assert response.status_code == 200
        assert b"Annualized Yield Calculation" in response.data

    def test_yield_breakdown_with_year_param(self, client):
        """Test yield breakdown page with year parameter."""
        response = client.get("/reports/yield-breakdown?year=2025")
        assert response.status_code == 200
        assert b"2025" in response.data

    def test_yield_breakdown_shows_formula(self, client):
        """Test that yield breakdown shows the calculation formula."""
        response = client.get("/reports/yield-breakdown")
        assert response.status_code == 200
        assert b"Total Dividends Received" in response.data
        assert b"Total Investment Amount" in response.data

    def test_yield_breakdown_with_investments(self, client, app, sample_investment):
        """Test yield breakdown with existing investments."""
        response = client.get("/reports/yield-breakdown")
        assert response.status_code == 200
        assert b"Test Investment" in response.data


class TestDividendGraphRoutes:
    """Tests for dividend graph routes."""

    def test_dividend_graph_page_loads(self, client):
        """Test that the dividend graph page loads successfully."""
        response = client.get("/reports/dividends-chart")
        assert response.status_code == 200
        assert b"Dividend Graph" in response.data

    def test_dividend_graph_with_year_filter(self, client):
        """Test dividend graph page with year filter."""
        response = client.get("/reports/dividends-chart?year=2025")
        assert response.status_code == 200
        assert b"2025" in response.data

    def test_dividend_graph_with_investment_filter(self, client, sample_investment):
        """Test dividend graph page with investment filter."""
        response = client.get(f"/reports/dividends-chart?investment_id={sample_investment.id}")
        assert response.status_code == 200
        assert b"Dividend Graph" in response.data

    def test_dividend_graph_shows_chart(self, client):
        """Test that dividend graph shows the chart container."""
        response = client.get("/reports/dividends-chart")
        assert response.status_code == 200
        assert b"dividendChart" in response.data

    def test_dividend_graph_with_data(self, client, sample_investment_with_dividend):
        """Test dividend graph with actual dividend data."""
        response = client.get("/reports/dividends-chart")
        assert response.status_code == 200
        assert b"chart_data" in response.data or b"chartData" in response.data

    def test_dividend_graph_has_cumulative_toggle(self, client):
        """Test that dividend graph has cumulative line toggle."""
        response = client.get("/reports/dividends-chart")
        assert response.status_code == 200
        assert b"Show Cumulative Line" in response.data
        assert b"showCumulative" in response.data

    def test_dividend_graph_cumulative_chart_elements(self, client):
        """Test that dividend graph has cumulative chart configuration."""
        response = client.get("/reports/dividends-chart")
        assert response.status_code == 200
        assert b"Cumulative Total" in response.data
        assert b"toggleCumulative" in response.data

    def test_dividend_graph_summary_cards(self, client):
        """Test that dividend graph shows Total Displayed and Highest summary cards."""
        response = client.get("/reports/dividends-chart")
        assert response.status_code == 200
        assert b"Total Displayed" in response.data
        assert b"Highest" in response.data
        # Average should not be present (removed)
        assert b">Average<" not in response.data


class TestPagination:
    """Tests for pagination functionality."""

    def test_index_pagination_default(self, client, app, sample_investment):
        """Test that index page has pagination controls."""
        response = client.get("/?hide_zero=false")
        assert response.status_code == 200
        # Page should load successfully with default pagination

    def test_index_pagination_with_page_param(self, client, app, sample_investment):
        """Test index page with page parameter."""
        response = client.get("/?page=1&hide_zero=false")
        assert response.status_code == 200
        assert b"Test Investment" in response.data

    def test_index_pagination_with_per_page_param(self, client, app, sample_investment):
        """Test index page with per_page parameter."""
        response = client.get("/?per_page=5&hide_zero=false")
        assert response.status_code == 200
        assert b"Test Investment" in response.data

    def test_view_investment_pagination(self, client, sample_investment_with_dividend):
        """Test that view investment page has pagination for dividends."""
        response = client.get(f"/investments/{sample_investment_with_dividend.id}")
        assert response.status_code == 200
        # Should show dividend history

    def test_view_investment_dividend_table_columns(self, client, sample_investment_with_dividend):
        """Test that dividend history table has correct columns (Date Received removed)."""
        response = client.get(f"/investments/{sample_investment_with_dividend.id}")
        assert response.status_code == 200
        # Should have these columns
        assert b"Period" in response.data
        assert b"Amount" in response.data
        assert b"Frequency" in response.data
        # Date Received column should NOT be present
        assert b">Date Received<" not in response.data

    def test_view_investment_pagination_with_params(self, client, sample_investment_with_dividend):
        """Test view investment page with pagination parameters."""
        response = client.get(
            f"/investments/{sample_investment_with_dividend.id}?page=1&per_page=10"
        )
        assert response.status_code == 200


class TestHideZeroDividendsFilter:
    """Tests for hide zero dividends filter."""

    def test_index_hide_zero_dividends_default(self, client, app, sample_investment):
        """Test that hide zero dividends filter is on by default."""
        response = client.get("/")
        assert response.status_code == 200
        # Investment with no dividends should be hidden by default

    def test_index_show_all_investments(self, client, app, sample_investment):
        """Test showing all investments when hide_zero is false."""
        response = client.get("/?hide_zero=false")
        assert response.status_code == 200
        assert b"Test Investment" in response.data

    def test_index_hide_zero_checkbox(self, client, app, sample_investment):
        """Test that hide zero dividends checkbox is present."""
        response = client.get("/?hide_zero=false")
        assert response.status_code == 200
        assert b"Hide zero dividends" in response.data


class TestInvestmentRoutes:
    """Tests for investment blueprint routes."""

    def test_add_investment_page_loads(self, client):
        """Test that add investment page loads."""
        response = client.get("/investments/new")
        assert response.status_code == 200
        assert b"Add Investment" in response.data

    def test_add_new_investment(self, client, app):
        """Test adding a new investment via POST."""
        response = client.post(
            "/investments/new",
            data={
                "name": "Apple Inc.",
                "ticker": "AAPL",
                "amount": "5000",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Created new investment" in response.data

        with app.app_context():
            investment = Investment.query.filter_by(name="Apple Inc.").first()
            assert investment is not None
            assert investment.ticker == "AAPL"
            assert investment.total_invested == 5000.0

    def test_add_to_existing_investment(self, client, app, sample_investment):
        """Test adding amount to existing investment."""
        response = client.post(
            "/investments/new",
            data={
                "name": "Test Investment",
                "ticker": "TEST",
                "amount": "2000",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Added" in response.data

        with app.app_context():
            investment = Investment.query.filter_by(name="Test Investment").first()
            assert investment.total_invested == 12000.0  # 10000 + 2000

    def test_add_investment_empty_name(self, client):
        """Test adding investment with empty name shows error."""
        response = client.post(
            "/investments/new",
            data={
                "name": "",
                "ticker": "TEST",
                "amount": "1000",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"required" in response.data.lower()

    def test_view_investment(self, client, sample_investment):
        """Test viewing investment details."""
        response = client.get(f"/investments/{sample_investment.id}")
        assert response.status_code == 200
        assert b"Test Investment" in response.data
        assert b"TEST" in response.data

    def test_view_investment_not_found(self, client):
        """Test viewing non-existent investment redirects."""
        response = client.get("/investments/99999", follow_redirects=True)
        assert response.status_code == 200
        assert b"not found" in response.data.lower()

    def test_edit_investment_page_loads(self, client, sample_investment):
        """Test edit investment page loads."""
        response = client.get(f"/investments/{sample_investment.id}/edit")
        assert response.status_code == 200
        assert b"Edit Investment" in response.data
        assert b"Test Investment" in response.data

    def test_edit_investment(self, client, app, sample_investment):
        """Test editing an investment."""
        response = client.post(
            f"/investments/{sample_investment.id}/edit",
            data={
                "name": "Updated Investment",
                "ticker": "UPD",
                "amount": "15000",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"updated successfully" in response.data.lower()

        with app.app_context():
            investment = db.session.get(Investment, sample_investment.id)
            assert investment.name == "Updated Investment"
            assert investment.ticker == "UPD"
            assert investment.total_invested == 15000.0

    def test_delete_investment(self, client, app, sample_investment):
        """Test deleting an investment."""
        inv_id = sample_investment.id
        response = client.post(
            f"/investments/{inv_id}/delete",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"deleted successfully" in response.data.lower()

        with app.app_context():
            assert db.session.get(Investment, inv_id) is None

    def test_api_investments(self, client, sample_investment):
        """Test API endpoint returns investment data."""
        response = client.get("/investments/api")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Investment"
        assert data[0]["ticker"] == "TEST"


class TestDividendRoutes:
    """Tests for dividend blueprint routes."""

    def test_add_dividend_page_loads(self, client, sample_investment):
        """Test add dividend page loads."""
        response = client.get("/dividends/new")
        assert response.status_code == 200
        assert b"Record Dividend" in response.data

    def test_add_dividend_page_no_investments(self, client):
        """Test add dividend page shows message when no investments."""
        response = client.get("/dividends/new")
        assert response.status_code == 200
        assert b"No investments found" in response.data

    def test_add_dividend_with_preselected(self, client, sample_investment):
        """Test add dividend page with preselected investment."""
        response = client.get(f"/dividends/new?investment_id={sample_investment.id}")
        assert response.status_code == 200
        assert b"selected" in response.data.lower()

    def test_add_dividend(self, client, app, sample_investment):
        """Test adding a dividend."""
        response = client.post(
            "/dividends/new",
            data={
                "investment_id": str(sample_investment.id),
                "amount": "100",
                "frequency": "quarterly",
                "notes": "Q4 2025",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Added quarterly dividend" in response.data

        with app.app_context():
            dividend = Dividend.query.filter_by(investment_id=sample_investment.id).first()
            assert dividend is not None
            assert dividend.amount == 100.0
            assert dividend.frequency == "quarterly"
            assert dividend.notes == "Q4 2025"

    def test_add_dividend_missing_investment(self, client):
        """Test adding dividend without selecting investment shows error."""
        response = client.post(
            "/dividends/new",
            data={
                "investment_id": "",
                "amount": "100",
                "frequency": "monthly",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"required" in response.data.lower()

    def test_add_dividend_invalid_frequency(self, client, sample_investment):
        """Test adding dividend with invalid frequency shows error."""
        response = client.post(
            "/dividends/new",
            data={
                "investment_id": str(sample_investment.id),
                "amount": "100",
                "frequency": "weekly",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"invalid" in response.data.lower()

    def test_delete_dividend(self, client, app, sample_investment_with_dividend):
        """Test deleting a dividend."""
        with app.app_context():
            dividend = Dividend.query.filter_by(
                investment_id=sample_investment_with_dividend.id
            ).first()
            div_id = dividend.id

        response = client.post(
            f"/dividends/{div_id}/delete",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"deleted successfully" in response.data.lower()

        with app.app_context():
            assert db.session.get(Dividend, div_id) is None

    def test_delete_dividend_not_found(self, client):
        """Test deleting non-existent dividend shows error."""
        response = client.post(
            "/dividends/99999/delete",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"not found" in response.data.lower()

    def test_edit_dividend_page_loads(self, client, app, sample_investment_with_dividend):
        """Test edit dividend page loads correctly."""
        with app.app_context():
            dividend = Dividend.query.filter_by(
                investment_id=sample_investment_with_dividend.id
            ).first()
            div_id = dividend.id
            div_amount = dividend.amount

        response = client.get(f"/dividends/{div_id}/edit")
        assert response.status_code == 200
        assert b"Edit Dividend" in response.data
        assert str(div_amount).encode() in response.data

    def test_edit_dividend_page_not_found(self, client):
        """Test edit dividend page with non-existent dividend shows error."""
        response = client.get(
            "/dividends/99999/edit",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"not found" in response.data.lower()

    def test_edit_dividend_post_success(self, client, app, sample_investment_with_dividend):
        """Test updating a dividend via POST."""
        with app.app_context():
            dividend = Dividend.query.filter_by(
                investment_id=sample_investment_with_dividend.id
            ).first()
            div_id = dividend.id

        response = client.post(
            f"/dividends/{div_id}/edit",
            data={
                "amount": "75",
                "frequency": "monthly",
                "notes": "Updated dividend",
                "period_month": "6",
                "period_year": "2025",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Updated monthly dividend" in response.data

        with app.app_context():
            updated_dividend = db.session.get(Dividend, div_id)
            assert updated_dividend.amount == 75.0
            assert updated_dividend.frequency == "monthly"
            assert updated_dividend.notes == "Updated dividend"
            assert updated_dividend.period_month == 6
            assert updated_dividend.period_year == 2025

    def test_edit_dividend_post_validation_error(
        self, client, app, sample_investment_with_dividend
    ):
        """Test updating dividend with invalid data shows error."""
        with app.app_context():
            dividend = Dividend.query.filter_by(
                investment_id=sample_investment_with_dividend.id
            ).first()
            div_id = dividend.id

        response = client.post(
            f"/dividends/{div_id}/edit",
            data={
                "amount": "invalid",
                "frequency": "monthly",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"invalid" in response.data.lower()

    def test_edit_dividend_with_investment_amount_at_time(
        self, client, app, sample_investment_with_dividend
    ):
        """Test updating dividend with investment amount at time."""
        with app.app_context():
            dividend = Dividend.query.filter_by(
                investment_id=sample_investment_with_dividend.id
            ).first()
            div_id = dividend.id

        response = client.post(
            f"/dividends/{div_id}/edit",
            data={
                "amount": "100",
                "frequency": "quarterly",
                "investment_amount_at_time": "8000",
                "period_month": "3",
                "period_year": "2025",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Updated quarterly dividend" in response.data

        with app.app_context():
            updated_dividend = db.session.get(Dividend, div_id)
            assert updated_dividend.investment_amount_at_time == 8000.0
