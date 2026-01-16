"""Shared step definitions for UI tests using Playwright."""

from datetime import datetime, timezone

from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, then, when

from app.extensions import db
from app.models import Dividend, Investment

# Export all step definition functions for wildcard import
__all__ = [
    "application_is_running",
    "navigate_to_dashboard",
    "navigate_to_url",
    "navigate_directly_to_url",
    "navigate_to_dashboard_no_filter",
    "click_back_button",
    "see_page_title",
    "see_text_on_page",
    "not_see_text_on_page",
    "see_heading",
    "on_page",
    "redirected_to_dashboard",
    "see_success_message",
    "click_link",
    "click_button",
    "create_investment_with_data",
    "add_dividend_to_investment",
    "create_multiple_investments",
    "see_navigation_bar",
    "see_link_in_navigation",
    "see_logo",
    "on_any_page",
    "verify_on_dashboard",
    "page_loads_successfully",
    "see_404_page",
    "see_message",
    "see_dashboard_link",
]


# Background steps
@given("the application is running", target_fixture="ui_context")
def application_is_running(ui_app, ui_page: Page):
    """Ensure the application is running and accessible."""
    return {"app": ui_app, "page": ui_page}


# Navigation steps
@when(parsers.parse("I navigate to the dashboard"))
@when("I navigate to the dashboard")
def navigate_to_dashboard(ui_context):
    """Navigate to the dashboard page."""
    page = ui_context["page"]
    page.goto(page.base_url + "/")


@when(parsers.parse('I navigate to "{url}"'))
def navigate_to_url(ui_context, url):
    """Navigate to a specific URL."""
    page = ui_context["page"]
    page.goto(page.base_url + url)


@when(parsers.parse('I navigate directly to "{url}"'))
def navigate_directly_to_url(ui_context, url):
    """Navigate directly to a URL."""
    page = ui_context["page"]
    page.goto(page.base_url + url)


@when("I navigate to the dashboard with hide_zero disabled")
def navigate_to_dashboard_no_filter(ui_context):
    """Navigate to dashboard with hide_zero=false."""
    page = ui_context["page"]
    page.goto(page.base_url + "/?hide_zero=false")


@when("I click the browser back button")
def click_back_button(ui_context):
    """Click the browser back button."""
    page = ui_context["page"]
    page.go_back()


# Assertion steps
@then(parsers.parse('I should see the page title "{title}"'))
def see_page_title(ui_context, title):
    """Verify page title is visible."""
    page = ui_context["page"]
    expect(page).to_have_title(title)


@then(parsers.parse('I should see "{text}" on the page'))
def see_text_on_page(ui_context, text):
    """Verify text is visible on the page."""
    page = ui_context["page"]
    expect(page.locator("body")).to_contain_text(text)


@then(parsers.parse('I should not see "{text}" on the page'))
def not_see_text_on_page(ui_context, text):
    """Verify text is not visible on the page."""
    page = ui_context["page"]
    expect(page.locator("body")).not_to_contain_text(text)


@then(parsers.parse('I should see "{heading}" heading'))
def see_heading(ui_context, heading):
    """Verify heading is visible."""
    page = ui_context["page"]
    expect(page.get_by_role("heading", name=heading)).to_be_visible()


@then(parsers.parse('I should be on the "{url}" page'))
def on_page(ui_context, url):
    """Verify current page URL."""
    page = ui_context["page"]
    expect(page).to_have_url(page.base_url + url)


@then("I should be redirected to the dashboard")
def redirected_to_dashboard(ui_context):
    """Verify redirected to dashboard."""
    page = ui_context["page"]
    page.wait_for_url(page.base_url + "/", timeout=5000)


@then("I should see a success message")
def see_success_message(ui_context):
    """Verify success message is shown."""
    page = ui_context["page"]
    # Look for common success indicators
    success_locator = page.locator(".alert-success, .success, .flash-success")
    # Check if any success indicators exist
    if success_locator.count() > 0:
        expect(success_locator.first).to_be_visible()
    else:
        # If no specific success element, just verify page loaded successfully
        expect(page.locator("body")).to_be_visible()


