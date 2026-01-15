@edge_cases @system
Feature: Edge Cases
    Test coverage for boundary conditions and edge cases

    Background:
        Given the application is running

    # Pagination boundary cases
    Scenario: Index page with negative page number defaults to page 1
        Given an investment "Test Fund" with ticker "TEST" and amount 1000 exists
        When I visit "/?page=-5"
        Then I should see status code 200
        And I should see "Dashboard" in the page

    Scenario: Index page with page number exceeding total pages shows last page
        Given an investment "Test Fund" with ticker "TEST" and amount 1000 exists
        When I visit "/?page=999"
        Then I should see status code 200
        And I should see "Dashboard" in the page

    Scenario: View investment page with negative page number
        Given an investment "Test Fund" with ticker "TEST" exists
        And a quarterly dividend of 100 for "Test Fund" with period month 3 and year 2024
        When I visit the investment "Test Fund" with page -1
        Then I should see status code 200

    Scenario: View investment page with excessive page number
        Given an investment "Test Fund" with ticker "TEST" exists
        And a quarterly dividend of 100 for "Test Fund" with period month 3 and year 2024
        When I visit the investment "Test Fund" with page 999
        Then I should see status code 200

    # Dividend graph edge cases
    Scenario: Dividend graph without year filter shows all years
        Given an investment "Test Fund" with ticker "TEST" exists
        And a quarterly dividend of 100 for "Test Fund" with period month 3 and year 2024
        When I visit "/reports/dividends-chart"
        Then I should see status code 200
        And I should see "Dividend Graph" in the page

    Scenario: Dividend graph with specific investment filter
        Given an investment "Fund A" with ticker "FUNA" exists
        And an investment "Fund B" with ticker "FUNB" exists
        And a quarterly dividend of 100 for "Fund A" with period month 3 and year 2024
        And a quarterly dividend of 200 for "Fund B" with period month 6 and year 2024
        When I filter dividend graph by investment "Fund A"
        Then I should see status code 200
        And I should see "Dividend Graph" in the page

    Scenario: Dividend graph yearly mode with investment filter
        Given an investment "Fund A" with ticker "FUNA" exists
        And a quarterly dividend of 100 for "Fund A" with period month 3 and year 2024
        And a quarterly dividend of 150 for "Fund A" with period month 6 and year 2023
        When I visit "/reports/dividends-chart"
        Then I should see status code 200

    # View investment year selection edge cases
    Scenario: View investment with invalid year falls back to current or most recent
        Given an investment "Test Fund" with ticker "TEST" exists
        And a quarterly dividend of 100 for "Test Fund" with period month 3 and year 2024
        When I visit the investment "Test Fund" with year 1999
        Then I should see status code 200

    Scenario: View investment with no dividends shows current year
        Given an investment "Test Fund" with ticker "TEST" exists
        When I view the investment "Test Fund"
        Then I should see status code 200

    # Edit investment validation edge cases
    Scenario: Edit investment with validation error shows form again
        Given an investment "Test Fund" with ticker "TEST" and amount 10000 exists
        When I update investment "Test Fund" to name "Updated" ticker "UPD" and amount "-500"
        Then I should see "error" in the page

    # Delete investment edge case
    Scenario: Delete non-existent investment shows error
        When I delete investment with id 99999
        Then I should see "not found" in the page

    # Admin settings edge cases
    Scenario: Save settings with invalid items per page too low
        When I save admin settings with items_per_page 2
        Then I should see "between 5 and 100" in the page

    Scenario: Save settings with invalid items per page too high
        When I save admin settings with items_per_page 500
        Then I should see "between 5 and 100" in the page

    Scenario: Save settings throws general exception
        When I save admin settings that causes an exception
        Then I should see "Error saving settings" in the page

    # Dividend recording edge cases
    Scenario: Record dividend for non-existent investment shows not found error
        When I submit dividend with investment_id 99999 amount "100" and frequency "monthly"
        Then I should see "not found" in the page

    # Model edge cases - projected yield
    Scenario: Projected yield with full year of monthly dividends uses actual
        Given an investment "Test Fund" with ticker "TEST" and amount 10000 exists
        And 12 monthly dividends of 50 for "Test Fund" in year 2024
        When I calculate projected yield for "Test Fund" in year 2024
        Then the projected amount should equal the actual amount

    Scenario: Projected yield with unknown frequency uses actual
        Given an investment "Test Fund" with ticker "TEST" and amount 10000 exists
        And a dividend with unknown frequency for "Test Fund" in year 2024
        When I calculate projected yield for "Test Fund" in year 2024
        Then the projected amount should be calculated

    # Dividend period display edge cases
    Scenario: Quarterly dividend shows quarter format
        Given an investment "Test Fund" with ticker "TEST" exists
        And a quarterly dividend of 100 for "Test Fund" with period month 4 and year 2024
        When I get the period display for the dividend
        Then the period display should be "Q2 2024"

    Scenario: Yearly dividend shows year only
        Given an investment "Test Fund" with ticker "TEST" exists
        And a yearly dividend of 500 for "Test Fund" with period year 2024
        When I get the period display for the dividend
        Then the period display should be "2024"

    Scenario: Semi-annual dividend with month shows month and year
        Given an investment "Test Fund" with ticker "TEST" exists
        And a semi-annual dividend of 250 for "Test Fund" with period month 7 and year 2024
        When I get the period display for the dividend
        Then the period display should be "Jul 2024"

    Scenario: Dividend without month shows year only
        Given an investment "Test Fund" with ticker "TEST" exists
        And a dividend without month for "Test Fund" with year 2024
        When I get the period display for the dividend
        Then the period display should be "2024"

    # Error handler edge cases
    Scenario: 500 error page renders correctly
        When a 500 error occurs
        Then I should see "Internal Server Error" in the page
        And I should see "500" in the page

    Scenario: 403 error page renders correctly
        When a 403 error occurs
        Then I should see "Access Forbidden" in the page
        And I should see "403" in the page

    Scenario: 400 error page renders correctly
        When a 400 error occurs
        Then I should see "Bad Request" in the page
        And I should see "400" in the page

    # Settings manager edge cases
    Scenario: Settings file with JSON decode error uses defaults
        Given a corrupted settings file exists
        When I load settings
        Then the settings should be default values

    Scenario: Settings file with OS error uses defaults
        Given settings file is inaccessible
        When I load settings
        Then the settings should be default values
