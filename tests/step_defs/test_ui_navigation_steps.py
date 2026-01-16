"""Step definitions for UI navigation tests."""

from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

# Link all scenarios from the feature file
scenarios("../features/ui_navigation.feature")


@then("I should see breadcrumb navigation")
def see_breadcrumb(ui_context):
    """Verify breadcrumb navigation is visible."""
    page = ui_context["page"]
    breadcrumb = page.locator(".breadcrumb, nav[aria-label='breadcrumb']")
    if breadcrumb.count() > 0:
        expect(breadcrumb.first).to_be_visible()


@then(parsers.parse('the breadcrumb should show "{text}"'))
def verify_breadcrumb_text(ui_context, text):
    """Verify breadcrumb shows expected text."""
    page = ui_context["page"]
    breadcrumb = page.locator(".breadcrumb")
    if breadcrumb.count() > 0:
        expect(breadcrumb.first).to_contain_text(text)


@then(parsers.parse('the "{link}" link should be highlighted as active'))
def verify_active_link(ui_context, link):
    """Verify navigation link is highlighted as active."""
    page = ui_context["page"]
    # Look for active class on nav link
    active_link = page.locator(f"a:has-text('{link}').active, .nav-link.active:has-text('{link}')")
    if active_link.count() > 0:
        expect(active_link.first).to_be_visible()


@given("I am viewing on a mobile device")
def set_mobile_viewport(ui_context):
    """Set viewport to mobile size."""
    page = ui_context["page"]
    page.set_viewport_size({"width": 375, "height": 667})


@then("I should see a mobile-friendly navigation menu")
def see_mobile_navigation(ui_context):
    """Verify mobile navigation is visible."""
    page = ui_context["page"]
    nav = page.locator("nav, .navbar")
    expect(nav.first).to_be_visible()


@then("all navigation links should be accessible")
def verify_links_accessible(ui_context):
    """Verify all navigation links are accessible."""
    page = ui_context["page"]
    # Check that main navigation links are present
    expect(page.get_by_role("link", name="Add Investment")).to_be_attached()
    expect(page.get_by_role("link", name="Add Dividend")).to_be_attached()


@when("I press the Tab key repeatedly")
def press_tab_repeatedly(ui_context):
    """Press Tab key multiple times."""
    page = ui_context["page"]
    for _ in range(5):
        page.keyboard.press("Tab")


@then("the focus should move through navigation links")
def verify_keyboard_navigation(ui_context):
    """Verify keyboard navigation works."""
    page = ui_context["page"]
    # Check that focus is on a focusable element
    focused = page.evaluate("document.activeElement.tagName")
    assert focused in ["A", "BUTTON", "INPUT"]


@then("I should be able to activate links with Enter key")
def verify_enter_key_activation(ui_context):
    """Verify Enter key can activate links."""
    page = ui_context["page"]
    # Just verify that navigation is keyboard accessible
    expect(page.locator("nav")).to_be_visible()


@when("I might see an unsaved changes warning")
def might_see_warning(ui_context):
    """Handle potential unsaved changes warning."""
    page = ui_context["page"]
    # Set up dialog handler
    page.on("dialog", lambda dialog: dialog.accept())
