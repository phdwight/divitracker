@user @ui @portfolio
Feature: UI Dashboard Operations
    As a user
    I want to interact with the DiviTracker dashboard through the web interface
    So that I can view and manage my portfolio

    Background:
        Given the application is running

    Scenario: View empty dashboard
        When I navigate to the dashboard
        Then I should see the page title "Dashboard - DiviTracker"
        And I should see "No investments yet" on the page
        And I should see the "Add Investment" link

    Scenario: View dashboard with investments
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        When I navigate to the dashboard
        Then I should see the page title "Dashboard - DiviTracker"
        And I should see "Apple Inc" on the page
        And I should see "AAPL" on the page
        And I should not see "No investments yet" on the page

    Scenario: Filter dashboard by year
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        And the investment has a quarterly dividend of 50 in month 3
        When I navigate to the dashboard
        And I select the current year from the year filter
        Then I should see "Apple Inc" on the page

    Scenario: Toggle hide zero dividends
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        And I have an investment "Google LLC" with ticker "GOOGL" and amount 5000
        And the investment "Apple Inc" has a quarterly dividend of 50 in month 3
        When I navigate to the dashboard
        And I toggle the "Hide investments with zero dividends" checkbox
        Then I should see "Apple Inc" on the page
        And I should not see "Google LLC" on the page

    Scenario: View portfolio summary
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        And the investment has a quarterly dividend of 50 in month 3
        When I navigate to the dashboard
        Then I should see "Total Invested" on the page
        And I should see "Annual Dividends" on the page
        And I should see "Annualized Yield" on the page

    Scenario: Change items per page
        Given I have 15 investments
        When I navigate to the dashboard with hide_zero disabled
        And I select "5" items per page
        Then I should see pagination controls
        And I should see page navigation

    Scenario: Navigate through pages
        Given I have 15 investments
        When I navigate to the dashboard with hide_zero disabled
        And I select "5" items per page
        And I click on the "Next" page link
        Then I should be on page 2
