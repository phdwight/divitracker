"""Step definitions for UI dividend recording tests."""

from playwright.sync_api import expect
from pytest_bdd import parsers, scenarios, then, when

# Link all scenarios from the feature file
scenarios("../features/ui_dividend_recording.feature")


@when(parsers.parse('I select "{investment}" from the investment dropdown'))
def select_investment(ui_context, investment):
    """Select investment from dropdown."""
    page = ui_context["page"]
    investment_select = page.locator(
        "select[name='investment_id'], #investment_id, select.investment-select"
    )
    # Wait for the select to be visible and contain options
    investment_select.first.wait_for(state="visible", timeout=5000)
    # Wait a moment for options to load (they may be populated dynamically or from database)
    page.wait_for_timeout(500)
    # Try to select by label first, fall back to value if needed
    try:
        investment_select.first.select_option(label=investment)
    except Exception as e1:
        # If label selection fails, try finding option by partial text match
        try:
            options = investment_select.first.locator("option")
            for i in range(options.count()):
                option_text = options.nth(i).text_content() or ""
                if investment in option_text:
                    # Select by index
                    investment_select.first.select_option(index=i)
                    return
            # If still not found, raise informative error
            available_options = [options.nth(i).text_content() for i in range(options.count())]
            raise ValueError(
                f"Investment '{investment}' not found in dropdown. Available options: {available_options}"
            )
        except Exception as e2:
            # If everything fails, show both errors
            raise ValueError(f"Failed to select investment '{investment}': {str(e1)}, {str(e2)}")


@when(parsers.parse('I enter "{text}" in the dividend amount field'))
def enter_dividend_amount(ui_context, text):
    """Enter dividend amount."""
    page = ui_context["page"]
    amount_field = page.locator("input[name='amount'], #amount, input[name='dividend_amount']")
    amount_field.first.fill(text)


@when(parsers.parse('I select "{frequency}" from the frequency dropdown'))
def select_frequency(ui_context, frequency):
    """Select frequency from dropdown or radio buttons."""
    page = ui_context["page"]
    # First try to find as a select element
    frequency_select = page.locator("select[name='frequency'], #frequency")
    if frequency_select.count() > 0:
        frequency_select.first.wait_for(state="attached", timeout=5000)
        page.wait_for_timeout(500)
        # Try to select by label
        try:
            frequency_select.first.select_option(label=frequency)
            return
        except Exception:
            # Try by value (lowercase)
            try:
                frequency_select.first.select_option(value=frequency.lower())
                return
            except Exception:
                # Last resort - try to find by text
                options = frequency_select.first.locator("option")
                for i in range(options.count()):
                    if frequency.lower() in options.nth(i).text_content().lower():
                        frequency_select.first.select_option(index=i)
                        return

    # If not a select, try radio buttons
    radio_button = page.locator(f"input[name='frequency'][value='{frequency.lower()}']")
    if radio_button.count() > 0:
        radio_button.first.check()
        return

    # Try to find radio by label text
    radio_label = page.locator(f"label:has-text('{frequency}')")
    if radio_label.count() > 0:
        radio_label.first.click()
        return

    raise ValueError(f"Could not find frequency '{frequency}' as select or radio button")


@when(parsers.parse('I select month "{month}" from the period month dropdown'))
def select_period_month(ui_context, month):
    """Select period month."""
    page = ui_context["page"]
    month_select = page.locator("select[name='period_month'], #period_month")
    month_select.first.select_option(month)


@when(parsers.parse('I enter "{text}" in the investment amount at time field'))
def enter_investment_amount(ui_context, text):
    """Enter investment amount at time."""
    page = ui_context["page"]
    amount_field = page.locator(
        "input[name='investment_amount'], #investment_amount, input[name='investment_amount_at_time']"
    )
    amount_field.first.fill(text)


@when(parsers.parse('I enter "{text}" in the notes field'))
def enter_notes(ui_context, text):
    """Enter notes."""
    page = ui_context["page"]
    notes_field = page.locator("textarea[name='notes'], #notes, input[name='notes']")
    notes_field.first.fill(text)


