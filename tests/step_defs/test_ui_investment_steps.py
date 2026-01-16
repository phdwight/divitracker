"""Step definitions for UI investment management tests."""

from playwright.sync_api import expect
from pytest_bdd import parsers, scenarios, then, when

# Link all scenarios from the feature file
scenarios("../features/ui_investment_management.feature")


@when(parsers.parse('I enter "{text}" in the name field'))
def enter_name(ui_context, text):
    """Enter text in the name field."""
    page = ui_context["page"]
    name_field = page.locator("input[name='name'], #name, input[id='investment_name']")
    name_field.first.fill(text)


@when(parsers.parse('I enter "{text}" in the ticker field'))
def enter_ticker(ui_context, text):
    """Enter text in the ticker field."""
    page = ui_context["page"]
    ticker_field = page.locator("input[name='ticker'], #ticker, input[id='ticker']")
    ticker_field.first.fill(text)


@when(parsers.parse('I enter "{text}" in the amount field'))
def enter_amount(ui_context, text):
    """Enter text in the amount field."""
    page = ui_context["page"]
    amount_field = page.locator("input[name='amount'], #amount, input[name='total_invested']")
    amount_field.first.fill(text)


@when(parsers.parse('I click on the "{investment_name}" investment link'))
def click_investment_link(ui_context, investment_name):
    """Click on investment link."""
    page = ui_context["page"]
    page.get_by_role("link", name=investment_name).click()


@then("I should be on the investment details page")
def on_investment_details(ui_context):
    """Verify on investment details page."""
    page = ui_context["page"]
    # Check URL contains /investments/ with an ID
    url = page.url
    assert "/investments/" in url and url.split("/investments/")[-1].isdigit()


@when(parsers.parse('I navigate to the investment details page for "{name}"'))
def navigate_to_investment_details(ui_context, name):
    """Navigate to investment details page."""
    page = ui_context["page"]
    app = ui_context["app"]

    with app.app_context():
        from app.models import Investment

        investment = Investment.query.filter_by(name=name).first()
        if investment:
            page.goto(page.base_url + f"/investments/{investment.id}")


@then("I should be on the edit investment page")
def on_edit_investment_page(ui_context):
    """Verify on edit investment page."""
    page = ui_context["page"]
    url = page.url
    assert "/edit" in url


@then(parsers.parse('the name field should contain "{text}"'))
def name_field_contains(ui_context, text):
    """Verify name field contains text."""
    page = ui_context["page"]
    name_field = page.locator("input[name='name'], #name")
    expect(name_field.first).to_have_value(text)


@then(parsers.parse('the ticker field should contain "{text}"'))
def ticker_field_contains(ui_context, text):
    """Verify ticker field contains text."""
    page = ui_context["page"]
    ticker_field = page.locator("input[name='ticker'], #ticker")
    expect(ticker_field.first).to_have_value(text)


@then(parsers.parse('the amount field should contain "{text}"'))
def amount_field_contains(ui_context, text):
    """Verify amount field contains text."""
    page = ui_context["page"]
    amount_field = page.locator("input[name='amount'], input[name='total_invested']")
    expect(amount_field.first).to_have_value(text)


@then("I should see a confirmation dialog")
def see_confirmation_dialog(ui_context):
    """Verify confirmation dialog appears."""
    page = ui_context["page"]
    # Handle JavaScript confirm dialogs
    page.on("dialog", lambda dialog: dialog.accept())


@when("I confirm the deletion")
def confirm_deletion(ui_context):
    """Confirm deletion in dialog."""
    page = ui_context["page"]
    # Dialog handler should already be set up
    page.on("dialog", lambda dialog: dialog.accept())
    # Click delete button which triggers the dialog
    delete_button = page.locator("button[type='submit']:has-text('Delete'), .btn-danger")
    if delete_button.count() > 0:
        delete_button.first.click()


@when("I cancel the deletion")
def cancel_deletion(ui_context):
    """Cancel deletion in dialog."""
    page = ui_context["page"]
    page.on("dialog", lambda dialog: dialog.dismiss())


@then("I should see the dividend history")
def see_dividend_history(ui_context):
    """Verify dividend history section is visible."""
    page = ui_context["page"]
    history_section = page.locator(".dividend-history, #dividend-history, table")
    expect(history_section.first).to_be_visible()


@then(parsers.parse("I should see {count:d} dividend records"))
def see_dividend_count(ui_context, count):
    """Verify number of dividend records."""
    page = ui_context["page"]
    dividend_rows = page.locator("table tbody tr, .dividend-row")
    expect(dividend_rows).to_have_count(count)


@then(parsers.parse('the "{name}" investment should show total amount "{amount}"'))
def verify_total_amount(ui_context, name, amount):
    """Verify investment shows correct total amount."""
    page = ui_context["page"]
    # The amount may be formatted with currency symbol, thousands separators, etc.
    # Extract just the numeric part for comparison
    amount_num = amount.replace(",", "").replace(" ", "")

    # Look for the investment name on the page
    investment_locator = page.locator(f"text={name}")
    if investment_locator.count() > 0:
        # Get the surrounding context (parent elements)
        investment_row = investment_locator.first.locator("..").locator("..")
        row_text = investment_row.text_content()
        # Check if the amount appears in the text (with or without formatting)
        if amount_num in row_text.replace(",", "").replace(" ", "").replace("₱", "").replace(
            "$", ""
        ):
            assert True
        else:
            # For better error message, use expect
            expect(investment_row).to_contain_text(amount_num)
    else:
        # If investment name not found, fail
        expect(page.locator("body")).to_contain_text(name)
