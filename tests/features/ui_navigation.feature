@user @ui @navigation
Feature: UI Navigation and Routing
    As a user
    I want to navigate through the application interface
    So that I can access different features easily

    Background:
        Given the application is running

    Scenario: View navigation bar
        When I navigate to the dashboard
        Then I should see the navigation bar
        And I should see the "DiviTracker" logo
        And I should see "Add Investment" link in navigation
        And I should see "Add Dividend" link in navigation
        And I should see "Graph" link in navigation
        And I should see "Settings" link in navigation

    Scenario: Navigate using logo
        Given I am on any page in the application
        When I click on the "DiviTracker" logo
        Then I should be redirected to the dashboard

    Scenario: Navigate to investment page via link
        When I navigate to the dashboard
        And I click on "Add Investment" in navigation
        Then I should be on the "/investments/new" page

    Scenario: Navigate to dividend page via link
        When I navigate to the dashboard
        And I click on "Add Dividend" in navigation
        Then I should be on the "/dividends/new" page

    Scenario: Navigate to graph page via link
        When I navigate to the dashboard
        And I click on "Graph" in navigation
        Then I should be on the "/reports/dividends-chart" page

    Scenario: Navigate to settings page via link
        When I navigate to the dashboard
        And I click on "Settings" in navigation
        Then I should be on the "/settings/" page

    Scenario: Back navigation works correctly
        When I navigate to the dashboard
        And I click on "Add Investment" in navigation
        And I click the browser back button
        Then I should be on the dashboard

    Scenario: Direct URL navigation
        When I navigate directly to "/investments/new"
        Then I should be on the "/investments/new" page
        And the page should load successfully

    Scenario: 404 page for invalid URL
        When I navigate to "/invalid-page-url"
        Then I should see a 404 error page
        And I should see "Page Not Found" message
        And I should see a link back to the dashboard

    Scenario: Breadcrumb navigation on investment details
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        When I navigate to the investment details page for "Apple Inc"
        Then I should see breadcrumb navigation
        And the breadcrumb should show "Dashboard > Apple Inc"

    Scenario: Active navigation indicator
        When I navigate to the dashboard
        Then the "Dashboard" link should be highlighted as active
        When I click on "Graph" in navigation
        Then the "Graph" link should be highlighted as active

    Scenario: Mobile responsive navigation
        Given I am viewing on a mobile device
        When I navigate to the dashboard
        Then I should see a mobile-friendly navigation menu
        And all navigation links should be accessible

    Scenario: Keyboard navigation
        When I navigate to the dashboard
        And I press the Tab key repeatedly
        Then the focus should move through navigation links
        And I should be able to activate links with Enter key

    Scenario: Navigation with unsaved changes warning
        When I navigate to "/investments/new"
        And I enter "Apple Inc" in the name field
        And I click on "Dashboard" in navigation
        Then I might see an unsaved changes warning
