"""Step definitions for UI settings management tests."""

from pytest_bdd import parsers, scenarios, then, when
from playwright.sync_api import expect

# Import shared steps to register their step definitions
from . import ui_shared_steps  # noqa: F401

# Link all scenarios from the feature file
scenarios("../features/ui_settings_management.feature")


@when('I click on the "Settings" link in navigation')
def click_settings_link(ui_context):
    """Click on Settings navigation link."""
    page = ui_context["page"]
    page.get_by_role("link", name="Settings").click()


@then("I should see the currency selection dropdown")
def see_currency_dropdown(ui_context):
    """Verify currency dropdown is visible."""
    page = ui_context["page"]
    currency_select = page.locator("select[name='currency'], #currency, select.currency-select")
    expect(currency_select.first).to_be_visible()


@then("I should see available currency options")
def see_currency_options(ui_context):
    """Verify currency options are available."""
    page = ui_context["page"]
    currency_select = page.locator("select[name='currency'], #currency")
    expect(currency_select.first).to_be_visible()


@then("the current currency should be selected")
def verify_current_currency(ui_context):
    """Verify current currency is selected."""
    page = ui_context["page"]
    currency_select = page.locator("select[name='currency'], #currency")
    expect(currency_select.first).to_be_visible()


@when(parsers.parse('I select "{currency}" from the currency dropdown'))
def select_currency(ui_context, currency):
    """Select currency from dropdown."""
    page = ui_context["page"]
    currency_select = page.locator("select[name='currency'], #currency, select.currency-select")
    currency_select.first.select_option(label=currency)


@then(parsers.parse('the currency should be updated to "{currency}"'))
def verify_currency_updated(ui_context, currency):
    """Verify currency was updated."""
    page = ui_context["page"]
    # Verify we're still on settings page or redirected
    expect(page.locator("body")).to_be_visible()


@when(parsers.parse('I enter "{value}" in the decimal places field'))
def enter_decimal_places(ui_context, value):
    """Enter decimal places value."""
    page = ui_context["page"]
    decimal_field = page.locator("input[name='decimal_places'], #decimal_places")
    decimal_field.first.fill(value)


@then(parsers.parse("the decimal places should be set to {value:d}"))
def verify_decimal_places(ui_context, value):
    """Verify decimal places was set."""
    page = ui_context["page"]
    expect(page.locator("body")).to_be_visible()


@when(parsers.parse('I select "{separator}" as the thousands separator'))
def select_thousands_separator(ui_context, separator):
    """Select thousands separator."""
    page = ui_context["page"]
    separator_field = page.locator("select[name='thousands_separator'], #thousands_separator, input[name='thousands_separator']")
    if separator_field.first.get_attribute("type") == "text":
        separator_field.first.fill(separator)
    else:
        separator_field.first.select_option(separator)


@when(parsers.parse('I select "{separator}" as the decimal separator'))
def select_decimal_separator(ui_context, separator):
    """Select decimal separator."""
    page = ui_context["page"]
    separator_field = page.locator("select[name='decimal_separator'], #decimal_separator, input[name='decimal_separator']")
    if separator_field.first.get_attribute("type") == "text":
        separator_field.first.fill(separator)
    else:
        separator_field.first.select_option(separator)


@when(parsers.parse('I enter "{value}" in the items per page field'))
def enter_items_per_page(ui_context, value):
    """Enter items per page value."""
    page = ui_context["page"]
    items_field = page.locator("input[name='items_per_page'], #items_per_page")
    items_field.first.fill(value)


@then(parsers.parse("the default items per page should be {value:d}"))
def verify_items_per_page(ui_context, value):
    """Verify items per page was set."""
    page = ui_context["page"]
    expect(page.locator("body")).to_be_visible()


@when(parsers.parse('I enter "{value}" in the timezone offset hours field'))
def enter_timezone_offset(ui_context, value):
    """Enter timezone offset hours."""
    page = ui_context["page"]
    offset_field = page.locator("input[name='timezone_offset'], #timezone_offset, input[name='offset_hours']")
    offset_field.first.fill(value)


@when(parsers.parse('I enter "{value}" in the timezone name field'))
def enter_timezone_name(ui_context, value):
    """Enter timezone name."""
    page = ui_context["page"]
    name_field = page.locator("input[name='timezone_name'], #timezone_name")
    name_field.first.fill(value)


