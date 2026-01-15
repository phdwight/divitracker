@user @dividends
Feature: Annual Dividends Calculation
    As an investor
    I want to see my annual dividend totals
    So that I can track my yearly dividend income

    Background:
        Given the application is configured for testing

    Scenario: Calculate annual dividends with monthly payments
        Given an investment "Monthly Payer" with 10000 dollars exists
        And I recorded 12 monthly dividends of 100 dollars each for the current year
        When I calculate the annual dividends
        Then the annual dividend total should be 1200 dollars

    Scenario: Calculate annual dividends with quarterly payments
        Given an investment "Quarterly Payer" with 10000 dollars exists
        And I recorded 4 quarterly dividends of 250 dollars each for the current year
        When I calculate the annual dividends
        Then the annual dividend total should be 1000 dollars

    Scenario: Calculate annual dividends with mixed frequencies
        Given an investment "Mixed Payer" with 10000 dollars exists
        And I recorded a quarterly dividend of 100 dollars for month 3
        And I recorded a quarterly dividend of 100 dollars for month 6
        And I recorded a monthly dividend of 50 dollars for month 7
        And I recorded a monthly dividend of 50 dollars for month 8
        When I calculate the annual dividends
        Then the annual dividend total should be 300 dollars

    Scenario: Calculate annual dividends with varying amounts
        Given an investment "Variable Payer" with 10000 dollars exists
        And I recorded a quarterly dividend of 100 dollars for month 3
        And I recorded a quarterly dividend of 150 dollars for month 6
        And I recorded a quarterly dividend of 120 dollars for month 9
        When I calculate the annual dividends
        Then the annual dividend total should be 370 dollars

    Scenario: Calculate annual dividends for a specific year
        Given an investment "Historical" with 10000 dollars exists
        And I recorded 4 quarterly dividends of 100 dollars each for year 2024
        When I calculate the annual dividends for year 2024
        Then the annual dividend total should be 400 dollars

    Scenario: Calculate annual dividends with no dividends
        Given an investment "New Investment" with 10000 dollars exists
        When I calculate the annual dividends
        Then the annual dividend total should be 0 dollars

    Scenario: Total dividends received across all time
        Given an investment "Long Term" with 10000 dollars exists
        And I recorded 4 quarterly dividends of 100 dollars each for year 2024
        And I recorded 4 quarterly dividends of 150 dollars each for year 2025
        When I calculate the total dividends received
        Then the total should be 1000 dollars