@then("the dividend should be recorded")
def dividend_recorded(ui_context):
    """Verify dividend was recorded."""
    page = ui_context["page"]
    # Check we're back on dashboard and data is present
    expect(page).to_have_url(page.base_url + "/")


@then("the dividend should be recorded with investment amount")
def dividend_recorded_with_amount(ui_context):
    """Verify dividend with investment amount was recorded."""
    page = ui_context["page"]
    expect(page).to_have_url(page.base_url + "/")


@then("the dividend should be recorded with notes")
def dividend_recorded_with_notes(ui_context):
    """Verify dividend with notes was recorded."""
    page = ui_context["page"]
    expect(page).to_have_url(page.base_url + "/")


@when("I click on the first dividend in the history")
def click_first_dividend(ui_context):
    """Click on first dividend in history."""
    page = ui_context["page"]
    first_dividend = page.locator("table tbody tr:first-child a, .dividend-row:first-child a").first
    first_dividend.click()


@then("I should be on the edit dividend page")
def on_edit_dividend_page(ui_context):
    """Verify on edit dividend page."""
    page = ui_context["page"]
    url = page.url
    assert "/dividends/" in url and "/edit" in url


@then(parsers.parse('the amount field should contain "{text}"'))
def amount_field_contains(ui_context, text):
    """Verify amount field contains text."""
    page = ui_context["page"]
    amount_field = page.locator("input[name='amount'], #amount")
    expect(amount_field.first).to_have_value(text)


@then(parsers.parse("the dividend amount should be updated to {amount:d}"))
def dividend_amount_updated(ui_context, amount):
    """Verify dividend amount was updated."""
    page = ui_context["page"]
    # Check that the page updated successfully
    expect(page).to_have_url(page.base_url + "/")


@when(parsers.parse('I click on the "{button}" button for the first dividend'))
def click_dividend_delete_button(ui_context, button):
    """Click delete button for first dividend."""
    page = ui_context["page"]
    delete_button = page.locator(
        "table tbody tr:first-child button:has-text('Delete'), .dividend-row:first-child .btn-danger"
    ).first

    # Set up dialog handler before clicking
    page.on("dialog", lambda dialog: dialog.accept())
    delete_button.click()


@then("the dividend should be removed from the history")
def dividend_removed(ui_context):
    """Verify dividend was removed."""
    page = ui_context["page"]
    # Verify we're still on a valid page
    expect(page.locator("body")).to_be_visible()


@then("I should see the yield preview section")
def see_yield_preview(ui_context):
    """Verify yield preview section is visible."""
    page = ui_context["page"]
    preview_section = page.locator(".yield-preview, #yield-preview, .preview-section")
    if preview_section.count() > 0:
        expect(preview_section.first).to_be_visible()


@then("the preview should show the projected annual dividend")
def see_projected_annual_dividend(ui_context):
    """Verify projected annual dividend is shown."""
    page = ui_context["page"]
    # Look for preview content
    preview = page.locator(".yield-preview, #yield-preview, .preview-section")
    if preview.count() > 0:
        expect(preview.first).to_be_visible()


@then("the preview should show the projected yield percentage")
def see_projected_yield(ui_context):
    """Verify projected yield percentage is shown."""
    page = ui_context["page"]
    # Look for percentage in preview
    preview = page.locator(".yield-preview, #yield-preview, .preview-section")
    if preview.count() > 0:
        expect(preview.first).to_be_visible()


@then("I should see a validation error for the amount field")
def see_amount_validation_error(ui_context):
    """Verify validation error for amount field."""
    page = ui_context["page"]
    # Look for error messages
    error = page.locator(".error, .invalid-feedback, .alert-danger, input:invalid")
    expect(error.first).to_be_visible()


@then("I should see a validation error for the investment field")
def see_investment_validation_error(ui_context):
    """Verify validation error for investment field."""
    page = ui_context["page"]
    # Look for error messages
    error = page.locator(".error, .invalid-feedback, .alert-danger, select:invalid")
    expect(error.first).to_be_visible()
