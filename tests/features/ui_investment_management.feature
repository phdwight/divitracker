@user @ui @investments
Feature: UI Investment Management
    As a user
    I want to manage my investments through the web interface
    So that I can track my portfolio

    Background:
        Given the application is running

    Scenario: Navigate to add investment page
        When I navigate to the dashboard
        And I click on the "Add Investment" link
        Then I should be on the "/investments/new" page
        And I should see "Add Investment" heading

    Scenario: Add a new investment successfully
        When I navigate to "/investments/new"
        And I enter "Apple Inc" in the name field
        And I enter "AAPL" in the ticker field
        And I enter "10000" in the amount field
        And I click the "Add Investment" button
        Then I should be redirected to the dashboard
        And I should see a success message
        And I should see "Apple Inc" on the page

    Scenario: Add investment without ticker
        When I navigate to "/investments/new"
        And I enter "Microsoft Corp" in the name field
        And I enter "15000" in the amount field
        And I click the "Add Investment" button
        Then I should be redirected to the dashboard
        And I should see "Microsoft Corp" on the page

    Scenario: View investment details
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        When I navigate to the dashboard
        And I click on the "Apple Inc" investment link
        Then I should be on the investment details page
        And I should see "Apple Inc" heading
        And I should see "AAPL" on the page
        And I should see "10000" on the page

    Scenario: Edit investment
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        When I navigate to the investment details page for "Apple Inc"
        And I click on the "Edit" button
        Then I should be on the edit investment page
        And the name field should contain "Apple Inc"
        And the ticker field should contain "AAPL"
        And the amount field should contain "10000"
        When I enter "12000" in the amount field
        And I click the "Update Investment" button
        Then I should be redirected to the dashboard
        And I should see "12000" on the page

    Scenario: Delete investment confirmation
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        When I navigate to the investment details page for "Apple Inc"
        And I click on the "Delete" button
        Then I should see a confirmation dialog
        When I confirm the deletion
        Then I should be redirected to the dashboard
        And I should not see "Apple Inc" on the page

    Scenario: Cancel investment deletion
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        When I navigate to the investment details page for "Apple Inc"
        And I click on the "Delete" button
        And I cancel the deletion
        Then I should still see "Apple Inc" on the page

    Scenario: View investment with dividend history
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        And the investment has a quarterly dividend of 50 in month 3
        And the investment has a quarterly dividend of 50 in month 6
        When I navigate to the investment details page for "Apple Inc"
        Then I should see the dividend history
        And I should see 2 dividend records

    Scenario: Add investment with existing name
        Given I have an investment "Apple Inc" with ticker "AAPL" and amount 10000
        When I navigate to "/investments/new"
        And I enter "Apple Inc" in the name field
        And I enter "5000" in the amount field
        And I click the "Add Investment" button
        Then I should be redirected to the dashboard
        And the "Apple Inc" investment should show total amount "15000"
