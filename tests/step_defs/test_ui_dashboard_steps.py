"""Step definitions for UI dashboard tests."""

from playwright.sync_api import expect
from pytest_bdd import parsers, scenarios, then, when

# Import shared steps to register their step definitions
from . import ui_shared_steps  # noqa: F401

# Link all scenarios from the feature file
scenarios("../features/ui_dashboard.feature")


@then('I should see the "Add Investment" link')
def see_add_investment_link(ui_context):
    """Verify Add Investment link is visible."""
    page = ui_context["page"]
    expect(page.get_by_role("link", name="Add Investment").first).to_be_visible()


@when(parsers.parse("I select the current year from the year filter"))
def select_current_year(ui_context):
    """Select current year from filter dropdown."""
    page = ui_context["page"]
    from datetime import datetime

    current_year = str(datetime.now().year)
    year_select = page.locator("select[name='year'], #year-filter, .year-filter")
    if year_select.count() > 0:
        year_select.first.select_option(current_year)


@when(parsers.parse('I toggle the "{checkbox_label}" checkbox'))
def toggle_checkbox(ui_context, checkbox_label):
    """Toggle a checkbox."""
    page = ui_context["page"]
    # Try to find checkbox by label or nearby text
    checkbox = page.locator("input[type='checkbox']").first
    if checkbox.count() > 0:
        checkbox.click()


@when(parsers.parse('I select "{value}" items per page'))
def select_items_per_page(ui_context, value):
    """Select items per page."""
    page = ui_context["page"]
    items_select = page.locator("select[name='per_page'], .per-page-select, select.items-per-page")
    if items_select.count() > 0:
        items_select.first.select_option(value)
        page.wait_for_load_state("networkidle")


@then("I should see pagination controls")
def see_pagination_controls(ui_context):
    """Verify pagination controls are visible."""
    page = ui_context["page"]
    pagination = page.locator(".pagination, nav[aria-label='pagination']")
    expect(pagination.first).to_be_visible()


@then("I should see page navigation")
def see_page_navigation(ui_context):
    """Verify page navigation is present."""
    page = ui_context["page"]
    # Look for next/previous links or page numbers
    nav_links = page.locator(".pagination a, .page-link")
    expect(nav_links.first).to_be_visible()


@when(parsers.parse('I click on the "{link_text}" page link'))
def click_page_link(ui_context, link_text):
    """Click on pagination link."""
    page = ui_context["page"]
    page.get_by_role("link", name=link_text).click()
    page.wait_for_load_state("networkidle")


@then(parsers.parse("I should be on page {page_num:d}"))
def verify_page_number(ui_context, page_num):
    """Verify current page number."""
    page = ui_context["page"]
    # Check URL for page parameter or active pagination link
    url = page.url
    assert (
        f"page={page_num}" in url
        or page.locator(f".page-item.active >> text={page_num}").count() > 0
    )
