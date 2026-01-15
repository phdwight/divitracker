@user @portfolio
Feature: Portfolio Summary
    As an investor
    I want to see a summary of my portfolio
    So that I can understand my overall investment performance

    Background:
        Given the application is configured for testing

    Scenario: Empty portfolio summary
        Given no investments exist
        When I request the portfolio summary
        Then the total invested should be 0 dollars
        And the total annual dividends should be 0 dollars
        And the overall yield should be 0.0 percent

    Scenario: Portfolio summary with single investment
        Given an investment "Growth Fund" with 10000 dollars exists
        And the investment has quarterly dividends of 100 dollars for the current year
        When I request the portfolio summary
        Then the total invested should be 10000 dollars
        And the total annual dividends should be 400 dollars
        And the overall yield should be 4.0 percent

    Scenario: Portfolio summary with multiple investments
        Given an investment "Fund A" with 10000 dollars exists
        And the investment "Fund A" has quarterly dividends of 100 dollars for the current year
        And an investment "Fund B" with 20000 dollars exists
        And the investment "Fund B" has quarterly dividends of 200 dollars for the current year
        When I request the portfolio summary
        Then the total invested should be 30000 dollars
        And the total annual dividends should be 1200 dollars

    Scenario: Portfolio yield excludes investments with zero dividends
        Given an investment "Active Fund" with 10000 dollars exists
        And the investment "Active Fund" has quarterly dividends of 100 dollars for the current year
        And an investment "Dormant Fund" with 20000 dollars exists
        When I request the portfolio summary
        Then the total invested should be 30000 dollars
        And the overall yield should be 4.0 percent

    Scenario: Portfolio summary for a specific year
        Given an investment "Historical Fund" with 15000 dollars exists
        And the investment "Historical Fund" has quarterly dividends of 150 dollars for year 2024
        When I request the portfolio summary for year 2024
        Then the total annual dividends for 2024 should be 600 dollars
