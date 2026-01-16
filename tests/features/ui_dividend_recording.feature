@user @ui @dividends
Feature: UI Dividend Recording
    As a user
    I want to record and manage dividends through the web interface
    So that I can track my investment income

    Background:
        Given the application is running
        And I have an investment "Apple Inc" with ticker "AAPL" and amount 10000

    Scenario: Navigate to add dividend page
        When I navigate to the dashboard
        And I click on the "Add Dividend" link
        Then I should be on the "/dividends/new" page
        And I should see "Record Dividend" heading

    Scenario: Record a quarterly dividend
        When I navigate to "/dividends/new"
        And I select "Apple Inc" from the investment dropdown
        And I enter "50" in the dividend amount field
        And I select "Quarterly" from the frequency dropdown
        And I click the "Record Dividend" button
        Then I should be redirected to the dashboard
        And I should see a success message
        And the dividend should be recorded

    Scenario: Record a monthly dividend with period
        When I navigate to "/dividends/new"
        And I select "Apple Inc" from the investment dropdown
        And I enter "25" in the dividend amount field
        And I select "Monthly" from the frequency dropdown
        And I select month "3" from the period month dropdown
        And I click the "Record Dividend" button
        Then I should be redirected to the dashboard
        And I should see a success message

    Scenario: Record a semi-annual dividend
        When I navigate to "/dividends/new"
        And I select "Apple Inc" from the investment dropdown
        And I enter "100" in the dividend amount field
        And I select "Semi-Annual" from the frequency dropdown
        And I click the "Record Dividend" button
        Then I should be redirected to the dashboard
        And the dividend should be recorded

    Scenario: Record a yearly dividend
        When I navigate to "/dividends/new"
        And I select "Apple Inc" from the investment dropdown
        And I enter "200" in the dividend amount field
        And I select "Yearly" from the frequency dropdown
        And I click the "Record Dividend" button
        Then I should be redirected to the dashboard
        And the dividend should be recorded

    Scenario: Record dividend with investment amount
        When I navigate to "/dividends/new"
        And I select "Apple Inc" from the investment dropdown
        And I enter "50" in the dividend amount field
        And I select "Quarterly" from the frequency dropdown
        And I enter "10500" in the investment amount at time field
        And I click the "Record Dividend" button
        Then I should be redirected to the dashboard
        And the dividend should be recorded with investment amount

    Scenario: Edit dividend
        Given the investment has a quarterly dividend of 50 in month 3
        When I navigate to the dashboard
        And I click on the first dividend in the history
        And I click on the "Edit" button
        Then I should be on the edit dividend page
        And the amount field should contain "50"
        When I enter "60" in the dividend amount field
        And I click the "Update Dividend" button
        Then I should be redirected to the dashboard
        And the dividend amount should be updated to 60

    Scenario: Delete dividend
        Given the investment has a quarterly dividend of 50 in month 3
        When I navigate to the investment details page for "Apple Inc"
        And I click on the "Delete" button for the first dividend
        Then I should see a confirmation dialog
        When I confirm the deletion
        Then the dividend should be removed from the history

    Scenario: View dividend yield preview
        When I navigate to "/dividends/new"
        And I select "Apple Inc" from the investment dropdown
        And I enter "50" in the dividend amount field
        And I select "Quarterly" from the frequency dropdown
        Then I should see the yield preview section
        And the preview should show the projected annual dividend
        And the preview should show the projected yield percentage

    Scenario: Record dividend with notes
        When I navigate to "/dividends/new"
        And I select "Apple Inc" from the investment dropdown
        And I enter "50" in the dividend amount field
        And I select "Quarterly" from the frequency dropdown
        And I enter "Q1 dividend payment" in the notes field
        And I click the "Record Dividend" button
        Then I should be redirected to the dashboard
        And the dividend should be recorded with notes

    Scenario: Validation - empty dividend amount
        When I navigate to "/dividends/new"
        And I select "Apple Inc" from the investment dropdown
        And I select "Quarterly" from the frequency dropdown
        And I click the "Record Dividend" button
        Then I should see a validation error for the amount field

    Scenario: Validation - no investment selected
        When I navigate to "/dividends/new"
        And I enter "50" in the dividend amount field
        And I select "Quarterly" from the frequency dropdown
        And I click the "Record Dividend" button
        Then I should see a validation error for the investment field
