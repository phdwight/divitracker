@user @routes
Feature: Web Routes
    As a user
    I want to navigate the DiviTracker web application
    So that I can manage my investments and dividends

    Background:
        Given the application is configured for testing

    # Error Handling
    Scenario: 404 page for non-existent route
        When I visit "/this-page-does-not-exist"
        Then I should see status code 404
        And I should see "404" in the page
        And I should see "Page Not Found" in the page

    Scenario: 404 page has navigation links
        When I visit "/non-existent-page"
        Then I should see status code 404
        And I should see navigation to dashboard

    Scenario: 404 shows error icon
        When I visit "/does-not-exist"
        Then I should see status code 404
        And I should see "error-icon" in the page

    # Main Routes
    Scenario: Index page loads successfully
        When I visit "/"
        Then I should see status code 200
        And I should see "DiviTracker" in the page

    Scenario: Index shows empty state when no investments
        When I visit "/"
        Then I should see status code 200
        And I should see "No investments yet" in the page

    Scenario: Index shows investments when they exist
        Given an investment "Test Investment" with ticker "TEST" exists
        When I visit "/?hide_zero=false"
        Then I should see status code 200
        And I should see "Test Investment" in the page

    Scenario: Yield breakdown page loads
        When I visit "/reports/yield-breakdown"
        Then I should see status code 200
        And I should see "Annualized Yield Calculation" in the page

    Scenario: Yield breakdown with year parameter
        When I visit "/reports/yield-breakdown?year=2025"
        Then I should see status code 200
        And I should see "2025" in the page

    Scenario: Yield breakdown shows formula
        When I visit "/reports/yield-breakdown"
        Then I should see "Total Dividends Received" in the page
        And I should see "Sum of Average Investment Amounts" in the page

    # Dividend Graph Routes
    Scenario: Dividend graph page loads
        When I visit "/reports/dividends-chart"
        Then I should see status code 200
        And I should see "Dividend Graph" in the page

    Scenario: Dividend graph with year filter
        When I visit "/reports/dividends-chart?year=2025"
        Then I should see status code 200
        And I should see "2025" in the page

    Scenario: Dividend graph shows chart container
        When I visit "/reports/dividends-chart"
        Then I should see "dividendChart" in the page

    Scenario: Dividend graph has cumulative toggle
        When I visit "/reports/dividends-chart"
        Then I should see "Show Cumulative Line" in the page
        And I should see "showCumulative" in the page

    Scenario: Dividend graph has summary cards
        When I visit "/reports/dividends-chart"
        Then I should see "Total Displayed" in the page
        And I should see "Highest" in the page

    # Pagination
    Scenario: Index pagination with page parameter
        Given an investment "Test Investment" with ticker "TEST" exists
        When I visit "/?page=1&hide_zero=false"
        Then I should see status code 200
        And I should see "Test Investment" in the page

    Scenario: Index pagination with per_page parameter
        Given an investment "Test Investment" with ticker "TEST" exists
        When I visit "/?per_page=5&hide_zero=false"
        Then I should see status code 200
        And I should see "Test Investment" in the page

    # Hide Zero Filter
    Scenario: Hide zero dividends filter checkbox
        Given an investment "Test Investment" with ticker "TEST" exists
        When I visit "/?hide_zero=false"
        Then I should see "Hide zero dividends" in the page

    # Investment Routes
    Scenario: Add investment page loads
        When I visit "/investments/new"
        Then I should see status code 200
        And I should see "Add Investment" in the page

    Scenario: Add new investment via POST
        When I submit new investment with name "Apple Inc." ticker "AAPL" and amount "5000"
        Then I should see "Created new investment" in the page
        And the investment "Apple Inc." should exist with ticker "AAPL" and amount 5000

    Scenario: Add to existing investment
        Given an investment "Test Investment" with ticker "TEST" and amount 10000 exists
        When I submit new investment with name "Test Investment" ticker "TEST" and amount "2000"
        Then I should see "Added" in the page
        And the investment "Test Investment" should have total 12000

    Scenario: Add investment with empty name shows error
        When I submit new investment with name "" ticker "TEST" and amount "1000"
        Then I should see "required" in the page

    Scenario: View investment details page
        Given an investment "Test Investment" with ticker "TEST" exists
        When I view the investment "Test Investment"
        Then I should see status code 200
        And I should see "Test Investment" in the page
        And I should see "TEST" in the page

    Scenario: View non-existent investment shows error
        When I visit "/investments/99999" with redirects
        Then I should see "not found" in the page

    Scenario: Edit investment page loads
        Given an investment "Test Investment" with ticker "TEST" exists
        When I visit the edit page for investment "Test Investment"
        Then I should see status code 200
        And I should see "Edit Investment" in the page

    Scenario: Edit investment via POST
        Given an investment "Test Investment" with ticker "TEST" and amount 10000 exists
        When I update investment "Test Investment" to name "Updated Investment" ticker "UPD" and amount "15000"
        Then I should see "updated successfully" in the page
        And the investment "Updated Investment" should exist with ticker "UPD" and amount 15000

    Scenario: Delete investment
        Given an investment "To Delete" with ticker "DEL" exists
        When I delete investment "To Delete"
        Then I should see "deleted successfully" in the page
        And the investment "To Delete" should not exist

    Scenario: API returns investment data
        Given an investment "Test Investment" with ticker "TEST" exists
        When I request "/investments/api"
        Then I should get JSON with investment "Test Investment"

    # Dividend Routes
    Scenario: Add dividend page loads with investments
        Given an investment "Test Investment" with ticker "TEST" exists
        When I visit "/dividends/new"
        Then I should see status code 200
        And I should see "Record Dividend" in the page

    Scenario: Add dividend page shows message when no investments
        When I visit "/dividends/new"
        Then I should see "No investments found" in the page

    Scenario: Add dividend page with preselected investment
        Given an investment "Test Investment" with ticker "TEST" exists
        When I visit add dividend page with preselected investment "Test Investment"
        Then I should see "selected" in the page

    Scenario: Add dividend via POST
        Given an investment "Test Investment" with ticker "TEST" exists
        When I submit dividend of "100" with frequency "quarterly" and notes "Q4 2025" for "Test Investment"
        Then I should see "Added quarterly dividend" in the page
        And the dividend should exist with amount 100 and frequency "quarterly"

    Scenario: Add dividend without investment shows error
        When I submit dividend of "100" with frequency "monthly" without investment
        Then I should see "required" in the page

    Scenario: Add dividend with invalid frequency shows error
        Given an investment "Test Investment" with ticker "TEST" exists
        When I submit dividend of "100" with frequency "weekly" for "Test Investment"
        Then I should see "invalid" in the page

    Scenario: Delete dividend
        Given an investment "Test Investment" with dividends exists
        When I delete a dividend for "Test Investment"
        Then I should see "deleted successfully" in the page

    Scenario: Delete non-existent dividend shows error
        When I try to delete dividend with ID 99999
        Then I should see "not found" in the page

    Scenario: Edit dividend page loads
        Given an investment "Test Investment" with dividends exists
        When I visit the edit page for a dividend of "Test Investment"
        Then I should see status code 200
        And I should see "Edit Dividend" in the page

    Scenario: Edit dividend page not found
        When I visit "/dividends/99999/edit" with redirects
        Then I should see "not found" in the page

    Scenario: Edit dividend via POST
        Given an investment "Test Investment" with dividends exists
        When I update a dividend for "Test Investment" to amount "75" frequency "monthly" and notes "Updated"
        Then I should see "Updated monthly dividend" in the page

    Scenario: Edit dividend with invalid data shows error
        Given an investment "Test Investment" with dividends exists
        When I update a dividend for "Test Investment" with invalid amount
        Then I should see "invalid" in the page

    Scenario: Edit dividend with investment amount at time
        Given an investment "Test Investment" with dividends exists
        When I update a dividend for "Test Investment" with investment amount "8000"
        Then I should see "Updated" in the page
        And the dividend should have investment amount at time 8000
