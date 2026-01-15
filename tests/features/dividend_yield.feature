@user @dividends
Feature: Dividend Yield Calculation
    As an investor
    I want to see accurate dividend yield calculations
    So that I can understand the return on my investments

    Background:
        Given the application is configured for testing

    Scenario: Calculate yield with constant investment balance
        Given I have an investment "ACME Corp" with 10000 dollars invested
        And I recorded 4 quarterly dividends of 100 dollars each for the current year
        When I calculate the dividend yield
        Then the yield should be 4.00 percent

    Scenario: Calculate yield with changing investment balance using average
        Given I have an investment "Growth Fund" with 15000 dollars currently invested
        And I recorded a Q1 dividend of 100 dollars with investment balance of 10000
        And I recorded a Q2 dividend of 100 dollars with investment balance of 12000
        And I recorded a Q3 dividend of 100 dollars with investment balance of 14000
        And I recorded a Q4 dividend of 100 dollars with investment balance of 15000
        When I calculate the dividend yield
        Then the average investment balance should be 12750 dollars
        And the yield should be 3.14 percent

    Scenario: Calculate yield with no dividends recorded
        Given I have an investment "New Fund" with 5000 dollars invested
        And no dividends have been recorded for the current year
        When I calculate the dividend yield
        Then the yield should be 0.00 percent

    Scenario: Calculate yield with zero investment
        Given I have an investment "Empty Fund" with 0 dollars invested
        When I calculate the dividend yield
        Then the yield should be 0.00 percent

    Scenario: Fall back to total invested when no investment amounts recorded
        Given I have an investment "Legacy Fund" with 10000 dollars invested
        And I recorded a Q1 dividend of 50 dollars without investment balance
        And I recorded a Q2 dividend of 50 dollars without investment balance
        When I get the investment amount for yield calculation
        Then the investment amount should be 10000 dollars

    Scenario: Calculate yield for a specific past year
        Given I have an investment "Historical Fund" with 20000 dollars currently invested
        And I recorded a Q1 dividend of 200 dollars with investment balance of 15000 for year 2024
        And I recorded a Q2 dividend of 200 dollars with investment balance of 16000 for year 2024
        When I calculate the dividend yield for year 2024
        Then the average investment balance should be 15500 dollars
        And the yield should be 2.58 percent

    Scenario: Investment amount averages only dividends with recorded amounts
        Given I have an investment "Mixed Fund" with 20000 dollars currently invested
        And I recorded a Q1 dividend of 100 dollars with investment balance of 10000
        And I recorded a Q2 dividend of 100 dollars without investment balance
        And I recorded a Q3 dividend of 100 dollars with investment balance of 14000
        When I get the investment amount for yield calculation
        Then the average investment balance should be 12000 dollars
