@user @dividends
Feature: Dividend Recording
    As an investor
    I want to record dividend payments
    So that I can track my dividend income

    Background:
        Given the application is configured for testing
        And an investment "Dividend Stock" with ticker "DIV" and 10000 dollars exists

    # Creating dividends
    Scenario: Record a quarterly dividend
        When I record a dividend of 100 dollars with frequency "quarterly" for "Dividend Stock"
        Then the dividend should be recorded successfully
        And the dividend should have amount 100 dollars
        And the dividend should have frequency "quarterly"

    Scenario: Record a monthly dividend with notes
        When I record a dividend of 50 dollars with frequency "monthly" and notes "January payment" for "Dividend Stock"
        Then the dividend should be recorded successfully
        And the dividend notes should be "January payment"

    Scenario: Record dividend with investment amount at time
        When I record a dividend of 100 dollars with frequency "monthly" and investment balance 5000 for "Dividend Stock"
        Then the dividend should be recorded successfully
        And the dividend investment amount at time should be 5000 dollars
        And the dividend yield at time should be 24.0 percent

    Scenario: Record dividend without selecting investment fails
        When I try to record a dividend of 100 dollars with frequency "monthly" without an investment
        Then I should see a validation error containing "required"

    Scenario: Record dividend with zero amount fails
        When I try to record a dividend of 0 dollars with frequency "monthly" for "Dividend Stock"
        Then I should see a validation error containing "positive"

    Scenario: Record dividend with invalid frequency fails
        When I try to record a dividend of 100 dollars with frequency "weekly" for "Dividend Stock"
        Then I should see a validation error containing "invalid frequency"

    Scenario: Record dividend for non-existent investment fails
        When I try to record a dividend of 100 dollars for investment ID 99999
        Then I should see a not found error

    # Updating dividends
    Scenario: Update dividend amount and frequency
        Given a dividend of 50 dollars with frequency "quarterly" exists for "Dividend Stock"
        When I update the dividend to 150 dollars with frequency "monthly"
        Then the dividend should have amount 150 dollars
        And the dividend should have frequency "monthly"

    Scenario: Update dividend with period information
        Given a dividend of 100 dollars with frequency "quarterly" exists for "Dividend Stock"
        When I update the dividend with period month 8 and year 2025
        Then the dividend period month should be 8
        And the dividend period year should be 2025

    # Deleting dividends
    Scenario: Delete a dividend
        Given a dividend of 100 dollars with frequency "quarterly" exists for "Dividend Stock"
        When I delete the dividend
        Then the dividend should no longer exist

    Scenario: Delete non-existent dividend fails
        When I try to delete a dividend with ID 99999
        Then I should see a not found error

    # Annualized calculations
    Scenario: Calculate annualized amount for monthly dividend
        When I record a dividend of 100 dollars with frequency "monthly" for "Dividend Stock"
        Then the annualized amount should be 1200 dollars

    Scenario: Calculate annualized amount for quarterly dividend
        When I record a dividend of 250 dollars with frequency "quarterly" for "Dividend Stock"
        Then the annualized amount should be 1000 dollars

    Scenario: Calculate annualized amount for yearly dividend
        When I record a dividend of 500 dollars with frequency "yearly" for "Dividend Stock"
        Then the annualized amount should be 500 dollars