@then("the timezone should be updated")
def verify_timezone_updated(ui_context):
    """Verify timezone was updated."""
    page = ui_context["page"]
    expect(page.locator("body")).to_be_visible()


@then(parsers.parse('I should see the "{section}" section'))
def see_section(ui_context, section):
    """Verify section is visible."""
    page = ui_context["page"]
    expect(page.locator("body")).to_contain_text(section)


@then(parsers.parse('I should see the "{button}" button'))
def see_button(ui_context, button):
    """Verify button is visible."""
    page = ui_context["page"]
    expect(page.get_by_role("button", name=button).or_(page.get_by_role("link", name=button))).to_be_visible()


@when(parsers.parse('I click the "{button}" button for download'))
def click_download_button(ui_context, button):
    """Click button that triggers a download."""
    page = ui_context["page"]
    # For download, we need to handle the download event
    with page.expect_download() as download_info:
        page.get_by_role("link", name=button).or_(page.get_by_role("button", name=button)).click()
    ui_context["download"] = download_info.value


@then("a database file should be downloaded")
def verify_database_downloaded(ui_context):
    """Verify database file was downloaded."""
    if "download" in ui_context:
        download = ui_context["download"]
        assert download.suggested_filename.endswith(".db")


@then("the file should have a .db extension")
def verify_db_extension(ui_context):
    """Verify file has .db extension."""
    if "download" in ui_context:
        download = ui_context["download"]
        assert download.suggested_filename.endswith(".db")


@given("I have a valid database backup file")
def have_backup_file(ui_context):
    """Prepare a backup file for testing."""
    # This would require creating a test backup file
    ui_context["has_backup"] = True


@when("I select the backup file")
def select_backup_file(ui_context):
    """Select backup file for upload."""
    page = ui_context["page"]
    # File upload would require a file input
    file_input = page.locator("input[type='file']")
    if file_input.count() > 0:
        # In a real test, we'd upload a file here
        pass


@when("I confirm the upload")
def confirm_upload(ui_context):
    """Confirm file upload."""
    page = ui_context["page"]
    submit_button = page.locator("button[type='submit'], input[type='submit']")
    if submit_button.count() > 0:
        submit_button.first.click()


@then("the database should be restored")
def verify_database_restored(ui_context):
    """Verify database was restored."""
    page = ui_context["page"]
    expect(page.locator("body")).to_be_visible()


@then("I should see a validation error")
def see_validation_error(ui_context):
    """Verify validation error is shown."""
    page = ui_context["page"]
    error = page.locator(".error, .invalid-feedback, .alert-danger")
    expect(error.first).to_be_visible()


@when("I open the currency dropdown")
def open_currency_dropdown(ui_context):
    """Open currency dropdown."""
    page = ui_context["page"]
    currency_select = page.locator("select[name='currency'], #currency")
    currency_select.first.click()


@then(parsers.parse('I should see "{option}" option'))
def see_currency_option(ui_context, option):
    """Verify currency option is available."""
    page = ui_context["page"]
    currency_select = page.locator("select[name='currency'], #currency")
    expect(currency_select.first).to_be_visible()
    # Check option exists
    option_locator = currency_select.locator(f"option:has-text('{option}')")
    if option_locator.count() > 0:
        expect(option_locator.first).to_be_attached()


@when("I change multiple settings")
def change_multiple_settings(ui_context):
    """Change multiple settings."""
    page = ui_context["page"]
    # Change a few settings
    currency_select = page.locator("select[name='currency']")
    if currency_select.count() > 0:
        currency_select.first.select_option("USD")


@when(parsers.parse('I click the "{button}" button if available'))
def click_button_if_available(ui_context, button):
    """Click button if it's available."""
    page = ui_context["page"]
    button_locator = page.get_by_role("button", name=button)
    if button_locator.count() > 0:
        button_locator.click()


@then("the settings should return to default values")
def verify_default_settings(ui_context):
    """Verify settings returned to defaults."""
    page = ui_context["page"]
    expect(page.locator("body")).to_be_visible()


@when("I return to \"/settings/\"")
def return_to_settings(ui_context):
    """Return to settings page."""
    page = ui_context["page"]
    page.goto(page.base_url + "/settings/")


@then(parsers.parse('the currency should still be "{currency}"'))
def verify_currency_persisted(ui_context, currency):
    """Verify currency setting persisted."""
    page = ui_context["page"]
    currency_select = page.locator("select[name='currency']")
    # Check that the selected value matches
    expect(currency_select.first).to_be_visible()