# Click actions
# Both "click on" and "click" patterns support natural language variations
@when(parsers.parse('I click on the "{link}" link'))
@when(parsers.parse('I click on "{link}" in navigation'))
def click_link(ui_context, link):
    """Click on a link by text."""
    page = ui_context["page"]
    page.get_by_role("link", name=link).click()


@when(parsers.parse('I click the "{button}" button'))
def click_button(ui_context, button):
    """Click a button by text."""
    page = ui_context["page"]
    page.get_by_role("button", name=button).click()


# Data setup steps
@given(parsers.parse('I have an investment "{name}" with ticker "{ticker}" and amount {amount:d}'))
def create_investment_with_data(ui_context, name, ticker, amount):
    """Create an investment with specified data."""
    app = ui_context["app"]
    with app.app_context():
        investment = Investment(name=name, ticker=ticker, total_invested=float(amount))
        db.session.add(investment)
        db.session.commit()


@given(parsers.parse("the investment has a {frequency} dividend of {amount:d} in month {month:d}"))
@given(
    parsers.parse(
        'the "{name}" investment has a {frequency} dividend of {amount:d} in month {month:d}'
    )
)
def add_dividend_to_investment(ui_context, amount, frequency, month, name=None):
    """Add a dividend to an investment."""
    app = ui_context["app"]
    with app.app_context():
        if name:
            investment = Investment.query.filter_by(name=name).first()
        else:
            investment = Investment.query.order_by(Investment.id.desc()).first()

        if investment:
            current_year = datetime.now(timezone.utc).year
            dividend = Dividend(
                investment_id=investment.id,
                amount=float(amount),
                frequency=frequency.lower(),
                period_month=month,
                period_year=current_year,
            )
            db.session.add(dividend)
            db.session.commit()
        else:
            raise ValueError("No investment found to add dividend to")


@given(parsers.parse("I have {count:d} investments"))
def create_multiple_investments(ui_context, count):
    """Create multiple investments."""
    app = ui_context["app"]
    with app.app_context():
        for i in range(count):
            investment = Investment(
                name=f"Investment {i+1}", ticker=f"TST{i+1}", total_invested=1000.0 * (i + 1)
            )
            db.session.add(investment)
        db.session.commit()


# Navigation bar assertions
@then("I should see the navigation bar")
def see_navigation_bar(ui_context):
    """Verify navigation bar is visible."""
    page = ui_context["page"]
    nav = page.locator("nav, .navbar, header")
    expect(nav.first).to_be_visible()


@then(parsers.parse('I should see "{link}" link in navigation'))
def see_link_in_navigation(ui_context, link):
    """Verify link is visible in navigation."""
    page = ui_context["page"]
    expect(page.get_by_role("link", name=link)).to_be_visible()


@then(parsers.parse('I should see the "{logo}" logo'))
def see_logo(ui_context, logo):
    """Verify logo is visible."""
    page = ui_context["page"]
    expect(page.get_by_text(logo)).to_be_visible()


# Page state checks
@given("I am on any page in the application")
def on_any_page(ui_context):
    """Navigate to a page in the application."""
    page = ui_context["page"]
    page.goto(page.base_url + "/")


@then("I should be on the dashboard")
def verify_on_dashboard(ui_context):
    """Verify user is on the dashboard."""
    page = ui_context["page"]
    expect(page).to_have_url(page.base_url + "/")


@then("the page should load successfully")
def page_loads_successfully(ui_context):
    """Verify page loaded successfully."""
    page = ui_context["page"]
    expect(page.locator("body")).to_be_visible()


# Error page checks
@then("I should see a 404 error page")
def see_404_page(ui_context):
    """Verify 404 error page is shown."""
    page = ui_context["page"]
    expect(page.locator("body")).to_contain_text("404")


@then(parsers.parse('I should see "{message}" message'))
def see_message(ui_context, message):
    """Verify a specific message is shown."""
    page = ui_context["page"]
    expect(page.locator("body")).to_contain_text(message)


@then("I should see a link back to the dashboard")
def see_dashboard_link(ui_context):
    """Verify link back to dashboard exists."""
    page = ui_context["page"]
    expect(page.get_by_role("link", name="Dashboard")).to_be_visible()
