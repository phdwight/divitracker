@user @ui @reports
Feature: UI Reports and Visualizations
    As a user
    I want to view dividend graphs and yield breakdowns through the web interface
    So that I can analyze my investment performance

    Background:
        Given the application is running
        And I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        And the investment has a quarterly dividend of 50 in month 3
        And the investment has a quarterly dividend of 50 in month 6
        And the investment has a quarterly dividend of 50 in month 9

    Scenario: Navigate to dividend graph page
        When I navigate to the dashboard
        And I click on the "Graph" link in navigation
        Then I should be on the "/reports/dividends-chart" page
        And I should see "Dividend Graph" heading

    Scenario: View dividend bar chart
        When I navigate to "/reports/dividends-chart"
        Then I should see the dividend chart canvas
        And I should see dividend data visualization

    Scenario: View cumulative line graph
        When I navigate to "/reports/dividends-chart"
        Then I should see the cumulative total toggle
        And the cumulative line should be visible on the chart

    Scenario: Toggle cumulative line graph
        When I navigate to "/reports/dividends-chart"
        And I click the "Show Cumulative Total" toggle
        Then the cumulative line should be hidden or shown

    Scenario: Filter dividend chart by year
        When I navigate to "/reports/dividends-chart"
        And I select the current year from the year filter dropdown
        Then the chart should show only current year data
        And I should see filtered dividend amounts

    Scenario: Filter dividend chart by investment
        Given I have an investment "Google LLC" with ticker "GOOGL" and amount 5000
        And the "Google LLC" investment has a quarterly dividend of 30 in month 3
        When I navigate to "/reports/dividends-chart"
        And I select "Apple Inc" from the investment filter dropdown
        Then the chart should show only "Apple Inc" dividend data

    Scenario: View dividend data table
        When I navigate to "/reports/dividends-chart"
        Then I should see the dividend data table
        And the table should have columns "Period", "Amount", "Cumulative Total"
        And I should see 3 rows in the data table

    Scenario: View chart summary statistics
        When I navigate to "/reports/dividends-chart"
        Then I should see "Total Displayed" statistic
        And I should see "Highest" dividend statistic
        And the statistics should show correct values

    Scenario: Navigate to yield breakdown page
        When I navigate to the dashboard
        And I click on the "Annualized Yield" card
        Then I should be on the "/reports/yield-breakdown" page
        And I should see "Annualized Yield Calculation" heading

    Scenario: View yield calculation formula
        When I navigate to "/reports/yield-breakdown"
        Then I should see the yield calculation formula
        And I should see "Annual Dividends / Average Investment Balance"

    Scenario: View per-investment yield breakdown
        When I navigate to "/reports/yield-breakdown"
        Then I should see the investment breakdown section
        And I should see "Apple Inc" in the breakdown
        And I should see the investment's contribution to overall yield

    Scenario: View yield breakdown with multiple investments
        Given I have an investment "Google LLC" with ticker "GOOGL" and amount 5000
        And the "Google LLC" investment has a quarterly dividend of 30 in month 3
        When I navigate to "/reports/yield-breakdown"
        Then I should see both "Apple Inc" and "Google LLC" in the breakdown
        And each investment should show its yield percentage

    Scenario: Filter yield breakdown by year
        When I navigate to "/reports/yield-breakdown"
        And I select the current year from the year filter
        Then the calculation should show only current year dividends
        And the yield should be calculated for the selected year

    Scenario: Print yield breakdown
        When I navigate to "/reports/yield-breakdown"
        And I trigger the print function
        Then the page should be formatted for printing

    Scenario: View empty dividend chart
        Given I navigate to "/reports/dividends-chart"
        And there are no dividends recorded
        Then I should see an empty state message
        And I should see a link to add dividends

    Scenario: View yield breakdown with no dividends
        Given there are no dividends recorded
        When I navigate to "/reports/yield-breakdown"
        Then I should see zero yield calculation
        And I should see an empty state message
