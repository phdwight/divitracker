# UI Tests with Playwright

This directory contains comprehensive UI tests for DiviTracker using pytest-bdd and Playwright.

## Overview

- **Framework**: pytest-bdd 8.1.0 with Playwright 1.57.0
- **Test Count**: 74 scenarios across 6 feature files
- **Style**: Gherkin (Given-When-Then)
- **Coverage**: All user operations in the application

## Quick Start

### First Time Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Chromium browser
playwright install chromium
```

### Running Tests

```bash
# Run all UI tests
pytest -m ui

# Run specific categories
pytest -m "ui and portfolio"      # Dashboard tests
pytest -m "ui and investments"    # Investment management
pytest -m "ui and dividends"      # Dividend recording
pytest -m "ui and reports"        # Graphs and reports
pytest -m "ui and settings"       # Settings page
pytest -m "ui and navigation"     # Navigation tests

# Debug mode (see browser)
pytest -m ui --headed

# Slow motion for debugging
pytest -m ui --headed --slowmo 1000

# Run specific test file
pytest tests/step_defs/test_ui_dashboard_steps.py

# Run with verbose output
pytest -m ui -v
```

## Test Structure

### Feature Files (`tests/features/ui_*.feature`)

1. **ui_dashboard.feature** (7 scenarios)
   - View empty/populated dashboard
   - Filter by year
   - Toggle zero dividends
   - Portfolio summary
   - Pagination

2. **ui_investment_management.feature** (11 scenarios)
   - Add/edit/delete investments
   - View investment details
   - Investment with dividends
   - Duplicate investment names

3. **ui_dividend_recording.feature** (13 scenarios)
   - Record dividends (all frequencies)
   - Edit/delete dividends
   - Yield preview
   - Form validation

4. **ui_reports_visualizations.feature** (19 scenarios)
   - Dividend bar chart
   - Cumulative line graph
   - Filter by year/investment
   - Yield breakdown
   - Data tables

5. **ui_settings_management.feature** (18 scenarios)
   - Currency configuration
   - Number formatting
   - Pagination settings
   - Timezone configuration
   - Database backup/restore

6. **ui_navigation.feature** (14 scenarios)
   - Navigation bar
   - Link navigation
   - Breadcrumbs
   - Mobile responsive
   - Keyboard navigation

### Step Definitions (`tests/step_defs/test_ui_*.py`)

Each feature file has a corresponding step definition file:
- `test_ui_dashboard_steps.py`
- `test_ui_investment_steps.py`
- `test_ui_dividend_steps.py`
- `test_ui_reports_steps.py`
- `test_ui_settings_steps.py`
- `test_ui_navigation_steps.py`

Shared steps are in `ui_shared_steps.py`.

## Writing New Tests

### 1. Add Scenario to Feature File

```gherkin
Scenario: My new test scenario
    Given the application is running
    When I navigate to the dashboard
    Then I should see "DiviTracker" on the page
```

### 2. Add Step Definition (if needed)

```python
from pytest_bdd import when, then

@when('I do something special')
def do_something_special(ui_context):
    page = ui_context["page"]
    page.get_by_role("button", name="Special").click()
```

### 3. Run the Test

```bash
pytest tests/step_defs/test_ui_myfeature_steps.py -v
```

## Fixtures

- `flask_app_for_ui`: Test Flask application instance
- `live_server`: Live Flask server URL (http://127.0.0.1:5555)
- `ui_page`: Playwright Page object with base_url set
- `ui_app`: Flask app with clean database for each test
- `ui_context`: Combined fixture with both app and page

## Common Patterns

### Navigation
```python
page.goto(page.base_url + "/investments/new")
```

### Assertions
```python
from playwright.sync_api import expect

expect(page.locator("body")).to_contain_text("Success")
expect(page.get_by_role("button", name="Save")).to_be_visible()
```

### Form Interactions
```python
page.locator("input[name='amount']").fill("1000")
page.locator("select[name='currency']").select_option("USD")
page.get_by_role("button", name="Submit").click()
```

## Troubleshooting

### Browser Not Found
```bash
playwright install chromium
```

### Tests Hanging
Check if the live server started successfully. Look for "Running on http://127.0.0.1:5555" in test output.

### Flaky Tests
Use `--headed` mode to see what's happening:
```bash
pytest -m ui --headed -v
```

### Selector Not Found
Inspect the page with:
```bash
pytest -m ui --headed --slowmo 1000
```

## Best Practices

1. **Use semantic locators**: Prefer `get_by_role()` over CSS selectors
2. **Wait automatically**: Playwright auto-waits for elements
3. **Isolate tests**: Each test gets a fresh database
4. **Use fixtures**: Share setup code via pytest fixtures
5. **Keep scenarios focused**: One scenario = one behavior

## CI/CD Integration

UI tests can run in CI with headless mode (default):

```yaml
- name: Run UI Tests
  run: |
    playwright install --with-deps chromium
    pytest -m ui
```

## Performance Tips

- UI tests are slower than unit tests - use selectively
- Run UI tests in parallel with pytest-xdist (if needed)
- Use `-m "not ui"` to skip UI tests during development
- Cache Playwright browsers in CI

## Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)
- [Gherkin Reference](https://cucumber.io/docs/gherkin/)
